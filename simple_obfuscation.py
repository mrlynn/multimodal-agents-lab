# SIMPLE OBFUSCATION - Add this to your notebook

import os
import base64

# Method 1: Simple Base64 Obfuscation
def get_serverless_url():
    """Get serverless URL with obfuscation"""
    # Try environment variable first
    env_url = os.getenv("WORKSHOP_BACKEND_URL")
    if env_url:
        # Check if it's base64 encoded
        if os.getenv("ENCODING_TYPE") == "base64":
            return base64.b64decode(env_url).decode()
        return env_url
    
    # Fallback to obfuscated hardcoded value
    encoded = "aHR0cHM6Ly81Ynp3bXBmM2t5ZHpjeTJrYno0cnRuNHo3aTBjcnhvaC5sYW1iZGEtdXJsLnVzLXdlc3QtMi5vbi5hd3Mv"
    return base64.b64decode(encoded).decode()

# Method 2: Split URL Obfuscation
def get_serverless_url_split():
    """Get serverless URL by reconstructing from parts"""
    # Split the URL into less obvious parts
    protocol = "https://"
    subdomain = "5bzwmpf3kydzcy2kbz4rtn4z7i0crxoh"
    domain = ".lambda-url.us-west-2.on.aws/"
    
    return protocol + subdomain + domain

# Method 3: Environment Variable Obfuscation
def get_serverless_url_env():
    """Get serverless URL from obfuscated environment variables"""
    # Try multiple environment variable names
    env_vars = [
        "WORKSHOP_BACKEND_URL",
        "ML_SERVICE_ENDPOINT", 
        "GENAI_PROXY_URL",
        "SERVERLESS_URL"  # fallback to original
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            return value
    
    # If no env var found, use the obfuscated default
    return get_serverless_url()

# Usage in your notebook:
# Replace this line:
# SERVERLESS_URL = os.getenv("SERVERLESS_URL")

# With this line:
SERVERLESS_URL = get_serverless_url()

print(f"✅ Serverless URL configured: {SERVERLESS_URL[:30]}...")

# Test that it works
import requests
try:
    response = requests.post(
        url=SERVERLESS_URL,
        json={"task": "get_api_key", "data": "google"}
    )
    if response.status_code == 200:
        print("✅ Obfuscated URL is working!")
    else:
        print(f"❌ URL test failed: {response.status_code}")
except Exception as e:
    print(f"❌ URL test error: {e}")