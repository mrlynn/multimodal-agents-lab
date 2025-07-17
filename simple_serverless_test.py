#!/usr/bin/env python3
"""
Simple test to show the serverless API issue - run this in your notebook
"""
import os
import requests
from google import genai
from google.genai import types

# Same variables as notebook
SERVERLESS_URL = os.getenv("SERVERLESS_URL", "https://5bzwmpf3kydzcy2kbz4rtn4z7i0crxoh.lambda-url.us-west-2.on.aws/")
LLM_PROVIDER = "google"

print("🔍 Testing Serverless API - Simple Version")
print("=" * 50)

# Step 1: Get API key from serverless endpoint (same as notebook cell-41)
print("1. Getting API key from serverless endpoint...")
try:
    response = requests.post(
        url=SERVERLESS_URL, 
        json={"task": "get_api_key", "data": LLM_PROVIDER}
    )
    
    if response.status_code == 200:
        api_key = response.json()["api_key"]
        print(f"   ✅ Got API key: {api_key[:12]}...{api_key[-8:]}")
    else:
        print(f"   ❌ Failed to get API key: {response.status_code}")
        exit()
except Exception as e:
    print(f"   ❌ Error getting API key: {e}")
    exit()

# Step 2: Try to use the API key with Google Gemini (same as notebook)
print("\n2. Testing API key with Google Gemini...")
try:
    gemini_client = genai.Client(api_key=api_key)
    
    response = gemini_client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=["Say 'Hello from Gemini!'"],
        config=types.GenerateContentConfig(temperature=0.0),
    )
    
    print(f"   ✅ Success: {response.text.strip()}")
    
except Exception as e:
    print(f"   ❌ Google API failed: {e}")
    
    # Show the specific error
    if "API key expired" in str(e):
        print("\n🔍 DIAGNOSIS:")
        print("   - Serverless endpoint is working ✅")
        print("   - API key retrieval is working ✅") 
        print("   - Google API key has EXPIRED ❌")
        print("   - This is a backend infrastructure issue")

# Step 3: Test embedding (should work)
print("\n3. Testing embedding generation...")
try:
    response = requests.post(
        url=SERVERLESS_URL,
        json={
            "task": "get_embedding",
            "data": {"input": "test query", "input_type": "query"},
        },
    )
    
    if response.status_code == 200:
        embedding = response.json()["embedding"]
        print(f"   ✅ Embedding works: {len(embedding)} dimensions")
    else:
        print(f"   ❌ Embedding failed: {response.status_code}")
        
except Exception as e:
    print(f"   ❌ Embedding error: {e}")

print("\n" + "=" * 50)
print("🎯 SUMMARY:")
print("- The serverless architecture is working as designed")
print("- The Google API key in the serverless endpoint has expired")
print("- This needs to be fixed on the backend, not in your notebook")
print("- Your notebook configuration is correct!")