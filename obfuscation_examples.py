#!/usr/bin/env python3
"""
Examples of different ways to obfuscate API keys and sensitive URLs
"""
import os
import base64
import hashlib
from urllib.parse import urlparse

# Method 1: Base64 Encoding
def base64_obfuscation():
    """Base64 encode/decode sensitive strings"""
    print("🔐 Method 1: Base64 Encoding")
    
    # Original sensitive data
    api_key = "AIzaSyAEaO1UMo9k844-ejiP_dfT7R-EJk0xy4Q"
    serverless_url = "https://5bzwmpf3kydzcy2kbz4rtn4z7i0crxoh.lambda-url.us-west-2.on.aws/"
    
    # Encode
    encoded_key = base64.b64encode(api_key.encode()).decode()
    encoded_url = base64.b64encode(serverless_url.encode()).decode()
    
    print(f"Original API key: {api_key}")
    print(f"Encoded API key: {encoded_key}")
    print(f"Original URL: {serverless_url}")
    print(f"Encoded URL: {encoded_url}")
    
    # Decode (how you'd use it)
    decoded_key = base64.b64decode(encoded_key).decode()
    decoded_url = base64.b64decode(encoded_url).decode()
    
    print(f"Decoded API key: {decoded_key}")
    print(f"Decoded URL: {decoded_url}")
    print()

# Method 2: Environment Variables with Obfuscated Names
def env_var_obfuscation():
    """Use obfuscated environment variable names"""
    print("🔐 Method 2: Obfuscated Environment Variables")
    
    # Instead of GOOGLE_API_KEY, use something like:
    obfuscated_names = [
        "WORKSHOP_AUTH_TOKEN",
        "ML_SERVICE_KEY", 
        "GENAI_ACCESS_CODE",
        "SERVERLESS_ENDPOINT_URL",
        "LAMBDA_PROXY_URL",
        "WORKSHOP_BACKEND_URL"
    ]
    
    print("Use obfuscated environment variable names:")
    for name in obfuscated_names:
        print(f"  export {name}='your-secret-value'")
    print()

# Method 3: Split and Reconstruct
def split_reconstruct():
    """Split sensitive data into parts"""
    print("🔐 Method 3: Split and Reconstruct")
    
    # Split API key
    key_parts = ["AIzaSyAEaO1U", "Mo9k844-ejiP", "_dfT7R-EJk0xy4Q"]
    reconstructed_key = "".join(key_parts)
    
    # Split URL
    url_parts = [
        "https://",
        "5bzwmpf3kydzcy2kbz4rtn4z7i0crxoh",
        ".lambda-url.us-west-2.on.aws/"
    ]
    reconstructed_url = "".join(url_parts)
    
    print(f"Key parts: {key_parts}")
    print(f"Reconstructed: {reconstructed_key}")
    print(f"URL parts: {url_parts}")
    print(f"Reconstructed: {reconstructed_url}")
    print()

# Method 4: Simple Caesar Cipher
def caesar_cipher(text, shift=3):
    """Simple Caesar cipher for obfuscation"""
    result = ""
    for char in text:
        if char.isalpha():
            ascii_offset = 65 if char.isupper() else 97
            result += chr((ord(char) - ascii_offset + shift) % 26 + ascii_offset)
        else:
            result += char
    return result

def caesar_obfuscation():
    """Use Caesar cipher for obfuscation"""
    print("🔐 Method 4: Caesar Cipher")
    
    original = "AIzaSyAEaO1UMo9k844-ejiP_dfT7R-EJk0xy4Q"
    encoded = caesar_cipher(original, 3)
    decoded = caesar_cipher(encoded, -3)
    
    print(f"Original: {original}")
    print(f"Encoded: {encoded}")
    print(f"Decoded: {decoded}")
    print()

# Method 5: Hash-based Lookup
def hash_lookup():
    """Use hash-based lookup for sensitive data"""
    print("🔐 Method 5: Hash-based Lookup")
    
    # Create a lookup table with hashed keys
    secrets = {
        "google_api": "AIzaSyAEaO1UMo9k844-ejiP_dfT7R-EJk0xy4Q",
        "serverless_endpoint": "https://5bzwmpf3kydzcy2kbz4rtn4z7i0crxoh.lambda-url.us-west-2.on.aws/"
    }
    
    # Hash the keys
    hashed_secrets = {}
    for key, value in secrets.items():
        hashed_key = hashlib.md5(key.encode()).hexdigest()[:8]
        hashed_secrets[hashed_key] = value
    
    print("Hashed lookup table:")
    for hashed_key, value in hashed_secrets.items():
        print(f"  {hashed_key}: {value[:20]}...")
    print()

# Method 6: Configuration File Obfuscation
def config_file_obfuscation():
    """Store obfuscated values in a config file"""
    print("🔐 Method 6: Configuration File")
    
    config_content = """
# workshop_config.py
import base64

# Obfuscated configuration
ENCODED_CONFIGS = {
    'auth_token': 'QUl6YVN5QUVhTzFVTW85azg0NC1lamlQX2RmVDdSLUVKazB4eTRR',
    'backend_url': 'aHR0cHM6Ly81Ynp3bXBmM2t5ZHpjeTJrYno0cnRuNHo3aTBjcnhvaC5sYW1iZGEtdXJsLnVzLXdlc3QtMi5vbi5hd3Mv'
}

def get_config(key):
    return base64.b64decode(ENCODED_CONFIGS[key]).decode()
"""
    
    print("Configuration file approach:")
    print(config_content)

# Method 7: Practical Implementation for Notebooks
def practical_notebook_implementation():
    """Practical implementation for Jupyter notebooks"""
    print("🔐 Method 7: Practical Notebook Implementation")
    
    notebook_code = '''
# Cell 1: Obfuscated configuration
import base64
import os

# Obfuscated endpoint (base64 encoded)
ENCODED_ENDPOINT = "aHR0cHM6Ly81Ynp3bXBmM2t5ZHpjeTJrYno0cnRuNHo3aTBjcnhvaC5sYW1iZGEtdXJsLnVzLXdlc3QtMi5vbi5hd3Mv"

def get_serverless_url():
    """Get the serverless URL from environment or decode obfuscated value"""
    return os.getenv("WORKSHOP_BACKEND_URL", base64.b64decode(ENCODED_ENDPOINT).decode())

def get_api_key_from_service():
    """Get API key from serverless endpoint"""
    import requests
    response = requests.post(
        url=get_serverless_url(),
        json={"task": "get_api_key", "data": "google"}
    )
    return response.json()["api_key"]

# Usage
SERVERLESS_URL = get_serverless_url()
api_key = get_api_key_from_service()
'''
    
    print("Notebook implementation:")
    print(notebook_code)

# Method 8: Environment-based Obfuscation
def env_based_obfuscation():
    """Use environment variables for different levels of obfuscation"""
    print("🔐 Method 8: Environment-based Obfuscation")
    
    env_setup = '''
# .env file
WORKSHOP_MODE=production
AUTH_SERVICE_URL=aHR0cHM6Ly81Ynp3bXBmM2t5ZHpjeTJrYno0cnRuNHo3aTBjcnhvaC5sYW1iZGEtdXJsLnVzLXdlc3QtMi5vbi5hd3Mv
ML_PROVIDER=google
BACKEND_ENCODING=base64

# Python code
import os
import base64

def get_backend_url():
    encoding = os.getenv("BACKEND_ENCODING", "plain")
    url = os.getenv("AUTH_SERVICE_URL")
    
    if encoding == "base64":
        return base64.b64decode(url).decode()
    return url
'''
    
    print("Environment-based approach:")
    print(env_setup)

if __name__ == "__main__":
    print("🔐 API KEY AND URL OBFUSCATION METHODS")
    print("=" * 60)
    
    base64_obfuscation()
    env_var_obfuscation()
    split_reconstruct()
    caesar_obfuscation()
    hash_lookup()
    config_file_obfuscation()
    practical_notebook_implementation()
    env_based_obfuscation()
    
    print("=" * 60)
    print("💡 RECOMMENDATIONS:")
    print("1. For notebooks: Use base64 encoding + environment variables")
    print("2. For production: Use proper secret management (AWS Secrets Manager, etc.)")
    print("3. For workshops: Use the serverless proxy pattern (current approach)")
    print("4. Always: Never commit secrets to version control")