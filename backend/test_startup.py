#!/usr/bin/env python3
"""Test script to verify backend starts correctly."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test all critical imports."""
    print("Testing imports...")

    try:
        from app.main import app
        print("✅ FastAPI app imported")
    except Exception as e:
        print(f"❌ Failed to import app: {e}")
        return False

    try:
        from app.models import (
            Team, User, SessionModel, SessionParticipant,
            SessionMessage, SessionEvent, TeamMetric
        )
        print("✅ All models imported")
    except Exception as e:
        print(f"❌ Failed to import models: {e}")
        return False

    try:
        from app.auth import create_access_token, verify_password
        print("✅ Auth functions imported")
    except Exception as e:
        print(f"❌ Failed to import auth: {e}")
        return False

    try:
        from app.collaboration.chat import ChatManager
        from app.collaboration.presence import PresenceManager
        from app.collaboration.connection_manager import ConnectionManager
        print("✅ Collaboration managers imported")
    except Exception as e:
        print(f"❌ Failed to import managers: {e}")
        return False

    try:
        from app.websocket import router
        print("✅ WebSocket router imported")
    except Exception as e:
        print(f"❌ Failed to import websocket: {e}")
        return False

    return True

def test_database_models():
    """Test database models can be created."""
    print("\nTesting database models...")

    try:
        from app.database import engine, Base

        # Try to create tables (in memory)
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create tables: {e}")
        return False

def test_token_generation():
    """Test JWT token generation."""
    print("\nTesting JWT token generation...")

    try:
        from app.auth import create_access_token, get_password_hash, verify_password
        from datetime import timedelta

        # Test token creation
        token = create_access_token(
            data={"sub": "test_user", "user_id": "test_123"},
            expires_delta=timedelta(hours=1)
        )
        print(f"✅ Token generated: {token[:50]}...")

        # Test password hashing
        password = "test_password"
        hashed = get_password_hash(password)
        print(f"✅ Password hashed: {hashed[:30]}...")

        # Test password verification
        is_valid = verify_password(password, hashed)
        if is_valid:
            print("✅ Password verification works")
        else:
            print("❌ Password verification failed")
            return False

        return True
    except Exception as e:
        print(f"❌ Failed token/password test: {e}")
        return False

def main():
    """Run all tests."""
    print("="*60)
    print("Backend Startup Test")
    print("="*60)

    tests = [
        ("Imports", test_imports),
        ("Database Models", test_database_models),
        ("Authentication", test_token_generation),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Test '{name}' crashed: {e}")
            results.append((name, False))

    print("\n" + "="*60)
    print("Test Results")
    print("="*60)

    all_passed = True
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
        if not result:
            all_passed = False

    print("="*60)

    if all_passed:
        print("\n🎉 All tests passed! Backend is ready to start.")
        print("\nTo start the server, run:")
        print("  uvicorn app.main:app --reload")
        return 0
    else:
        print("\n❌ Some tests failed. Please fix the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
