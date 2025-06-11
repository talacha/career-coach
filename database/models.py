import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, LargeBinary, Text, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ResumeSubmission(Base):
    __tablename__ = "resume_submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    filename = Column(String)
    pdf_content = Column(LargeBinary)  # Store PDF as BLOB
    extracted_text = Column(Text)
    job_description = Column(Text)
    analysis_result = Column(JSON)
    alignment_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
class InterviewSession(Base):
    __tablename__ = "interview_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    job_role = Column(String)
    focus_areas = Column(JSON)
    interview_type = Column(String)
    total_questions = Column(Integer, default=0)
    average_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

class InterviewQuestion(Base):
    __tablename__ = "interview_questions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    interview_session_id = Column(Integer)
    question_text = Column(Text)
    answer_text = Column(Text)
    feedback = Column(JSON)
    score = Column(Float)
    question_order = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create all tables
def create_tables():
    Base.metadata.create_all(bind=engine)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()