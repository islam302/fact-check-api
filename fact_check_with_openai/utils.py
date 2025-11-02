import os, traceback, requests, json
from typing import List, Dict
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime

load_dotenv()

def translate_date_references(text: str) -> str:
    """
    إرجاع النص كما هو دون تغيير المراجع الزمنية
    لتجنب تغيير معنى البحث عند استخدام كلمات مثل "اليوم"
    """
    # إرجاع النص كما هو دون أي تعديل
    return text

def generate_professional_news_article_from_analysis(claim_text: str, case: str, talk: str, sources: List[Dict], lang: str = "ar") -> str:
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

**MANDATORY REQUIREMENT:**
- You MUST write about the headline and analysis provided in the user message
- Extract ALL facts and details from the Fact-check Analysis provided by the user
- Do NOT create unrelated news - only use information from the provided analysis
- The headline is: "{claim_text}"
- Use the analysis to write the news article about this specific headline

**CRITICAL INSTRUCTIONS FOR TRUE NEWS:**
- You MUST write about the headline and analysis provided in the user message
- Start DIRECTLY with the news event/statement itself (e.g., "أرسلت [الدولة/الهيئة]..." or "[Entity] sent...")
- Write as a DIRECT NEWS REPORT, NOT as analysis or verification
- First paragraph: Report the main event naturally with details (who, what, when, where, participants, etc.) based on the provided analysis
- Second paragraph: Discuss the topics, themes, or issues that were addressed/covered, using details from the analysis
- Third paragraph: Provide additional context about sessions, discussions, or highlights from the analysis
- AVOID any mention of "verification", "fact-check", "results", "تحقق", "نتائج التحقق" anywhere in the article
- Write naturally and smoothly as if reporting events as they happened
- Mention official sources and statements naturally from the analysis provided

**STRUCTURE TEMPLATE FOR TRUE NEWS:**
1. **Opening Paragraph**: Start directly with the event from the headline (e.g., "أرسلت [الدولة]..." or "[Entity] sent...") with key details from the analysis
2. **Second Paragraph**: Discuss the details, quantities, beneficiaries, or specific information from the analysis
3. **Third Paragraph**: Additional context about significance, continuation, or broader implications from the analysis

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
        You are a professional journalist at an international news agency writing in {lang.upper()}.

        Write a polished, factual, and concise news report that follows the official style of agencies such as QNA, WAM, and SPA.

        **STYLE TO FOLLOW (VERY IMPORTANT):**
        - Begin directly with the main event using a strong news verb (e.g., "أرسلت"، "أعلنت"، "اختتمت"، "وقّعت").
        - First paragraph: summarize the event (who, what, where, why) in one flowing sentence.
        - Second paragraph: include factual details — quantities, participating entities, dates, beneficiaries, or program names.
        - Third paragraph: provide broader meaning or context — humanitarian, diplomatic, developmental, or cooperative significance.
        - Keep tone neutral, official, and humanitarian in tone.
        - Avoid any mention of verification, analysis, or fact-checking.
        - Use formal Modern Standard Arabic (MSA).

        **TARGET STYLE EXAMPLE:**
        أرسلت دولة قطر مساعدات إغاثية وإنسانية عاجلة إلى مدينة الدبة في الولاية الشمالية بجمهورية السودان، في إطار التزامها الثابت بدعم الشعب السوداني، لا سيما في ظل الظروف الإنسانية الصعبة التي يعيشها المدنيون من نقص حاد في الغذاء واحتياج متزايد لمستلزمات الإيواء والمواد الأساسية.

        وتشمل المساعدات نحو 3 آلاف سلة غذائية و1650 خيمة إيواء ومستلزمات أخرى، مقدمة من صندوق قطر للتنمية وقطر الخيرية، لدعم النازحين من مدينة الفاشر والمناطق المجاورة، ومن المقرر أن يستفيد منها أكثر من 50 ألف شخص، فضلا عن إنشاء مخيم خاص بالمساعدات القطرية تحت مسمى قطر الخير.

        ويعد هذا الدعم امتدادا لجهود دولة قطر المتواصلة في الوقوف إلى جانب الشعب السوداني الشقيق وتخفيف معاناته جراء النزاع المسلح، كما يجسد دورها الريادي في تعزيز الاستجابة الإنسانية وبناء جسور التضامن مع الشعوب المتضررة في مختلف أنحاء العالم.

        **REQUIREMENTS:**
        - Language: {lang.upper()} only
        - Length: 150–220 words
        - Structure: exactly 3 paragraphs (intro, details, context)
        - Tone: factual, diplomatic, humanitarian
        - No analysis, no opinion, no “fact-checking” terms
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
أرسلت دولة قطر مساعدات إغاثية وإنسانية عاجلة إلى مدينة الدبة في الولاية الشمالية بجمهورية السودان، في إطار التزامها الثابت بدعم الشعب السوداني، لا سيما في ظل الظروف الإنسانية الصعبة التي يعيشها المدنيون من نقص حاد في الغذاء واحتياج متزايد لمستلزمات الإيواء والمواد الأساسية.

وتشمل المساعدات نحو 3 آلاف سلة غذائية و1650 خيمة إيواء ومستلزمات أخرى، مقدمة من صندوق قطر للتنمية وقطر الخيرية، لدعم النازحين من مدينة الفاشر والمناطق المجاورة، ومن المقرر أن يستفيد منها أكثر من 50 ألف شخص، فضلا عن إنشاء مخيم خاص بالمساعدات القطرية تحت مسمى قطر الخير.

ويعد هذا الدعم امتدادا لجهود دولة قطر المتواصلة في الوقوف إلى جانب الشعب السوداني الشقيق وتخفيف معاناته جراء النزاع المسلح، كما يجسد دورها الريادي في تعزيز الاستجابة الإنسانية وبناء جسور التضامن مع الشعوب المتضررة في مختلف أنحاء العالم.

**CRITICAL REQUIREMENTS:**
- The news article MUST be about the headline provided: "{claim_text}"
- You MUST use ALL the information from the Fact-check Analysis provided below
- The Fact-check Analysis contains the actual facts and details - extract them and write the news article based on them
- Do NOT invent or create unrelated news - only use information from the analysis
- Follow the exact structure shown in the example above
- First paragraph: Start directly with the event from the headline (who, what, when, where, participants) using details from the analysis
- Second paragraph: Discuss the details, quantities, beneficiaries, or specific information from the analysis
- Third paragraph: Additional context about significance, continuation, or broader implications from the analysis
- Write as a direct news report, NOT as verification or fact-check
- AVOID any mention of "verification", "fact-check", "results", "تحقق", "نتائج التحقق"
- Use the analysis data to inform your reporting, but present it as breaking news
- The article MUST be relevant to the headline: "{claim_text}"
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
        
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": FACT_CHECK_NEWS_PROMPT},
                {"role": "user", "content": user_message}
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

def generate_analytical_news_article(headline: str, analysis: str, lang: str = "ar") -> str:
    """
    Generate a professional analytical news article using international news agency style
    Based on provided headline and fact-check analysis
    """
    
    # Professional analytical journalism prompt
    ANALYTICAL_NEWS_PROMPT = f"""
You are a senior editor-in-chief at a major international news agency (like Reuters or AFP) with 20+ years of experience in analytical journalism and fact-checking.

**REQUIRED EXPERTISE:**
1. **Editor-in-Chief**: Oversee editorial standards and journalistic integrity
2. **Analytical Journalist**: Provide deep and objective analysis
3. **Fact-Checking Specialist**: Present verified information clearly
4. **Breaking News Editor**: Handle developing stories with incomplete information
5. **Geopolitical Analyst**: Provide geopolitical and military context
6. **Public Interest Journalist**: Focus on what the public needs to know
7. **Crisis Communication Specialist**: Handle sensitive and unconfirmed information

**ANALYTICAL NEWS STANDARDS:**
- **Accuracy**: Build the article based on reliable information and sources
- **Objectivity**: Present information clearly and objectively
- **Transparency**: Clearly state what was found and what remains unclear
- **Context**: Provide background and historical perspective
- **Balance**: Include all relevant viewpoints fairly
- **Responsibility**: Consider public impact of reporting
- **Clarity**: Write for general audience understanding
- **Completeness**: Cover all important aspects of the story

**CRITICAL WRITING APPROACH:**

**FOR UNCONFIRMED NEWS:**
Write a professional news article in the style of international agencies.
Begin by reporting what is being circulated or claimed in media/social platforms in an objective manner such as: "Social media platforms circulated claims stating that..." or "Reports spread claiming that...", then report the actual situation: no evidence found, unconfirmed, or refuted.
Write as DIRECT NEWS REPORTING, NOT as a fact-check or verification result.
AVOID mentioning "verification" or "fact-check" anywhere in the article.

**FOR CONFIRMED NEWS:**
Write a professional news article in the style of international agencies.
Begin the news with the main statement or event itself, NOT with phrases like "verification results confirmed" or "analysis shows".
Present the information as breaking news or a news report, NOT as analysis or verification.
Write naturally as if reporting events as they happened.
AVOID any mention of "verification", "fact-check", "analysis", "investigation", or "confirmation".

**PROFESSIONAL TERMINOLOGY REQUIRED:**
- "The ministry announced..."
- "The authority confirmed..."
- "According to an official statement..."
- "This represents a step towards..."
- "The development comes as..."
- "This coincides with..."
- "Sources indicate that..."
- "The move signals..."
- "This follows..."
- "The announcement marks..."

**ARTICLE STRUCTURE:**
1. **Opening Sentence**: Strong and neutral journalistic sentence that places the reader in the atmosphere of the event
2. **Second Paragraph**: Provide key information and context in professional language
3. **Middle Paragraphs**: Expand with logical geopolitical or military context
4. **Concluding Paragraph**: Reflections or broader questions related to the event without taking a position

**LANGUAGE POLICY:**
- Write ENTIRELY in {lang.upper()} language
- Use professional journalistic terminology
- Maintain consistency in terminology
- Adapt cultural context appropriately
- Use formal, respectful language

**RESPONSE FORMAT:**
Write a professional news article (150-250 words) that reports the story directly.
Build the article on the information provided to inform readers.
Present what is known and what remains unclear in a natural news reporting style.

**PROVIDED DATA:**
Headline: {headline}
News Information: {analysis}

**REQUIREMENTS:**
- Language: {lang.upper()} entirely
- Style: Professional news reporting (like AFP, Reuters, AP)
- Tone: Objective, transparent, informative
- Structure: News article format with structured paragraphs
"""

    try:
        print("📰 Generating analytical news article...")
        
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": ANALYTICAL_NEWS_PROMPT}
            ],
            temperature=0.1,  # Very low temperature for factual, measured content
            max_tokens=500,   # Allow enough tokens for 150-250 words
            top_p=0.9,        # Focus on most likely responses
            frequency_penalty=0.1,  # Slight penalty to avoid repetition
            presence_penalty=0.1    # Encourage diverse vocabulary
        )
        
        article = response.choices[0].message.content.strip()
        print("✅ Analytical news article generated successfully")
        return article
        
    except Exception as e:
        print(f"❌ Error generating analytical news article: {e}")
        error_messages = {
            "ar": "عذراً، حدث خطأ أثناء كتابة المقال التحليلي. يرجى المحاولة مرة أخرى.",
            "en": "Sorry, an error occurred while writing the analytical article. Please try again.",
            "fr": "Désolé, une erreur s'est produite lors de la rédaction de l'article analytique. Veuillez réessayer.",
            "es": "Lo siento, ocurrió un error al escribir el artículo analítico. Por favor, inténtalo de nuevo.",
        }
        return error_messages.get(lang, error_messages["en"])

def generate_x_tweet(claim_text: str, case: str, talk: str, sources: List[Dict], lang: str = "ar") -> str:
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
        
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": X_TWEET_PROMPT},
                {"role": "user", "content": user_message}
            ],
            temperature=0.3,  # Balanced creativity and accuracy
            max_tokens=150,   # Enough for tweet + some buffer
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

client = OpenAI(api_key=OPENAI_API_KEY)

def _lang_hint_from_claim(text: str) -> str:
    try:
        resp = client.chat.completions.create(
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


def check_fact_simple(claim_text: str, k_sources: int = 5, generate_news: bool = False, preserve_sources: bool = False, generate_tweet: bool = False) -> dict:
    try:
        # ترجمة المراجع الزمنية في النص
        processed_claim = translate_date_references(claim_text)
        print(f"🧠 Fact-checking: {processed_claim}")
        lang = _lang_hint_from_claim(processed_claim)

        results = []
        for domain in NEWS_AGENCIES:
            domain_results = _fetch_serp(f"{processed_claim} site:{domain}", extra={"hl": lang} if lang else None, num=2)
            results += domain_results
        google_results = _fetch_serp(processed_claim, extra={"hl": lang} if lang else None, num=k_sources)
        results += google_results

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
        
        # Generate professional news article if requested for all cases (true, false, uncertain)
        news_article = ""
        if generate_news:
            print("📰 Generating professional news article as requested...")
            # Use the fact-check analysis (talk) and sources for news generation
            news_article = generate_professional_news_article_from_analysis(processed_claim, case, talk, results, lang)
        
        # Generate X tweet if requested for all cases (true, false, uncertain)
        x_tweet = ""
        if generate_tweet:
            print("🐦 Generating X tweet as requested...")
            # Use the original search results for tweet generation
            x_tweet = generate_x_tweet(processed_claim, case, talk, results, lang)
        
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
            lang = _lang_hint_from_claim(processed_claim if 'processed_claim' in locals() else claim_text)
        except Exception:
            lang = "en"
        return {"case": "غير مؤكد", "talk": error_by_lang.get(lang, error_by_lang["en"]), "sources": [], "news_article": None}
