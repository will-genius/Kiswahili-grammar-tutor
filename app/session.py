from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas import LearnerSessionInput, TutorResponse, GrammarErrorDetail
import uuid
from app.models import SessionLog
from app.mock_mcp_clients import MockAINLPCoreClient, MockPedagogicalEngineClient
from app.rag_service import fetch_validated_rule
from app.voice_service import VoiceService

router = APIRouter()

# Initialize the AI and Pedagogical MCP clients
ai_core = MockAINLPCoreClient()
pedagogical_engine = MockPedagogicalEngineClient()
voice_service = VoiceService()

@router.post("/message", response_model=TutorResponse)
async def handle_session_message(
    payload: LearnerSessionInput,
    db: AsyncSession = Depends(get_db)
):
    """
    POST /session/message
    Handles incoming learner messages via the THiNK Learning Companion wrapper.
    """
    if not payload.text and not payload.audio:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payload must contain either text or audio."
        )
    # Process Audio Input (STT)
    if payload.audio:
        # Pass the learner's UI language toggle to the voice service
        input_text = voice_service.transcribe_audio(payload.audio, payload.lang)
    else:
        input_text = payload.text
    

    #  AI Analysis & Orchestration 
    ai_output = ai_core.analyze_text(input_text)
    
    scaffold_output = pedagogical_engine.scaffold(
        learner_id=payload.learner_id, 
        ai_output=ai_output, 
        current_level=1
    )
    
    error_flags = [error.rule_id for error in ai_output.errors]
    
    if ai_output.is_correct or not ai_output.errors:
        reply_text = "Vizuri sana! Umepata." if payload.lang == "sw" else "Very good! You got it right."
    else:
        primary_error = ai_output.errors[0]
        
        # Execute the RAG lookup using the AI's flagged rule_id
        validated_rule = fetch_validated_rule(primary_error.rule_id)
        
        #  Enforce the Guardrail
        if not validated_rule:
            # Fallback if the AI hallucinated a rule_id not in our curriculum
            reply_text = "Samahani, siwezi kuthibitisha kosa hili kwa sasa." if payload.lang == "sw" else "Sorry, I cannot validate this error right now."
            scaffold_output.scaffold_type = "guardrail_blocked"
        else:
            # Safely pull the curriculum-mapped bilingual explanations from the KB
            explanation = validated_rule["explanation_sw"] if payload.lang == "sw" else validated_rule["explanation_en"]
            
            # Apply the deterministic scaffold strategy using validated data
            if scaffold_output.scaffold_type == "hint_only":
                reply_text = f"Kuna kosa dogo kwenye neno '{primary_error.span}'. Fikiria tena." if payload.lang == "sw" else f"There is a small mistake at '{primary_error.span}'. Think again."
            elif scaffold_output.scaffold_type == "explain_rule":
                reply_text = f"{explanation} Kosa lako: '{primary_error.span}'. Sahihisho: '{primary_error.correction}'."
            else:
                reply_text = f"Sahihisho ni (The correction is): '{primary_error.correction}'."

    #  Process Audio Output 
    reply_audio = None
    if payload.audio:
        # If the learner spoke, the tutor speaks back
        reply_audio = voice_service.synthesize_speech(reply_text, payload.lang)

    # State Management & Offline Logging 
    new_log = SessionLog(
        learner_id=payload.learner_id,
        input_text=input_text,
        reply_text=reply_text,
        error_flags=error_flags,
        scaffold_type=scaffold_output.scaffold_type,
        synced=False  # Offline edge sync status flag
    )
    
    db.add(new_log)
    await db.commit()
    await db.refresh(new_log)


    return TutorResponse(
        session_id=new_log.session_id,
        reply_text=reply_text,
        reply_audio=reply_audio,
        error_flags=error_flags,
        scaffold_type=scaffold_output.scaffold_type,
        synced=new_log.synced
    )