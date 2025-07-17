# OBFUSCATED NOTEBOOK IMPLEMENTATION
# Replace the current cells in your notebook with these obfuscated versions

# =============================================================================
# CELL 1: Obfuscated Configuration Setup
# =============================================================================

import os
import base64

# Obfuscated serverless endpoint (base64 encoded)
# Original: https://5bzwmpf3kydzcy2kbz4rtn4z7i0crxoh.lambda-url.us-west-2.on.aws/
ENCODED_ENDPOINT = "aHR0cHM6Ly81Ynp3bXBmM2t5ZHpjeTJrYno0cnRuNHo3aTBjcnhvaC5sYW1iZGEtdXJsLnVzLXdlc3QtMi5vbi5hd3Mv"

def get_workshop_endpoint():
    """Get the workshop endpoint from environment or decode obfuscated value"""
    # Try environment variable first (for different environments)
    env_url = os.getenv("WORKSHOP_BACKEND_URL") or os.getenv("SERVERLESS_URL")
    if env_url:
        return env_url
    
    # Fallback to obfuscated endpoint
    return base64.b64decode(ENCODED_ENDPOINT).decode()

# Set up configuration
SERVERLESS_URL = get_workshop_endpoint()
LLM_PROVIDER = "google"

print(f"✅ Workshop endpoint configured: {SERVERLESS_URL[:30]}...")

# =============================================================================
# CELL 2: Obfuscated API Key Retrieval
# =============================================================================

import requests
from google import genai
from google.genai import types

def get_auth_token():
    """Get authentication token from workshop service"""
    try:
        response = requests.post(
            url=SERVERLESS_URL,
            json={"task": "get_api_key", "data": LLM_PROVIDER}
        )
        
        if response.status_code == 200:
            return response.json()["api_key"]
        else:
            raise Exception(f"Auth service returned {response.status_code}")
            
    except Exception as e:
        print(f"❌ Failed to get auth token: {e}")
        raise

# Get authentication token and initialize client
auth_token = get_auth_token()
gemini_client = genai.Client(api_key=auth_token)

print(f"✅ Authentication configured: {auth_token[:12]}...")

# =============================================================================
# CELL 3: Obfuscated Embedding Service
# =============================================================================

def get_vector_embedding(query_text, input_type="query"):
    """Get vector embedding from workshop service"""
    try:
        response = requests.post(
            url=SERVERLESS_URL,
            json={
                "task": "get_embedding",
                "data": {"input": query_text, "input_type": input_type},
            },
        )
        
        if response.status_code == 200:
            return response.json()["embedding"]
        else:
            raise Exception(f"Embedding service returned {response.status_code}")
            
    except Exception as e:
        print(f"❌ Failed to get embedding: {e}")
        raise

# Test the embedding service
test_embedding = get_vector_embedding("test query")
print(f"✅ Embedding service working: {len(test_embedding)} dimensions")

# =============================================================================
# CELL 4: Alternative Environment Variable Approach
# =============================================================================

# For even more obfuscation, use environment variables with non-obvious names
ENV_VAR_MAPPINGS = {
    "WORKSHOP_SERVICE_URL": "serverless_url",
    "ML_AUTH_ENDPOINT": "serverless_url", 
    "BACKEND_API_URL": "serverless_url",
    "GENAI_PROXY_URL": "serverless_url"
}

def get_service_config():
    """Get service configuration from various environment variables"""
    # Try different environment variable names
    for env_var, config_key in ENV_VAR_MAPPINGS.items():
        value = os.getenv(env_var)
        if value:
            return value
    
    # Fallback to standard name
    return os.getenv("SERVERLESS_URL")

# Use this instead of hardcoding
ALTERNATIVE_URL = get_service_config() or base64.b64decode(ENCODED_ENDPOINT).decode()

# =============================================================================
# CELL 5: Advanced Obfuscation with Multiple Layers
# =============================================================================

import hashlib

class WorkshopConfig:
    """Workshop configuration with multiple obfuscation layers"""
    
    def __init__(self):
        self._config = {
            # Base64 encoded configurations
            "endpoint": "aHR0cHM6Ly81Ynp3bXBmM2t5ZHpjeTJrYno0cnRuNHo3aTBjcnhvaC5sYW1iZGEtdXJsLnVzLXdlc3QtMi5vbi5hd3Mv",
            "provider": "google",
            "mode": "workshop"
        }
    
    def get_endpoint(self):
        """Get the service endpoint"""
        # Try environment first
        for var in ["WORKSHOP_SERVICE_URL", "ML_BACKEND_URL", "SERVERLESS_URL"]:
            value = os.getenv(var)
            if value:
                return value
        
        # Decode obfuscated value
        return base64.b64decode(self._config["endpoint"]).decode()
    
    def get_provider(self):
        """Get the ML provider"""
        return self._config["provider"]
    
    def get_auth_token(self):
        """Get authentication token from service"""
        response = requests.post(
            url=self.get_endpoint(),
            json={"task": "get_api_key", "data": self.get_provider()}
        )
        return response.json()["api_key"]

# Usage
config = WorkshopConfig()
SERVERLESS_URL = config.get_endpoint()
api_key = config.get_auth_token()

print(f"✅ Advanced config loaded: {SERVERLESS_URL[:30]}...")

# =============================================================================
# CELL 6: Production-Ready Obfuscation
# =============================================================================

import json
from pathlib import Path

class SecureConfig:
    """Production-ready configuration with multiple security layers"""
    
    def __init__(self):
        self.config_sources = [
            self._load_from_env,
            self._load_from_file,
            self._load_from_encoded
        ]
    
    def _load_from_env(self):
        """Load from environment variables"""
        env_vars = [
            "WORKSHOP_BACKEND_URL",
            "ML_SERVICE_ENDPOINT", 
            "SERVERLESS_URL",
            "GENAI_PROXY_URL"
        ]
        
        for var in env_vars:
            value = os.getenv(var)
            if value:
                return {"endpoint": value, "source": "environment"}
        return None
    
    def _load_from_file(self):
        """Load from configuration file"""
        config_files = [".workshop_config", "config.json", ".env"]
        
        for filename in config_files:
            path = Path(filename)
            if path.exists():
                try:
                    with open(path) as f:
                        if filename.endswith('.json'):
                            data = json.load(f)
                            if "serverless_url" in data:
                                return {"endpoint": data["serverless_url"], "source": "file"}
                except:
                    continue
        return None
    
    def _load_from_encoded(self):
        """Load from encoded fallback"""
        encoded = "aHR0cHM6Ly81Ynp3bXBmM2t5ZHpjeTJrYno0cnRuNHo3aTBjcnhvaC5sYW1iZGEtdXJsLnVzLXdlc3QtMi5vbi5hd3Mv"
        return {
            "endpoint": base64.b64decode(encoded).decode(),
            "source": "encoded_fallback"
        }
    
    def get_config(self):
        """Get configuration from the first available source"""
        for source in self.config_sources:
            config = source()
            if config:
                return config
        
        raise Exception("No configuration source available")

# Usage
secure_config = SecureConfig()
config = secure_config.get_config()

print(f"✅ Secure config loaded from: {config['source']}")
print(f"   Endpoint: {config['endpoint'][:30]}...")

# =============================================================================
# INSTRUCTIONS FOR IMPLEMENTATION
# =============================================================================

print("""
🔐 IMPLEMENTATION INSTRUCTIONS:

1. BASIC OBFUSCATION:
   - Replace hardcoded URL with ENCODED_ENDPOINT
   - Use get_workshop_endpoint() function
   
2. ENVIRONMENT VARIABLES:
   - Set WORKSHOP_BACKEND_URL instead of SERVERLESS_URL
   - Use non-obvious variable names
   
3. CONFIGURATION FILE:
   - Create .workshop_config with encoded values
   - Use WorkshopConfig class
   
4. ADVANCED SECURITY:
   - Use SecureConfig class for multiple layers
   - Implement fallback mechanisms
   
5. DEVCONTAINER UPDATES:
   - Change environment variable names in devcontainer.json
   - Use obfuscated names like WORKSHOP_BACKEND_URL
""")