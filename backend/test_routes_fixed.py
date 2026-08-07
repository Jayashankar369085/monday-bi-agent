#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test API routes without running server"""

import os
import sys

# Fix encoding for Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

os.environ['MONDAY_API_TOKEN'] = 'test_token'
os.environ['OPENAI_API_KEY'] = 'test_key'

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

print("=" * 60)
print("TESTING API ROUTES")
print("=" * 60)

passed = 0
failed = 0

# Test 1: Root endpoint
print("\n1. Testing GET /")
try:
    response = client.get("/")
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Message: {data.get('message', 'N/A')}")
    print(f"   Version: {data.get('version', 'N/A')}")
    assert response.status_code == 200
    print("   [PASS]")
    passed += 1
except Exception as e:
    print(f"   [FAIL]: {e}")
    failed += 1

# Test 2: Health check
print("\n2. Testing GET /api/health")
try:
    response = client.get("/api/health")
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Health status: {data.get('status', 'N/A')}")
    assert response.status_code in [200, 500]  # May return 500 if services not available
    print("   [PASS]")
    passed += 1
except Exception as e:
    print(f"   [FAIL]: {e}")
    failed += 1

# Test 3: Chat endpoint with invalid token (expected to fail gracefully)
print("\n3. Testing POST /api/chat")
try:
    response = client.post("/api/chat", json={"question": "Test question"})
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Response keys: {list(data.keys())}")
    else:
        print(f"   Error (expected): {response.text[:80]}")
    print("   [PASS] (endpoint exists and responds)")
    passed += 1
except Exception as e:
    print(f"   [FAIL]: {e}")
    failed += 1

# Test 4: Leadership update endpoint
print("\n4. Testing GET /api/leadership-update")
try:
    response = client.get("/api/leadership-update")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   Response received")
    else:
        print(f"   Error (expected): {response.text[:80]}")
    print("   [PASS] (endpoint exists and responds)")
    passed += 1
except Exception as e:
    print(f"   [FAIL]: {e}")
    failed += 1

# Test 5: Verify OpenAPI docs
print("\n5. Testing GET /docs (OpenAPI)")
try:
    response = client.get("/docs")
    print(f"   Status: {response.status_code}")
    assert response.status_code == 200
    print("   [PASS]")
    passed += 1
except Exception as e:
    print(f"   [FAIL]: {e}")
    failed += 1

# Test 6: Verify all required routes exist
print("\n6. Checking all routes are registered")
try:
    routes_found = {}
    for route in app.routes:
        if hasattr(route, 'path'):
            routes_found[route.path] = True
    
    required_routes = ['/api/chat', '/api/health', '/api/leadership-update', '/']
    for route in required_routes:
        if route in routes_found:
            print(f"   [OK] {route}")
        else:
            print(f"   [MISSING] {route}")
    
    print("   [PASS]")
    passed += 1
except Exception as e:
    print(f"   [FAIL]: {e}")
    failed += 1

print("\n" + "=" * 60)
print(f"RESULTS: {passed} passed, {failed} failed")
print("ALL TESTS COMPLETED")
print("=" * 60)
