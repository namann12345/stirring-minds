#!/usr/bin/env python3
"""
Test script to verify all required packages are installed
"""

import sys

def test_imports():
    """Test if all critical packages can be imported"""
    
    packages = {
        "FastAPI": "fastapi",
        "Uvicorn": "uvicorn",
        "Pydantic": "pydantic",
        "Motor (MongoDB async)": "motor",
        "PyMongo": "pymongo",
        "Pandas": "pandas",
        "NumPy": "numpy",
        "Scikit-learn": "sklearn",
        "OpenAI": "openai",
        "Groq": "groq",
        "ReportLab": "reportlab",
        "Requests": "requests",
        "Python-Jose": "jose",
        "Passlib": "passlib",
        "AioFiles": "aiofiles",
        "Python-dotenv": "dotenv",
    }
    
    failed = []
    
    print("🔍 Testing package imports...\n")
    
    for name, module in packages.items():
        try:
            __import__(module)
            print(f"✅ {name:30} - OK")
        except ImportError as e:
            print(f"❌ {name:30} - FAILED: {e}")
            failed.append(name)
    
    print("\n" + "="*60)
    
    if failed:
        print(f"⚠️  {len(failed)} package(s) failed to import:")
        for name in failed:
            print(f"   - {name}")
        return False
    else:
        print("✅ All packages imported successfully!")
        print("\n🚀 Your backend is ready to deploy!")
        return True

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
