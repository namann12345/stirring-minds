#!/usr/bin/env python
"""
Verify all critical imports from main.py can be loaded
Run this before pushing to Render to catch any missing packages
"""
import sys

critical_imports = {
    "fastapi": "FastAPI web framework",
    "uvicorn": "ASGI server",
    "pydantic": "Data validation",
    "jwt": "JWT token handling (PyJWT)",
    "passlib": "Password hashing",
    "jose": "JWT utilities (python_jose)",
    "pandas": "Data processing",
    "numpy": "Numerical computing",
    "scipy": "Scientific computing",
    "openpyxl": "Excel file handling",
    "motor": "Async MongoDB driver",
    "pymongo": "MongoDB client",
    "bson": "BSON encoding",
    "reportlab": "PDF generation",
    "openai": "OpenAI API",
    "groq": "Groq API",
    "sklearn": "Scikit-learn ML library",
    "dotenv": "Environment variables",
    "requests": "HTTP client",
    "httpx": "Async HTTP client",
    "jsonschema": "JSON validation",
    "colorama": "Terminal colors",
}

failed = []
passed = []

print("\n" + "=" * 70)
print("VERIFYING CRITICAL IMPORTS FOR RENDER DEPLOYMENT")
print("=" * 70 + "\n")

for module_name, description in critical_imports.items():
    try:
        __import__(module_name)
        status = "✅ PASS"
        passed.append(module_name)
    except ImportError as e:
        status = f"❌ FAIL: {str(e)}"
        failed.append((module_name, str(e)))
    
    print(f"{status:50} | {module_name:20} | {description}")

print("\n" + "=" * 70)
print(f"SUMMARY: {len(passed)}/{len(critical_imports)} imports successful")
print("=" * 70 + "\n")

if failed:
    print("❌ FAILED IMPORTS:")
    for module_name, error in failed:
        print(f"  - {module_name}: {error}")
    sys.exit(1)
else:
    print("✅ ALL CRITICAL IMPORTS AVAILABLE - READY FOR RENDER DEPLOYMENT")
    sys.exit(0)
