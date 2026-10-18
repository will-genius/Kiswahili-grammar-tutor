from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas import LearnerSessionInput, TutorResponse, GrammarErrorDetail
import uuid

router = APIRouter()

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

    # Temporary mock response while Developer 2 wires the AI Core
    mock_session_id = str(uuid.uuid4())
    mock_errors = [
        GrammarErrorDetail(
            span="watoto anakula",
            rule_id="RULE_NOUN_CLASS_A_WA_01",
            correction="watoto wanakula",
            explanation_sw="Nomino za ngeli ya A-WA huchukua kiambishi cha nafsi 'wa-' kwenye kitendo.",
            explanation_en="Class 1/2 nouns require the subject prefix 'wa-' for plurals."
        )
    ]

    return TutorResponse(
        session_id=mock_session_id,
        reply_text="Jaribu tena! Angalia patano la kisarufi la neno 'watoto'.",
        reply_audio=None,
        error_flags=mock_errors,
        scaffold_type="hint",
        synced=False
    )