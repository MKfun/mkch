import hashlib
import hmac
import secrets
import time
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.cache import cache

class PoWChallenge(models.Model):
    challenge = models.CharField(max_length=64, unique=True)
    session_key = models.CharField(max_length=40, db_index=True)
    difficulty = models.IntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    hmac_signature = models.CharField(max_length=64)
    
    @classmethod
    def create_challenge(cls, session_key, difficulty=5, ttl=1800): 
        challenge = secrets.token_hex(32)
        expires_at = timezone.now() + timezone.timedelta(seconds=ttl)
        
        hmac_signature = hmac.new(
            settings.SECRET_KEY.encode(),
            f"{challenge}{session_key}{expires_at.timestamp()}".encode(),
            hashlib.sha256
        ).hexdigest()
        
        return cls.objects.create(
            challenge=challenge,
            session_key=session_key,
            difficulty=difficulty,
            expires_at=expires_at,
            hmac_signature=hmac_signature
        )
    
    def is_valid(self, session_key):
        if self.used or timezone.now() > self.expires_at:
            return False
        
        if self.session_key != session_key:
            return False
        
        expected_hmac = hmac.new(
            settings.SECRET_KEY.encode(),
            f"{self.challenge}{session_key}{self.expires_at.timestamp()}".encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(self.hmac_signature, expected_hmac)
    
    def validate_solution(self, nonce, response, elapsed_time, session_key):
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"PoW: validate_solution - used: {self.used}, expires_at: {self.expires_at}, now: {timezone.now()}")
        logger.info(f"PoW: validate_solution - session_key match: {self.session_key == session_key}")
        
        if timezone.now() > self.expires_at:
            logger.warning(f"PoW: Challenge expired - now: {timezone.now()}, expires: {self.expires_at}")
            return False, "Challenge expired"
        
        if self.session_key != session_key:
            logger.warning(f"PoW: Invalid session - expected: {self.session_key}, got: {session_key}")
            return False, "Invalid session"
        
        expected_hmac = hmac.new(
            settings.SECRET_KEY.encode(),
            f"{self.challenge}{session_key}{self.expires_at.timestamp()}".encode(),
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(self.hmac_signature, expected_hmac):
            return False, "Invalid challenge signature"
        
        if elapsed_time < 1.0 or elapsed_time > 300:
            return False, "Invalid execution time"
        
        calc_string = f"{self.challenge}{nonce}"
        calculated = hashlib.sha256(calc_string.encode()).hexdigest()
        
        if calculated != response:
            return False, "Invalid solution"
        
        if not response.startswith('0' * self.difficulty):
            return False, "Insufficient difficulty"
        
        return True, "Valid solution"
