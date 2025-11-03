from __future__ import annotations
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.http import JsonResponse, HttpRequest, HttpResponse
import traceback

from .utils import check_image_fact_and_ai_async


@method_decorator(csrf_exempt, name="dispatch")
class ImageFactCheckView(View):
    """
    POST /image_check/
    Body: Form-data with 'image' file
    Optional: 'lang' query parameter (ar, en, fr, es, etc.)
    
    Response:
    {
        ok: true,
        is_ai_generated: bool,
        ai_confidence: float (0.0-1.0),
        ai_indicators: [str],
        fact_check: {
            case: str,
            talk: str,
            extracted_text: str,
            claims: [str],
            sources: [{title, url, snippet}]
        },
        image_analysis: {
            description: str,
            context: str,
            notable_elements: [str]
        },
        manipulation_signs: [str],
        language: str
    }
    
    ⚡ ASYNC VERSION - Uses OpenAI Vision API for image analysis
    """

    async def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        try:
            # Check if image file was uploaded
            if 'image' not in request.FILES:
                return JsonResponse(
                    {"ok": False, "error": "No image file provided. Please upload an image with key 'image'."},
                    status=400,
                )
            
            image_file = request.FILES['image']
            
            # Validate file type
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
            if image_file.content_type not in allowed_types:
                return JsonResponse(
                    {"ok": False, "error": f"Invalid file type. Allowed types: {', '.join(allowed_types)}"},
                    status=400,
                )
            
            # Check file size (max 10MB)
            max_size = 10 * 1024 * 1024  # 10MB
            if image_file.size > max_size:
                return JsonResponse(
                    {"ok": False, "error": f"Image file too large. Maximum size: 10MB"},
                    status=400,
                )
            
            # Get optional language parameter
            lang = request.GET.get('lang') or request.POST.get('lang')
            if lang:
                lang = lang.strip().lower()
                valid_langs = ['ar', 'en', 'fr', 'es', 'de', 'cs', 'tr', 'ru']
                if lang not in valid_langs:
                    lang = None  # Will auto-detect
            
            # Analyze image
            result = await check_image_fact_and_ai_async(image_file, lang=lang)
            
            # Check if there was an error
            if 'error' in result:
                return JsonResponse(
                    {
                        "ok": False,
                        "error": result.get("error"),
                        "is_ai_generated": result.get("is_ai_generated"),
                        "ai_confidence": result.get("ai_confidence"),
                        "fact_check": result.get("fact_check", {}),
                        "language": result.get("language", "en")
                    },
                    status=500,
                )
            
            # Return success response
            return JsonResponse(
                {
                    "ok": True,
                    "is_ai_generated": result.get("is_ai_generated"),
                    "ai_confidence": result.get("ai_confidence"),
                    "ai_indicators": result.get("ai_indicators", []),
                    "fact_check": result.get("fact_check", {}),
                    "image_analysis": result.get("image_analysis", {}),
                    "manipulation_signs": result.get("manipulation_signs", []),
                    "language": result.get("language", "en")
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
