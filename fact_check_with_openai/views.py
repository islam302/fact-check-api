from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.http import JsonResponse
import json
import traceback

from .utils import check_fact_with_rag


@method_decorator(csrf_exempt, name="dispatch")
class FactCheckWithOpenaiView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body.decode("utf-8"))
            query = data.get("query")
            if not query:
                return JsonResponse({"ok": False, "error": "query is required"}, status=400)

            # ✅ بعد التوحيد: بنمرر k_sources بدل k_sources_extra
            result = check_fact_with_rag(query, k_sources=10)

            # ✅ رجّع المفتاح الموحد "sources"
            return JsonResponse({
                "ok": True,
                "query": query,
                "case": result.get("case"),
                "talk": result.get("talk"),
                "sources": result.get("sources", []),
            })

        except Exception as e:
            return JsonResponse({
                "ok": False,
                "error": str(e),
                "trace": traceback.format_exc()
            }, status=500)
