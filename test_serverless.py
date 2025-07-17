#!/usr/bin/env python3
"""
Test the serverless endpoint to verify it's working correctly
"""
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SERVERLESS_URL = os.getenv("SERVERLESS_URL", "https://5bzwmpf3kydzcy2kbz4rtn4z7i0crxoh.lambda-url.us-west-2.on.aws/")
LLM_PROVIDER = "google"

def test_serverless_endpoint():
    """Test the serverless endpoint for API key retrieval"""
    print(f"🔍 Testing serverless endpoint: {SERVERLESS_URL}")
    
    try:
        # Test API key retrieval
        response = requests.post(
            url=SERVERLESS_URL, 
            json={"task": "get_api_key", "data": LLM_PROVIDER}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Serverless endpoint is working!")
            
            if "api_key" in result:
                api_key = result["api_key"]
                print(f"   API key retrieved: {api_key[:8]}...{api_key[-4:]}" if len(api_key) > 12 else "   API key retrieved")
                
                # Test the API key with Google Gemini
                test_google_api_key(api_key)
            else:
                print(f"❌ No API key in response: {result}")
        else:
            print(f"❌ Serverless endpoint failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing serverless endpoint: {str(e)}")

def test_google_api_key(api_key):
    """Test the retrieved API key with Google Gemini"""
    try:
        from google import genai
        from google.genai import types
        
        # Initialize client with API key
        gemini_client = genai.Client(api_key=api_key)
        
        # Test with a simple generation
        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=["Say 'API test successful'"],
            config=types.GenerateContentConfig(temperature=0.0),
        )
        
        print(f"✅ Google API key is valid!")
        print(f"   Test response: {response.text.strip()}")
        
    except Exception as e:
        print(f"❌ Google API key test failed: {str(e)}")

def test_embedding_endpoint():
    """Test the embedding generation endpoint"""
    print(f"\n🔍 Testing embedding endpoint...")
    
    try:
        response = requests.post(
            url=SERVERLESS_URL,
            json={
                "task": "get_embedding",
                "data": {"input": "test query", "input_type": "query"},
            },
        )
        
        if response.status_code == 200:
            result = response.json()
            if "embedding" in result:
                embedding = result["embedding"]
                print(f"✅ Embedding endpoint is working!")
                print(f"   Embedding dimension: {len(embedding)}")
            else:
                print(f"❌ No embedding in response: {result}")
        else:
            print(f"❌ Embedding endpoint failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing embedding endpoint: {str(e)}")

if __name__ == "__main__":
    print("🚀 Testing Serverless Endpoint Configuration")
    print("=" * 50)
    
    test_serverless_endpoint()
    test_embedding_endpoint()
    
    print("\n" + "=" * 50)
    print("✅ Test complete!")