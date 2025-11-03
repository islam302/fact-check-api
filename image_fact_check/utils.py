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
    تحليل الصورة لتحديد إذا كانت مصنوعة بالذكاء الاصطناعي، معدلة بـ Photoshop، أو مزورة
    
    Args:
        image_file: Django UploadedFile أو ملف صورة
        lang: (مهمل - سيتم استخدام العربية دائماً)
    
    Returns:
        dict مع:
        - is_ai_generated: bool (إذا كانت الصورة مصنوعة بالذكاء الاصطناعي)
        - is_photoshopped: bool (إذا كانت الصورة معدلة بـ Photoshop أو برامج التعديل)
        - is_fake: bool (إذا كانت الصورة مزورة بأي طريقة)
        - message: str (رسالة بالعربية توضح النتيجة بالتفصيل)
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
        
        # استخدام العربية دائماً
        lang = "ar"
        
        # إنشاء موجه شامل للتحقق من AI، Photoshop، والتلاعب
        IMAGE_ANALYSIS_PROMPT = """
أنت خبير في اكتشاف الصور المزورة والمعدلة.

مهمتك: تحديد إذا كانت الصورة:
1. مصنوعة بالذكاء الاصطناعي (AI-generated)
2. معدلة أو مزورة باستخدام برامج مثل Photoshop
3. مزورة بطريقة أخرى (deepfake، تركيب، تلاعب)

**علامات الصور المصنوعة بالذكاء الاصطناعي:**
- تفاصيل غير طبيعية أو متناسقة بشكل مثالي
- مشاكل في عرض النصوص (أحرف مشوهة، كلمات غير صحيحة)
- ألوان أو إضاءة غير متسقة
- نسب غير واقعية للأجسام
- أنماط مثالية أو متكررة بشكل غير طبيعي
- أخطاء في الفيزياء أو المنطق

**علامات الصور المعدلة بـ Photoshop أو برامج التعديل:**
- حواف غير طبيعية حول الكائنات المضافة أو المحذوفة
- اختلافات في جودة الدقة أو الوضوح بين أجزاء الصورة
- أنماط ضغط مختلفة في أجزاء مختلفة من الصورة
- إضاءة أو ظلال غير متسقة مع البيئة
- ألوان أو تدرجات لا تتطابق مع السياق
- تكرار غير طبيعي للنماذج أو الأنماط
- أخطاء في المنظور أو التلاعب بالأحجام
- علامات استخدام أدوات Clone Stamp أو Healing Brush
- دمج عناصر من صور مختلفة مع اختلافات واضحة

**علامات الصور المزورة (Deepfake أو تركيب):**
- عدم تطابق بين الوجه والجسم (ألوان البشرة، الإضاءة)
- مشاكل في محاذاة الوجه مع الرأس
- تشوهات حول حواف الوجه المزروع
- حركة غير طبيعية في الفيديو (إذا كان الفيديو)
- اختلافات في جودة الأجزاء المختلفة
- تباين غير منطقي بين عناصر الصورة

**الصور الحقيقية الأصلية:**
- تفاصيل طبيعية وواقعية
- إضاءة وظلال متسقة في جميع أجزاء الصورة
- نصوص واضحة ومقروءة (إن وجدت)
- نسب واقعية
- جودة موحدة في جميع أجزاء الصورة
- حواف طبيعية حول الكائنات

**التنسيق المطلوب (JSON فقط):**
{
  "is_ai_generated": true/false,
  "is_photoshopped": true/false,
  "is_fake": true/false,
  "confidence": 0.0-1.0,
  "message": "رسالة بالعربية توضح النتيجة بالتفصيل (مثل: 'الصورة معدلة باستخدام Photoshop' أو 'الصورة مزورة' أو 'الصورة حقيقية وأصلية')",
  "detection_details": "تفاصيل العلامات المكتشفة (بالعربية)"
}

**تعليمات مهمة:**
- أجب فقط بالعربية
- أعد JSON صحيح فقط بدون أي نص إضافي
- كن دقيقاً في التحليل
- إذا كانت الصورة مزورة ولكنك غير متأكد من الطريقة، ضع is_fake=true
- is_fake=true يشمل جميع أنواع التزوير (AI، Photoshop، تركيب، إلخ)
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
                            "text": "حلل هذه الصورة وحدد إذا كانت: 1) مصنوعة بالذكاء الاصطناعي، 2) معدلة بـ Photoshop أو برامج التعديل، 3) مزورة بطريقة أخرى. أعد الرد بالعربية فقط."
                        }
                    ]
                }
            ],
            temperature=0.1,
            max_tokens=400
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
            print(f"📄 Response content: {answer[:500]}")
            # Fallback response
            parsed = {
                "is_ai_generated": None,
                "is_photoshopped": None,
                "is_fake": None,
                "confidence": 0.5,
                "message": "حدث خطأ أثناء تحليل الصورة. يرجى المحاولة مرة أخرى.",
                "detection_details": ""
            }
        
        # استخراج المعلومات
        is_ai = parsed.get("is_ai_generated", False)
        is_photoshopped = parsed.get("is_photoshopped", False)
        is_fake = parsed.get("is_fake", False)
        confidence = parsed.get("confidence", parsed.get("ai_confidence", 0.5))
        message = parsed.get("message", "")
        detection_details = parsed.get("detection_details", "")
        
        # إنشاء رسالة واضحة إذا لم تكن موجودة
        if not message:
            if is_fake:
                if is_ai:
                    message = "الصورة مصنوعة بالذكاء الاصطناعي"
                elif is_photoshopped:
                    message = "الصورة معدلة أو مزورة باستخدام برامج التعديل مثل Photoshop"
                else:
                    message = "الصورة مزورة أو معدلة"
            else:
                message = "الصورة حقيقية وأصلية"
        
        # إضافة التفاصيل للرسالة
        if detection_details and detection_details not in message:
            message = f"{message}\n\n{detection_details}"
        
        return {
            "is_ai_generated": is_ai,
            "is_photoshopped": is_photoshopped,
            "is_fake": is_fake,
            "message": message.strip()
        }
        
    except Exception as e:
        print(f"❌ Error in image analysis: {e}")
        print(traceback.format_exc())
        return {
            "is_ai_generated": None,
            "is_photoshopped": None,
            "is_fake": None,
            "message": "حدث خطأ أثناء تحليل الصورة. يرجى المحاولة مرة أخرى.",
            "error": str(e)
        }

