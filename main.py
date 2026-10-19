from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional

# Import the mock clients we built in the previous step
from mock_mcp_clients import MockAINLPCoreClient, MockPedagogicalEngineClient

app = FastAPI(title="Kiswahili Grammar Tutor CBot")

# Initialize the shared service clients
ai_core = MockAINLPCoreClient()
pedagogical_engine = MockPedagogicalEngineClient()

# ==========================================
# STEP 1: Define API Contract Schemas
# ==========================================
class LearnerSessionInput(BaseModel):
    learner_id: str
    text: Optional[str] = None
    audio: Optional[str] = None
    lang: str  # "sw" or "en"

class TutorResponse(BaseModel):
    reply_text: str
    reply_audio: Optional[str] = None
    error_flags: List[str]
    scaffold_type: str

# ==========================================
# STEP 2: The Core Orchestration Endpoint
# ==========================================
@app.post("/session/message", response_model=TutorResponse)
async def process_learner_message(payload: LearnerSessionInput):
    input_text = payload.text or ""
    
    # 1. AI Analysis: Detect morphological and grammar errors
    ai_output = ai_core.analyze_text(input_text)
    
    # 2. Pedagogical Engine: Determine how to scaffold the response
    # (Hardcoding current_level=1 for now until DB state is wired by Developer 1)
    scaffold_output = pedagogical_engine.scaffold(
        learner_id=payload.learner_id, 
        ai_output=ai_output, 
        current_level=1
    )
    
    # 3. Response Assembly: Format output based on correct/error path and language
    error_flags = [error.rule_id for error in ai_output.errors]
    
    if ai_output.is_correct or not ai_output.errors:
        reply_text = "Vizuri sana! Umepata." if payload.lang == "sw" else "Very good! You got it right."
    else:
        primary_error = ai_output.errors[0]
        # Dynamically switch explanation language based on the UI toggle
        explanation = primary_error.explanation_sw if payload.lang == "sw" else primary_error.explanation_en
        
        # Apply the deterministic scaffold strategy
        if scaffold_output.scaffold_type == "hint_only":
            reply_text = f"Kuna kosa dogo kwenye neno '{primary_error.span}'. Fikiria tena." if payload.lang == "sw" else f"There is a small mistake at '{primary_error.span}'. Think again."
        elif scaffold_output.scaffold_type == "explain_rule":
            reply_text = f"{explanation} Kosa lako: '{primary_error.span}'. Sahihisho: '{primary_error.correction}'."
        else:
            reply_text = f"Sahihisho ni (The correction is): '{primary_error.correction}'."
            
    # 4. Return to Interaction Layer (via Companion router)
    return TutorResponse(
        reply_text=reply_text,
        reply_audio=None,  # Placeholder for Week 3 TTS integration
        error_flags=error_flags,
        scaffold_type=scaffold_output.scaffold_type
    )

# To run this server locally:
# uvicorn main:app --reload --port 8000