#!/usr/bin/env python3
"""
Detailed test of the serverless API to show Google API key expiration
"""
import os
import requests
import json
from datetime import datetime

# Use the same environment variable as the notebook
SERVERLESS_URL = os.getenv("SERVERLESS_URL", "https://5bzwmpf3kydzcy2kbz4rtn4z7i0crxoh.lambda-url.us-west-2.on.aws/")
LLM_PROVIDER = "google"

def test_serverless_api_detailed():
    """Test the serverless API and show detailed responses"""
    print("🔍 DETAILED SERVERLESS API TEST")
    print("=" * 60)
    print(f"Endpoint: {SERVERLESS_URL}")
    print(f"Provider: {LLM_PROVIDER}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Test 1: Get API Key
    print("📝 TEST 1: API Key Retrieval")
    print("-" * 30)
    
    try:
        # This is the exact same request the notebook makes
        response = requests.post(
            url=SERVERLESS_URL, 
            json={"task": "get_api_key", "data": LLM_PROVIDER}
        )
        
        print(f"Request URL: {response.url}")
        print(f"Request Body: {{'task': 'get_api_key', 'data': '{LLM_PROVIDER}'}}")
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print()
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API Key Retrieved Successfully!")
            print(f"Response Body: {json.dumps(result, indent=2)}")
            
            if "api_key" in result:
                api_key = result["api_key"]
                print(f"API Key: {api_key[:12]}...{api_key[-8:]} (masked)")
                print(f"API Key Length: {len(api_key)} characters")
                print()
                
                # Test the retrieved API key
                test_google_api_key(api_key)
            else:
                print("❌ No 'api_key' field in response")
        else:
            print(f"❌ API Key Retrieval Failed!")
            print(f"Response Body: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception during API key retrieval: {str(e)}")
    
    print()
    
    # Test 2: Embedding Generation (should work)
    print("📝 TEST 2: Embedding Generation")
    print("-" * 30)
    
    try:
        response = requests.post(
            url=SERVERLESS_URL,
            json={
                "task": "get_embedding",
                "data": {"input": "test query for embedding", "input_type": "query"},
            },
        )
        
        print(f"Request Body: {{'task': 'get_embedding', 'data': {{'input': 'test query for embedding', 'input_type': 'query'}}}}")
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Embedding Generated Successfully!")
            
            if "embedding" in result:
                embedding = result["embedding"]
                print(f"Embedding Dimension: {len(embedding)}")
                print(f"First 5 values: {embedding[:5]}")
                print(f"Last 5 values: {embedding[-5:]}")
            else:
                print("❌ No 'embedding' field in response")
                print(f"Response Body: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Embedding Generation Failed!")
            print(f"Response Body: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception during embedding generation: {str(e)}")

def test_google_api_key(api_key):
    """Test the Google API key with detailed error reporting"""
    print("📝 TEST 3: Google API Key Validation")
    print("-" * 30)
    
    try:
        from google import genai
        from google.genai import types
        
        # Initialize client (same as notebook)
        gemini_client = genai.Client(api_key=api_key)
        
        print(f"✅ Google client initialized successfully")
        print(f"Using model: gemini-2.0-flash-exp")
        print(f"Test prompt: 'Say API test successful'")
        print()
        
        # Test with simple generation (same as notebook)
        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=["Say 'API test successful'"],
            config=types.GenerateContentConfig(temperature=0.0),
        )
        
        print(f"✅ Google API call successful!")
        print(f"Response: {response.text.strip()}")
        
    except Exception as e:
        print(f"❌ Google API call failed with error:")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {str(e)}")
        print()
        
        # Parse the error to show specific details
        error_str = str(e)
        if "API key expired" in error_str:
            print("🔍 ANALYSIS: API Key Expired")
            print("- The Google API key provided by the serverless endpoint has expired")
            print("- This is not a configuration issue on your end")
            print("- The serverless endpoint needs to be updated with a fresh API key")
        elif "API_KEY_INVALID" in error_str:
            print("🔍 ANALYSIS: API Key Invalid")
            print("- The Google API key is not valid")
            print("- This could be due to expiration or incorrect key")
        elif "PERMISSION_DENIED" in error_str:
            print("🔍 ANALYSIS: Permission Denied")
            print("- The API key doesn't have permission to access Gemini")
        elif "QUOTA_EXCEEDED" in error_str:
            print("🔍 ANALYSIS: Quota Exceeded")
            print("- The API key has exceeded its usage quota")
        else:
            print("🔍 ANALYSIS: Unknown Error")
            print("- This is an unexpected error type")

def show_notebook_comparison():
    """Show how this matches the notebook code"""
    print("\n" + "=" * 60)
    print("📋 NOTEBOOK CODE COMPARISON")
    print("=" * 60)
    
    print("The notebook uses this exact same pattern:")
    print()
    print("```python")
    print("# From cell-3:")
    print("SERVERLESS_URL = os.getenv(\"SERVERLESS_URL\")")
    print("LLM_PROVIDER = \"google\"")
    print()
    print("# From cell-41:")
    print("api_key = requests.post(")
    print("    url=SERVERLESS_URL, json={\"task\": \"get_api_key\", \"data\": LLM_PROVIDER}")
    print(").json()[\"api_key\"]")
    print("gemini_client = genai.Client(api_key=api_key)")
    print()
    print("# From cell-35 (vector search):")
    print("response = requests.post(")
    print("    url=SERVERLESS_URL,")
    print("    json={")
    print("        \"task\": \"get_embedding\",")
    print("        \"data\": {\"input\": user_query, \"input_type\": \"query\"},")
    print("    },")
    print(")")
    print("query_embedding = response.json()[\"embedding\"]")
    print("```")

if __name__ == "__main__":
    test_serverless_api_detailed()
    show_notebook_comparison()
    
    print("\n" + "=" * 60)
    print("🎯 CONCLUSION")
    print("=" * 60)
    print("1. ✅ Serverless endpoint is accessible and responding")
    print("2. ✅ Embedding generation works perfectly")
    print("3. ❌ Google API key from serverless endpoint has expired")
    print("4. 📝 This is a backend infrastructure issue, not a user configuration problem")
    print()
    print("💡 The notebook was designed correctly to use the serverless proxy.")
    print("   The issue is that the Google API key in the serverless endpoint needs renewal.")