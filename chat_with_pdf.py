#!/usr/bin/env python3
"""
CLI Chat Interface for Multimodal PDF Agent
===========================================

Interactive command-line interface to chat with the ingested PDF using
Gemini 2.0 Flash with function calling and vector search capabilities.

Prerequisites:
- PDF must already be processed and ingested into MongoDB
- Environment variables must be set (MONGODB_URI, SERVERLESS_URL or GOOGLE_API_KEY)
- Vector search index must be ready

Usage:
    python chat_with_pdf.py
    python chat_with_pdf.py --memory  # Enable session memory
    python chat_with_pdf.py --react   # Enable ReAct agent
"""

import os
import sys
import uuid
from pathlib import Path
from datetime import datetime
from typing import List, Optional

from pymongo import MongoClient
from PIL import Image
import numpy as np
import requests

# Load environment variables from .env if available
env_path = Path('.') / '.env'
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            if '=' in line and not line.strip().startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value.strip('"\'')

# Configuration
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://admin:mongodb@localhost:27017/")
SERVERLESS_URL = os.getenv("SERVERLESS_URL")
DB_NAME = "mongodb_aiewf"
COLLECTION_NAME = "multimodal_workshop_voyageai"
HISTORY_COLLECTION = "history_chat"
VS_INDEX_NAME = "vector_index_voyageai"

# Color output for better UX
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header():
    """Print colorful header"""
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.CYAN}{Colors.BOLD}🤖 MULTIMODAL PDF CHAT AGENT{Colors.ENDC}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BLUE}💬 Chat with your PDF using AI-powered search{Colors.ENDC}")
    print(f"{Colors.BLUE}🔍 Powered by MongoDB Vector Search + Gemini 2.0 Flash{Colors.ENDC}")
    print(f"{Colors.YELLOW}💡 Type 'help' for commands, 'quit' to exit{Colors.ENDC}\n")

def show_success(msg): 
    print(f"{Colors.GREEN}✅ {msg}{Colors.ENDC}")

def show_error(msg): 
    print(f"{Colors.RED}❌ {msg}{Colors.ENDC}")

def show_info(msg): 
    print(f"{Colors.BLUE}ℹ️ {msg}{Colors.ENDC}")

def show_warning(msg): 
    print(f"{Colors.YELLOW}⚠️ {msg}{Colors.ENDC}")

def show_agent(msg):
    print(f"{Colors.MAGENTA}🤖 {msg}{Colors.ENDC}")

def show_user(msg):
    print(f"{Colors.CYAN}👤 {msg}{Colors.ENDC}")

# Global variables for configuration
USE_MEMORY = False
USE_REACT = False
SESSION_ID = None
mongodb_client = None
collection = None
history_collection = None
gemini_client = None

def initialize_connections():
    """Initialize MongoDB and Gemini connections"""
    global mongodb_client, collection, history_collection, gemini_client
    
    try:
        # Connect to MongoDB
        mongodb_client = MongoClient(MONGODB_URI)
        result = mongodb_client.admin.command("ping")
        
        if result.get("ok") != 1:
            show_error("MongoDB connection failed")
            return False
            
        collection = mongodb_client[DB_NAME][COLLECTION_NAME]
        history_collection = mongodb_client[DB_NAME][HISTORY_COLLECTION]
        
        show_success("Connected to MongoDB")
        
        # Check if data exists
        doc_count = collection.count_documents({})
        if doc_count == 0:
            show_error("No documents found in collection!")
            show_info("Please run the extraction pipeline first")
            return False
            
        show_success(f"Found {doc_count} documents in collection")
        
        # Initialize Gemini client
        api_key = None
        
        if SERVERLESS_URL:
            try:
                response = requests.post(
                    url=SERVERLESS_URL, 
                    json={"task": "get_api_key", "data": "google"}
                )
                if response.status_code == 200:
                    api_key = response.json().get("api_key")
            except:
                pass
        
        if not api_key:
            api_key = os.getenv("GOOGLE_API_KEY")
        
        if not api_key:
            show_error("No Gemini API key available!")
            show_info("Set GOOGLE_API_KEY environment variable or configure SERVERLESS_URL")
            return False
        
        # Import and initialize Gemini
        try:
            from google import genai
            from google.genai import types
            
            gemini_client = genai.Client(api_key=api_key)
            show_success("Gemini client initialized")
            
            return True
            
        except ImportError:
            show_error("Google genai library not installed!")
            show_info("Install with: pip install google-genai")
            return False
            
    except Exception as e:
        show_error(f"Initialization failed: {e}")
        return False

def generate_query_embedding(text_query: str) -> Optional[List[float]]:
    """Generate embedding for query text"""
    try:
        if SERVERLESS_URL:
            response = requests.post(
                url=SERVERLESS_URL,
                json={
                    "task": "get_embedding",
                    "data": {"input": text_query, "input_type": "query"},
                },
            )
            if response.status_code == 200:
                embedding = response.json()["embedding"]
                # Normalize the embedding
                norm = np.linalg.norm(embedding)
                if norm > 0:
                    embedding = (np.array(embedding) / norm).tolist()
                return embedding
            else:
                show_error(f"Embedding generation failed: {response.status_code}")
                return None
        else:
            show_warning("No embedding service available")
            return None
            
    except Exception as e:
        show_error(f"Embedding generation error: {e}")
        return None

def vector_search_tool(user_query: str) -> List[str]:
    """
    Retrieve information using vector search to answer a user query.
    
    Args:
        user_query (str): The user's query string.
        
    Returns:
        List[str]: List of image file paths retrieved from vector search.
    """
    try:
        show_info(f"🔍 Searching for: {user_query}")
        
        # Generate query embedding
        query_embedding = generate_query_embedding(user_query)
        
        if not query_embedding:
            show_error("Failed to generate query embedding")
            return []
        
        # Define aggregation pipeline
        pipeline = [
            {
                "$vectorSearch": {
                    "index": VS_INDEX_NAME,
                    "path": "embedding",
                    "queryVector": query_embedding,
                    "numCandidates": 150,
                    "limit": 2,
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "key": 1,
                    "width": 1,
                    "height": 1,
                    "page_number": 1,
                    "score": {"$meta": "vectorSearchScore"},
                }
            },
        ]

        # Execute the aggregation pipeline
        results = list(collection.aggregate(pipeline))
        
        # Extract image keys and scores
        keys = [result["key"] for result in results]
        scores = [result["score"] for result in results]
        
        if keys:
            show_success(f"Found {len(keys)} relevant images")
            for i, (key, score) in enumerate(zip(keys, scores)):
                show_info(f"  {i+1}. Page {Path(key).stem} (score: {score:.4f})")
        else:
            show_warning("No relevant images found")
        
        return keys
        
    except Exception as e:
        show_error(f"Vector search failed: {e}")
        import traceback
        traceback.print_exc()
        return []

def setup_gemini_tools():
    """Setup Gemini function calling tools"""
    from google.genai import types
    
    # Define the function declaration
    get_information_declaration = {
        "name": "get_information_for_question_answering",
        "description": "Retrieve information using vector search to answer a user query. Uses advanced embeddings for enhanced similarity matching.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_query": {
                    "type": "string",
                    "description": "Query string to use for vector search",
                }
            },
            "required": ["user_query"],
        },
    }
    
    tools = types.Tool(function_declarations=[get_information_declaration])
    tools_config = types.GenerateContentConfig(tools=[tools], temperature=0.0)
    
    return tools_config

def store_chat_message(session_id: str, role: str, message_type: str, content: str):
    """Store chat message in MongoDB for memory"""
    if not USE_MEMORY:
        return
        
    try:
        message = {
            "session_id": session_id,
            "role": role,
            "type": message_type,
            "content": content,
            "timestamp": datetime.now(),
        }
        history_collection.insert_one(message)
    except Exception as e:
        show_warning(f"Failed to store message: {e}")

def retrieve_session_history(session_id: str) -> List:
    """Retrieve chat history for session"""
    if not USE_MEMORY:
        return []
        
    try:
        cursor = history_collection.find({"session_id": session_id}).sort("timestamp", 1)
        messages = []
        
        for msg in cursor:
            if msg["type"] == "text":
                messages.append(msg["content"])
            elif msg["type"] == "image":
                try:
                    messages.append(Image.open(msg["content"]))
                except Exception as e:
                    show_warning(f"Could not load image {msg['content']}: {e}")
        
        return messages
    except Exception as e:
        show_warning(f"Failed to retrieve history: {e}")
        return []

def select_tool(messages: List):
    """Use LLM to decide which tool to call"""
    try:
        from google.genai import types
        
        system_prompt = [
            (
                "You're an AI assistant. Based on the given information, decide which tool to use. "
                "If the user is asking to explain an image, don't call any tools unless that would help you better explain the image. "
                "Here is the provided information:\n"
            )
        ]
        
        contents = system_prompt + messages
        tools_config = setup_gemini_tools()
        
        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=contents, 
            config=tools_config
        )
        
        if response.candidates and response.candidates[0].content.parts:
            return response.candidates[0].content.parts[0].function_call
        
        return None
        
    except Exception as e:
        show_error(f"Tool selection failed: {e}")
        return None

def generate_answer(user_query: str, images: List = []) -> str:
    """Generate answer using Gemini with retrieved context"""
    try:
        from google.genai import types
        
        # Retrieve conversation history if using memory
        history = retrieve_session_history(SESSION_ID) if USE_MEMORY else []
        
        # Decide if tools need to be called
        messages_for_tool = history + [user_query] if history else [user_query]
        tool_call = select_tool(messages_for_tool)
        
        # If a tool call is needed
        if (tool_call is not None and 
            tool_call.name == "get_information_for_question_answering"):
            
            show_agent(f"🛠️ Using tool: {tool_call.name}")
            tool_images = vector_search_tool(**tool_call.args)
            images.extend(tool_images)
        
        # Verify images exist and can be opened
        valid_images = []
        for img_path in images:
            try:
                if Path(img_path).exists():
                    img = Image.open(img_path)
                    valid_images.append(img)
            except Exception as e:
                show_warning(f"Failed to open image {img_path}: {e}")
        
        # Prepare system prompt
        system_prompt = (
            "Answer the questions based on the provided context only. "
            "If the context is not sufficient, say I DON'T KNOW. "
            "DO NOT use any other information to answer the question."
        )
        
        # Prepare contents for LLM
        contents = [system_prompt]
        if history:
            contents.extend(history)
        contents.extend([user_query] + valid_images)
        
        # Generate response
        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash",
            contents=contents,
            config=types.GenerateContentConfig(temperature=0.0),
        )
        
        answer = response.text
        
        # Store in memory if enabled
        if USE_MEMORY:
            store_chat_message(SESSION_ID, "user", "text", user_query)
            for img_path in images:
                store_chat_message(SESSION_ID, "user", "image", img_path)
            store_chat_message(SESSION_ID, "agent", "text", answer)
        
        return answer
        
    except Exception as e:
        show_error(f"Answer generation failed: {e}")
        return "I apologize, but I encountered an error while processing your question."

def generate_answer_react(user_query: str, images: List = []) -> str:
    """Generate answer using ReAct (Reasoning + Acting) approach"""
    try:
        from google.genai import types
        
        show_agent("🧠 Starting ReAct reasoning...")
        
        system_prompt = [
            (
                "You are an AI assistant with access to document search capabilities. "
                "Based on the current information, decide if you have enough to answer the user query, or if you need more information. "
                "If you have enough information, respond with 'ANSWER: <your answer>'. "
                "If you need more information, respond with 'TOOL: <question for the tool>'. Keep the question concise. "
                f"User query: {user_query}\n"
                "Current information:\n"
            )
        ]
        
        max_iterations = 3
        current_iteration = 0
        current_information = []
        
        # Add user-provided images
        if images:
            current_information.extend([Image.open(img) for img in images if Path(img).exists()])
        
        while current_iteration < max_iterations:
            current_iteration += 1
            show_agent(f"🔄 ReAct Iteration {current_iteration}")
            
            # Generate reasoning and decision
            response = gemini_client.models.generate_content(
                model="gemini-2.0-flash",
                contents=system_prompt + current_information,
                config=types.GenerateContentConfig(temperature=0.0),
            )
            
            decision = response.text
            show_info(f"💭 Decision: {decision[:100]}...")
            
            # Check for final answer
            if "ANSWER:" in decision:
                final_answer = decision.split("ANSWER:", 1)[1].strip()
                show_success(f"✅ Final answer reached in {current_iteration} iterations")
                return final_answer
            
            # Check for tool usage
            elif "TOOL:" in decision:
                tool_query = decision.split("TOOL:", 1)[1].strip()
                show_agent(f"🛠️ Requesting search: {tool_query}")
                
                tool_images = vector_search_tool(tool_query)
                
                if tool_images:
                    new_images = []
                    for img_path in tool_images:
                        if Path(img_path).exists():
                            try:
                                new_images.append(Image.open(img_path))
                            except:
                                pass
                    current_information.extend(new_images)
                    show_success(f"➕ Added {len(new_images)} images to context")
                else:
                    current_information.append("No relevant information found for this query.")
            else:
                show_warning("Unclear decision from agent")
                current_information.append("Unable to determine next action.")
        
        show_warning(f"⚠️ Reached maximum iterations ({max_iterations})")
        return "I couldn't find a definitive answer after exploring the available information. Please try rephrasing your question."
        
    except Exception as e:
        show_error(f"ReAct agent failed: {e}")
        return "I encountered an error while processing your question with the ReAct approach."

def show_help():
    """Show help information"""
    print(f"\n{Colors.YELLOW}{Colors.BOLD}📚 AVAILABLE COMMANDS:{Colors.ENDC}")
    print(f"  {Colors.CYAN}help{Colors.ENDC}     - Show this help message")
    print(f"  {Colors.CYAN}quit{Colors.ENDC}     - Exit the chat")
    print(f"  {Colors.CYAN}clear{Colors.ENDC}    - Clear conversation history (memory mode)")
    print(f"  {Colors.CYAN}status{Colors.ENDC}   - Show current configuration")
    print(f"\n{Colors.YELLOW}{Colors.BOLD}💡 EXAMPLE QUESTIONS:{Colors.ENDC}")
    print(f"  {Colors.GREEN}What is the Pass@1 accuracy of DeepSeek R1 on AIME 2024?{Colors.ENDC}")
    print(f"  {Colors.GREEN}What are the key contributions of this paper?{Colors.ENDC}")
    print(f"  {Colors.GREEN}How does DeepSeek R1 compare to other models?{Colors.ENDC}")
    print()

def show_status():
    """Show current configuration status"""
    print(f"\n{Colors.YELLOW}{Colors.BOLD}⚙️ CURRENT CONFIGURATION:{Colors.ENDC}")
    print(f"  Session ID: {Colors.CYAN}{SESSION_ID}{Colors.ENDC}")
    print(f"  Memory: {Colors.GREEN if USE_MEMORY else Colors.RED}{'Enabled' if USE_MEMORY else 'Disabled'}{Colors.ENDC}")
    print(f"  ReAct: {Colors.GREEN if USE_REACT else Colors.RED}{'Enabled' if USE_REACT else 'Disabled'}{Colors.ENDC}")
    print(f"  Database: {Colors.CYAN}{DB_NAME}.{COLLECTION_NAME}{Colors.ENDC}")
    
    if USE_MEMORY:
        history_count = len(retrieve_session_history(SESSION_ID))
        print(f"  History: {Colors.CYAN}{history_count} messages{Colors.ENDC}")
    print()

def clear_history():
    """Clear conversation history"""
    if not USE_MEMORY:
        show_warning("Memory is not enabled")
        return
        
    try:
        result = history_collection.delete_many({"session_id": SESSION_ID})
        show_success(f"Cleared {result.deleted_count} messages from history")
    except Exception as e:
        show_error(f"Failed to clear history: {e}")

def main():
    """Main chat loop"""
    global USE_MEMORY, USE_REACT, SESSION_ID
    
    # Parse command line arguments
    if "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__)
        return
    
    USE_MEMORY = "--memory" in sys.argv
    USE_REACT = "--react" in sys.argv
    SESSION_ID = str(uuid.uuid4())[:8]
    
    print_header()
    
    # Show configuration
    if USE_MEMORY:
        show_info("💾 Session memory enabled")
    if USE_REACT:
        show_info("🧠 ReAct agent mode enabled")
    
    # Initialize connections
    if not initialize_connections():
        show_error("Failed to initialize. Exiting.")
        return
    
    show_success("🚀 Chat agent ready! Ask me anything about the PDF.")
    
    # Main chat loop
    while True:
        try:
            # Get user input
            user_input = input(f"\n{Colors.CYAN}{Colors.BOLD}You: {Colors.ENDC}").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.lower() in ['quit', 'exit', 'q']:
                show_info("👋 Goodbye!")
                break
            elif user_input.lower() == 'help':
                show_help()
                continue
            elif user_input.lower() == 'clear':
                clear_history()
                continue
            elif user_input.lower() == 'status':
                show_status()
                continue
            
            # Generate response
            print(f"\n{Colors.MAGENTA}{Colors.BOLD}Agent: {Colors.ENDC}", end="")
            
            if USE_REACT:
                response = generate_answer_react(user_input)
            else:
                response = generate_answer(user_input)
            
            print(f"{response}\n")
            
        except KeyboardInterrupt:
            show_info("\n👋 Goodbye!")
            break
        except Exception as e:
            show_error(f"Chat error: {e}")

if __name__ == "__main__":
    main()