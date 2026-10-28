from fastapi import FastAPI, HTTPException, Request,UploadFile, File
from contextlib import asynccontextmanager
from app.config import settings
from app.database import init_db
import app.models
from app.session import router as session_router
import os
from pydantic import BaseModel
import shutil
from app.evaluation_service import ExerciseEvaluator
from app.rag_service import query_knowledge_base 
from app.tutor_service import TutorService
from dotenv import load_dotenv
load_dotenv()

class EvaluationRequest(BaseModel):
    exercise_id: str
    student_answer: str
class ChatRequest(BaseModel):
    message: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- WARM-UP ON BOOT ---
    print(" Warming up embedding model and ChromaDB in the background...")
    try:
        # Run a dummy query to force model weights into RAM before any student connects
        query_knowledge_base("Warm up query", k=1)
        print("Knowledge base and embeddings successfully warmed up and cached!")
    except Exception as e:
        print(f" Warm-up warning: {e}")
        
    yield
    
    # Free up memory when the server shuts down
    app.state.evaluator = None

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

app.include_router(session_router, prefix="/session", tags=["Session"])

@app.get("/health")
async def health_check():
    return {"status": "online", "mode": "offline-edge-ready"}

tutor_service = TutorService()

class ChatMessageRequest(BaseModel):
    message: str

@app.post("/api/chat/message")
async def handle_student_chat(payload: ChatMessageRequest):
    """
    Main conversational tutor endpoint. Takes student text, 
    retrieves curriculum context, and prepares the scaffolded response.
    """
    try:
        result = tutor_service.generate_response(payload.message)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

tutor = TutorService()
@app.post("/api/chat/voice")
async def chat_with_voice(file: UploadFile = File(...)):
    """
    Receives voice recording bytes, transcribes via Groq Whisper, 
    queries the RAG tutor, and returns both text and transcription.
    """
    temp_audio_path = f"temp_{file.filename or 'input.wav'}"
    
    try:
        # Save uploaded audio stream temporarily
        with open(temp_audio_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Transcribe audio to text using Groq Whisper
        transcribed_text = tutor.transcribe_audio(temp_audio_path)
        
        if not transcribed_text or "Error" in transcribed_text:
            return {"status": "error", "message": "Failed to transcribe audio."}
            
        # Pass transcribed text into your RAG tutor logic
        response_data = tutor.generate_response(transcribed_text)
        
        return {
            "status": "success",
            "transcribed_query": transcribed_text,
            "tutor_response": response_data["tutor_response"],
            "retrieved_context_used": response_data.get("retrieved_context_used", [])
        }
        
    finally:
        # Clean up temporary audio file
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)

#  Add the evaluation endpoint
@app.post("/api/evaluate")
async def evaluate_student_answer(request: Request, payload: EvaluationRequest):
    # Retrieve the pre-loaded evaluator from the app state
    evaluator = request.app.state.evaluator
    
    if not evaluator:
        raise HTTPException(status_code=500, detail="Evaluator service is offline.")
        
    result = evaluator.evaluate_answer(payload.exercise_id, payload.student_answer)
    
    if result.get("status") == "error":
        raise HTTPException(status_code=404, detail=result.get("message"))
        
    return result

@app.post("/api/chat/retrieval")
async def retrieve_context(payload: ChatRequest):
    context = query_knowledge_base(payload.message, k=2)
    
    return {
        "query": payload.message, 
        "retrieved_context": context
    }


# run using uvicorn app.main:app --reload --port 8000