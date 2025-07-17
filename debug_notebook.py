#!/usr/bin/env python3
"""
Debug utility for Multimodal Agents Lab notebook execution in Codespaces
"""
import os
import sys
import json
from datetime import datetime
import google.generativeai as genai
import voyageai
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def check_environment():
    """Check environment variables and API keys"""
    print_section("Environment Check")
    
    # Required environment variables
    env_vars = {
        "MONGODB_URI": os.environ.get("MONGODB_URI"),
        "SERVERLESS_URL": os.environ.get("SERVERLESS_URL"),
        "GOOGLE_API_KEY": os.environ.get("GOOGLE_API_KEY"),
        "VOYAGE_API_KEY": os.environ.get("VOYAGE_API_KEY")
    }
    
    # Display environment status
    for var, value in env_vars.items():
        if value:
            if "API_KEY" in var:
                # Mask API keys for security
                masked = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
                print(f"✅ {var}: {masked}")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: NOT SET")
    
    return env_vars

def test_mongodb_connection(uri):
    """Test MongoDB connection"""
    print_section("MongoDB Connection Test")
    
    if not uri:
        print("❌ MongoDB URI not set")
        return False
    
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        # Test connection
        client.admin.command('ping')
        print(f"✅ Successfully connected to MongoDB")
        
        # List databases
        dbs = client.list_database_names()
        print(f"   Available databases: {', '.join(dbs)}")
        
        client.close()
        return True
    except Exception as e:
        print(f"❌ MongoDB connection failed: {str(e)}")
        return False

def test_google_api(api_key):
    """Test Google Gemini API"""
    print_section("Google Gemini API Test")
    
    if not api_key:
        print("❌ Google API key not set")
        print("\n📝 To fix this:")
        print("   1. Get an API key from: https://makersuite.google.com/app/apikey")
        print("   2. Set it as an environment variable:")
        print("      export GOOGLE_API_KEY='your-api-key-here'")
        print("   3. Or add it to a .env file in the project root")
        return False
    
    try:
        genai.configure(api_key=api_key)
        
        # List available models
        models = genai.list_models()
        print("✅ Google API key is valid")
        print("   Available models:")
        for model in models:
            if "generateContent" in model.supported_generation_methods:
                print(f"   - {model.name}")
        
        # Test with a simple generation
        model = genai.GenerativeModel("gemini-2.0-flash-exp")
        response = model.generate_content("Say 'API test successful'")
        print(f"\n✅ Test generation: {response.text.strip()}")
        
        return True
    except Exception as e:
        print(f"❌ Google API test failed: {str(e)}")
        
        if "API key expired" in str(e):
            print("\n📝 Your API key has expired. Please:")
            print("   1. Generate a new key at: https://makersuite.google.com/app/apikey")
            print("   2. Update your environment variable or .env file")
        elif "API_KEY_INVALID" in str(e):
            print("\n📝 Your API key is invalid. Please check:")
            print("   1. The key is correctly copied (no extra spaces)")
            print("   2. The key is active in your Google Cloud Console")
        
        return False

def test_voyage_api(api_key):
    """Test Voyage AI API"""
    print_section("Voyage AI API Test")
    
    if not api_key:
        print("⚠️  Voyage API key not set (will use free tier)")
        return True  # Free tier is available
    
    try:
        vo = voyageai.Client(api_key=api_key)
        
        # Test embedding generation
        result = vo.embed(
            ["Test embedding"],
            model="voyage-3-lite",
            input_type="document"
        )
        
        print(f"✅ Voyage API key is valid")
        print(f"   Generated embedding dimension: {len(result.embeddings[0])}")
        
        return True
    except Exception as e:
        print(f"⚠️  Voyage API test failed: {str(e)}")
        print("   Will fall back to free tier")
        return True  # Free tier fallback

def create_env_template():
    """Create a template .env file"""
    print_section("Creating .env Template")
    
    template = """# Multimodal Agents Lab Environment Variables

# MongoDB Connection (provided by Codespaces)
MONGODB_URI="mongodb://admin:mongodb@mongodb:27017/"

# Serverless URL (provided)
SERVERLESS_URL="https://5bzwmpf3kydzcy2kbz4rtn4z7i0crxoh.lambda-url.us-west-2.on.aws/"

# Google Gemini API Key (required)
# Get yours at: https://makersuite.google.com/app/apikey
GOOGLE_API_KEY="your-google-api-key-here"

# Voyage AI API Key (optional - will use free tier if not provided)
# Get yours at: https://www.voyageai.com/
VOYAGE_API_KEY=""
"""
    
    env_path = "/Users/michael.lynn/code/ai4/original/multimodal-agents-lab/.env.template"
    
    with open(env_path, 'w') as f:
        f.write(template)
    
    print(f"✅ Created .env.template file")
    print("   Copy this to .env and add your API keys")

def main():
    """Run all debug checks"""
    print(f"\n🔍 Multimodal Agents Lab Debug Tool")
    print(f"   Timestamp: {datetime.now().isoformat()}")
    print(f"   Python: {sys.version.split()[0]}")
    print(f"   Working Dir: {os.getcwd()}")
    
    # Check environment
    env_vars = check_environment()
    
    # Test connections
    mongodb_ok = test_mongodb_connection(env_vars["MONGODB_URI"])
    google_ok = test_google_api(env_vars["GOOGLE_API_KEY"])
    voyage_ok = test_voyage_api(env_vars["VOYAGE_API_KEY"])
    
    # Create template if needed
    if not os.path.exists(".env"):
        create_env_template()
    
    # Summary
    print_section("Summary")
    
    if mongodb_ok and google_ok and voyage_ok:
        print("✅ All systems operational!")
        print("\n📝 Next steps:")
        print("   1. Open your notebook: jupyter notebook lab.ipynb")
        print("   2. Run the cells in order")
        print("   3. The agent should work correctly now")
    else:
        print("❌ Some issues detected")
        print("\n📝 To fix:")
        
        if not mongodb_ok:
            print("   - Check MongoDB container is running: docker ps")
            print("   - Verify connection string in environment")
        
        if not google_ok:
            print("   - Set up Google API key (see instructions above)")
            print("   - Add to .env file or environment variable")
        
        print("\n   Run this script again after fixing to verify")

if __name__ == "__main__":
    main()