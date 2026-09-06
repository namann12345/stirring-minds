#!/usr/bin/env python3
"""
Final verification script for Render deployment
Tests all critical components before deploying
"""

import os
import sys
from pathlib import Path

def check_files():
    """Check if all required files exist"""
    print("📁 Checking required files...\n")
    
    files = {
        "main.py": "FastAPI application",
        "requirements.txt": "Python dependencies",
        "render.yaml": "Render configuration",
        ".env": "Environment variables (DO NOT COMMIT)",
    }
    
    all_exist = True
    for filename, description in files.items():
        path = Path(filename)
        if path.exists():
            print(f"✅ {filename:20} - {description}")
        else:
            print(f"❌ {filename:20} - MISSING: {description}")
            all_exist = False
    
    return all_exist

def check_env_variables():
    """Check if critical environment variables are set"""
    print("\n🔐 Checking environment variables...\n")
    
    required_vars = {
        "MONGODB_URI": "MongoDB connection string",
        "MONGODB_DB_NAME": "Database name",
        "SECRET_KEY": "JWT secret key",
    }
    
    all_set = True
    for var_name, description in required_vars.items():
        value = os.getenv(var_name)
        if value and len(value) > 5:
            masked = value[:10] + "***" + value[-5:] if len(value) > 15 else "***"
            print(f"✅ {var_name:20} - SET ({masked})")
        else:
            print(f"⚠️  {var_name:20} - NOT SET or EMPTY")
            all_set = False
    
    return all_set

def check_packages():
    """Check if all critical packages are installed"""
    print("\n📦 Checking critical packages...\n")
    
    packages = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("pydantic", "Pydantic"),
        ("motor", "Motor (MongoDB)"),
        ("pandas", "Pandas"),
    ]
    
    all_installed = True
    for module_name, display_name in packages:
        try:
            __import__(module_name)
            print(f"✅ {display_name:20} - Installed")
        except ImportError:
            print(f"❌ {display_name:20} - NOT INSTALLED")
            all_installed = False
    
    return all_installed

def check_render_yaml():
    """Check render.yaml configuration"""
    print("\n⚙️  Checking render.yaml...\n")
    
    try:
        with open("render.yaml", "r") as f:
            content = f.read()
        
        checks = {
            "rootDir: backend" in content or "root_dir: backend" in content: "Root directory configured",
            "autonomous-report-backend" in content: "Service name configured",
            "pip install" in content: "Build command configured",
            "gunicorn" in content: "Start command uses gunicorn",
            "main:app" in content: "FastAPI app reference correct",
        }
        
        all_ok = True
        for check, description in checks.items():
            if check:
                print(f"✅ {description}")
            else:
                print(f"⚠️  {description} - VERIFY")
                all_ok = False
        
        return all_ok
    except FileNotFoundError:
        print("❌ render.yaml not found!")
        return False

def print_summary(files_ok, env_ok, packages_ok, render_ok):
    """Print final summary"""
    print("\n" + "="*60)
    print("📊 DEPLOYMENT READINESS SUMMARY")
    print("="*60 + "\n")
    
    checks = [
        ("Files & Structure", files_ok),
        ("Environment Variables", env_ok),
        ("Python Packages", packages_ok),
        ("Render Configuration", render_ok),
    ]
    
    all_passed = all(status for _, status in checks)
    
    for name, status in checks:
        symbol = "✅" if status else "⚠️ "
        print(f"{symbol} {name:30} {'READY' if status else 'NEEDS ATTENTION'}")
    
    print("\n" + "="*60)
    
    if all_passed:
        print("✅ YOUR BACKEND IS READY FOR RENDER DEPLOYMENT! 🚀")
        print("\nNext steps:")
        print("1. Update render.yaml with your GitHub repo URL")
        print("2. Push to GitHub: git push origin main")
        print("3. Go to Render dashboard and create Web Service")
        print("4. Set environment variables in Render")
        print("5. Click Deploy!")
    else:
        print("⚠️  SOME ITEMS NEED ATTENTION")
        print("\nFix issues and run this script again")
        print("Check RENDER_READY.md for detailed instructions")
    
    print("="*60 + "\n")
    
    return all_passed

def main():
    print("\n" + "="*60)
    print("🔍 RENDER DEPLOYMENT VERIFICATION")
    print("="*60 + "\n")
    
    files_ok = check_files()
    env_ok = check_env_variables()
    packages_ok = check_packages()
    render_ok = check_render_yaml()
    
    ready = print_summary(files_ok, env_ok, packages_ok, render_ok)
    
    sys.exit(0 if ready else 1)

if __name__ == "__main__":
    main()
