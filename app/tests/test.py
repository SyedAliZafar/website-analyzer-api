"""
Test script to verify Gemini API configuration
Run this to diagnose Gemini issues: python test_gemini.py
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import get_settings
from app.core.logging import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


async def test_gemini():
    """Test Gemini API configuration and connectivity"""
    
    print("=" * 60)
    print("GEMINI API CONFIGURATION TEST")
    print("=" * 60)
    
    # Test 1: Check settings
    print("\n[1] Checking configuration...")
    settings = get_settings()
    
    if settings.gemini_api_key:
        print(f"✅ GEMINI_API_KEY is configured (length: {len(settings.gemini_api_key)})")
        print(f"   First 10 chars: {settings.gemini_api_key[:10]}...")
    else:
        print("❌ GEMINI_API_KEY is NOT configured")
        print("   Please set GEMINI_API_KEY in your .env file")
        return
    
    # Test 2: Try to initialize Gemini
    print("\n[2] Testing Gemini initialization...")
    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        print("✅ Gemini model initialized successfully")
    except Exception as exc:
        print(f"❌ Failed to initialize Gemini: {exc}")
        return
    
    # Test 3: Try a simple request
    print("\n[3] Testing Gemini API call...")
    try:
        test_prompt = """
You are a test bot. Respond with valid JSON only:
{
  "status": "success",
  "message": "Gemini is working correctly"
}
"""
        print("   Sending test prompt...")
        
        # Use threading to avoid blocking
        response = await asyncio.to_thread(
            model.generate_content,
            test_prompt
        )
        
        print("   Response received!")
        print(f"   Response text: {response.text[:200]}")
        
        # Try to parse as JSON
        import json
        response_text = response.text.strip()
        if response_text.startswith("```"):
            response_text = response_text.split("```", 2)[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
        response_text = response_text.strip()
        
        data = json.loads(response_text)
        print(f"✅ Gemini API is working! Response: {data}")
        
    except Exception as exc:
        print(f"❌ Gemini API call failed: {exc}")
        import traceback
        traceback.print_exc()
        return
    
    # Test 4: Test with the actual GeminiAnalyzer class
    print("\n[4] Testing GeminiAnalyzer class...")
    try:
        from app.services.gemini import GeminiAnalyzer
        from app.models.schemas import AIInsights
        
        analyzer = GeminiAnalyzer()
        
        if not analyzer.model:
            print("❌ GeminiAnalyzer failed to initialize model")
            return
        
        print("✅ GeminiAnalyzer initialized successfully")
        
        # Test generate_insights with minimal data
        print("   Testing generate_insights...")
        insights = await analyzer.generate_insights(
            url="https://example.com",
            desktop=None,
            mobile=None,
            overall_score=75.0
        )
        
        print(f"✅ Insights generated successfully!")
        print(f"   Summary: {insights.summary}")
        print(f"   Strengths: {len(insights.strengths)}")
        print(f"   Weaknesses: {len(insights.weaknesses)}")
        
    except Exception as exc:
        print(f"❌ GeminiAnalyzer test failed: {exc}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED - Gemini is configured correctly!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_gemini())