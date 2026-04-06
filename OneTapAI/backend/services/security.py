"""
Security Service for ZIEL-MAS
Handles token generation, encryption, and permission scoping
"""

import jwt
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
from loguru import logger


class SecurityService:
    """
    Security service for token management and encryption
    Handles JWT tokens, encryption/decryption, and permission scoping
    """

    def __init__(
        self,
        jwt_secret: str,
        encryption_key: Optional[str] = None,
        jwt_algorithm: str = "HS256",
        token_expiry_hours: int = 24
    ):
        if not jwt_secret or len(jwt_secret) < 16:
            raise ValueError("JWT secret must be at least 16 characters long")

        self.jwt_secret = jwt_secret
        self.jwt_algorithm = jwt_algorithm
        self.token_expiry_hours = token_expiry_hours

        # Initialize encryption
        if encryption_key:
            # Validate encryption key length
            if len(encryption_key) < 32:
                raise ValueError("Encryption key must be at least 32 characters long")

            # Derive a proper key from the provided secret
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'ziel_mas_salt',  # In production, use a random salt per application
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(encryption_key.encode()))
            self.cipher = Fernet(key)
        else:
            # Generate a new key (should be saved for production)
            self.cipher = Fernet.generate_key()
            self.cipher = Fernet(self.cipher)

    # Token Generation and Validation

    def generate_execution_token(self, execution_id: str, user_id: Optional[str] = None) -> str:
        """
        Generate a secure execution token
        Returns a JWT token containing execution reference
        """
        try:
            payload = {
                "execution_id": execution_id,
                "user_id": user_id,
                "type": "execution",
                "iat": datetime.utcnow(),
                "exp": datetime.utcnow() + timedelta(hours=self.token_expiry_hours),
                "jti": secrets.token_hex(16)  # Unique token ID
            }

            token = jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
            logger.info(f"Generated execution token for {execution_id}")
            return token
        except Exception as e:
            logger.error(f"Failed to generate execution token: {e}")
            raise

    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Validate and decode a JWT token
        Returns payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=[self.jwt_algorithm]
            )
            logger.info(f"Validated token for execution {payload.get('execution_id')}")
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None

    def generate_api_key(self, user_id: str) -> str:
        """Generate an API key for a user"""
        key_prefix = f"ziel_{user_id[:8]}"
        random_part = secrets.token_urlsafe(32)
        return f"{key_prefix}_{random_part}"

    def hash_api_key(self, api_key: str) -> str:
        """Hash an API key for storage"""
        return hashlib.sha256(api_key.encode()).hexdigest()

    # Encryption and Decryption

    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        try:
            encrypted = self.cipher.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise

    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        try:
            encrypted = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self.cipher.decrypt(encrypted)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise

    def encrypt_dict(self, data: Dict[str, Any]) -> str:
        """Encrypt a dictionary (converts to JSON first)"""
        import json
        json_str = json.dumps(data)
        return self.encrypt_data(json_str)

    def decrypt_dict(self, encrypted_data: str) -> Dict[str, Any]:
        """Decrypt to a dictionary"""
        import json
        json_str = self.decrypt_data(encrypted_data)
        return json.loads(json_str)

    # Permission Scoping

    def check_permission(self, required_permission: str, user_permissions: List[str]) -> bool:
        """Check if user has required permission"""
        # Admin has all permissions
        if "admin" in user_permissions:
            return True

        # Direct match
        if required_permission in user_permissions:
            return True

        # Wildcard matching (e.g., "api.*" matches "api.execute")
        for perm in user_permissions:
            if perm.endswith("*"):
                prefix = perm[:-1]
                if required_permission.startswith(prefix):
                    return True

        return False

    def scope_token_permissions(
        self,
        token: str,
        allowed_actions: List[str],
        allowed_resources: List[str] = None
    ) -> Dict[str, Any]:
        """
        Add permission scoping to a token
        Limits what the token can be used for
        """
        payload = self.validate_token(token)
        if not payload:
            raise ValueError("Invalid token")

        payload["allowed_actions"] = allowed_actions
        if allowed_resources:
            payload["allowed_resources"] = allowed_resources

        # Re-encode with new permissions
        new_token = jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
        return new_token

    def verify_token_permission(self, token: str, required_action: str) -> bool:
        """Verify if token has permission for specific action"""
        payload = self.validate_token(token)
        if not payload:
            return False

        allowed_actions = payload.get("allowed_actions", [])
        return required_action in allowed_actions or "*" in allowed_actions

    # Input Validation

    def validate_intent(self, intent: str) -> tuple[bool, Optional[str]]:
        """
        Validate user intent for security
        Checks for malicious patterns, injection attempts, etc.
        """
        # Check for empty or whitespace-only intent
        if not intent or not intent.strip():
            return False, "Intent cannot be empty or whitespace only"

        # Check for intent length
        if len(intent) >= 10000:
            return False, "Intent must be between 1 and 10000 characters"

        # Check for potential injection patterns
        dangerous_patterns = [
            # XSS patterns (case-insensitive checks will be done separately)
            "<script>", "javascript:", "eval(", "exec(",
            "onerror=", "onload=", "onclick=", "<img", "<iframe", "<object",
            # SQL Injection patterns (more comprehensive)
            "DROP TABLE", "DELETE FROM", "INSERT INTO", "UPDATE", "' OR '", "' OR '1'='1",
            "'; DROP", "1' OR '1'='1", "UNION SELECT", "'; --", "';--", "--", "/*", "*/",
            "admin'--", "admin' --", "'--", "' --", "'#", "' #", "or 1=1", "or 1=1--",
            "exec(", "execute(", "sp_executesql", "xp_cmdshell",
            # Command injection
            "__import__", "subprocess", "os.system", "$(", "`", "exec(", ";", "|", "&",
            # Path traversal (including URL-encoded)
            "../../", "..\\", "/etc/passwd", "\\windows\\system32", "..%2f", "..%5c",
            "%2e%2e", "%252e", "%2f", "%5c", "etc/passwd", "windows\\system32",
            # LDAP injection (more comprehensive)
            "*)(", "*)(uid=*", "*)(&", "(|(cn=*)", "*)(mail=*", "*)(&(objectclass=*",
            "*))%00", "*)%", "*|%00", "*)%", "*)(*", "*)(cn=*))%",
            # XML injection
            "<!ENTITY", "SYSTEM", "DOCTYPE", "]]>",
            # Header injection
            "\r\n", "\n", "%0d", "%0a",
            # Template injection
            "{{", "}}", "{%", "%}",
            # Null bytes
            "%00", "\\x00", "\\u0000",
        ]

        intent_lower = intent.lower()
        for pattern in dangerous_patterns:
            if pattern.lower() in intent_lower:
                logger.warning(f"Potentially malicious intent detected: {pattern}")
                return False, f"Intent contains forbidden pattern: {pattern}"

        # Additional checks for complex patterns
        # Check for newlines in intent (header injection)
        if '\n' in intent or '\r' in intent:
            logger.warning("Potentially malicious intent detected: newline characters")
            return False, "Intent contains forbidden newline characters"

        # Check for template injection patterns
        if "{{" in intent or "}}" in intent or "{%" in intent or "%}" in intent:
            logger.warning("Potentially malicious intent detected: template injection")
            return False, "Intent contains forbidden template injection patterns"

        return True, None

    def validate_url(self, url: str) -> bool:
        """Validate URL is safe and allowed"""
        from urllib.parse import urlparse

        try:
            parsed = urlparse(url)
            if not parsed.scheme or parsed.scheme not in ["http", "https"]:
                return False

            if parsed.scheme == "http" and "localhost" not in parsed.netloc:
                logger.warning(f"Insecure HTTP URL detected: {url}")
                return False

            return True
        except Exception:
            return False

    # Rate Limiting Helpers

    def generate_rate_limit_key(self, user_id: str, action: str) -> str:
        """Generate a key for rate limiting"""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H")
        return f"ratelimit:{user_id}:{action}:{timestamp}"

    # Audit Logging Helpers

    def create_audit_hash(self, data: Dict[str, Any]) -> str:
        """Create a hash for audit trail verification"""
        import json
        json_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()

    # Session Management

    def create_session_token(self, user_id: str, session_data: Dict[str, Any]) -> str:
        """Create a session token for user"""
        payload = {
            "user_id": user_id,
            "type": "session",
            "session_data": session_data,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)

    def validate_session_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate session token and return session data"""
        try:
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=[self.jwt_algorithm]
            )
            if payload.get("type") != "session":
                return None
            return payload
        except jwt.InvalidTokenError:
            return None

    # Secure Random Generation

    def generate_secure_id(self, prefix: str = "") -> str:
        """Generate a secure random ID"""
        random_part = secrets.token_urlsafe(16)
        return f"{prefix}{random_part}" if prefix else random_part

    def generate_nonce(self) -> str:
        """Generate a nonce for cryptographic operations"""
        return secrets.token_hex(16)

    # API Whitelist Management

    def is_api_allowed(self, api_url: str, whitelist: List[str]) -> bool:
        """Check if API URL is in whitelist"""
        from urllib.parse import urlparse

        try:
            parsed = urlparse(api_url)
            domain = parsed.netloc

            for allowed in whitelist:
                if domain.endswith(allowed) or allowed == "*":
                    return True

            logger.warning(f"API not in whitelist: {api_url}")
            return False
        except Exception as e:
            logger.error(f"API validation error: {e}")
            return False

    # Password Management

    def hash_password(self, password: str) -> str:
        """Hash a password using secure hashing (bcrypt-like format)"""
        # For better security, use bcrypt-like format: $2b$12$salt22characters31charactershash
        import bcrypt

        # Generate salt and hash
        salt = bcrypt.gensalt().decode('utf-8')
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt.encode('utf-8')).decode('utf-8')

        return hashed

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        import bcrypt

        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception:
            return False

    def generate_random_string(self, length: int = 16) -> str:
        """Generate a random string for tokens, keys, etc."""
        import secrets
        import string
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
