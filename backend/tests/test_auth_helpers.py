import os
import sys
import pytest
from datetime import datetime, timedelta, timezone
import jwt

# Add parent directory to path so we can import backend modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.utils.auth_helpers import (
    hash_password,
    verify_password,
    generate_token,
    decode_token,
    JWT_SECRET_KEY,
    JWT_EXPIRATION_HOURS,
    JWT_ALGORITHM,
)


# Password Hashing Tests 

class TestHashPassword:
    
    def test_hash_password_valid(self):
        password = "testpassword123"
        hashed = hash_password(password)
        
        assert hashed is not None
        assert isinstance(hashed, str)
        assert len(hashed) > 0
        assert hashed != password  # Should be different from original
    
    def test_hash_password_different_hashes(self):
        password = "samepassword"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        # Hashes should be different due to salt, but both should verify
        assert hash1 != hash2
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True
    
    def test_hash_password_empty_string(self):
        with pytest.raises(ValueError, match="Password must be a non-empty string"):
            hash_password("")
    
    def test_hash_password_none(self):
        with pytest.raises(ValueError, match="Password must be a non-empty string"):
            hash_password(None)
    
    def test_hash_password_non_string(self):
        with pytest.raises(ValueError, match="Password must be a non-empty string"):
            hash_password(12345)
        
        with pytest.raises(ValueError, match="Password must be a non-empty string"):
            hash_password([])
        
        with pytest.raises(ValueError, match="Password must be a non-empty string"):
            hash_password({})


# Password Verification Tests 

class TestVerifyPassword:
    
    def test_verify_password_correct(self):
        password = "correctpassword"
        hashed = hash_password(password)
        
        result = verify_password(password, hashed)
        assert result is True
    
    def test_verify_password_incorrect(self):
        password = "correctpassword"
        wrong_password = "wrongpassword"
        hashed = hash_password(password)
        
        result = verify_password(wrong_password, hashed)
        assert result is False
    
    def test_verify_password_empty_hashed(self):
        result = verify_password("anypassword", "")
        assert result is False
    
    def test_verify_password_none_hashed(self):
        result = verify_password("anypassword", None)
        assert result is False
    
    def test_verify_password_different_passwords(self):
        password1 = "password1"
        password2 = "password2"
        hashed = hash_password(password1)
        
        assert verify_password(password1, hashed) is True
        assert verify_password(password2, hashed) is False


# Token Generation Tests 

class TestGenerateToken:
    
    def test_generate_token_valid_email(self):
        email = "test@example.com"
        token = generate_token(email)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_generate_token_contains_email(self):
        email = "user@test.com"
        token = generate_token(email)
        
        # Decode token to verify payload
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        assert payload["email"] == email
        assert payload["sub"] == email
    
    def test_generate_token_has_expiration(self):
        email = "test@example.com"
        token = generate_token(email)
        
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        assert "exp" in payload
        assert "iat" in payload
        
        # Check expiration is in the future
        exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        now = datetime.now(timezone.utc)
        assert exp_time > now
    
    def test_generate_token_expiration_time(self):
        email = "test@example.com"
        token = generate_token(email)
        
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        iat_time = datetime.fromtimestamp(payload["iat"], tz=timezone.utc)
        exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        
        # Check expiration is approximately JWT_EXPIRATION_HOURS from now
        time_diff = exp_time - iat_time
        expected_hours = timedelta(hours=JWT_EXPIRATION_HOURS)
        
        # Allow small margin for execution time
        assert abs((time_diff - expected_hours).total_seconds()) < 5
    
    def test_generate_token_different_emails(self):
        email1 = "user1@test.com"
        email2 = "user2@test.com"
        
        token1 = generate_token(email1)
        token2 = generate_token(email2)
        
        assert token1 != token2
        
        # Verify tokens contain correct emails
        payload1 = jwt.decode(token1, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        payload2 = jwt.decode(token2, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        assert payload1["email"] == email1
        assert payload2["email"] == email2


# Token Decoding Tests 

class TestDecodeToken:
    
    def test_decode_token_valid(self):
        email = "test@example.com"
        token = generate_token(email)
        
        payload = decode_token(token)
        
        assert payload is not None
        assert payload["email"] == email
        assert payload["sub"] == email
        assert "iat" in payload
        assert "exp" in payload
    
    def test_decode_token_expired(self):
        # Create an expired token manually
        now = datetime.now(timezone.utc)
        exp = now - timedelta(hours=1)  # Expired 1 hour ago
        payload = {
            "sub": "test@example.com",
            "email": "test@example.com",
            "iat": int((now - timedelta(hours=2)).timestamp()),
            "exp": int(exp.timestamp()),
        }
        expired_token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        if isinstance(expired_token, bytes):
            expired_token = expired_token.decode("utf-8")
        
        result = decode_token(expired_token)
        assert result is None
    
    def test_decode_token_invalid_signature(self):
        email = "test@example.com"
        token = generate_token(email)
        
        # Modify token to have invalid signature
        invalid_token = token[:-5] + "xxxxx"
        
        result = decode_token(invalid_token)
        assert result is None
    
    def test_decode_token_wrong_secret(self):
        email = "test@example.com"
        # Generate token with different secret
        wrong_secret = "wrong-secret-key"
        payload = {
            "sub": email,
            "email": email,
            "iat": int(datetime.now(timezone.utc).timestamp()),
            "exp": int((datetime.now(timezone.utc) + timedelta(hours=24)).timestamp()),
        }
        wrong_token = jwt.encode(payload, wrong_secret, algorithm=JWT_ALGORITHM)
        if isinstance(wrong_token, bytes):
            wrong_token = wrong_token.decode("utf-8")
        
        result = decode_token(wrong_token)
        assert result is None
    
    def test_decode_token_malformed(self):
        malformed_token = "not.a.valid.token"
        
        result = decode_token(malformed_token)
        assert result is None
    
    def test_decode_token_empty_string(self):
        result = decode_token("")
        assert result is None
    
    def test_decode_token_none(self):
        # This might raise an exception, but let's test it
        try:
            result = decode_token(None)
            # If it doesn't raise, it should return None
            assert result is None
        except (TypeError, AttributeError):
            # If it raises an exception, that's also acceptable behavior
            pass
    
    def test_decode_token_round_trip(self):
        email = "roundtrip@test.com"
        token = generate_token(email)
        payload = decode_token(token)
        
        assert payload is not None
        assert payload["email"] == email

