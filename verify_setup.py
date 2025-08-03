import os
from dotenv import load_dotenv
import voyageai
from google import genai
from pymongo import MongoClient

# Load environment variables
load_dotenv()

def verify_setup():
    """Verify all workshop prerequisites are configured correctly."""
    
    print("🔍 Verifying Workshop Setup...\n")
    
    checks_passed = 0
    total_checks = 3
    
    # Check Voyage AI
    try:
        voyage_client = voyageai.Client(api_key=os.getenv("VOYAGE_API_KEY"))
        response = voyage_client.embed(texts=["test"], model="voyage-2")
        print("✅ Voyage AI API key verified")
        checks_passed += 1
    except Exception as e:
        print(f"❌ Voyage AI verification failed: {e}")
    
    # Check Gemini
    try:
        gemini_client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash",
            contents="Test"
        )
        print("✅ Google Gemini API key verified")
        checks_passed += 1
    except Exception as e:
        print(f"❌ Gemini verification failed: {e}")
    
    # Check MongoDB
    try:
        mongodb_client = MongoClient(os.getenv("MONGODB_URI"))
        result = mongodb_client.admin.command("ping")
        if result.get("ok") == 1:
            print("✅ MongoDB Atlas connection verified")
            checks_passed += 1
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
    
    # Summary
    print(f"\n📊 Setup Status: {checks_passed}/{total_checks} checks passed")
    
    if checks_passed == total_checks:
        print("\n🎉 All prerequisites configured successfully!")
        print("You're ready to start the workshop!")
        return True
    else:
        print("\n⚠️ Some prerequisites are missing.")
        print("Please review the errors above and check your .env file.")
        return False

if __name__ == "__main__":
    verify_setup()