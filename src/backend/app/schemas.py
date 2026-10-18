from pydantic import BaseModel, Field
from typing import Optional, List

class LearnerSessionInput(BaseModel):
    learner_id: str = Field(..., description="Unique learner UUID")
    text: Optional[str] = Field(None, description="Learner input text in Swahili/English")
    audio: Optional[str] = Field(None, description="Base64 encoded audio or reference")
    lang: str = Field("sw", description="Active session language toggle ('sw' or 'en')")

class GrammarErrorDetail(BaseModel):
    span: str
    rule_id: str
    correction: str
    explanation_sw: str
    explanation_en: str

class TutorResponse(BaseModel):
    session_id: str
    reply_text: str
    reply_audio: Optional[str] = None
    error_flags: List[GrammarErrorDetail] = []
    scaffold_type: str = "hint"
    synced: bool = False