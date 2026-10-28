import os
import logging
from dotenv import load_dotenv
from groq import Groq
from app.rag_service import query_knowledge_base
import time

# Load environment variables from the .env file
load_dotenv()

logger = logging.getLogger(__name__)

class TutorService:
    def __init__(self, llm_client=None):
        # Fetch the API key from environment variables (.env)
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            logger.warning(" GROQ_API_KEY not found in environment variables or .env file.")
      
        self.client = Groq(api_key=api_key) if api_key else None
        self.model_name = "openai/gpt-oss-20b"

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

        # Retrieve the top 2 precise micro-chunks 
        retrieved_docs = query_knowledge_base(student_message, k=2)
        
        # --- STRICT KB GUARDRAIL ---
        if not retrieved_docs or len(retrieved_docs) == 0:
            return {
                "status": "success",
                "student_message": student_message,
                "tutor_response": "Samahani, sikupata taarifa hii kwenye nyaraka za mtaala. Tafadhali uliza swali linalohusu mtaala. / I couldn't find this information in the curriculum documents. Please ask a question related to the curriculum.",
                "prompt_sent_to_llm": "",
                "retrieved_context_used": []
            }
        
        # Extract and concatenate the text content from the retrieved chunks
        context_text = "\n\n".join([doc["content"] for doc in retrieved_docs])
        
        # Construct the bilingual pedagogical system prompt
        system_prompt = f"""You are an encouraging and supportive bilingual educational tutor (English and Kiswahili) for students using low-spec edge devices. 
Your task is to answer the student's question or explain the concept using ONLY the provided curriculum context below. 

Language Rule: Detect the language of the student's message (or use their preference) and reply in that exact same language (English or Kiswahili). Keep the response encouraging, concise, and clear.

Curriculum Context (Retrieved Knowledge):
{context_text}

Student Message: {student_message}
"""

        # Generate response via Groq API
        try:
            chat_completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": system_prompt}],
                temperature=0.3, # Lower temperature for precise curriculum adherence
            )
            tutor_reply = chat_completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Groq API call failed: {e}")
            tutor_reply = f"Samahani, kumesitawi tatizo la kiufundi: {str(e)}"
            
        return {
            "status": "success",
            "student_message": student_message,
            "tutor_response": tutor_reply,
            "prompt_sent_to_llm": system_prompt,
            "retrieved_context_used": retrieved_docs # Included so the UI can render the source cards!
        }

    def generate_response_stream(self, student_message: str, preferred_language: str = "auto"):
        """
        Streams the Groq API response token-by-token for lightning-fast UI rendering.
        """
        if not self.client:
            yield "Samahani, ufunguo wa Groq API haupatikani kwenye faili la .env."
            return

        # Retrieve the top 2 precise micro-chunks 
        retrieved_docs = query_knowledge_base(student_message, k=2)
        
        # --- STRICT KB GUARDRAIL FOR STREAMING ---
        if not retrieved_docs or len(retrieved_docs) == 0:
            yield "Samahani, sikupata taarifa hii kwenye nyaraka za mtaala. / I couldn't find this information in the curriculum documents."
            return

        context_text = "\n\n".join([doc["content"] for doc in retrieved_docs])
        
        # Construct the bilingual pedagogical system prompt
        system_prompt = f"""You are an encouraging and supportive bilingual educational tutor (English and Kiswahili) for students using low-spec edge devices. 
Your task is to answer the student's question or explain the concept using ONLY the provided curriculum context below. 

Language Rule: Detect the language of the student's message (or use their preference) and reply in that exact same language (English or Kiswahili). Keep the response encouraging, concise, and clear.

Curriculum Context (Retrieved Knowledge):
{context_text}

Student Message: {student_message}
"""

        # Stream response chunks via Groq API
        try:
            stream = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": system_prompt}],
                stream=True,
            )
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
        except Exception as e:
            logger.error(f"Groq streaming failed: {e}")
            yield f"Samahani, kumesitawi tatizo la kiufundi: {str(e)}"

    def transcribe_audio(self, audio_file_path: str) -> str:
        """
        Transcribes recorded student audio using Groq's whisper-large-v3-turbo model.
        """
        if not self.client:
            return "Samahani, Groq client haipatikani."
            
        try:
            with open(audio_file_path, "rb") as file:
                transcription = self.client.audio.transcriptions.create(
                    file=(audio_file_path, file.read()),
                    model="whisper-large-v3-turbo",
                    prompt="Huu ni mfumo wa elimu wa Kenya. Maswali yanahusu ufahamu, ufupisho, hotuba,uandishi wa barua,insha,ripoti,fasisihi simulizina fasihi andishi na masomo ya Kiswahili na Kiingereza."
                )
            return transcription.text
        except Exception as e:
            logger.error(f"Whisper transcription failed: {e}")
            return f"Error in transcription: {str(e)}"