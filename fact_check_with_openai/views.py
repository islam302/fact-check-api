from __future__ import annotations

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.http import JsonResponse, HttpRequest, HttpResponse
import json
import traceback

from .utils import check_fact_simple, generate_analytical_news_article


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

            query = (payload.get("query") or "").strip()
            if not query:
                return JsonResponse(
                    {"ok": False, "error": "query is required"},
                    status=400,
                )

            # ✅ نمرّر k_sources (الموحد) بدل أي اسم قديم
            # ✅ نمرّر generate_news إذا كان مطلوباً
            # ✅ نمرّر preserve_sources إذا كان مطلوباً
            # ✅ نمرّر generate_tweet إذا كان مطلوباً
            generate_news = payload.get("generate_news", False)
            preserve_sources = payload.get("preserve_sources", False)
            generate_tweet = payload.get("generate_tweet", False)
            result = check_fact_simple(query, k_sources=10, generate_news=generate_news, preserve_sources=preserve_sources, generate_tweet=generate_tweet)

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
