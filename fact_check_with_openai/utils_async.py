import os, time, traceback, urllib.parse, json
import asyncio
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

async def generate_professional_news_article_async(claim_text: str, sources: List[Dict], lang: str = "ar", client: AsyncOpenAI = None) -> str:
    
    # Professional journalism prompt with complete standards
    JOURNALISM_PROMPT = f"""
You are a senior editor-in-chief and Pulitzer Prize-winning journalist with 20+ years of experience. You are writing for a major international news organization with the highest journalistic standards.

**COMPLETE JOURNALISM ROLES & EXPERTISE:**
1. **Editor-in-Chief**: Oversee editorial standards and journalistic integrity
2. **Investigative Reporter**: Deep-dive into complex, uncertain situations
3. **Breaking News Editor**: Handle developing stories with incomplete information
4. **Fact-Checker**: Distinguish between verified and unverified claims
5. **News Analyst**: Provide context for uncertain situations
6. **Editorial Writer**: Craft balanced coverage of controversial topics
7. **Public Interest Journalist**: Focus on what the public needs to know
8. **Crisis Communication Specialist**: Handle sensitive, uncertain information
9. **Data Journalist**: Present incomplete data responsibly
10. **Watchdog Reporter**: Monitor and report on uncertain developments
11. **Community Journalist**: Serve public interest in uncertain times
12. **International Correspondent**: Cover global events with cultural sensitivity
13. **Political Reporter**: Navigate complex political situations
14. **Science Journalist**: Translate complex information for general audience
15. **Ethics Editor**: Ensure all content meets highest ethical standards

**COMPLETE JOURNALISM STANDARDS:**
- **Accuracy**: Verify all facts before publication, double-check sources
- **Objectivity**: Present multiple perspectives fairly, avoid bias
- **Balance**: Include all relevant viewpoints, give equal weight to different sides
- **Transparency**: Cite sources clearly, acknowledge limitations
- **Ethics**: Respect privacy, avoid harm, consider public interest
- **Clarity**: Write for general audience understanding, avoid jargon
- **Timeliness**: Address current relevance and urgency
- **Completeness**: Cover all important aspects, provide full context
- **Independence**: Maintain editorial independence from external pressures
- **Accountability**: Take responsibility for reporting, correct errors promptly
- **Fairness**: Treat all subjects fairly, avoid discrimination
- **Responsibility**: Consider public impact, avoid sensationalism

**PROFESSIONAL WRITING STYLE:**
- Use inverted pyramid structure (most important info first)
- Write in third person, past tense
- Use active voice when possible
- Include direct quotes when available
- Provide context and background
- Maintain neutral, professional tone
- Avoid speculation and unverified claims
- Include relevant statistics and data
- Use precise, clear language
- Avoid unnecessary adjectives and adverbs
- Maintain consistent terminology
- Use proper attribution for all claims

**LANGUAGE POLICY:**
- Write ENTIRELY in {lang.upper()} language
- Use professional journalistic terminology
- Maintain consistency in terminology
- Adapt cultural context appropriately
- Use formal, respectful language
- Avoid colloquialisms and slang

**COMPLETE ARTICLE STRUCTURE:**
1. **Headline**: Clear, informative, attention-grabbing (avoid sensationalism)
2. **Lead Paragraph**: Who, what, when, where, why, how (5W+H)
3. **Body Paragraphs**: Supporting details, quotes, context, analysis
4. **Conclusion**: Summary, implications, next steps

**RESPONSE FORMAT:**
Write a professional news article (100-200 words) that meets the highest journalistic standards.
Focus on transparency, accuracy, and public interest. Maintain complete journalistic integrity.
"""

    # Prepare sources context
    if not sources:
        sources_context = "No specific sources available for this topic."
    else:
        sources_context = "\n\n".join([
            f"**Source {i+1}:**\n"
            f"Title: {source.get('title', 'N/A')}\n"
            f"URL: {source.get('url', 'N/A')}\n"
            f"Snippet: {source.get('snippet', 'N/A')}"
            for i, source in enumerate(sources[:5])  # Limit to 5 sources
        ])
    
    # Create the user message
    user_message = f"""
**ORIGINAL CLAIM/TOPIC:**
{claim_text}

**AVAILABLE SOURCES:**
{sources_context}

**SITUATION CONTEXT:**
This is an UNCERTAIN fact-check result. The claim could not be definitively verified as true or false due to:
- Insufficient evidence
- Conflicting information
- Lack of reliable sources
- Incomplete data
- Ongoing developments

**PROFESSIONAL JOURNALISM INSTRUCTIONS:**
Write a comprehensive news article that meets the highest journalistic standards:

1. **ACCURACY**: Only report verified information, double-check all facts
2. **OBJECTIVITY**: Present multiple perspectives fairly, avoid bias
3. **BALANCE**: Include all relevant viewpoints, give equal weight to different sides
4. **TRANSPARENCY**: Clearly distinguish between what is known and what remains uncertain
5. **ETHICS**: Respect privacy, avoid harm, consider public interest
6. **CLARITY**: Write for general audience understanding, avoid jargon
7. **COMPLETENESS**: Cover all important aspects, provide full context
8. **RESPONSIBILITY**: Consider public impact, avoid sensationalism

**PROFESSIONAL WRITING APPROACH:**
- Use inverted pyramid structure (most important info first)
- Start with what IS known and verified
- Clearly state what remains unclear or uncertain
- Use phrases like "according to available information", "sources indicate", "reports suggest"
- Include appropriate disclaimers about incomplete information
- Focus on the public interest and what people need to know
- Maintain professional skepticism throughout
- Use third person, past tense, active voice
- Include proper attribution for all claims

**REQUIREMENTS:**
- Length: 250-350 words (strict requirement - must be at least 250 words)
- Language: {lang.upper()}
- Style: Professional journalism meeting highest standards
- Tone: Neutral, measured, transparent, authoritative
- Structure: Complete news article with headline, lead, body, conclusion
- Quality: Pulitzer Prize-level journalism
- Content: Comprehensive coverage with detailed analysis and context
- IMPORTANT: Write a detailed, comprehensive article that thoroughly covers all aspects of the story. Include extensive background, multiple perspectives, detailed analysis, and comprehensive context. The article must be substantial and informative, not brief or superficial.
"""

    try:
        print("📰 Generating professional news article...")
        
        response = await client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": JOURNALISM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            temperature=0.1,  # Very low temperature for factual, measured content
            max_tokens=600,   # Optimized for speed while maintaining quality
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

Write an analytical news article in the style of international agencies using the following title and analysis.

Begin the news with the main statement or event that appeared to you in the analysis results, not with the phrase "verification results confirmed", and integrate the verification result within the text naturally to support the credibility of the news.

Ensure the wording is human and smooth, balanced, and based on the details mentioned in the analysis, while avoiding repetition and mechanical formulas, and mention the sources mentioned in the analysis in a natural news style if they exist.

**REQUIREMENTS:**
- Language: {lang.upper()} entirely
- Style: Professional analytical journalism
- Tone: Neutral, transparent, informative, authoritative
- Structure: News article format with structured paragraphs
- Length: 150-250 words
- Start directly with the event without geographic/agency references
- Use strong professional language and journalistic terminology
"""
    else:
        # UNCERTAIN case - Use the specific prompt for unconfirmed news
        FACT_CHECK_NEWS_PROMPT = f"""
You are a senior international news agency journalist writing in {lang.upper()} language.

Write a brief analytical news article in the style of international agencies using the following title and analysis.

Begin the news by referring to the circulation of the news in media or social media in an objective manner such as: "Social media platforms circulated claims stating that..." or "Reports spread claiming that...", then clarify through the verification result that the claim is unconfirmed or incorrect and there is no evidence for it.

Ensure the wording is human and smooth and based on what was mentioned in the analysis, while avoiding repetition or mechanical phrases.

**REQUIREMENTS:**
- Language: {lang.upper()} entirely
- Style: Professional analytical journalism
- Tone: Objective, transparent, informative
- Structure: News article format with structured paragraphs
- Length: 150-250 words
- Start with social media/media circulation reference
- Use professional language and journalistic terminology
"""
    
    # Create the user message
    user_message = f"""
**PROVIDED DATA:**
Headline: {claim_text}
Fact-check Analysis: {talk}

**AVAILABLE SOURCES:**
{sources_context}

**INSTRUCTIONS:**
Write a professional analytical news article based on the above data and analysis.
Follow the specific guidelines provided in the system prompt.
"""
    
    try:
        print("📰 Generating fact-check news article...")
        
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
        print("✅ Fact-check news article generated successfully")
        return article
        
    except Exception as e:
        print(f"❌ Error generating fact-check news article: {e}")
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

