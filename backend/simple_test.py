import sys
import os

print("Python version:", sys.version)
print("Python path:", sys.executable)
print("Current dir:", os.getcwd())
print("App dir exists:", os.path.exists('app'))
print("Main.py exists:", os.path.exists('app/main.py'))

try:
    import fastapi
    print("FastAPI available: Yes")
except:
    print("FastAPI available: No")

try:
    from app.core.config import settings
    print("Config loaded: Yes")
except Exception as e:
    print(f"Config load error: {e}")

try:
    from app.main import app
    print("App loaded: Yes")
    print(f"Routes: {len(app.routes)}")
except Exception as e:
    print(f"App load error: {e}")
