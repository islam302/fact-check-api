import os, time, traceback, requests, urllib.parse, json
from typing import List, Dict
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime

load_dotenv()

def translate_date_references(text: str) -> str:
    """
    ترجمة المراجع الزمنية في النص إلى تواريخ محددة
    مثل: "اليوم" -> التاريخ الحالي
    """
    if not text:
        return text
    
    # الحصول على التاريخ الحالي
    today = datetime.now()
    today_arabic = today.strftime('%Y-%m-%d')
    today_formatted = today.strftime('%d/%m/%Y')
    
    # قائمة بالكلمات التي تشير إلى "اليوم" في لغات مختلفة
    today_words = {
        'ar': ['اليوم', 'هذا اليوم', 'اليوم الحالي'],
        'en': ['today', 'this day'],
        'fr': ['aujourd\'hui', 'ce jour'],
        'es': ['hoy', 'este día'],
        'de': ['heute', 'dieser tag'],
        'tr': ['bugün', 'bu gün'],
        'ru': ['сегодня', 'этот день'],
        'cs': ['dnes', 'dnešní den']
    }
    
    # استبدال كلمة "اليوم" بالتاريخ الحالي
    modified_text = text
    
    for language, words in today_words.items():
        for word in words:
            # البحث عن الكلمة مع مراعاة الحالة (case-insensitive)
            import re
            pattern = re.compile(re.escape(word), re.IGNORECASE)
            modified_text = pattern.sub(today_arabic, modified_text)
    
    return modified_text

def generate_professional_news_article(claim_text: str, sources: List[Dict], lang: str = "ar") -> str:

    
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
        
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": JOURNALISM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            temperature=0.1,  # Very low temperature for factual, measured content
            max_tokens=800,   # Allow enough tokens for 250-350 words
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

def generate_professional_news_article_from_analysis(claim_text: str, case: str, talk: str, sources: List[Dict], lang: str = "ar") -> str:
    """
    Generate a professional news article based on fact-check analysis and sources
    Uses the analysis (talk) and sources to create a balanced, journalistic piece
    """
    
    # Professional journalism prompt for fact-check analysis
    FACT_CHECK_NEWS_PROMPT = f"""
You are a senior editor-in-chief and Pulitzer Prize-winning journalist with 20+ years of experience. You are writing for a major international news organization with the highest journalistic standards.

**COMPLETE JOURNALISM ROLES & EXPERTISE:**
1. **Editor-in-Chief**: Oversee editorial standards and journalistic integrity
2. **Fact-Checking Specialist**: Present verified information clearly
3. **Investigative Reporter**: Deep-dive into complex, uncertain situations
4. **Breaking News Editor**: Handle developing stories with incomplete information
5. **News Analyst**: Provide context for uncertain situations
6. **Public Interest Journalist**: Focus on what the public needs to know
7. **Crisis Communication Specialist**: Handle sensitive, uncertain information
8. **Ethics Editor**: Ensure all content meets highest ethical standards

**FACT-CHECK NEWS STANDARDS:**
- **Accuracy**: Base article on the fact-check analysis, not the original claim
- **Objectivity**: Present the fact-check result clearly and objectively
- **Transparency**: Clearly state what was found and what remains unclear
- **Context**: Provide background and historical perspective
- **Balance**: Include all relevant viewpoints fairly
- **Responsibility**: Consider public impact of reporting
- **Clarity**: Write for general audience understanding
- **Completeness**: Cover all important aspects of the fact-check

**WRITING APPROACH FOR FACT-CHECK NEWS:**
- Start with the fact-check result (uncertain/false/true)
- Explain what was investigated and what was found
- Present the analysis clearly and objectively
- Include relevant context and background
- Use the available sources to support the analysis
- Maintain professional skepticism throughout
- Focus on what is known vs. what is uncertain
- Avoid speculation beyond the fact-check analysis

**LANGUAGE POLICY:**
- Write ENTIRELY in {lang.upper()} language
- Use professional journalistic terminology
- Maintain consistency in terminology
- Adapt cultural context appropriately
- Use formal, respectful language

**ARTICLE STRUCTURE:**
1. **Headline**: Clear, informative, based on fact-check result
2. **Lead Paragraph**: Fact-check result, what was investigated, key findings
3. **Body Paragraphs**: Detailed analysis, context, sources, implications
4. **Conclusion**: Summary of findings and what remains unclear

**RESPONSE FORMAT:**
Write a professional news article (100-200 words) that reports on the fact-check investigation.
Base the article on the analysis provided, not on confirming or denying the original claim.
Focus on transparency about what was found and what remains uncertain.
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
    
    # Create the user message
    user_message = f"""
**FACT-CHECK INVESTIGATION:**
Original Claim: {claim_text}
Fact-Check Result: {case}
Analysis: {talk}

**AVAILABLE SOURCES:**
{sources_context}

**INSTRUCTIONS:**
Write a professional news article that reports on this fact-check investigation:

1. **Start with the fact-check result** - clearly state what was found
2. **Explain the investigation** - what was looked into and how
3. **Present the analysis** - what the fact-checkers found
4. **Include context** - relevant background information
5. **Use sources** - reference the available sources appropriately
6. **Be transparent** - clearly state what is known vs. uncertain
7. **Avoid speculation** - stick to the fact-check analysis

**IMPORTANT:**
- Do NOT confirm or deny the original claim
- Report on the fact-check process and findings
- Base the article on the analysis provided
- Maintain journalistic objectivity
- Focus on transparency and accuracy

**REQUIREMENTS:**
- Length: 100-200 words (strict requirement)
- Language: {lang.upper()}
- Style: Professional journalism reporting on fact-check
- Tone: Objective, transparent, informative
- Structure: News article format with headline, lead, body, conclusion
"""

    try:
        print("📰 Generating fact-check news article...")
        
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": FACT_CHECK_NEWS_PROMPT},
                {"role": "user", "content": user_message}
            ],
            temperature=0.1,  # Very low temperature for factual, measured content
            max_tokens=400,   # Allow enough tokens for 100-200 words
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

def generate_confirmed_news_article(headline: str, analysis: str, lang: str = "en") -> str:
    """
    Generate a professional confirmed news article in English using international news agency style
    Based on provided headline and fact-check analysis
    """
    
    # Professional confirmed news prompt in English
    CONFIRMED_NEWS_PROMPT = f"""
You are a senior editor-in-chief at a major international news agency (like Reuters or AFP) with 20+ years of experience in analytical journalism and fact-checking.

**REQUIRED EXPERTISE:**
1. **Editor-in-Chief**: Oversee editorial standards and journalistic integrity
2. **Analytical Journalist**: Provide deep and objective analysis
3. **Fact-Checking Specialist**: Present verified information clearly
4. **Breaking News Editor**: Handle developing stories with incomplete information
5. **Geopolitical Analyst**: Provide geopolitical and military context
6. **Public Interest Journalist**: Focus on what the public needs to know
7. **Crisis Communication Specialist**: Handle sensitive and unconfirmed information

**CONFIRMED NEWS STANDARDS:**
- **Accuracy**: Build the article on fact-check analysis, not the original claim
- **Objectivity**: Present fact-check results clearly and objectively
- **Transparency**: Clearly state what was found and what remains unclear
- **Context**: Provide background and historical perspective
- **Balance**: Include all relevant viewpoints fairly
- **Responsibility**: Consider public impact of reporting
- **Clarity**: Write for general audience understanding
- **Completeness**: Cover all important aspects of the fact-check

**WRITING APPROACH FOR CONFIRMED NEWS:**
- Start directly with the confirmed event without mentioning city name or agency name
- Follow with a paragraph including the official source or statement that confirmed the news
- Add analytical background about the event's importance, political or economic context, or regional and international implications
- Conclude with a paragraph linking the event to broader trends or projects or mentioning reactions if any

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
1. **Opening Sentence**: Direct description of the confirmed event (what happened, who announced, when)
2. **Second Paragraph**: Include official source or statement that confirmed the news
3. **Middle Paragraphs**: Analytical background about importance, context, implications
4. **Concluding Paragraph**: Link to broader trends or mention reactions

**LANGUAGE POLICY:**
- Write ENTIRELY in {lang.upper()} language
- Use professional journalistic terminology
- Maintain consistency in terminology
- Adapt cultural context appropriately
- Use formal, respectful language
- Avoid mentioning geographic location or agency name in the introduction

**RESPONSE FORMAT:**
Write a professional analytical news article (150-250 words) that reports on the confirmed event.
Build the article on the analysis provided, focusing on the confirmed nature of the information.
Maintain journalistic neutrality and professionalism throughout.

**PROVIDED DATA:**
Headline: {headline}
Confirmation Analysis: {analysis}

**REQUIREMENTS:**
- Language: {lang.upper()} entirely
- Style: Professional analytical journalism reporting on confirmed news
- Tone: Neutral, transparent, informative, authoritative
- Structure: News article format with structured paragraphs
- Start directly with the event without geographic/agency references
- Use strong professional language and journalistic terminology
"""

    try:
        print("📰 Generating confirmed news article...")
        
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": CONFIRMED_NEWS_PROMPT}
            ],
            temperature=0.1,  # Very low temperature for factual, measured content
            max_tokens=500,   # Allow enough tokens for 150-250 words
            top_p=0.9,        # Focus on most likely responses
            frequency_penalty=0.1,  # Slight penalty to avoid repetition
            presence_penalty=0.1    # Encourage diverse vocabulary
        )
        
        article = response.choices[0].message.content.strip()
        print("✅ Confirmed news article generated successfully")
        return article
        
    except Exception as e:
        print(f"❌ Error generating confirmed news article: {e}")
        error_messages = {
            "ar": "عذراً، حدث خطأ أثناء كتابة المقال التحليلي. يرجى المحاولة مرة أخرى.",
            "en": "Sorry, an error occurred while writing the confirmed news article. Please try again.",
            "fr": "Désolé, une erreur s'est produite lors de la rédaction de l'article analytique. Veuillez réessayer.",
            "es": "Lo siento, ocurrió un error al escribir el artículo analítico. Por favor, inténtalo de nuevo.",
        }
        return error_messages.get(lang, error_messages["en"])

def generate_analytical_news_article(headline: str, analysis: str, lang: str = "ar") -> str:
    """
    Generate a professional analytical news article using international news agency style
    Based on provided headline and fact-check analysis
    """
    
    # Professional analytical journalism prompt
    ANALYTICAL_NEWS_PROMPT = f"""
أنت محرر أول في وكالة أنباء دولية كبرى مثل رويترز أو AP، مع خبرة 20+ سنة في الصحافة التحليلية والتحقق من الأخبار.

**المهارات المطلوبة:**
1. **محرر أول**: الإشراف على المعايير التحريرية والنزاهة الصحفية
2. **صحفي تحليلي**: تقديم تحليل عميق وموضوعي
3. **مختص في التحقق**: عرض المعلومات المحققة بوضوح
4. **محرر أخبار عاجلة**: التعامل مع القصص المتطورة والمعلومات غير المكتملة
5. **محلل جيوسياسي**: تقديم السياق الجيوسياسي والعسكري
6. **صحفي المصلحة العامة**: التركيز على ما يحتاج الجمهور لمعرفته
7. **مختص اتصالات الأزمات**: التعامل مع المعلومات الحساسة وغير المؤكدة

**معايير الخبر التحليلي:**
- **الدقة**: بناء المقال على التحليل التحققي، وليس على الادعاء الأصلي
- **الموضوعية**: عرض نتيجة التحقق بوضوح وموضوعية
- **الشفافية**: بيان واضح لما تم العثور عليه وما يبقى غير واضح
- **السياق**: تقديم خلفية وتوضيح تاريخي
- **التوازن**: تضمين جميع وجهات النظر ذات الصلة بإنصاف
- **المسؤولية**: مراعاة التأثير العام للتقرير
- **الوضوح**: الكتابة لفهم الجمهور العام
- **الشمولية**: تغطية جميع الجوانب المهمة للتحقق

**أسلوب الكتابة للخبر التحليلي:**
- البدء بجملة صحفية قوية ومحايدة تضع القارئ في جو الحدث دون جزم أو تأكيد لصحة الادعاء
- توضيح التحليل التحققي بلغة مهنية، مع الإشارة إلى غياب التأكيدات الرسمية أو وجود تضارب في المعلومات
- التوسع بسياق جيوسياسي أو عسكري منطقي بناءً على التحليل
- استخدام لغة تحليلية موضوعية
- الختام بفقرة تتناول انعكاسات أو تساؤلات أوسع متعلقة بالحدث، دون تبني موقف

**المصطلحات المهنية المطلوبة:**
- "لا يمكن تأكيد ذلك"
- "وفقًا لتقارير تحليلية"
- "بحسب مراقبين"
- "تشير تقديرات أولية إلى"
- "لا توجد معطيات قاطعة"
- "يثير ذلك جدلًا واسعًا"
- "يتزامن هذا مع"
- "تشير الخلفية الميدانية إلى"
- "وتُعد هذه التطورات جزءًا من"
- "ما يثير تساؤلات حول"

**هيكل المقال:**
1. **الفقرة الأولى**: جملة صحفية قوية ومحايدة تضع القارئ في جو الحدث
2. **الفقرة الثانية**: توضيح التحليل التحققي بلغة مهنية
3. **الفقرات الوسطى**: توسع بسياق جيوسياسي أو عسكري منطقي
4. **الفقرة الختامية**: انعكاسات أو تساؤلات أوسع دون تبني موقف

**سياسة اللغة:**
- الكتابة بالكامل باللغة العربية
- استخدام المصطلحات الصحفية المهنية
- الحفاظ على الاتساق في المصطلحات
- تكييف السياق الثقافي بشكل مناسب
- استخدام لغة رسمية ومحترمة

**تنسيق الاستجابة:**
اكتب مقالاً إخبارياً تحليلياً احترافياً (150-250 كلمة) يقدم تقريراً عن التحقق.
بناء المقال على التحليل المقدم، وليس على تأكيد أو نفي الادعاء الأصلي.
التركيز على الشفافية حول ما تم العثور عليه وما يبقى غير واضح.

**المعطيات:**
العنوان: {headline}
تحليل التحقق: {analysis}

**المطلوب:**
- اللغة: العربية بالكامل
- الأسلوب: صحافة تحليلية احترافية تقدم تقريراً عن التحقق
- النبرة: موضوعية، شفافة، إعلامية
- الهيكل: تنسيق مقال إخباري مع فقرات متدرجة
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

        return {
            "case": case, 
            "talk": talk, 
            "sources": sources,
            "news_article": news_article if generate_news else None,
            "x_tweet": x_tweet if generate_tweet else None
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
