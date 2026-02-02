"""
Test script to verify Gemini API key loading from app/services/.env
Run from project root:
    python app/services/test_gemini_env.py
"""

import os
from pathlib import Path
from dotenv import load_dotenv


def main():
    print("=" * 60)
    print("GEMINI ENV LOADING TEST (services/.env)")
    print("=" * 60)

    # 1️⃣ Resolve .env path exactly like gemini.py
    env_path = Path(__file__).parent / ".env"

    print("\n[1] Environment file check")
    print("Expected .env path:", env_path)
    print(".env exists:", env_path.exists())

    if not env_path.exists():
        print("❌ .env file NOT FOUND")
        return

    # 2️⃣ Load .env
    load_dotenv(dotenv_path=env_path, override=True)

    print("\n[2] Environment variables after load")
    print("GEMINI_API_KEY in os.environ:", "GEMINI_API_KEY" in os.environ)

    gemini_key = os.getenv("GEMINI_API_KEY")

    # 3️⃣ Key validation
    print("\n[3] Gemini key validation")

    if not gemini_key:
        print("❌ GEMINI_API_KEY is EMPTY or NOT SET")
        return

    gemini_key = gemini_key.strip()

    print("✅ GEMINI_API_KEY loaded successfully")
    print("Key length:", len(gemini_key))
    print("Key preview:", f"{gemini_key[:6]}...{gemini_key[-4:]}")

    # 4️⃣ Final verdict
    print("\n[4] Verdict")
    print("Gemini key usable:", gemini_key.startswith("AIza"))

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
