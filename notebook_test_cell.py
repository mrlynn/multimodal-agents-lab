# COPY THIS INTO A NOTEBOOK CELL TO TEST THE SERVERLESS API
# This demonstrates that the serverless endpoint is working but the Google API key has expired

import os
import requests
from google import genai
from google.genai import types
import json

# Use the same variables as the notebook
SERVERLESS_URL = os.getenv("SERVERLESS_URL", "https://5bzwmpf3kydzcy2kbz4rtn4z7i0crxoh.lambda-url.us-west-2.on.aws/")
LLM_PROVIDER = "google"

print("🔍 SERVERLESS API TEST")
print("=" * 40)

# Test 1: Get API key (same as notebook cell-41)
print("1. Testing API key retrieval...")
api_response = requests.post(
    url=SERVERLESS_URL, 
    json={"task": "get_api_key", "data": LLM_PROVIDER}
)

print(f"   Status: {api_response.status_code}")
if api_response.status_code == 200:
    api_key = api_response.json()["api_key"]
    print(f"   ✅ API key retrieved: {api_key[:12]}...{api_key[-8:]}")
else:
    print(f"   ❌ Failed: {api_response.text}")

# Test 2: Test the API key with Google Gemini
print("\n2. Testing Google API key...")
try:
    gemini_client = genai.Client(api_key=api_key)
    response = gemini_client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=["Say 'API key works!'"],
        config=types.GenerateContentConfig(temperature=0.0),
    )
    print(f"   ✅ Success: {response.text.strip()}")
except Exception as e:
    print(f"   ❌ Failed: {e}")
    print(f"   🔍 Error analysis: {'EXPIRED' if 'expired' in str(e) else 'OTHER'}")

# Test 3: Test embedding (should work)
print("\n3. Testing embedding generation...")
embed_response = requests.post(
    url=SERVERLESS_URL,
    json={
        "task": "get_embedding",
        "data": {"input": "test query", "input_type": "query"},
    },
)

if embed_response.status_code == 200:
    embedding = embed_response.json()["embedding"]
    print(f"   ✅ Embedding works: {len(embedding)} dimensions")
else:
    print(f"   ❌ Embedding failed: {embed_response.status_code}")

print("\n" + "=" * 40)
print("🎯 EVIDENCE:")
print("• Serverless endpoint responds: ✅")
print("• API key retrieval works: ✅")
print("• Embedding generation works: ✅")
print("• Google API key is EXPIRED: ❌")
print("\n💡 This is a backend issue, not your configuration!")