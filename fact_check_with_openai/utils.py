import os, time, traceback, requests, urllib.parse, json
from typing import List, Dict, Tuple
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime

load_dotenv()

SERPAPI_KEY = os.getenv("SERPAPI_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
SERPAPI_HL = os.getenv("SERPAPI_HL", "ar")
SERPAPI_GL = os.getenv("SERPAPI_GL", "")
NEWS_AGENCIES = [d.strip() for d in os.getenv("NEWS_AGENCIES", "aljazeera.net,una-oic.org,bbc.com").split(",") if d.strip()]

if not SERPAPI_KEY or not OPENAI_API_KEY:
    raise RuntimeError("⚠️ رجاءً ضع SERPAPI_KEY و OPENAI_API_KEY في .env")

client = OpenAI(api_key=OPENAI_API_KEY)


# -------------------- Helpers --------------------
def _domain_of(url: str) -> str:
    try:
        netloc = urllib.parse.urlparse(url).netloc.lower()
        if netloc.startswith("www."):
            netloc = netloc[4:]
        return netloc
    except Exception:
        return ""

def _dedupe(results: List[Dict]) -> List[Dict]:
    seen = set()
    out = []
    for r in results:
        link = r.get("link") or r.get("url") or ""
        key = link.strip()
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out

def _fetch_serp(q: str, num_results: int = 10, retries: int = 2, backoff: float = 1.5,
                extra_params: Dict | None = None) -> Dict:
    url = "https://serpapi.com/search.json"
    params = {
        "q": q,
        "api_key": SERPAPI_KEY,
        "hl": SERPAPI_HL,
        "gl": SERPAPI_GL,
        "num": num_results
    }
    if extra_params:
        params.update(extra_params)
    for attempt in range(retries + 1):
        try:
            r = requests.get(url, params=params, timeout=25)
            r.raise_for_status()
            return r.json()
        except Exception:
            if attempt == retries:
                raise
            time.sleep(backoff ** attempt)
    return {}

def _to_items(data: Dict) -> List[Dict]:
    items = []
    for it in data.get("organic_results", []):
        items.append({
            "title": it.get("title") or "",
            "snippet": it.get("snippet") or (it.get("snippet_highlighted_words", [""]) or [""])[0],
            "link": it.get("link") or it.get("displayed_link") or "",
        })
    # نظّف الفارغ
    return [x for x in items if x["title"] or x["snippet"] or x["link"]]


# -------------------- Searches --------------------
def search_general(query: str, n: int = 10, serp_extra: Dict | None = None) -> List[Dict]:
    data = _fetch_serp(query, num_results=n, extra_params=serp_extra)
    return _to_items(data)[:n]

def search_agencies(query: str, agencies: List[str], per_site: int = 4,
                    serp_extra: Dict | None = None) -> List[Dict]:
    all_items = []
    for d in agencies:
        q = f"{query} site:{d}"
        data = _fetch_serp(q, num_results=per_site, extra_params=serp_extra)
        items = _to_items(data)[:per_site]
        all_items.extend(items)
    return all_items

def search_news(query: str, n: int = 10, when: str = "1d") -> List[Dict]:
    data = _fetch_serp(query, num_results=n, extra_params={
        "engine": "google_news",
        "when": when
    })
    items = []
    for it in data.get("news_results", []):
        items.append({
            "title": it.get("title") or "",
            "snippet": it.get("snippet") or "",
            "link": it.get("link") or "",
            "date": it.get("date") or ""
        })
    return [x for x in items if x["title"] or x["snippet"] or x["link"]]

def mixed_search(query: str, agencies: List[str], general_top: int = 12, per_site: int = 5,
                 max_total: int = 30, intent: dict | None = None) -> List[Dict]:
    intent = intent or {"temporal": {"type":"none","window_hours":0,"date_iso":""}}
    t_type = intent["temporal"]["type"]
    win_h = intent["temporal"]["window_hours"]
    date_iso = intent["temporal"]["date_iso"]

    news_when = ""
    serp_extra = None  # <-- دا اللي هنمرّره لـ SerpAPI

    if t_type == "same_day":
        news_when = "4h" if win_h and win_h <= 12 else "1d"
        serp_extra = {"tbs": ("qdr:h" if win_h and win_h <= 12 else "qdr:d")}
    elif t_type == "specific_date" and date_iso:
        mmdd = _date_mmddyyyy(date_iso)
        if mmdd:
            serp_extra = {"tbs": f"cdr:1,cd_min:{mmdd},cd_max:{mmdd}"}

    # 1) وكالات
    agency_items = search_agencies(query, agencies, per_site=per_site, serp_extra=serp_extra)

    # 2) أخبار حديثة
    news_items = search_news(query, n=10, when=news_when) if news_when else []

    # 3) ويب عام
    general_items = search_general(query, n=general_top, serp_extra=serp_extra)

    combined = _dedupe(agency_items + news_items + general_items)
    for it in combined:
        it["domain"] = _domain_of(it.get("link",""))
    return combined[:max_total]

def _lang_hint_from_claim(text: str) -> str:
    """
    تخمين بسيط للغة الادعاء:
    - لو فيه حروف عربية بنسبة معتبرة → ar
    - غير كده → en (تقدر توسّع لاحقاً)
    """
    if not text:
        return "en"
    ar_count = sum(1 for ch in text if '\u0600' <= ch <= '\u06FF')
    ratio = ar_count / max(1, len(text))
    return "ar" if ratio >= 0.15 else "en"


# ====== Intent extraction (language + time intent) ======
INTENT_SYS = (
    "You are a multilingual information extraction assistant. "
    "Given a claim in ANY language, extract structured intent.\n"
    "Return STRICT JSON with keys: "
    '{"lang_hint","temporal":{"type","window_hours","date_iso"},"entities","keywords"}.\n'
    "- lang_hint: BCP-47 like 'ar','en','fr',... inferred from the claim language.\n"
    "- temporal.type ∈ {\"same_day\",\"specific_date\",\"none\"}.\n"
    "- temporal.window_hours: integer (suggest 6-48 when type=same_day; else 0).\n"
    "- temporal.date_iso: ISO date 'YYYY-MM-DD' if the claim mentions a specific date; otherwise empty.\n"
    "- entities: list of salient places/persons/orgs as strings (optional, short).\n"
    "- keywords: short list of 3–8 search terms (no URLs), in the claim language.\n"
    "Output JSON only."
)

def analyze_claim_intent(claim_text: str) -> dict:
    resp = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": INTENT_SYS},
            {"role": "user", "content": claim_text.strip()},
        ],
        temperature=0.0,
    )
    raw = (resp.choices[0].message.content or "").strip()
    try:
        intent = json.loads(raw)
    except Exception:
        # فولباك بسيط لو حصل شيء
        intent = {
            "lang_hint": _lang_hint_from_claim(claim_text),
            "temporal": {"type": "none", "window_hours": 0, "date_iso": ""},
            "entities": [],
            "keywords": []
        }
    # حراسة بسيطة
    t = intent.get("temporal") or {}
    intent["temporal"] = {
        "type": t.get("type") if t.get("type") in {"same_day","specific_date","none"} else "none",
        "window_hours": int(t.get("window_hours") or 0),
        "date_iso": t.get("date_iso") or ""
    }
    intent["lang_hint"] = intent.get("lang_hint") or _lang_hint_from_claim(claim_text)
    return intent


def _date_mmddyyyy(iso: str) -> str:
    try:
        dt = datetime.strptime(iso, "%Y-%m-%d")
        return dt.strftime("%m/%d/%Y")
    except Exception:
        return ""



FACT_PROMPT_SYSTEM = (
    "You are a rigorous fact-checking assistant. Use ONLY the sources provided below.\n"
    "- If evidence is insufficient, conflicting, or off-topic, the verdict must be: Uncertain.\n"
    "- Prefer official catalogs and reputable agencies over blogs or social posts.\n"
    "- Match the claim's date/place/magnitude when relevant; do not infer beyond the given sources.\n\n"
    f"- answer in langauge of the query (LANG_HINT).\n\n"
    "LANG POLICY:\n"
    "• You MUST write **all free-text fields** in the language specified by LANG_HINT below.\n"
    "• Keep JSON KEYS EXACTLY as: \"الحالة\", \"talk\", \"sources\" (do not translate keys).\n"
    "• The value of \"الحالة\" must be localized to LANG_HINT "
    "(Arabic: حقيقي/كاذب/غير مؤكد; English: True/False/Uncertain; French: Vrai/Faux/Incertain; etc.).\n"
    "• In the closing paragraph label inside \"talk\", use a localized label in LANG_HINT "
    "(Arabic: \"روابط رئيسية:\"; English: \"Key sources:\"), and number items according to that locale.\n\n"
    "RESPONSE FORMAT (JSON ONLY — no extra text):\n"
    "{\n"
    '  "الحالة": "<Localized verdict>",\n'
    '  "talk": "<A clear paragraph (300–400 words) in LANG_HINT that starts with a decisive sentence about evidence, '
    'then explains why using ONLY the provided sources, and ends with a localized label + a numbered list matching sources order>",\n'
    '  "sources": [ {"title":"<title>","url":"<url>"}, {"title":"<title>","url":"<url>"}, {"title":"<title>","url":"<url>"} ]\n'
    "- add some Diversity in sources"
    "}\n"
    "Rules:\n"
    "1) Output STRICTLY valid JSON (UTF-8). No commentary before/after.\n"
    "2) In \"talk\", the closing section must include a localized label followed by a numbered list that EXACTLY matches the order of items in `sources`.\n"
    "3) Do not fabricate or guess URLs or titles. If unsure, keep the array shorter.\n"
)

# -------------------- Main RAG --------------------

def check_fact_with_rag(claim_text: str, k_sources: int = 10) -> dict:
    try:
        # 0) تحليل النية متعدد اللغات
        intent = analyze_claim_intent(claim_text)
        lang_hint = intent.get("lang_hint") or _lang_hint_from_claim(claim_text)

        # 1) جمع النتائج مع مراعاة النية
        results = mixed_search(
            claim_text,
            agencies=NEWS_AGENCIES,
            general_top=12,
            per_site=5,
            max_total=30,
            intent=intent
        )
        if not results:
            return {"case": "غير مؤكد", "talk": "لم يتم العثور على مصادر كافية حديثة.", "sources": []}

        # 2) بناء السياق أولًا
        def clip(s: str, n: int = 220) -> str:
            s = (s or "").strip()
            return s if len(s) <= n else (s[:n] + "…")

        context_blocks = []
        for it in results:
            title = clip(it.get("title", ""), 160)
            snippet = clip(it.get("snippet", ""), 260)
            link = (it.get("link") or "").strip()
            domain = it.get("domain", "")
            block = f"المصدر: {domain}\nعنوان: {title}\nملخص: {snippet}\nرابط: {link}"
            context_blocks.append(block)
        context_text = "\n\n---\n\n".join(context_blocks)

        # 3) إعداد البرومبت والرسالة
        current_date = datetime.now().strftime("%Y-%m-%d")
        system_prompt = FACT_PROMPT_SYSTEM.replace("LANG_HINT", lang_hint)
        user_msg = (
            f"LANG_HINT: {lang_hint}\n"
            f"CURRENT_DATE: {current_date}\n"
            f"INTENT: {json.dumps(intent, ensure_ascii=False)}\n\n"
            f"الادعاء:\n{claim_text}\n\n"
            f"السياق (لا تستخدم أي معرفة خارج هذه المصادر):\n{context_text}"
        )

        # 4) نداء OpenAI
        resp = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.2,
        )
        answer = (resp.choices[0].message.content or "").strip()

        # 5) Parsing + fallback كما هو عندك
        parsed = None
        try:
            parsed = json.loads(answer)
        except Exception:
            src = _pick_sources_from_results(results, k_sources)
            talk = _fallback_talk(claim_text, src)
            return {"case": "غير مؤكد", "talk": talk, "sources": src}

        sources = list(parsed.get("sources") or [])
        if not sources:
            sm = parsed.get("sources_main") or []
            se = parsed.get("sources_extra") or []
            sources = list(sm) + list(se)
        sources = [s for s in sources if s.get("title") and s.get("url")]

        needed = max(0, k_sources - len(sources))
        if needed:
            seen = {s["url"] for s in sources}
            for it in results:
                link = it.get("link")
                title = (it.get("title") or "").strip()
                if not link or not title or link in seen:
                    continue
                sources.append({"title": title, "url": link})
                seen.add(link)
                needed -= 1
                if needed == 0:
                    break
        sources = sources[:k_sources]

        case = parsed.get("الحالة", "غير مؤكد")
        talk = parsed.get("talk") or _fallback_talk(claim_text, sources)

        return {"case": case, "talk": talk, "sources": sources}

    except Exception as e:
        traceback.print_exc()
        return {"case": "غير مؤكد", "talk": f"⚠️ حدث خطأ أثناء التنفيذ: {e}", "sources": []}


# -------------------- Utilities (fallbacks) --------------------
def _pick_sources_from_results(results: List[Dict], k_sources: int):
    """اختر حتى k_sources من نتائج البحث."""
    picked = []
    seen = set()
    for it in results:
        link = it.get("link")
        title = (it.get("title") or "").strip()
        if not link or not title or link in seen:
            continue
        picked.append({"title": title, "url": link})
        seen.add(link)
        if len(picked) >= k_sources:
            break
    return picked

def _fallback_talk(claim_text: str, sources: List[Dict]) -> str:
    """
    فقرة طويلة شبيهة بـ facticity.ai إذا فشل JSON.
    تستخدم المصادر المعطاة فقط بالصياغة النهائية المطلوبة.
    """
    # جهّز عدّ مرقّم لأول 3 مصادر (أو أقل إن لم تتوفر)
    numbered = []
    for i, s in enumerate(sources[:3], start=1):
        name = s.get("title", "").strip() or "مصدر موثوق"
        numbered.append(f"{i}\u066B {name}")

    base = (
        "لا يتوفر دليل قاطع يؤكد هذا الادعاء وفقًا للمصادر المتاحة ضمن نطاق البحث. "
        "تشير السجلات والتقارير المفتوحة المعتمدة إلى أن الأحداث الكبرى ذات الصلة قد وقعت في تواريخ مختلفة "
        "أو بمقادير لا تتطابق مع تفاصيل الادعاء؛ وبناءً عليه، لا يمكن الجزم بصحته دون أدلة إضافية. "
        "اعتمد هذا الحكم على مراجعة موجزة لمخرجات البحث الموثوقة وأرشيفات الرصد المعروفة، "
        "مع مراعاة التطابق الدقيق في التاريخ والمكان والقدر عند الاقتضاء. "
        "وعند غياب تطابق واضح في تلك العناصر، يكون القرار الأقرب هو عدم التأكد.\n\n"
        "روابط رئيسية:"
    )

    tail = ""
    if numbered:
        tail = "\n" + "\n".join(numbered)
    else:
        tail = "\n١\u066B مصدر موثوق"

    return base + tail
