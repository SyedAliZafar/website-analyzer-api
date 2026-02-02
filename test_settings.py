"""
Debug script to test your exact Gemini API key configuration.
Run: python debug_api_key.py
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))


def check_env_file():
    """Check if .env file exists and contains the keys"""
    print("\n" + "=" * 60)
    print("STEP 1: Checking .env file")
    print("=" * 60)
    
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file NOT found in current directory")
        print(f"   Current directory: {Path.cwd()}")
        print("   Please create a .env file with your API keys")
        return False
    
    print(f"✅ .env file found at: {env_file.absolute()}")
    
    # Read and check contents
    with open(env_file, 'r') as f:
        contents = f.read()
    
    has_gemini = "GEMINI_API_KEY" in contents
    has_pagespeed = "PAGESPEED_API_KEY" in contents
    
    print(f"   GEMINI_API_KEY in file: {'✅ Yes' if has_gemini else '❌ No'}")
    print(f"   PAGESPEED_API_KEY in file: {'✅ Yes' if has_pagespeed else '❌ No'}")
    
    return has_gemini


def check_env_loading():
    """Check if environment variables are loaded"""
    print("\n" + "=" * 60)
    print("STEP 2: Checking environment variable loading")
    print("=" * 60)
    
    # Try loading with python-dotenv
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ python-dotenv loaded successfully")
    except ImportError:
        print("⚠️ python-dotenv not installed")
    
    # Check if variables are in environment
    gemini_key = os.getenv("GEMINI_API_KEY")
    pagespeed_key = os.getenv("PAGESPEED_API_KEY")
    
    if gemini_key:
        print(f"✅ GEMINI_API_KEY loaded from environment")
        print(f"   Length: {len(gemini_key)} characters")
        print(f"   First 10 chars: {gemini_key[:10]}...")
        print(f"   Starts with 'AIza': {'✅ Yes' if gemini_key.startswith('AIza') else '❌ No'}")
    else:
        print("❌ GEMINI_API_KEY NOT loaded from environment")
    
    if pagespeed_key:
        print(f"✅ PAGESPEED_API_KEY loaded from environment")
        print(f"   Length: {len(pagespeed_key)} characters")
        print(f"   First 10 chars: {pagespeed_key[:10]}...")
    else:
        print("❌ PAGESPEED_API_KEY NOT loaded from environment")
    
    return gemini_key


def check_pydantic_settings():
    """Check if Pydantic settings loads the keys"""
    print("\n" + "=" * 60)
    print("STEP 3: Checking Pydantic Settings loading")
    print("=" * 60)
    
    try:
        from app.core.config import get_settings
        settings = get_settings()
        
        print("✅ Settings loaded successfully")
        
        if settings.gemini_api_key:
            print(f"✅ settings.gemini_api_key loaded")
            print(f"   Length: {len(settings.gemini_api_key)} characters")
            print(f"   First 10 chars: {settings.gemini_api_key[:10]}...")
            print(f"   Starts with 'AIza': {'✅ Yes' if settings.gemini_api_key.startswith('AIza') else '❌ No'}")
        else:
            print("❌ settings.gemini_api_key is None")
        
        if settings.pagespeed_api_key:
            print(f"✅ settings.pagespeed_api_key loaded")
            print(f"   Length: {len(settings.pagespeed_api_key)} characters")
        else:
            print("❌ settings.pagespeed_api_key is None")
        
        return settings.gemini_api_key.get_secret_value()

        
    except Exception as exc:
        print(f"❌ Failed to load settings: {exc}")
        import traceback
        traceback.print_exc()
        return None

def test_gemini_api(api_key: str):
    print("\n" + "=" * 60)
    print("STEP 4: Testing Gemini API directly")
    print("=" * 60)

    from google import genai
    import os

    # 🔥 FORCE THE KEY (override any poisoned env var)
    clean_key = api_key.strip()
    os.environ["GOOGLE_API_KEY"] = clean_key
    os.environ["GEMINI_API_KEY"] = clean_key

    print(f"🔑 Testing with API key: {clean_key[:10]}...")
    print(f"🔎 Raw repr: {repr(clean_key)}")

    client = genai.Client(api_key=clean_key)
    print("✅ Gemini client initialized")

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Reply with just: {'status': 'ok'}"
    )

    print("✅ Gemini API responded successfully!")
    print(response.text)



def main():
    print("\n" + "=" * 70)
    print("  GEMINI API KEY DEBUGGING TOOL")
    print("=" * 70)
    
    # Step 1: Check .env file
    has_env_file = check_env_file()
    
    # Step 2: Check environment loading
    env_api_key = check_env_loading()
    
    # Step 3: Check Pydantic settings
    settings_api_key = check_pydantic_settings()
    
    # Step 4: Test actual API if we have a key
    if settings_api_key:
        test_gemini_api(settings_api_key)
    elif env_api_key:
        print("\n⚠️ API key found in environment but not in settings - configuration issue")
        test_gemini_api(env_api_key)
    else:
        print("\n❌ No API key found - cannot test Gemini API")
    
    print("\n" + "=" * 70)
    print("  DEBUGGING COMPLETE")
    print("=" * 70)
    
    # Summary
    print("\n📋 SUMMARY:")
    print(f"   .env file exists: {'✅' if has_env_file else '❌'}")
    print(f"   Environment variables loaded: {'✅' if env_api_key else '❌'}")
    print(f"   Pydantic settings loaded: {'✅' if settings_api_key else '❌'}")
    
    if not has_env_file:
        print("\n💡 NEXT STEPS:")
        print("   1. Create a .env file in your project root")
        print("   2. Add: GEMINI_API_KEY=your_key_here")
        print("   3. Get your API key from: https://aistudio.google.com/app/apikey")
    elif not settings_api_key:
        print("\n💡 NEXT STEPS:")
        print("   1. Check your .env file format (no quotes, no spaces around =)")
        print("   2. Restart your application to reload environment variables")
        print("   3. Verify the API key starts with 'AIza'")


if __name__ == "__main__":
    main()