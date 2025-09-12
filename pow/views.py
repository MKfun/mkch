import json
import time
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.cache import cache
from django.utils import timezone
from .models import PoWChallenge

logger = logging.getLogger(__name__)

def check_rate_limit(request, key_prefix, limit=10, window=60):
    client_ip = request.META.get('REMOTE_ADDR', 'unknown')
    cache_key = f"{key_prefix}:{client_ip}"
    
    current_time = timezone.now().timestamp()
    requests = cache.get(cache_key, [])
    
    requests = [req_time for req_time in requests if current_time - req_time < window]
    
    if len(requests) >= limit:
        return False
    
    requests.append(current_time)
    cache.set(cache_key, requests, window)
    return True

@require_http_methods(["GET"])
def get_challenge(request):
    client_ip = request.META.get('REMOTE_ADDR', 'unknown')
    logger.info(f"PoW: Challenge request from {client_ip}")
    
    if not check_rate_limit(request, 'pow_challenge', limit=5, window=60):
        logger.warning(f"PoW: Rate limit exceeded for {client_ip}")
        return JsonResponse({'error': 'Rate limit exceeded'}, status=429)
    
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key
    
    challenge = PoWChallenge.create_challenge(session_key, difficulty=5, ttl=3600)  
    logger.info(f"PoW: Created challenge {challenge.challenge[:8]}... for session {session_key[:8]}...")
    logger.info(f"PoW: Challenge expires at {challenge.expires_at}, TTL: 3600s")
    
    return JsonResponse({
        'challenge': challenge.challenge,
        'difficulty': challenge.difficulty
    })

@require_http_methods(["POST"])
@csrf_exempt
def validate_challenge(request):
    client_ip = request.META.get('REMOTE_ADDR', 'unknown')
    logger.info(f"PoW: Validation request from {client_ip}")
    
    if not check_rate_limit(request, 'pow_validate', limit=20, window=60):
        logger.warning(f"PoW: Rate limit exceeded for validation {client_ip}")
        return JsonResponse({'valid': False, 'error': 'Rate limit exceeded'}, status=429)
    
    try:
        data = json.loads(request.body)
        challenge_id = data.get('challenge')
        nonce = data.get('nonce')
        response = data.get('response')
        elapsed_time = data.get('elapsedTime')
        client_meta = data.get('meta') or {}
        
        logger.info(f"PoW: Validating challenge {challenge_id[:8]}... nonce={nonce}, time={elapsed_time:.2f}s")
        try:
            logger.info(f"PoW: Client meta - hasWorkers={client_meta.get('hasWorkers')} hasCrypto={client_meta.get('hasCrypto')} threads={client_meta.get('threads')} mode={client_meta.get('mode')} reason={client_meta.get('reason')}")
            if client_meta.get('mode') == 'single':
                logger.warning(f"PoW: Client running in single-thread mode, reason={client_meta.get('reason')}")
        except Exception:
            pass
        
        if not all([challenge_id, nonce, response, elapsed_time]):
            logger.warning(f"PoW: Missing fields in validation from {client_ip}")
            return JsonResponse({'valid': False, 'error': 'Missing fields'}, status=400)
        
        session_key = request.session.session_key
        if not session_key:
            logger.warning(f"PoW: No session for validation from {client_ip}")
            return JsonResponse({'valid': False, 'error': 'No session'}, status=400)
        
        try:
            challenge = PoWChallenge.objects.get(challenge=challenge_id)
        except PoWChallenge.DoesNotExist:
            logger.warning(f"PoW: Invalid challenge {challenge_id[:8]}... from {client_ip}")
            return JsonResponse({'valid': False, 'error': 'Invalid challenge'}, status=400)
        
        time_remaining = (challenge.expires_at - timezone.now()).total_seconds()
        logger.info(f"PoW: Challenge expires in {time_remaining:.1f}s")
        logger.info(f"PoW: Challenge created at {challenge.created_at}, expires at {challenge.expires_at}")
        logger.info(f"PoW: Challenge used: {challenge.used}, session_key match: {challenge.session_key == session_key}")
        logger.info(f"PoW: Current time: {timezone.now()}")
        
        valid, message = challenge.validate_solution(nonce, response, elapsed_time, session_key)
        
        if valid:
            logger.info(f"PoW: Valid solution from {client_ip} - nonce={nonce}, time={elapsed_time:.2f}s")
            request.session['pow_validated'] = True
            request.session['pow_challenge'] = challenge_id
            return JsonResponse({'valid': True, 'message': message})
        else:
            logger.warning(f"PoW: Invalid solution from {client_ip} - {message}")
            return JsonResponse({'valid': False, 'error': message}, status=400)
            
    except json.JSONDecodeError:
        logger.error(f"PoW: Invalid JSON from {client_ip}")
        return JsonResponse({'valid': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"PoW: Error validating from {client_ip}: {e}")
        return JsonResponse({'valid': False, 'error': str(e)}, status=500)
