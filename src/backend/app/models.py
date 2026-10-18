import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, JSON, ForeignKey
from app.database import Base

class LearnerProfile(Base):
    __tablename__ = "learner_profiles"

    learner_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=True)
    grade_level = Column(String, default="Junior Secondary")
    competency_level = Column(String, default="beginner")
    created_at = Column(DateTime, default=datetime.utcnow)

class SessionLog(Base):
    __tablename__ = "session_logs"

    session_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    learner_id = Column(String, ForeignKey("learner_profiles.learner_id"), nullable=False)
    input_text = Column(String, nullable=True)
    reply_text = Column(String, nullable=False)
    error_flags = Column(JSON, default=list)
    scaffold_type = Column(String, default="hint")
    synced = Column(Boolean, default=False)  # Offline edge sync status flag
    timestamp = Column(DateTime, default=datetime.utcnow)