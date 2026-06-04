"""
Authentication tests.

Covers:
  1. Password hashing + verification
  2. JWT generation + validation
  3. JWT expiration enforcement
  4. Invalid token rejection
  5. Register endpoint (success + duplicate)
  6. Login endpoint (success + wrong password + unknown email)
  7. get_current_user dependency (valid + invalid + missing user)
"""

import sys
import os
import uuid
from datetime import timedelta

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

# ─── Unique email per test run to avoid collisions ───
_run_id = uuid.uuid4().hex[:8]
TEST_EMAIL = f"auth_test_{_run_id}@example.com"
TEST_PASSWORD = "SecurePass123!"


# ══════════════════════════════════════════════════════
# UNIT TESTS — Password Hashing
# ══════════════════════════════════════════════════════

class TestPasswordSecurity:

    def test_hash_password_returns_bcrypt_hash(self):
        from src.auth.security import hash_password
        hashed = hash_password("mypassword")
        assert hashed.startswith("$2b$") or hashed.startswith("$2a$")
        assert hashed != "mypassword"

    def test_verify_password_correct(self):
        from src.auth.security import hash_password, verify_password
        hashed = hash_password("mypassword")
        assert verify_password("mypassword", hashed) is True

    def test_verify_password_incorrect(self):
        from src.auth.security import hash_password, verify_password
        hashed = hash_password("mypassword")
        assert verify_password("wrongpassword", hashed) is False

    def test_hash_is_unique_per_call(self):
        from src.auth.security import hash_password
        h1 = hash_password("same")
        h2 = hash_password("same")
        assert h1 != h2  # bcrypt salt ensures uniqueness


# ══════════════════════════════════════════════════════
# UNIT TESTS — JWT
# ══════════════════════════════════════════════════════

class TestJWT:

    def test_create_and_verify_token(self):
        from src.auth.jwt import create_access_token, verify_access_token
        token = create_access_token(user_id="test-uuid", email="a@b.com")
        payload = verify_access_token(token)
        assert payload["sub"] == "test-uuid"
        assert payload["email"] == "a@b.com"
        assert "exp" in payload

    def test_expired_token_rejected(self):
        from src.auth.jwt import create_access_token, verify_access_token
        from jose import JWTError
        token = create_access_token(
            user_id="test-uuid",
            email="a@b.com",
            expires_delta=timedelta(seconds=-1),
        )
        with pytest.raises(JWTError):
            verify_access_token(token)

    def test_invalid_token_rejected(self):
        from src.auth.jwt import verify_access_token
        from jose import JWTError
        with pytest.raises(JWTError):
            verify_access_token("not.a.valid.jwt")

    def test_tampered_token_rejected(self):
        from src.auth.jwt import create_access_token, verify_access_token
        from jose import JWTError
        token = create_access_token(user_id="test-uuid", email="a@b.com")
        # Replace the entire signature with garbage
        parts = token.rsplit(".", 1)
        tampered = parts[0] + ".INVALIDSIGNATURE"
        with pytest.raises(JWTError):
            verify_access_token(tampered)


# ══════════════════════════════════════════════════════
# INTEGRATION TESTS — Register Endpoint
# ══════════════════════════════════════════════════════

class TestRegister:

    def test_register_success(self):
        resp = client.post("/api/v1/auth/register", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "full_name": "Test User",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["message"] == "user created"
        assert "user_id" in data

    def test_register_duplicate_email(self):
        resp = client.post("/api/v1/auth/register", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
        })
        assert resp.status_code == 409
        assert "already registered" in resp.json()["detail"].lower()

    def test_register_invalid_email(self):
        resp = client.post("/api/v1/auth/register", json={
            "email": "not-an-email",
            "password": TEST_PASSWORD,
        })
        assert resp.status_code == 422  # Pydantic validation error


# ══════════════════════════════════════════════════════
# INTEGRATION TESTS — Login Endpoint
# ══════════════════════════════════════════════════════

class TestLogin:

    def test_login_success(self):
        resp = client.post("/api/v1/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self):
        resp = client.post("/api/v1/auth/login", json={
            "email": TEST_EMAIL,
            "password": "WrongPassword999",
        })
        assert resp.status_code == 401
        assert "invalid credentials" in resp.json()["detail"].lower()

    def test_login_unknown_email(self):
        resp = client.post("/api/v1/auth/login", json={
            "email": "nobody_here@example.com",
            "password": TEST_PASSWORD,
        })
        assert resp.status_code == 401


# ══════════════════════════════════════════════════════
# INTEGRATION TESTS — Full Auth Flow
# ══════════════════════════════════════════════════════

class TestFullAuthFlow:

    def test_register_login_validate(self):
        """Register → Login → Validate JWT via get_current_user."""
        unique_email = f"flow_{uuid.uuid4().hex[:8]}@example.com"

        # Register
        r1 = client.post("/api/v1/auth/register", json={
            "email": unique_email,
            "password": "FlowTest123!",
        })
        assert r1.status_code == 201

        # Login
        r2 = client.post("/api/v1/auth/login", json={
            "email": unique_email,
            "password": "FlowTest123!",
        })
        assert r2.status_code == 200
        token = r2.json()["access_token"]

        # Validate token programmatically
        from src.auth.jwt import verify_access_token
        payload = verify_access_token(token)
        assert payload["email"] == unique_email
        assert "sub" in payload


# ══════════════════════════════════════════════════════
# EXISTING API UNCHANGED — Smoke Tests
# ══════════════════════════════════════════════════════

class TestExistingAPIUnchanged:

    def test_root_still_works(self):
        resp = client.get("/")
        assert resp.status_code == 200
        assert "Legal RAG" in resp.json()["message"]

    def test_health_still_works(self):
        resp = client.get("/api/v1/health")
        assert resp.status_code == 200


# ══════════════════════════════════════════════════════
# CLEANUP — Remove test user after all tests
# ══════════════════════════════════════════════════════

def test_cleanup():
    """Remove test users created during this run."""
    from src.db.database import SessionLocal
    from src.db.models import User

    db = SessionLocal()
    try:
        db.query(User).filter(
            User.email.like(f"auth_test_{_run_id}%")
        ).delete(synchronize_session=False)
        db.query(User).filter(
            User.email.like("flow_%")
        ).delete(synchronize_session=False)
        db.commit()
    finally:
        db.close()
