import os
import logging
from dotenv import load_dotenv
from google import genai
from app.rag_service import query_knowledge_base
import time

# Load environment variables from the .env file
load_dotenv()

logger = logging.getLogger(__name__)

class TutorService:
    def __init__(self, llm_client=None):
        # Fetch the API key from environment variables (.env)
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.warning(" GEMINI_API_KEY not found in environment variables or .env file.")
            
        # Initialize the Gemini client safely with the loaded key
        self.client = genai.Client(api_key=api_key) if api_key else None
        
        # Using Gemini Flash for fast, lightweight, and free-tier friendly responses
        self.model_name = "gemini-3.8-flash"

    def generate_response(self, student_message: str, preferred_language: str = "auto") -> dict:
        """
        Orchestrates bilingual RAG retrieval and prompt construction for the student.
        """
        if not self.client:
            return {
                "status": "error",
                "student_message": student_message,
                "tutor_response": "Samahani, ufunguo wa Gemini API (API key) haupatikani kwenye mfumo. Tafadhali hakikisha umeiweka kwenye faili la .env.",
                "prompt_sent_to_llm": ""
            }

        # 1. Retrieve the top 2 precise micro-chunks 
        retrieved_docs = query_knowledge_base(student_message, k=2)
        
        # Extract and concatenate the text content from the retrieved chunks
        context_text = "\n\n".join([doc["content"] for doc in retrieved_docs])
        
        # 2. Construct the bilingual pedagogical system prompt
        system_prompt = f"""You are an encouraging and supportive bilingual educational tutor (English and Kiswahili) for students using low-spec edge devices. 
Your task is to answer the student's question or explain the concept using ONLY the provided curriculum context below. 

Language Rule: Detect the language of the student's message (or use their preference) and reply in that exact same language (English or Kiswahili). Keep the response encouraging, concise, and clear.

Curriculum Context (Retrieved Knowledge):
{context_text}

Student Message: {student_message}
"""

        # 3. Generate response via Gemini API
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=system_prompt,
            )
            tutor_reply = response.text
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            tutor_reply = f"Samahani, kumesitawi tatizo la kiufundi: {str(e)}"
            
        return {
            "status": "success",
            "student_message": student_message,
            "tutor_response": tutor_reply,
            "prompt_sent_to_llm": system_prompt
        }
    def generate_response_stream(self, student_message: str, preferred_language: str = "auto"):
        """
        Streams the Gemini response token-by-token for lightning-fast UI rendering.
        """
        if not self.client:
            yield "Samahani, ufunguo wa Gemini API haupatikani kwenye faili la .env."
            return

        # Retrieve the top 2 precise micro-chunks 
        retrieved_docs = query_knowledge_base(student_message, k=2)
        context_text = "\n\n".join([doc["content"] for doc in retrieved_docs])
        
        #  Construct the bilingual pedagogical system prompt
        system_prompt = f"""You are an encouraging and supportive bilingual educational tutor (English and Kiswahili) for students using low-spec edge devices. 
Your task is to answer the student's question or explain the concept using ONLY the provided curriculum context below. 

Language Rule: Detect the language of the student's message (or use their preference) and reply in that exact same language (English or Kiswahili). Keep the response encouraging, concise, and clear.

Curriculum Context (Retrieved Knowledge):
{context_text}

Student Message: {student_message}
"""

        #  Stream response chunks via Gemini API
        try:
            response_stream = self.client.models.generate_content_stream(
                model=self.model_name,
                contents=system_prompt,
            )
            for chunk in response_stream:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            logger.error(f"Gemini streaming failed: {e}")
            yield f"Samahani, kumesitawi tatizo la kiufundi: {str(e)}"