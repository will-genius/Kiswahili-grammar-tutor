# used to verify that your FastAPI retrieval endpoint is successfully pulling the right context from ChromaDB
import requests
import json

# Make sure your FastAPI server is running on port 8000
API_URL = "http://127.0.0.1:8000/api/chat/retrieval"

def test_retrieval(query_text):
    print(f"\n{'='*50}")
    print(f"  Student Query: {query_text}")
    print(f"{'='*50}")
    
    payload = {"message": query_text}
    
    try:
        # Send POST request to your FastAPI endpoint
        response = requests.post(API_URL, json=payload)
        response.raise_for_status() 
        
        result = response.json()
        
        # Print the retrieved context beautifully
        print(" Retrieved Context from ChromaDB:")
        print(json.dumps(result["retrieved_context"], indent=2, ensure_ascii=False))
        
    except requests.exceptions.RequestException as e:
        print(f"Connection Error: Is FastAPI running? {e}")

if __name__ == "__main__":
    #  Testing vocabulary 
    test_retrieval("Ufahamu ni nini hasa?")
    
    #  Testing speech writing concepts 
    test_retrieval("Nataka kuandika hotuba, nianzeje?")
    
    #  Testing literature criticism 
    test_retrieval("Mhakiki wa fasihi anapaswa kuzingatia mambo gani?")