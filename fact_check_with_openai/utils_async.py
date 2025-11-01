import os, traceback, json
import asyncio
import re
from typing import List, Dict
from dotenv import load_dotenv
from openai import AsyncOpenAI
from datetime import datetime
import aiohttp

load_dotenv()

def translate_date_references(text: str) -> str:
    """
    إرجاع النص كما هو دون تغيير المراجع الزمنية
    لتجنب تغيير معنى البحث عند استخدام كلمات مثل "اليوم"
    """
    # إرجاع النص كما هو دون أي تعديل
    return text

async def generate_professional_news_article_from_analysis_async(claim_text: str, case: str, talk: str, sources: List[Dict], lang: str = "ar", client: AsyncOpenAI = None) -> str:
    """
    Generate a professional news article based on fact-check analysis and sources
    Uses the analysis (talk) and sources to create a balanced, journalistic piece
    """
    
    # Prepare sources context
    if not sources:
        sources_context = "No specific sources available for this investigation."
    else:
        sources_context = "\n\n".join([
            f"**Source {i+1}:**\n"
            f"Title: {source.get('title', 'N/A')}\n"
            f"URL: {source.get('url', 'N/A')}\n"
            f"Snippet: {source.get('snippet', 'N/A')}"
            for i, source in enumerate(sources[:5])  # Limit to 5 sources
        ])
    
    # Determine the prompt based on the case
    if case.lower() in {"حقيقي", "true", "vrai", "verdadero", "pravda"}:
        # TRUE case - Use the specific prompt for confirmed news
        FACT_CHECK_NEWS_PROMPT = f"""
You are a senior international news agency journalist writing in {lang.upper()} language.

Write a professional news article in the style of international news agencies based on the provided headline and analysis.

**CRITICAL INSTRUCTIONS FOR TRUE NEWS:**
- Start DIRECTLY with the news event/statement itself (e.g., "اختُتمت اليوم أعمال..." or "Today concluded the works of...")
- Write as a DIRECT NEWS REPORT, NOT as analysis or verification
- First paragraph: Report the main event naturally with details (who, what, when, where, participants, etc.)
- Second paragraph: Discuss the topics, themes, or issues that were addressed/covered
- Third paragraph: Provide additional context about sessions, discussions, or highlights
- AVOID any mention of "verification", "fact-check", "results", "تحقق", "نتائج التحقق" anywhere in the article
- Write naturally and smoothly as if reporting events as they happened
- Mention official sources and statements naturally

**STRUCTURE TEMPLATE FOR TRUE NEWS:**
1. **Opening Paragraph**: Start directly with the event (e.g., "اختُتمت اليوم أعمال..." or "Today concluded...") with key details
2. **Second Paragraph**: Discuss the topics, themes, or issues that were covered
3. **Third Paragraph**: Additional context about sessions, discussions, or highlights

**REQUIREMENTS:**
- Language: {lang.upper()} entirely
- Style: Professional news reporting (like AFP, Reuters, AP)
- Tone: Neutral, factual, authoritative
- Structure: Exactly 3 paragraphs following the template above
- Length: 150-250 words
- Must follow the exact structure template
- Use professional journalistic language
- NO mention of verification or fact-checking
"""
    else:
        # UNCERTAIN case - Use the specific prompt for unconfirmed news
        FACT_CHECK_NEWS_PROMPT = f"""
You are a senior international news agency journalist writing in {lang.upper()} language.

Write a professional news article in the style of international news agencies based on the provided headline and analysis.

**CRITICAL INSTRUCTIONS FOR UNCERTAIN NEWS:**
- Start with: "تداولت منصات التواصل الاجتماعي مزاعم تفيد بأن [الادعاء]" (or equivalent in the target language)
- Follow immediately with: "غير أن نتائج التحقق أظهرت أن هذا الادعاء لا يمكن تأكيده" (or equivalent: "However, verification results showed that this claim cannot be confirmed")
- Then explain the available information and why the claim cannot be confirmed
- Provide historical context or relevant background information if available
- End with a clear conclusion that the claim lacks reliable evidence

**STRUCTURE TEMPLATE:**
1. **Opening**: "تداولت منصات التواصل الاجتماعي مزاعم تفيد بأن [الادعاء]، غير أن نتائج التحقق أظهرت أن هذا الادعاء لا يمكن تأكيده."
2. **Body**: Explain available information, historical context, and evidence that contradicts or doesn't support the claim
3. **Conclusion**: "وبناءً على ذلك، يتبيّن أن الادعاء المتداول يفتقر إلى أي أساس من الأدلة الموثوقة، ولا توجد مصادر تدعم صحته."

**REQUIREMENTS:**
- Language: {lang.upper()} entirely
- Style: Professional news reporting
- Tone: Objective, transparent, informative
- Structure: News article format with structured paragraphs
- Length: 150-250 words
- Must follow the exact structure template above
- Use professional journalistic language
"""
    
    # Create the user message
    if case.lower() in {"حقيقي", "true", "vrai", "verdadero", "pravda"}:
        user_message = f"""
**PROVIDED DATA:**
Headline: {claim_text}
Fact-check Analysis: {talk}

**AVAILABLE SOURCES:**
{sources_context}

**EXAMPLE FORMAT FOR TRUE NEWS (ARABIC):**
اختُتمت اليوم أعمال المؤتمر العدلي الدولي في العاصمة السعودية الرياض، تحت شعار "نُيَسِّر الوصول للعدالة بتقنيات رقمية"، وشارك فيه أكثر من 4000 مشارك، و 50 متحدثاً وخبيراً دوليّاً.

وناقش المؤتمر قضايا عدة أبرزها مستقبل القضاء في ظل التحول الرقمي، والتجارب الدولية في التحول الرقمي، والبعد القانوني للذكاء الاصطناعي، وتوظيف الذكاء الاصطناعي في تحسين العدالة، وتحليل البيانات لتحسين العدالة، ومستقبل الوسائل البديلة لتسوية النزاعات في ظل التحول الرقمي.

وسلَّطت الجلسات الحوارية الضوء على مجموعة من الموضوعات التي تتناول دور التحول الرقمي والذكاء الاصطناعي في المجالين العدلي والقضائي.

**INSTRUCTIONS:**
- Follow the exact structure shown in the example above
- First paragraph: Start directly with the event (who, what, when, where, participants)
- Second paragraph: Discuss the topics, themes, or issues that were covered
- Third paragraph: Additional context about sessions, discussions, or highlights
- Write as a direct news report, NOT as verification or fact-check
- AVOID any mention of "verification", "fact-check", "results", "تحقق", "نتائج التحقق"
- Use the analysis data to inform your reporting, but present it as breaking news
- Adapt the structure to the target language ({lang.upper()}) while maintaining the same meaning
"""
    else:
        user_message = f"""
**PROVIDED DATA:**
Headline: {claim_text}
Fact-check Analysis: {talk}

**AVAILABLE SOURCES:**
{sources_context}

**EXAMPLE FORMAT FOR UNCERTAIN NEWS (ARABIC):**
تداولت منصات التواصل الاجتماعي مزاعم تفيد بأن [الادعاء]، غير أن نتائج التحقق أظهرت أن هذا الادعاء لا يمكن تأكيده.

وبحسب المعلومات المتاحة، [شرح المعلومات المتاحة والسبب في عدم التأكيد]. [معلومات تاريخية أو سياق إذا كان متاحاً].

وبناءً على ذلك، يتبيّن أن الادعاء المتداول يفتقر إلى أي أساس من الأدلة الموثوقة، ولا توجد مصادر تدعم صحته.

**INSTRUCTIONS:**
- Follow the exact structure shown in the example above
- Use the analysis data to explain why the claim cannot be confirmed
- Include historical context or relevant background when available
- End with the conclusion that the claim lacks reliable evidence
- Adapt the structure to the target language ({lang.upper()}) while maintaining the same meaning
"""
    
    try:
        print("📰 Generating news article...")
        
        response = await client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": FACT_CHECK_NEWS_PROMPT}
            ],
            temperature=0.1,  # Very low temperature for factual, measured content
            max_tokens=400,   # Allow enough tokens for 150-250 words
            top_p=0.9,        # Focus on most likely responses
            frequency_penalty=0.1,  # Slight penalty to avoid repetition
            presence_penalty=0.1    # Encourage diverse vocabulary
        )
        
        article = response.choices[0].message.content.strip()
        print("✅ News article generated successfully")
        return article
        
    except Exception as e:
        print(f"❌ Error generating news article: {e}")
        error_messages = {
            "ar": "عذراً، حدث خطأ أثناء كتابة المقال الإخباري. يرجى المحاولة مرة أخرى.",
            "en": "Sorry, an error occurred while writing the news article. Please try again.",
            "fr": "Désolé, une erreur s'est produite lors de la rédaction de l'article de presse. Veuillez réessayer.",
            "es": "Lo siento, ocurrió un error al escribir el artículo de noticias. Por favor, inténtalo de nuevo.",
        }
        return error_messages.get(lang, error_messages["en"])

async def generate_x_tweet_async(claim_text: str, case: str, talk: str, sources: List[Dict], lang: str = "ar", client: AsyncOpenAI = None) -> str:
    """
    Generate a professional X (Twitter) tweet based on fact-check results
    Optimized for X platform with proper formatting and engagement
    """
    
    # X/Twitter specific prompt
    X_TWEET_PROMPT = f"""
You are a professional social media journalist and X (Twitter) content creator with expertise in:

**X PLATFORM EXPERTISE:**
1. **Social Media Journalist**: Create engaging, accurate news content for X
2. **Viral Content Creator**: Understand what drives engagement on X
3. **Fact-Checking Specialist**: Present verified information clearly
4. **Crisis Communication**: Handle sensitive information responsibly
5. **Community Manager**: Engage audiences while maintaining credibility
6. **Digital Storyteller**: Tell compelling stories in limited characters
7. **Breaking News Reporter**: Handle urgent, time-sensitive information
8. **Public Interest Communicator**: Serve public interest on social media

**X PLATFORM REQUIREMENTS:**
- Maximum 280 characters (strict limit)
- Use hashtags strategically (2-3 relevant hashtags)
- Include emojis appropriately for engagement
- Write for mobile-first audience
- Use clear, concise language
- Include call-to-action when appropriate
- Maintain professional credibility
- Respect X community guidelines

**TWEET STRUCTURE FOR FACT-CHECKING:**
1. **Hook**: Attention-grabbing opening
2. **Fact**: Clear statement of the fact-check result
3. **Context**: Brief explanation or key detail
4. **Hashtags**: Relevant, trending hashtags
5. **Emojis**: Strategic use for engagement and clarity

**LANGUAGE POLICY:**
- Write ENTIRELY in {lang.upper()} language
- Use professional but engaging tone
- Adapt to social media communication style
- Maintain journalistic credibility
- Use appropriate emojis for the language/culture

**ENGAGEMENT STRATEGY:**
- Start with compelling hook
- Use numbers/statistics when available
- Include relevant hashtags
- Use emojis strategically
- End with clear conclusion or call-to-action
- Maintain professional credibility

**RESPONSE FORMAT:**
Generate a single, professional X tweet (max 280 characters) that:
- Clearly states the fact-check result
- Engages the audience appropriately
- Maintains journalistic credibility
- Uses relevant hashtags and emojis
- Respects X platform guidelines
"""

    # Prepare context based on fact-check result (only True or Uncertain)
    if case.lower() in {"حقيقي", "true", "vrai", "verdadero", "pravda"}:
        result_emoji = "✅"
        result_text = "حقيقي" if lang == "ar" else "TRUE"
        tone = "confirming"
    else:  # uncertain
        result_emoji = "⚠️"
        result_text = "غير مؤكد" if lang == "ar" else "UNCERTAIN"
        tone = "uncertain"

    # Create the user message
    user_message = f"""
**FACT-CHECK RESULT:**
Claim: {claim_text}
Result: {case} ({result_text})
Analysis: {talk}

**SOURCES:**
{len(sources)} sources available

**INSTRUCTIONS:**
Create a professional X tweet that:
1. Clearly communicates the fact-check result
2. Engages the audience appropriately
3. Uses relevant hashtags and emojis
4. Maintains journalistic credibility
5. Respects X platform guidelines
6. Stays within 280 character limit

**TONE:** {tone}
**LANGUAGE:** {lang.upper()}
**PLATFORM:** X (Twitter)
**CHARACTER LIMIT:** 280 characters maximum
"""

    try:
        print("🐦 Generating X tweet...")
        
        response = await client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": X_TWEET_PROMPT},
                {"role": "user", "content": user_message}
            ],
            temperature=0.3,  # Balanced creativity and accuracy
            max_tokens=100,   # Optimized for tweet length (280 chars max)
            top_p=0.9,
            frequency_penalty=0.1,
            presence_penalty=0.1
        )
        
        tweet = response.choices[0].message.content.strip()
        
        # Ensure tweet is within character limit
        if len(tweet) > 280:
            tweet = tweet[:277] + "..."
        
        print("✅ X tweet generated successfully")
        return tweet
        
    except Exception as e:
        print(f"❌ Error generating X tweet: {e}")
        error_messages = {
            "ar": "⚠️ حدث خطأ أثناء إنشاء التغريدة. يرجى المحاولة مرة أخرى.",
            "en": "⚠️ An error occurred while generating the tweet. Please try again.",
            "fr": "⚠️ Une erreur s'est produite lors de la génération du tweet. Veuillez réessayer.",
            "es": "⚠️ Ocurrió un error al generar el tweet. Por favor, inténtalo de nuevo.",
        }
        return error_messages.get(lang, error_messages["en"])

SERPAPI_KEY = os.getenv("SERPAPI_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
SERPAPI_HL = os.getenv("SERPAPI_HL", "ar")
SERPAPI_GL = os.getenv("SERPAPI_GL", "")
NEWS_AGENCIES = [d.strip() for d in os.getenv("NEWS_AGENCIES", "aljazeera.net,una-oic.org,bbc.com").split(",") if d.strip()]

if not SERPAPI_KEY or not OPENAI_API_KEY:
    raise RuntimeError("⚠️ رجاءً ضع SERPAPI_KEY و OPENAI_API_KEY في .env")

# Create async OpenAI client
async_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

async def _lang_hint_from_claim_async(text: str) -> str:
    try:
        resp = await async_client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "Detect the input language and return ONLY its ISO 639-1 code (like ar, en, fr, es, de)."},
                {"role": "user", "content": text.strip()},
            ],
            temperature=0.0,
            max_tokens=5
        )
        lang = (resp.choices[0].message.content or "").strip().lower()
        if len(lang) == 2:
            return lang
    except Exception:
        pass

    # fallback
    ar_count = sum(1 for ch in text if '\u0600' <= ch <= '\u06FF')
    ratio = ar_count / max(1, len(text))
    return "ar" if ratio >= 0.15 else "en"

async def _fetch_serp_async(session: aiohttp.ClientSession, query: str, extra: Dict | None = None, num: int = 10) -> List[Dict]:
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
        async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=20)) as response:
            response.raise_for_status()
            data = await response.json()
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
        print(f"❌ Error fetching from SerpAPI: {e}")
        return []

FACT_PROMPT_SYSTEM = (
    "You are a rigorous fact-checking assistant. Use ONLY the sources provided below.\n"
    "- You can ONLY return TWO possible verdicts: True OR Uncertain.\n"
    "- If the claim is supported by credible sources with clear evidence → verdict: True\n"
    "- If evidence is insufficient, conflicting, unclear, or off-topic → verdict: Uncertain\n"
    "- IMPORTANT: There is NO 'False' option. If you cannot confirm something as True, mark it as Uncertain.\n"
    "- Prefer official catalogs and reputable agencies over blogs or social posts.\n"
    "- Match the claim's date/place/magnitude when relevant; do not infer beyond the given sources.\n\n"

    "LANGUAGE POLICY:\n"
    "- You MUST respond **entirely** in the language specified by LANG_HINT.\n"
    "- Do NOT switch to another language or translate.\n"
    "- Examples:\n"
    "   • If LANG_HINT = 'fr' → respond fully in French.\n"
    "   • If LANG_HINT = 'ar' → respond fully in Arabic.\n"
    "   • If LANG_HINT = 'en' → respond fully in English.\n"
    "   • If LANG_HINT = 'es' → respond fully in Spanish.\n"
    "   • If LANG_HINT = 'cs' → respond fully in Czech.\n\n"

    "FORMAT RULES:\n"
    "• You MUST write all free-text fields strictly in LANG_HINT language.\n"
    "• JSON keys must remain EXACTLY as: \"الحالة\", \"talk\", \"sources\" (do not translate keys).\n"
    "• The value of \"الحالة\" must be ONLY one of these two options (localized):\n"
    "   - Arabic: حقيقي / غير مؤكد (ONLY these two options)\n"
    "   - English: True / Uncertain (ONLY these two options)\n"
    "   - French: Vrai / Incertain (ONLY these two options)\n"
    "   - Spanish: Verdadero / Incierto (ONLY these two options)\n"
    "   - Czech: Pravda / Nejisté (ONLY these two options)\n"
    "• NEVER use: False, Faux, Falso, Nepravda, كاذب - these are NOT valid options!\n"

    "RESPONSE FORMAT (JSON ONLY — no extra text):\n"
    "{\n"
    '  \"الحالة\": \"<Localized verdict: True OR Uncertain ONLY>\",\n'
    '  \"talk\": \"<Explanation paragraph ~350 words in LANG_HINT>\",\n'
    '  \"sources\": [ {\"title\": \"<title>\", \"url\": \"<url>\"}, ... ]\n'
    "}\n\n"

    "FINAL RULES:\n"
    "1) Output STRICTLY valid JSON (UTF-8). No extra commentary before or after.\n"
    "2) If the claim is Uncertain → keep 'sources' as an empty array [].\n"
    "3) If the claim is True → include ALL confirming sources (no fixed limit).\n"
    "4) Do not fabricate URLs or titles; use only provided sources.\n"
    "5) REMEMBER: You can ONLY return True or Uncertain. There is NO False option.\n"
)


def classify_source_support(source: dict, claim_text: str = "") -> str:
    """
    Classify a source as 'supporting' (مؤيد), 'opposing' (معارض), or 'neutral' (محايد)
    Based on content analysis and alignment with the claim
    """
    url = source.get("url", "").lower()
    title = source.get("title", "").lower()
    snippet = source.get("snippet", "").lower()
    claim_lower = claim_text.lower()
    
    # Supporting indicators (مؤيد)
    supporting_indicators = [
        'confirm', 'confirmed', 'verify', 'verified', 'true', 'accurate', 'correct',
        'support', 'back', 'prove', 'evidence', 'fact', 'reality', 'actual',
        'official', 'announced', 'declared', 'stated', 'reported',
        'تأكيد', 'تأكد', 'صحيح', 'حقيقي', 'دعم', 'إثبات', 'دليل', 'واقع',
        'رسمي', 'أعلن', 'صرح', 'ذكر', 'أفاد'
    ]
    
    # Opposing indicators (معارض)
    opposing_indicators = [
        'deny', 'denied', 'false', 'fake', 'hoax', 'misinformation', 'disinformation',
        'incorrect', 'wrong', 'untrue', 'debunk', 'refute', 'contradict', 'oppose',
        'reject', 'dispute', 'challenge', 'question', 'doubt', 'skeptical',
        'إنكار', 'كاذب', 'مزيف', 'خاطئ', 'خطأ', 'رفض', 'تناقض', 'معارضة',
        'تشكيك', 'شك', 'تساؤل', 'تحدي'
    ]
    
    # Neutral indicators (محايد)
    neutral_indicators = [
        'unclear', 'uncertain', 'unknown', 'investigating', 'pending', 'ongoing',
        'developing', 'breaking', 'update', 'report', 'news', 'analysis',
        'غير واضح', 'غير مؤكد', 'غير معروف', 'تحقيق', 'قيد البحث', 'جاري',
        'تطوير', 'عاجل', 'تحديث', 'تقرير', 'خبر', 'تحليل'
    ]
    
    # Count supporting indicators
    supporting_count = 0
    for indicator in supporting_indicators:
        if indicator in title or indicator in snippet:
            supporting_count += 1
    
    # Count opposing indicators
    opposing_count = 0
    for indicator in opposing_indicators:
        if indicator in title or indicator in snippet:
            opposing_count += 1
    
    # Count neutral indicators
    neutral_count = 0
    for indicator in neutral_indicators:
        if indicator in title or indicator in snippet:
            neutral_count += 1
    
    # Check for social media or blog indicators (usually less reliable)
    social_indicators = ['twitter.com', 'facebook.com', 'instagram.com', 'tiktok.com', 'blog', 'blogspot', 'wordpress.com']
    is_social_media = any(indicator in url for indicator in social_indicators)
    
    # Check for credible news sources
    credible_domains = [
        'reuters.com', 'bbc.com', 'cnn.com', 'ap.org', 'afp.com',
        'aljazeera.com', 'dw.com', 'france24.com', 'rt.com',
        'gov.', 'edu.', 'who.int', 'un.org', 'imf.org', 'worldbank.org',
        'spa.gov.sa', 'wam.ae', 'mena.gov.ae', 'qna.org.qa',
        'alwatan.com.sa', 'okaz.com.sa', 'alriyadh.com',
        'alhayat.com', 'asharqalawsat.com', 'alquds.co.uk'
    ]
    is_credible = any(domain in url for domain in credible_domains)
    
    # Weight the indicators based on credibility
    credibility_weight = 2 if is_credible else 1
    social_media_penalty = 0.5 if is_social_media else 1
    
    # Calculate weighted scores
    supporting_score = supporting_count * credibility_weight * social_media_penalty
    opposing_score = opposing_count * credibility_weight * social_media_penalty
    neutral_score = neutral_count * credibility_weight * social_media_penalty
    
    # Determine classification based on highest score
    if supporting_score > opposing_score and supporting_score > neutral_score:
        return "supporting"
    elif opposing_score > supporting_score and opposing_score > neutral_score:
        return "opposing"
    else:
        return "neutral"


def calculate_source_percentages(sources: list, claim_text: str = "") -> dict:
    """
    Calculate the percentage of supporting, opposing, and neutral sources
    """
    if not sources:
        return {
            "supporting_percentage": 0.0,
            "opposing_percentage": 0.0,
            "neutral_percentage": 0.0,
            "total_sources": 0,
            "supporting_count": 0,
            "opposing_count": 0,
            "neutral_count": 0
        }
    
    supporting_count = 0
    opposing_count = 0
    neutral_count = 0
    
    for source in sources:
        classification = classify_source_support(source, claim_text)
        if classification == "supporting":
            supporting_count += 1
        elif classification == "opposing":
            opposing_count += 1
        else:  # neutral
            neutral_count += 1
    
    total_sources = len(sources)
    supporting_percentage = (supporting_count / total_sources) * 100 if total_sources > 0 else 0
    opposing_percentage = (opposing_count / total_sources) * 100 if total_sources > 0 else 0
    neutral_percentage = (neutral_count / total_sources) * 100 if total_sources > 0 else 0
    
    return {
        "supporting_percentage": round(supporting_percentage, 1),
        "opposing_percentage": round(opposing_percentage, 1),
        "neutral_percentage": round(neutral_percentage, 1),
        "total_sources": total_sources,
        "supporting_count": supporting_count,
        "opposing_count": opposing_count,
        "neutral_count": neutral_count
    }


async def check_fact_simple_async(claim_text: str, k_sources: int = 5, generate_news: bool = False, preserve_sources: bool = False, generate_tweet: bool = False) -> dict:
    try:
        # ترجمة المراجع الزمنية في النص
        processed_claim = translate_date_references(claim_text)
        print(f"🧠 Fact-checking: {processed_claim}")
        
        # Create aiohttp session for parallel HTTP requests
        async with aiohttp.ClientSession() as session:
            # Run language detection and searches in parallel for maximum speed
            lang_task = _lang_hint_from_claim_async(processed_claim)
            
            # Prepare all search queries (start immediately without waiting for language)
            search_tasks = []
            
            # Add news agency searches
            for domain in NEWS_AGENCIES:
                search_tasks.append(
                    _fetch_serp_async(session, f"{processed_claim} site:{domain}", extra=None, num=2)
                )
            
            # Add general Google search
            search_tasks.append(
                _fetch_serp_async(session, processed_claim, extra=None, num=k_sources)
            )
            
            # Execute language detection and all searches in parallel
            print(f"🚀 Running language detection + {len(search_tasks)} parallel search queries...")
            all_results = await asyncio.gather(lang_task, *search_tasks)
            
            # Extract language and search results
            lang = all_results[0]
            search_results = all_results[1:]
            
            # Combine all results
            results = []
            for result_list in search_results:
                results.extend(result_list)

        print(f"🔎 Total combined results: {len(results)}")

        if not results:
            no_results_by_lang = {
                "ar": "لم يتم العثور على نتائج بحث.",
                "en": "No search results were found.",
                "fr": "Aucun résultat de recherche trouvé.",
                "es": "No se encontraron resultados de búsqueda.",
                "cs": "Nebyly nalezeny žádné výsledky vyhledávání.",
                "de": "Es wurden keine Suchergebnisse gefunden.",
                "tr": "Arama sonuçları bulunamadı.",
                "ru": "Результаты поиска не найдены.",
            }
            return {"case": "غير مؤكد", "talk": no_results_by_lang.get(lang, no_results_by_lang["en"]), "sources": [], "news_article": None}

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
{processed_claim}

السياق:
{context}
""".strip()

        print("📤 Sending prompt to OpenAI (fact-checking)")
        resp = await async_client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.2,
            max_tokens=800,  # Enough for comprehensive fact-check
        )
        answer = (resp.choices[0].message.content or "").strip()
        
        # Clean up the answer - remove markdown code blocks if present
        if answer.startswith("```"):
            answer = answer.strip("` \n")
            if answer.lower().startswith("json"):
                answer = answer[4:].strip()
        
        # Try to extract JSON if it's wrapped in other text
        json_match = re.search(r'\{[\s\S]*\}', answer)
        if json_match:
            answer = json_match.group(0)
        
        # Parse JSON with error handling
        try:
            parsed = json.loads(answer)
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON parsing error: {e}")
            print(f"📄 Response content (first 500 chars): {answer[:500]}")
            
            # Try multiple strategies to fix JSON
            parsed = None  # Initialize to track if parsing succeeded
            
            # Strategy 1: Try to find the JSON object in the response
            json_match = re.search(r'\{[\s\S]*\}', answer)
            if json_match:
                answer = json_match.group(0)
                try:
                    parsed = json.loads(answer)
                except json.JSONDecodeError:
                    pass
            
            # Strategy 2: Try to fix unterminated strings
            if parsed is None and "Unterminated string" in str(e):
                # Try to fix by finding the position and closing the string
                # Simple approach: find the last incomplete string and try to close it
                lines = answer.split('\n')
                fixed_lines = []
                for i, line in enumerate(lines):
                    # Check if this line has an unterminated string (odd number of unescaped quotes)
                    unescaped_quotes = [m.start() for m in re.finditer(r'(?<!\\)"', line)]
                    if len(unescaped_quotes) % 2 != 0:
                        # Unterminated string - try to close it at the end
                        if not line.rstrip().endswith('"'):
                            # Add closing quote and remove any trailing incomplete content
                            line = line.rstrip()
                            # Try to find where the string should end
                            last_quote_pos = unescaped_quotes[-1]
                            # If there's content after the last quote, it might be incomplete
                            if len(line) > last_quote_pos + 1:
                                # Check if there's a comma or other valid JSON after
                                remaining = line[last_quote_pos + 1:].strip()
                                if not remaining.startswith(','):
                                    # Likely incomplete - close the string
                                    line = line[:last_quote_pos + 1] + '"'
                            else:
                                line = line + '"'
                    fixed_lines.append(line)
                fixed_answer = '\n'.join(fixed_lines)
                
                try:
                    parsed = json.loads(fixed_answer)
                except json.JSONDecodeError:
                    parsed = None
            
            # Strategy 3: Try to extract fields using regex if parsing still failed
            if parsed is None:
                try:
                    # Extract case
                    case_match = re.search(r'"الحالة"\s*:\s*"([^"]+)"', answer)
                    case = case_match.group(1) if case_match else "غير مؤكد"
                    
                    # Extract talk - handle multi-line strings
                    # First try to find talk field with its value
                    talk_match = re.search(r'"talk"\s*:\s*"((?:[^"\\]|\\.)*)"', answer, re.DOTALL)
                    if not talk_match:
                        # Try simpler pattern
                        talk_match = re.search(r'"talk"\s*:\s*"([^"]*)"', answer)
                    talk = talk_match.group(1) if talk_match else "لا توجد معلومات متاحة."
                    # Clean up escape sequences
                    talk = talk.replace('\\"', '"').replace('\\n', '\n').replace('\\\\', '\\')
                    
                    # Extract sources array
                    sources_match = re.search(r'"sources"\s*:\s*\[(.*?)\]', answer, re.DOTALL)
                    sources = []
                    if sources_match:
                        sources_str = sources_match.group(1)
                        # Try to parse individual source objects
                        source_matches = re.findall(r'\{[^}]*\}', sources_str)
                        for src_match in source_matches:
                            title_match = re.search(r'"title"\s*:\s*"([^"]*)"', src_match)
                            url_match = re.search(r'"url"\s*:\s*"([^"]*)"', src_match)
                            if title_match and url_match:
                                sources.append({
                                    "title": title_match.group(1),
                                    "url": url_match.group(1)
                                })
                    
                    parsed = {
                        "الحالة": case,
                        "talk": talk,
                        "sources": sources
                    }
                except Exception as parse_error:
                    print(f"❌ Failed to parse JSON with all strategies: {parse_error}")
                    # Return uncertain result as fallback
                    return {
                        "case": "غير مؤكد",
                        "talk": "حدث خطأ أثناء معالجة نتائج التحقق. يرجى المحاولة مرة أخرى.",
                        "sources": [],
                        "news_article": None,
                        "x_tweet": None,
                        "source_statistics": {}
                    }

        case = parsed.get("الحالة", "غير مؤكد")
        talk = parsed.get("talk", "")
        sources = parsed.get("sources", [])

        uncertain_terms = {
            "ar": {"غير مؤكد"},
            "en": {"uncertain"},
            "fr": {"incertain"},
            "es": {"incierto"},
            "cs": {"nejisté", "nejiste", "nejistá"},
            "de": {"unsicher"},
            "tr": {"belirsiz"},
            "ru": {"неопределенно", "неопределённо", "неопределенный"},
        }
        lowered = case.strip().lower()
        is_uncertain = lowered in {t for s in uncertain_terms.values() for t in s}
        
        # Prepare parallel tasks for news and tweet generation
        generation_tasks = []
        news_article = ""
        x_tweet = ""
        
        if generate_news:
            print("📰 Generating professional news article as requested...")
            generation_tasks.append(
                generate_professional_news_article_from_analysis_async(processed_claim, case, talk, results, lang, async_client)
            )
        
        if generate_tweet:
            print("🐦 Generating X tweet as requested...")
            generation_tasks.append(
                generate_x_tweet_async(processed_claim, case, talk, results, lang, async_client)
            )
        
        # Execute generation tasks in parallel if any
        if generation_tasks:
            print(f"🚀 Running {len(generation_tasks)} parallel generation tasks...")
            generation_results = await asyncio.gather(*generation_tasks)
            
            # Assign results based on what was requested
            result_idx = 0
            if generate_news:
                news_article = generation_results[result_idx]
                result_idx += 1
            if generate_tweet:
                x_tweet = generation_results[result_idx]
        
        # Clear sources for uncertain results unless explicitly requested to preserve them
        # But if preserve_sources is true, use the original search results instead of AI sources
        if is_uncertain:
            if preserve_sources:
                # Use original search results when preserving sources
                sources = [{"title": r.get("title", ""), "url": r.get("link", ""), "snippet": r.get("snippet", "")} for r in results]
            else:
                # Clear sources as per original logic
                sources = []

        # Calculate source percentages for all sources (including original search results)
        all_sources = [{"title": r.get("title", ""), "url": r.get("link", ""), "snippet": r.get("snippet", "")} for r in results]
        source_percentages = calculate_source_percentages(all_sources, processed_claim)

        return {
            "case": case, 
            "talk": talk, 
            "sources": sources,
            "news_article": news_article if generate_news else None,
            "x_tweet": x_tweet if generate_tweet else None,
            "source_statistics": source_percentages
        }

    except Exception as e:
        print("❌ Error:", traceback.format_exc())
        error_by_lang = {
            "ar": "⚠️ حدث خطأ أثناء التحقق.",
            "en": "⚠️ An error occurred during fact-checking.",
            "fr": "⚠️ Une erreur s'est produite lors de la vérification des faits.",
            "es": "⚠️ Se produjo un error durante la verificación de hechos.",
            "cs": "⚠️ Během ověřování faktů došlo k chybě.",
            "de": "⚠️ Bei der Faktenprüfung ist ein Fehler aufgetreten.",
            "tr": "⚠️ Doğrulama sırasında bir hata oluştu.",
            "ru": "⚠️ Во время проверки фактов произошла ошибка.",
        }
        try:
            lang = await _lang_hint_from_claim_async(processed_claim if 'processed_claim' in locals() else claim_text)
        except Exception:
            lang = "en"
        return {"case": "غير مؤكد", "talk": error_by_lang.get(lang, error_by_lang["en"]), "sources": [], "news_article": None}


# Keep synchronous version for backward compatibility - it will call async version internally
def check_fact_simple(claim_text: str, k_sources: int = 5, generate_news: bool = False, preserve_sources: bool = False, generate_tweet: bool = False) -> dict:
    """Synchronous wrapper for async fact-checking"""
    return asyncio.run(check_fact_simple_async(claim_text, k_sources, generate_news, preserve_sources, generate_tweet))

