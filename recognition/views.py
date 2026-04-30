"""
recognition/views.py
API endpoint that receives audio from the browser,
runs the ML model, and returns the predicted note.
"""
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .predict_note import predict_from_bytes

logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def recognize_audio(request):
    """
    POST /api/recognize/
    Body: multipart/form-data with field 'audio' (Blob/File)

    Always returns JSON — never a 500 page.
    """
    audio_file = request.FILES.get('audio')
    if not audio_file:
        return JsonResponse({'error': 'No audio file provided.'}, status=400)

    if audio_file.size > 5 * 1024 * 1024:
        return JsonResponse({'error': 'Audio file too large.'}, status=400)

    try:
        audio_bytes = audio_file.read()
        result = predict_from_bytes(audio_bytes)
        return JsonResponse(result)

    except Exception as exc:
        logger.exception("[recognize_audio] Inference error: %s", exc)
        # Never crash the app — return demo-mode fallback
        import random
        fallback_notes = [
            'DO4','RE4','MI4','FA4','SOL4','LA4','SI4',
            'DO5','RE5','MI5','FA5','SOL5','LA5','SI5','DO6',
        ]
        note = random.choice(fallback_notes)
        return JsonResponse({
            'note': note,
            'confidence': 0.5,
            'top_k': [{'note': note, 'confidence': 0.5}],
            'demo_mode': True,
            'error_info': str(exc),
        })


@csrf_exempt
@require_POST
def warmup(request):
    """
    POST /api/warmup/
    Forces the CNN model to load into memory.
    Called by the loading page before the user starts playing.
    Returns the same format as recognize_audio.
    """
    audio_file = request.FILES.get('audio')
    if not audio_file:
        # Even without audio, just trigger the model load
        from .predict_note import _load
        _load()
        return JsonResponse({'ready': True, 'demo_mode': True, 'note': 'DO4', 'confidence': 1.0})

    try:
        audio_bytes = audio_file.read()
        result = predict_from_bytes(audio_bytes)
        result['ready'] = True
        return JsonResponse(result)
    except Exception as exc:
        logger.exception("[warmup] Error: %s", exc)
        return JsonResponse({'ready': True, 'demo_mode': True, 'note': 'DO4', 'confidence': 1.0})
