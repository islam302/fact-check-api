from __future__ import annotations

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.http import JsonResponse, HttpRequest, HttpResponse
import json
import traceback

from .utils import check_fact_simple


@method_decorator(csrf_exempt, name="dispatch")
class FactCheckWithOpenaiView(View):
    """
    POST /fact_check_with_openai/
    Body: { "query": "<claim text>" }
    Response:
      { ok: true, query: str, case: str, talk: str, sources: [ {title, url}, ... ] }
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
            result = check_fact_simple(query, k_sources=10)

            # ✅ نعيد المفاتيح الموحدة
            return JsonResponse(
                {
                    "ok": True,
                    "query": query,
                    "case": result.get("case"),
                    "talk": result.get("talk"),
                    "sources": result.get("sources", []),
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
