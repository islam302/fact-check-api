import os, traceback, json
import asyncio
import re
import base64
from typing import List, Dict, Optional
from dotenv import load_dotenv
from openai import AsyncOpenAI
import aiohttp
from io import BytesIO
from PIL import Image

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
SERPAPI_HL = os.getenv("SERPAPI_HL", "ar")
SERPAPI_GL = os.getenv("SERPAPI_GL", "")

if not OPENAI_API_KEY:
    raise RuntimeError("⚠️ Please set OPENAI_API_KEY in .env")

# Create async OpenAI client
async_client = AsyncOpenAI(api_key=OPENAI_API_KEY)


async def _lang_hint_from_claim_async(text: str) -> str:
    """Detect language from text"""
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
    """Fetch search results from SerpAPI"""
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


async def check_image_fact_and_ai_async(image_file, lang: Optional[str] = None) -> dict:
    """
    Analyze an image to:
    1. Fact-check the content shown in the image
    2. Determine if the image is AI-generated
    
    Args:
        image_file: Django UploadedFile or file-like object containing the image
        lang: Optional language hint (ar, en, fr, etc.). Auto-detected if None.
    
    Returns:
        dict with keys:
        - is_ai_generated: bool
        - ai_confidence: float (0.0-1.0)
        - fact_check: dict with case, talk, sources
        - image_analysis: str (detailed description)
        - language: str (detected language)
    """
    try:
        print("🖼️ Starting image analysis...")
        
        # Read and process image
        image_data = image_file.read()
        image = Image.open(BytesIO(image_data))
        
        # Convert to RGB if necessary (handles RGBA, P, etc.)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize if too large (OpenAI Vision has size limits)
        max_size = 2048
        if image.width > max_size or image.height > max_size:
            image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        # Convert to base64
        buffered = BytesIO()
        image.save(buffered, format="JPEG", quality=85)
        img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        # Auto-detect language if not provided
        if lang is None:
            print("🌐 Detecting language from image content...")
            try:
                # First, get a basic description to detect language
                basic_response = await async_client.chat.completions.create(
                    model=OPENAI_MODEL,
                    messages=[
                        {
                            "role": "system",
                            "content": "Describe what you see in the image briefly in one sentence. Use the same language as any text visible in the image, or English if no text is visible."
                        },
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{img_base64}"
                                    }
                                }
                            ]
                        }
                    ],
                    max_tokens=50
                )
                description_text = basic_response.choices[0].message.content or ""
                lang = await _lang_hint_from_claim_async(description_text)
                print(f"✅ Detected language: {lang}")
            except Exception as e:
                print(f"⚠️ Language detection failed: {e}, defaulting to 'en'")
                lang = "en"
        
        # Create comprehensive analysis prompt
        IMAGE_ANALYSIS_PROMPT = f"""
You are an expert image analyst and fact-checker specializing in:
1. **AI-Generated Image Detection**: Identifying if images are created by AI (DALL-E, Midjourney, Stable Diffusion, etc.)
2. **Content Fact-Checking**: Verifying claims, text, and information visible in images
3. **Image Authenticity Assessment**: Detecting signs of manipulation, editing, or fabrication

**ANALYSIS TASKS:**
Analyze the provided image and respond with a JSON object containing:

1. **AI Generation Detection:**
   - Determine if the image appears to be AI-generated
   - Look for telltale signs: unnatural details, perfect symmetry, unusual artifacts, text rendering issues, inconsistent lighting, unrealistic proportions, etc.
   - Provide confidence level (0.0 to 1.0) where 1.0 means definitely AI-generated, 0.0 means definitely real photo
   - Consider: AI images often have perfect/complex patterns, unusual details, text rendering problems, inconsistent physics, etc.

2. **Content Fact-Checking:**
   - Extract any text, claims, or information visible in the image
   - Assess if claims made in the image are factual or require verification
   - Provide verdict: "حقيقي" (True), "غير مؤكد" (Uncertain), or "مزيف" (False/Misleading) in Arabic, or "True"/"Uncertain"/"False" in English
   - Explain your reasoning based on visual evidence

3. **Detailed Image Description:**
   - Provide a comprehensive description of what's shown in the image
   - Note any text, symbols, logos, or identifiable elements
   - Describe context, setting, and notable features

**LANGUAGE POLICY:**
- Respond ENTIRELY in {lang.upper()} language
- Use localized terms for verdicts:
  - Arabic: حقيقي / غير مؤكد / مزيف
  - English: True / Uncertain / False
  - French: Vrai / Incertain / Faux
  - Spanish: Verdadero / Incierto / Falso

**RESPONSE FORMAT (JSON ONLY):**
{{
  "is_ai_generated": true/false,
  "ai_confidence": 0.0-1.0,
  "ai_indicators": ["list of specific signs that suggest AI generation"],
  "fact_check": {{
    "case": "حقيقي/غير مؤكد/مزيف" or "True/Uncertain/False",
    "talk": "Detailed explanation of fact-check results (~300 words in {lang.upper()})",
    "extracted_text": "Any text visible in the image",
    "claims": ["List of specific claims made in the image"]
  }},
  "image_analysis": {{
    "description": "Comprehensive description of image content",
    "context": "Context and setting of the image",
    "notable_elements": ["List of important elements visible"]
  }},
  "manipulation_signs": ["Any signs of editing or manipulation detected"]
}}

**CRITICAL INSTRUCTIONS:**
- Output ONLY valid JSON, no additional text
- Be thorough in analysis but concise in response
- If text in image is in different language, note it
- Consider metadata implications (watermarks, timestamps visible in image)
- For AI detection, look for: perfect details, unusual patterns, text rendering issues, inconsistent shadows/lighting, unnatural proportions
"""
        
        print("🤖 Sending image to OpenAI Vision API for analysis...")
        
        response = await async_client.chat.completions.create(
            model=OPENAI_MODEL,  # GPT-4o supports vision
            messages=[
                {
                    "role": "system",
                    "content": IMAGE_ANALYSIS_PROMPT
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{img_base64}"
                            }
                        },
                        {
                            "type": "text",
                            "text": f"Analyze this image and provide fact-checking and AI-generation detection. Language: {lang.upper()}"
                        }
                    ]
                }
            ],
            temperature=0.2,
            max_tokens=1500
        )
        
        answer = (response.choices[0].message.content or "").strip()
        
        # Clean up JSON response
        if answer.startswith("```"):
            answer = answer.strip("` \n")
            if answer.lower().startswith("json"):
                answer = answer[4:].strip()
        
        # Extract JSON if wrapped
        json_match = re.search(r'\{[\s\S]*\}', answer)
        if json_match:
            answer = json_match.group(0)
        
        # Parse JSON
        try:
            parsed = json.loads(answer)
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON parsing error: {e}")
            print(f"📄 Response content (first 500 chars): {answer[:500]}")
            # Fallback response
            parsed = {
                "is_ai_generated": None,
                "ai_confidence": 0.5,
                "ai_indicators": ["Unable to analyze"],
                "fact_check": {
                    "case": "غير مؤكد" if lang == "ar" else "Uncertain",
                    "talk": "حدث خطأ أثناء تحليل الصورة. يرجى المحاولة مرة أخرى." if lang == "ar" else "An error occurred during image analysis. Please try again.",
                    "extracted_text": "",
                    "claims": []
                },
                "image_analysis": {
                    "description": "Unable to analyze image",
                    "context": "",
                    "notable_elements": []
                },
                "manipulation_signs": []
            }
        
        # Search for sources if there are specific claims
        fact_check_result = parsed.get("fact_check", {})
        claims = fact_check_result.get("claims", [])
        extracted_text = fact_check_result.get("extracted_text", "")
        
        sources = []
        if extracted_text or claims:
            # Try to fact-check the extracted text
            query_text = extracted_text or " ".join(claims[:2])
            if query_text.strip():
                print(f"🔍 Fact-checking extracted content: {query_text[:100]}...")
                try:
                    async with aiohttp.ClientSession() as session:
                        # Quick search for verification
                        search_results = await _fetch_serp_async(session, query_text, num=5)
                        sources = [
                            {"title": r.get("title", ""), "url": r.get("link", ""), "snippet": r.get("snippet", "")}
                            for r in search_results[:5]
                        ]
                        print(f"✅ Found {len(sources)} sources for verification")
                except Exception as search_error:
                    print(f"⚠️ Source search failed: {search_error}")
        
        return {
            "is_ai_generated": parsed.get("is_ai_generated", False),
            "ai_confidence": parsed.get("ai_confidence", 0.5),
            "ai_indicators": parsed.get("ai_indicators", []),
            "fact_check": {
                "case": fact_check_result.get("case", "غير مؤكد" if lang == "ar" else "Uncertain"),
                "talk": fact_check_result.get("talk", ""),
                "extracted_text": extracted_text,
                "claims": claims,
                "sources": sources
            },
            "image_analysis": parsed.get("image_analysis", {}),
            "manipulation_signs": parsed.get("manipulation_signs", []),
            "language": lang
        }
        
    except Exception as e:
        print(f"❌ Error in image analysis: {e}")
        print(traceback.format_exc())
        error_by_lang = {
            "ar": "حدث خطأ أثناء تحليل الصورة",
            "en": "An error occurred during image analysis",
            "fr": "Une erreur s'est produite lors de l'analyse de l'image",
            "es": "Ocurrió un error durante el análisis de la imagen"
        }
        lang = lang or "en"
        return {
            "is_ai_generated": None,
            "ai_confidence": 0.5,
            "ai_indicators": [],
            "fact_check": {
                "case": "غير مؤكد" if lang == "ar" else "Uncertain",
                "talk": error_by_lang.get(lang, error_by_lang["en"]),
                "extracted_text": "",
                "claims": [],
                "sources": []
            },
            "image_analysis": {
                "description": error_by_lang.get(lang, error_by_lang["en"]),
                "context": "",
                "notable_elements": []
            },
            "manipulation_signs": [],
            "language": lang,
            "error": str(e)
        }

