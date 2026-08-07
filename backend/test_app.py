#!/usr/bin/env python
"""Test FastAPI app startup"""

import sys
import os

# Set test environment
os.environ['MONDAY_API_TOKEN'] = 'test_token'
os.environ['OPENAI_API_KEY'] = 'test_key'

try:
    from app.main import app
    print("✓ FastAPI app imported successfully")
    print(f"✓ App title: {app.title}")
    print(f"✓ App version: {app.version}")
    print(f"✓ Routes registered: {len(app.routes)}")
    
    # List routes
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            print(f"  - {route.path} {route.methods}")
    
    print("\n✓ SUCCESS: Backend can start")
    sys.exit(0)
except Exception as e:
    print(f"✗ FAILED: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
