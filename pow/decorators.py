# это оч костыльно, но вроде должно работать. изначально я пытался сделать через golang, но мне сказ
# то что "сасай, разделять бекенд и фронтенд не будем", так что будет так что пингуйте если развалится
from functools import wraps
import logging
from django.http import JsonResponse
from django.shortcuts import render
from django.core.cache import cache
from django.utils import timezone
from .models import PoWChallenge
from boards.models_tools import get_or_create_anon

logger = logging.getLogger(__name__)

def require_pow(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.method == 'POST':
            client_ip = request.META.get('REMOTE_ADDR', 'unknown')
            logger.info(f"PoW: Checking validation for {client_ip}")
            anon = get_or_create_anon(request)
            if anon.passcodes.exists():
                logger.info(f"PoW: Bypass for passcode user {client_ip}")
                return view_func(request, *args, **kwargs)
            
            if not request.session.get('pow_validated'):
                logger.warning(f"PoW: No validation found for {client_ip}")
                return render(request, 'pow/pow_required.html', {
                    'error': 'Требуется доказательство работы'
                })
            
            challenge_id = request.session.get('pow_challenge')
            logger.info(f"PoW: Decorator - challenge_id: {challenge_id}, session_key: {request.session.session_key}")
            if challenge_id:
                try:
                    challenge = PoWChallenge.objects.get(challenge=challenge_id)
                    logger.info(f"PoW: Decorator - challenge found: used={challenge.used}, expires_at={challenge.expires_at}")
                    logger.info(f"PoW: Decorator - session_key match: {challenge.session_key == request.session.session_key}")
                    if timezone.now() > challenge.expires_at:
                        logger.warning(f"PoW: Challenge expired for {client_ip}")
                        request.session.pop('pow_validated', None)
                        request.session.pop('pow_challenge', None)
                        return render(request, 'pow/pow_required.html', {
                            'error': 'Доказательство работы истекло'
                        })
                    if challenge.session_key != request.session.session_key:
                        logger.warning(f"PoW: Challenge session mismatch for {client_ip}")
                        request.session.pop('pow_validated', None)
                        request.session.pop('pow_challenge', None)
                        return render(request, 'pow/pow_required.html', {
                            'error': 'Недействительное доказательство работы'
                        })
                except PoWChallenge.DoesNotExist:
                    logger.warning(f"PoW: Invalid challenge for {client_ip}")
                    request.session.pop('pow_validated', None)
                    request.session.pop('pow_challenge', None)
                    return render(request, 'pow/pow_required.html', {
                        'error': 'Недействительное доказательство работы'
                    })
            
            logger.info(f"PoW: Validation passed for {client_ip}, clearing session")
            request.session.pop('pow_validated', None)
            request.session.pop('pow_challenge', None)
            
        return view_func(request, *args, **kwargs)
    return wrapper
