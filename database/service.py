import uuid
from sqlalchemy.orm import Session
from database.models import ResumeSubmission, InterviewSession, InterviewQuestion, get_db, create_tables
from typing import Optional, List, Dict, Any
from datetime import datetime

class DatabaseService:
    def __init__(self):
        # Create tables if they don't exist
        create_tables()
    
    def save_resume_submission(self, 
                             session_id: str,
                             filename: str,
                             pdf_content: bytes,
                             extracted_text: str,
                             job_description: str,
                             analysis_result: Dict[str, Any]) -> int:
        """Save resume submission to database"""
        db = next(get_db())
        try:
            submission = ResumeSubmission(
                session_id=session_id,
                filename=filename,
                pdf_content=pdf_content,
                extracted_text=extracted_text,
                job_description=job_description,
                analysis_result=analysis_result,
                alignment_score=analysis_result.get('alignment_score', 0)
            )
            db.add(submission)
            db.commit()
            db.refresh(submission)
            return submission.id
        finally:
            db.close()
    
    def save_interview_session(self,
                             session_id: str,
                             job_role: str,
                             focus_areas: List[str],
                             interview_type: str) -> int:
        """Save interview session to database"""
        db = next(get_db())
        try:
            session = InterviewSession(
                session_id=session_id,
                job_role=job_role,
                focus_areas=focus_areas,
                interview_type=interview_type
            )
            db.add(session)
            db.commit()
            db.refresh(session)
            return session.id
        finally:
            db.close()
    
    def save_interview_question(self,
                              session_id: str,
                              interview_session_id: int,
                              question_text: str,
                              answer_text: str,
                              feedback: Dict[str, Any],
                              score: float,
                              question_order: int) -> int:
        """Save interview question and answer to database"""
        db = next(get_db())
        try:
            question = InterviewQuestion(
                session_id=session_id,
                interview_session_id=interview_session_id,
                question_text=question_text,
                answer_text=answer_text,
                feedback=feedback,
                score=score,
                question_order=question_order
            )
            db.add(question)
            db.commit()
            db.refresh(question)
            return question.id
        finally:
            db.close()
    
    def update_interview_session_completion(self,
                                          session_id: str,
                                          total_questions: int,
                                          average_score: float):
        """Update interview session with completion data"""
        db = next(get_db())
        try:
            session = db.query(InterviewSession).filter(
                InterviewSession.session_id == session_id
            ).first()
            
            if session:
                session.total_questions = total_questions
                session.average_score = average_score
                session.completed_at = datetime.utcnow()
                db.commit()
        finally:
            db.close()
    
    def get_resume_submissions_by_session(self, session_id: str) -> List[ResumeSubmission]:
        """Get all resume submissions for a session"""
        db = next(get_db())
        try:
            return db.query(ResumeSubmission).filter(
                ResumeSubmission.session_id == session_id
            ).all()
        finally:
            db.close()
    
    def get_interview_sessions_by_session(self, session_id: str) -> List[InterviewSession]:
        """Get all interview sessions for a session"""
        db = next(get_db())
        try:
            return db.query(InterviewSession).filter(
                InterviewSession.session_id == session_id
            ).all()
        finally:
            db.close()
    
    def get_interview_questions_by_session(self, session_id: str) -> List[InterviewQuestion]:
        """Get all interview questions for a session"""
        db = next(get_db())
        try:
            return db.query(InterviewQuestion).filter(
                InterviewQuestion.session_id == session_id
            ).order_by(InterviewQuestion.question_order).all()
        finally:
            db.close()
    
    def get_recent_submissions(self, limit: int = 10) -> List[ResumeSubmission]:
        """Get recent resume submissions"""
        db = next(get_db())
        try:
            return db.query(ResumeSubmission).order_by(
                ResumeSubmission.created_at.desc()
            ).limit(limit).all()
        finally:
            db.close()
    
    def get_session_statistics(self, session_id: str) -> Dict[str, Any]:
        """Get statistics for a session"""
        db = next(get_db())
        try:
            resume_count = db.query(ResumeSubmission).filter(
                ResumeSubmission.session_id == session_id
            ).count()
            
            interview_count = db.query(InterviewSession).filter(
                InterviewSession.session_id == session_id
            ).count()
            
            questions_count = db.query(InterviewQuestion).filter(
                InterviewQuestion.session_id == session_id
            ).count()
            
            avg_score = db.query(InterviewQuestion).filter(
                InterviewQuestion.session_id == session_id
            ).with_entities(InterviewQuestion.score).all()
            
            average_score = sum([s[0] for s in avg_score if s[0]]) / len(avg_score) if avg_score else 0
            
            return {
                "resume_submissions": resume_count,
                "interview_sessions": interview_count,
                "total_questions": questions_count,
                "average_score": round(average_score, 2)
            }
        finally:
            db.close()

# Global database service instance
db_service = DatabaseService()