import os, time, traceback, requests, urllib.parse, json
from typing import List, Dict
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime

load_dotenv()

SERPAPI_KEY = os.getenv("SERPAPI_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
SERPAPI_HL = os.getenv("SERPAPI_HL", "ar")
SERPAPI_GL = os.getenv("SERPAPI_GL", "")
NEWS_AGENCIES = [d.strip() for d in os.getenv("NEWS_AGENCIES", "aljazeera.net,una-oic.org,bbc.com").split(",") if d.strip()]

if not SERPAPI_KEY or not OPENAI_API_KEY:
    raise RuntimeError("⚠️ رجاءً ضع SERPAPI_KEY و OPENAI_API_KEY في .env")

client = OpenAI(api_key=OPENAI_API_KEY)

def _lang_hint_from_claim(text: str) -> str:
    if not text:
        return "en"
    ar_count = sum(1 for ch in text if '\u0600' <= ch <= '\u06FF')
    ratio = ar_count / max(1, len(text))
    return "ar" if ratio >= 0.15 else "en"

def _fetch_serp(query: str, extra: Dict | None = None, num: int = 10) -> List[Dict]:
    url = "https://serpapi.com/search.json"
    params = {
        "q": query,
        "api_key": SERPAPI_KEY,
        "hl": SERPAPI_HL,
        "gl": SERPAPI_GL,
        "num": num
    }
    if extra:
        params.update(extra)
    try:
        print(f"🔍 Fetching: {query}")
        r = requests.get(url, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()
        results = []
        for it in data.get("organic_results", []):
            results.append({
                "title": it.get("title") or "",
                "snippet": it.get("snippet") or (it.get("snippet_highlighted_words", [""]) or [""])[0],
                "link": it.get("link") or it.get("displayed_link") or "",
            })
        print(f"✅ Found {len(results)} results for query: {query}")
        return [r for r in results if r["title"] or r["snippet"] or r["link"]]
    except Exception as e:
        print("❌ Error fetching from SerpAPI:", e)
        return []

FACT_PROMPT_SYSTEM = (
    "You are a rigorous fact-checking assistant. Use ONLY the sources provided below.\n"
    "- If evidence is insufficient, conflicting, or off-topic, the verdict must be: Uncertain.\n"
    "- Prefer official catalogs and reputable agencies over blogs or social posts.\n"
    "- Match the claim's date/place/magnitude when relevant; do not infer beyond the given sources.\n\n"
    "- You MUST respond **entirely** in LANG_HINT language, never translate to another language.\n"
    "- If LANG_HINT is 'fr', response MUST be fully in French.\n"
    "- If LANG_HINT is 'ar', response MUST be fully in Arabic.\n"
    "- If LANG_HINT is 'en', response MUST be fully in English.\n"

    "LANG POLICY:\n"
    "• You MUST write **all free-text fields** in the language specified by LANG_HINT below.\n"
    "• Keep JSON KEYS EXACTLY as: \"الحالة\", \"talk\", \"sources\" (do not translate keys).\n"
    "• The value of \"الحالة\" must be localized to LANG_HINT "
    "(Arabic: حقيقي/كاذب/غير مؤكد; English: True/False/Uncertain).\n"
    "• In the closing paragraph label inside \"talk\", use a localized label in LANG_HINT "
    "(Arabic: \"روابط رئيسية:\"; English: \"Key sources:\").\n\n"
    "RESPONSE FORMAT (JSON ONLY — no extra text):\n"
    "{\n"
    '  "الحالة": "<Localized verdict>",\n'
    '  "talk": "<Explanation paragraph ~350 words>",\n'
    '  "sources": [ {"title":"<title>","url":"<url>"}, ... ]\n'
    "}\n"
    "Rules:\n"
    "1) Output STRICTLY valid JSON (UTF-8). No commentary before/after.\n"
    "2) If claim is uncertain, keep 'sources' empty.\n"
    "3) If verdict is True, return ALL confirming sources (no fixed limit)."
)

def check_fact_simple(claim_text: str, k_sources: int = 5) -> dict:
    try:
        print(f"🧠 Fact-checking: {claim_text}")
        lang = _lang_hint_from_claim(claim_text)

        results = []
        for domain in NEWS_AGENCIES:
            domain_results = _fetch_serp(f"{claim_text} site:{domain}", num=2)
            results += domain_results
        google_results = _fetch_serp(claim_text, num=k_sources)
        results += google_results

        print(f"🔎 Total combined results: {len(results)}")

        if not results:
            return {"case": "غير مؤكد", "talk": "لم يتم العثور على نتائج بحث.", "sources": []}

        def clip(s: str, n: int) -> str:
            return s.strip() if len(s) <= n else s[:n] + "…"

        context = "\n\n---\n\n".join(
            f"عنوان: {clip(r['title'], 100)}\nملخص: {clip(r['snippet'], 200)}\nرابط: {r['link']}"
            for r in results
        )

        system_prompt = FACT_PROMPT_SYSTEM.replace("LANG_HINT", lang)
        user_msg = f"""
LANG_HINT: {lang}
CURRENT_DATE: {datetime.now().strftime('%Y-%m-%d')}

الادعاء:
{claim_text}

السياق:
{context}
""".strip()

        print("📤 Sending prompt to OpenAI")
        resp = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.2,
        )
        answer = (resp.choices[0].message.content or "").strip()
        if answer.startswith("```"):
            answer = answer.strip("` \n")
            if answer.lower().startswith("json"):
                answer = answer[4:].strip()

        parsed = json.loads(answer)

        case = parsed.get("الحالة", "غير مؤكد")
        talk = parsed.get("talk", "")
        sources = parsed.get("sources", [])

        if case == "غير مؤكد" or case.lower() == "uncertain":
            sources = []

        return {"case": case, "talk": talk, "sources": sources}

    except Exception as e:
        print("❌ Error:", traceback.format_exc())
        return {"case": "غير مؤكد", "talk": f"⚠️ حدث خطأ أثناء التحقق: {e}", "sources": []}
