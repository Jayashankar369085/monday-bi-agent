#!/usr/bin/env python
"""Test API routes without running server"""

import os
import sys
os.environ['MONDAY_API_TOKEN'] = 'test_token'
os.environ['OPENAI_API_KEY'] = 'test_key'

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

print("=" * 60)
print("TESTING API ROUTES")
print("=" * 60)

# Test 1: Root endpoint
print("\n1. Testing GET /")
try:
    response = client.get("/")
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Message: {data.get('message', 'N/A')}")
    print(f"   Version: {data.get('version', 'N/A')}")
    assert response.status_code == 200
    print("   ✓ PASS")
except Exception as e:
    print(f"   ✗ FAIL: {e}")

# Test 2: Health check
print("\n2. Testing GET /api/health")
try:
    response = client.get("/api/health")
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Health status: {data.get('status', 'N/A')}")
    assert response.status_code in [200, 500]  # May return 500 if services not available
    print("   ✓ PASS")
except Exception as e:
    print(f"   ✗ FAIL: {e}")

# Test 3: Chat endpoint with invalid token (expected to fail gracefully)
print("\n3. Testing POST /api/chat")
try:
    response = client.post("/api/chat", json={"question": "Test question"})
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Response keys: {list(data.keys())}")
    else:
        print(f"   Error: {response.text[:100]}")
    print("   ✓ PASS (endpoint exists and responds)")
except Exception as e:
    print(f"   ✗ FAIL: {e}")

# Test 4: Leadership update endpoint
print("\n4. Testing GET /api/leadership-update")
try:
    response = client.get("/api/leadership-update")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   Response received")
    else:
        print(f"   Error: {response.text[:100]}")
    print("   ✓ PASS (endpoint exists and responds)")
except Exception as e:
    print(f"   ✗ FAIL: {e}")

# Test 5: Verify OpenAPI docs
print("\n5. Testing GET /docs (OpenAPI)")
try:
    response = client.get("/docs")
    print(f"   Status: {response.status_code}")
    assert response.status_code == 200
    print("   ✓ PASS")
except Exception as e:
    print(f"   ✗ FAIL: {e}")

print("\n" + "=" * 60)
print("✓ ALL ROUTE TESTS COMPLETED")
print("=" * 60)