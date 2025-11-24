from __future__ import annotations
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.http import JsonResponse, HttpRequest, HttpResponse
import json
import traceback
import asyncio
from asgiref.sync import sync_to_async

# Import async utilities
from .utils_async import (
    check_fact_simple_async,
    async_client,
    OPENAI_MODEL,
    is_news_content_async
)

# Keep sync imports for backward compatibility endpoints
from .utils import (
    generate_analytical_news_article,
    generate_professional_news_article_from_analysis,
    generate_x_tweet
)

# Import dashboard model
from dashboard.models import FactCheckHistory


@method_decorator(csrf_exempt, name="dispatch")
class FactCheckWithOpenaiView(View):
    """
    POST /fact_check_with_openai/
    Body: { 
      "query": "<claim text>",
      "generate_news": true/false (optional, default: false),
      "preserve_sources": true/false (optional, default: false),
      "generate_tweet": true/false (optional, default: false)
    }
    Response:
      { 
        ok: true, 
        query: str, 
        case: str, 
        talk: str, 
        sources: [ {title, url}, ... ],
        news_article: str (only if generate_news=true),
        x_tweet: str (only if generate_tweet=true)
      }
    
    ⚡ ASYNC VERSION - Much faster with parallel operations!
    """

    async def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        try:
            # تأكّد من أن البودي JSON صالح
            try:
                payload = json.loads(request.body.decode("utf-8"))
            except json.JSONDecodeError:
                return JsonResponse(
                    {"ok": False, "error": "Invalid JSON body"},
                    status=400,
                )

            query = (payload.get("query") or "").strip()
            if not query:
                return JsonResponse(
                    {"ok": False, "error": "query is required"},
                    status=400,
                )

            # ✅ التحقق من أن النص متعلق بالأخبار فقط
            is_valid, reason = await is_news_content_async(query)
            if not is_valid:
                return JsonResponse(
                    {"ok": False, "error": reason or "النص المقدم لا يتعلق بالأخبار أو السياق الصحفي. يرجى إرسال محتوى إخباري فقط."},
                    status=400,
                )

            # ✅ استخدام النسخة الـ async للسرعة الفائقة
            # ✅ نمرّر k_sources (الموحد) بدل أي اسم قديم
            # ✅ نمرّر generate_news إذا كان مطلوباً
            # ✅ نمرّر preserve_sources إذا كان مطلوباً
            # ✅ نمرّر generate_tweet إذا كان مطلوباً
            generate_news = payload.get("generate_news", False)
            preserve_sources = payload.get("preserve_sources", False)
            generate_tweet = payload.get("generate_tweet", False)
            
            # استخدام النسخة الـ async
            result = await check_fact_simple_async(query, k_sources=10, generate_news=generate_news, preserve_sources=preserve_sources, generate_tweet=generate_tweet)

            # ✅ حفظ النتيجة في قاعدة البيانات
            try:
                # الحصول على IP و User Agent
                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                if x_forwarded_for:
                    ip_address = x_forwarded_for.split(',')[0]
                else:
                    ip_address = request.META.get('REMOTE_ADDR')

                user_agent = request.META.get('HTTP_USER_AGENT', '')

                # حفظ في Database باستخدام sync_to_async
                await sync_to_async(FactCheckHistory.objects.create)(
                    query=query,
                    case=result.get("case", "unverified"),
                    talk=result.get("talk", ""),
                    sources=result.get("sources", []),
                    news_article=result.get("news_article"),
                    x_tweet=result.get("x_tweet"),
                    ip_address=ip_address,
                    user_agent=user_agent
                )
                print(f"✅ Successfully saved to database: {query[:50]}...")
            except Exception as db_error:
                # في حالة فشل حفظ البيانات، نطبع الخطأ لكن نكمل
                print(f"❌ Error saving to database: {db_error}")
                import traceback
                traceback.print_exc()

            # ✅ نعيد المفاتيح الموحدة
            return JsonResponse(
                {
                    "ok": True,
                    "query": query,
                    "case": result.get("case"),
                    "talk": result.get("talk"),
                    "sources": result.get("sources", []),
                    "news_article": result.get("news_article"),
                    "x_tweet": result.get("x_tweet"),
                },
                status=200,
            )

        except Exception as e:
            return JsonResponse(
                {
                    "ok": False,
                    "error": str(e),
                    "trace": traceback.format_exc(),
                },
                status=500,
            )


@method_decorator(csrf_exempt, name="dispatch")
class AnalyticalNewsView(View):
    """
    POST /fact_check_with_openai/analytical_news/
    Body: { 
      "headline": "<news headline>",
      "analysis": "<fact-check analysis>",
      "lang": "ar" (optional, default: "ar")
    }
    Response:
      { 
        ok: true, 
        headline: str, 
        analysis: str,
        analytical_article: str
      }
    """

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        try:
            # تأكّد من أن البودي JSON صالح
            try:
                payload = json.loads(request.body.decode("utf-8"))
            except json.JSONDecodeError:
                return JsonResponse(
                    {"ok": False, "error": "Invalid JSON body"},
                    status=400,
                )

            headline = (payload.get("headline") or "").strip()
            analysis = (payload.get("analysis") or "").strip()
            lang = payload.get("lang", "ar")

            if not headline:
                return JsonResponse(
                    {"ok": False, "error": "headline is required"},
                    status=400,
                )

            if not analysis:
                return JsonResponse(
                    {"ok": False, "error": "analysis is required"},
                    status=400,
                )

            # توليد المقال التحليلي
            analytical_article = generate_analytical_news_article(headline, analysis, lang)

            return JsonResponse(
                {
                    "ok": True,
                    "headline": headline,
                    "analysis": analysis,
                    "analytical_article": analytical_article,
                },
                status=200,
            )

        except Exception as e:
            return JsonResponse(
                {
                    "ok": False,
                    "error": str(e),
                    "trace": traceback.format_exc(),
                },
                status=500,
            )


@method_decorator(csrf_exempt, name="dispatch")
class ComposeNewsView(View):
    """
    POST /fact_check_with_openai/compose_news/
    صياغة خبر احترافي من نتيجة الفحص دون حفظ في قاعدة البيانات
    
    Body: { 
      "claim_text": "<النص المراد فحصه>",
      "case": "<حقيقي/كاذب/غير مؤكد>",
      "talk": "<التحليل>",
      "sources": [{"title": "", "url": "", "snippet": ""}],
      "lang": "ar" (optional, default: "ar")
    }
    Response:
      { 
        ok: true, 
        news_article: str
      }
    """

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        try:
            try:
                payload = json.loads(request.body.decode("utf-8"))
            except json.JSONDecodeError:
                return JsonResponse(
                    {"ok": False, "error": "Invalid JSON body"},
                    status=400,
                )

            claim_text = (payload.get("claim_text") or "").strip()
            case = (payload.get("case") or "").strip()
            talk = (payload.get("talk") or "").strip()
            sources = payload.get("sources", [])
            lang = payload.get("lang", "ar")

            if not claim_text:
                return JsonResponse(
                    {"ok": False, "error": "claim_text is required"},
                    status=400,
                )

            if not case:
                return JsonResponse(
                    {"ok": False, "error": "case is required"},
                    status=400,
                )

            if not talk:
                return JsonResponse(
                    {"ok": False, "error": "talk is required"},
                    status=400,
                )

            # توليد المقال الإخباري من نتيجة الفحص
            news_article = generate_professional_news_article_from_analysis(
                claim_text=claim_text,
                case=case,
                talk=talk,
                sources=sources,
                lang=lang
            )

            return JsonResponse(
                {
                    "ok": True,
                    "news_article": news_article,
                },
                status=200,
            )

        except Exception as e:
            return JsonResponse(
                {
                    "ok": False,
                    "error": str(e),
                    "trace": traceback.format_exc(),
                },
                status=500,
            )


@method_decorator(csrf_exempt, name="dispatch")
class ComposeTweetView(View):
    """
    POST /fact_check_with_openai/compose_tweet/
    صياغة تغريدة احترافية من نتيجة الفحص دون حفظ في قاعدة البيانات
    
    Body: { 
      "claim_text": "<النص المراد فحصه>",
      "case": "<حقيقي/كاذب/غير مؤكد>",
      "talk": "<التحليل>",
      "sources": [{"title": "", "url": "", "snippet": ""}],
      "lang": "ar" (optional, default: "ar")
    }
    Response:
      { 
        ok: true, 
        x_tweet: str
      }
    """

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        try:
            try:
                payload = json.loads(request.body.decode("utf-8"))
            except json.JSONDecodeError:
                return JsonResponse(
                    {"ok": False, "error": "Invalid JSON body"},
                    status=400,
                )

            claim_text = (payload.get("claim_text") or "").strip()
            case = (payload.get("case") or "").strip()
            talk = (payload.get("talk") or "").strip()
            sources = payload.get("sources", [])
            lang = payload.get("lang", "ar")

            if not claim_text:
                return JsonResponse(
                    {"ok": False, "error": "claim_text is required"},
                    status=400,
                )

            if not case:
                return JsonResponse(
                    {"ok": False, "error": "case is required"},
                    status=400,
                )

            if not talk:
                return JsonResponse(
                    {"ok": False, "error": "talk is required"},
                    status=400,
                )

            # توليد التغريدة من نتيجة الفحص
            x_tweet = generate_x_tweet(
                claim_text=claim_text,
                case=case,
                talk=talk,
                sources=sources,
                lang=lang
            )

            return JsonResponse(
                {
                    "ok": True,
                    "x_tweet": x_tweet,
                },
                status=200,
            )

        except Exception as e:
            return JsonResponse(
                {
                    "ok": False,
                    "error": str(e),
                    "trace": traceback.format_exc(),
                },
                status=500,
            )
