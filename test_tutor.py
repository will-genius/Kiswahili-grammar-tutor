# Tests the overal system to see if the data is being fetched as expected
import requests
import json

# Ensure your FastAPI server is running on port 8000
API_URL = "http://127.0.0.1:8000/api/chat/message"

def test_tutor(message: str):
    print(f"\n{'='*60}")
    print(f" Student Message: {message}")
    print(f"{'='*60}")
    
    payload = {"message": message}
    
    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()
        
        result = response.json()
        
        print("\n AI Tutor Response:")
        print(result.get("tutor_response"))
        
        print("\n Grounding Source (ChromaDB Chunks Used):")
        for i, doc in enumerate(result.get("retrieved_context_used", [])):
            print(f"  [{i+1}] File: {doc['metadata'].get('source_file')} | Topic: {doc['metadata'].get('topic_title')}")
            
    except requests.exceptions.RequestException as e:
        print(f" Connection Error: Is FastAPI running with your GEMINI_API_KEY set? Details: {e}")

if __name__ == "__main__":
    #  Swahili Query (Comprehension/Ufahamu)
    test_tutor("Ufahamu ni nini hasa na nifanye nini ili niufahamu vizuri?")
    
    #  English Query (Speech Writing/Hotuba)
    test_tutor("How do I structure a speech and what should I include in the introduction?")