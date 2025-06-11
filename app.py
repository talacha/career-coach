import streamlit as st
import os
import uuid
from services.resume_analyzer import ResumeAnalyzer
from services.interview_coach import InterviewCoach
from utils.pdf_parser import PDFParser
from database.service import db_service

# Page configuration - must be first
st.set_page_config(
    page_title="AI Career Coach",
    page_icon="🎯",
    layout="wide"
)

# Custom CSS for color scheme
st.markdown("""
<style>
    /* Main color variables */
    :root {
        --primary-dark: #173B3F;
        --secondary-dark: #0F292C;
        --light-green: #B0D6CE;
        --white: #FFFFFF;
        --pale-green: #D8EFC8;
        --success-green: #2BAE66;
        --error-red: #E01E5A;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, var(--primary-dark) 0%, var(--secondary-dark) 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: var(--white);
        text-align: center;
    }
    
    /* Score metrics */
    .stMetric {
        background-color: var(--pale-green);
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid var(--success-green);
    }
    
    /* Success messages */
    .stSuccess {
        background-color: var(--pale-green);
        border: 1px solid var(--success-green);
        color: var(--primary-dark);
    }
    
    /* Warning messages */
    .stWarning {
        background-color: #FFF3CD;
        border: 1px solid #FFC107;
        color: var(--primary-dark);
    }
    
    /* Error messages */
    .stError {
        background-color: #F8D7DA;
        border: 1px solid var(--error-red);
        color: var(--primary-dark);
    }
    
    /* Info messages */
    .stInfo {
        background-color: var(--light-green);
        border: 1px solid var(--primary-dark);
        color: var(--primary-dark);
    }
    
    /* Chat messages */
    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        border-left: 4px solid var(--success-green);
    }
    
    .interviewer-message {
        background-color: var(--light-green);
        color: var(--primary-dark);
    }
    
    .candidate-message {
        background-color: var(--pale-green);
        color: var(--primary-dark);
    }
    
    .feedback-message {
        background-color: var(--white);
        border-left-color: var(--success-green);
        color: var(--primary-dark);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: var(--pale-green);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, var(--success-green) 0%, var(--primary-dark) 100%);
        color: var(--white);
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, var(--primary-dark) 0%, var(--secondary-dark) 100%);
        color: var(--white);
    }
    
    /* Section headers */
    .section-header {
        background: linear-gradient(90deg, var(--light-green) 0%, var(--pale-green) 100%);
        padding: 1rem;
        border-radius: 8px;
        color: var(--primary-dark);
        font-weight: bold;
        margin: 1rem 0;
    }
    
    /* File uploader */
    .stFileUploader > div {
        background-color: var(--pale-green);
        border: 2px dashed var(--success-green);
        border-radius: 8px;
    }
    
    /* Text areas */
    .stTextArea > div > div > textarea {
        background-color: var(--white);
        border: 2px solid var(--light-green);
        border-radius: 8px;
        color: var(--primary-dark);
    }
    
    /* Text inputs */
    .stTextInput > div > div > input {
        background-color: var(--white);
        border: 2px solid var(--light-green);
        border-radius: 8px;
        color: var(--primary-dark);
    }
    
    /* Multiselect */
    .stMultiSelect > div > div {
        background-color: var(--white);
        border: 2px solid var(--light-green);
        border-radius: 8px;
    }
    
    /* Radio buttons */
    .stRadio > div {
        background-color: var(--pale-green);
        padding: 1rem;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False
if "interview_active" not in st.session_state:
    st.session_state.interview_active = False
if "current_question" not in st.session_state:
    st.session_state.current_question = None
if "user_session_id" not in st.session_state:
    st.session_state.user_session_id = str(uuid.uuid4())
if "interview_session_id" not in st.session_state:
    st.session_state.interview_session_id = None
if "question_count" not in st.session_state:
    st.session_state.question_count = 0



# Main title with custom styling
st.markdown("""
<div class="main-header">
    <h1>🎯 AI Career Coach</h1>
    <p>Your personal AI-powered career coaching platform</p>
</div>
""", unsafe_allow_html=True)

# Sidebar for navigation
st.sidebar.title("Navigation")
mode = st.sidebar.radio("Choose Mode:", ["Resume Analysis", "Interview Practice", "Dashboard"])

# Show session statistics in sidebar
try:
    stats = db_service.get_session_statistics(st.session_state.user_session_id)
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Your Session Stats")
    st.sidebar.metric("Resume Submissions", stats["resume_submissions"])
    st.sidebar.metric("Interview Sessions", stats["interview_sessions"])
    st.sidebar.metric("Total Questions", stats["total_questions"])
    if stats["average_score"] > 0:
        st.sidebar.metric("Average Score", f"{stats['average_score']}/10")
except Exception as e:
    st.sidebar.warning("Could not load session statistics")

# Initialize services
@st.cache_resource
def initialize_services():
    return ResumeAnalyzer(), InterviewCoach(), PDFParser()

resume_analyzer, interview_coach, pdf_parser = initialize_services()

if mode == "Resume Analysis":
    st.header("📄 Resume Analysis & Optimization")
    
    # Two columns for inputs
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Upload Resume")
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
        
    with col2:
        st.subheader("Job Description")
        job_description = st.text_area(
            "Paste the job description here:",
            height=200,
            placeholder="Paste the full job description you're applying for..."
        )
    
    # Analysis button
    if st.button("🔍 Analyze Resume", type="primary"):
        if uploaded_file is not None and job_description.strip():
            with st.spinner("Analyzing your resume..."):
                try:
                    # Extract text from PDF
                    resume_text = pdf_parser.extract_text_from_pdf(uploaded_file)
                    
                    if resume_text.strip():
                        # Perform analysis
                        analysis_result = resume_analyzer.analyze_resume(resume_text, job_description)
                        
                        # Store submission in database
                        try:
                            # Get PDF content as bytes
                            uploaded_file.seek(0)  # Reset file pointer
                            pdf_bytes = uploaded_file.read()
                            
                            # Save to database
                            submission_id = db_service.save_resume_submission(
                                session_id=st.session_state.user_session_id,
                                filename=uploaded_file.name,
                                pdf_content=pdf_bytes,
                                extracted_text=resume_text,
                                job_description=job_description,
                                analysis_result=analysis_result
                            )
                            st.info(f"Resume submission saved (ID: {submission_id})")
                        except Exception as db_error:
                            st.warning(f"Analysis completed but failed to save to database: {str(db_error)}")
                        
                        # Display results
                        st.success("Analysis Complete!")
                        
                        # Alignment Score
                        st.subheader("📊 Alignment Score")
                        score = analysis_result.get("alignment_score", 0)
                        st.metric("Overall Alignment", f"{score}/10")
                        
                        # Create score color based on value
                        if score >= 8:
                            score_color = "#2BAE66"
                            score_emoji = "🟢"
                        elif score >= 6:
                            score_color = "#FFC107"
                            score_emoji = "🟡"
                        else:
                            score_color = "#E01E5A"
                            score_emoji = "🔴"
                        
                        st.markdown(f"""
                        <div style="background-color: {score_color}15; padding: 1rem; border-radius: 8px; border-left: 4px solid {score_color}; margin: 1rem 0;">
                            <strong style="color: {score_color};">{score_emoji} Score Interpretation:</strong> {analysis_result.get('score_interpretation', 'N/A')}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Gaps and Improvements
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.subheader("⚠️ Identified Gaps")
                            gaps = analysis_result.get("gaps", [])
                            if gaps:
                                for gap in gaps:
                                    st.markdown(f"• {gap}")
                            else:
                                st.info("No major gaps identified!")
                        
                        with col2:
                            st.subheader("💡 Improvement Suggestions")
                            suggestions = analysis_result.get("suggestions", [])
                            if suggestions:
                                for suggestion in suggestions:
                                    st.markdown(f"• {suggestion}")
                            else:
                                st.info("Your resume looks great!")
                        
                        # Keywords Analysis
                        st.subheader("🔑 Keyword Analysis")
                        keywords_analysis = analysis_result.get("keywords_analysis", {})
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("**Missing Keywords:**")
                            missing_keywords = keywords_analysis.get("missing_keywords", [])
                            if missing_keywords:
                                for keyword in missing_keywords:
                                    st.markdown(f"• {keyword}")
                            else:
                                st.info("No missing keywords identified!")
                        
                        with col2:
                            st.markdown("**Present Keywords:**")
                            present_keywords = keywords_analysis.get("present_keywords", [])
                            if present_keywords:
                                for keyword in present_keywords:
                                    st.markdown(f"✅ {keyword}")
                            else:
                                st.info("Keyword analysis not available")
                        
                        st.session_state.analysis_done = True
                        
                    else:
                        st.error("Could not extract text from the PDF. Please ensure the file is readable.")
                        
                except Exception as e:
                    st.error(f"Error during analysis: {str(e)}")
        else:
            st.warning("Please upload a resume PDF and provide a job description.")

elif mode == "Interview Practice":
    st.header("🎤 Interactive Interview Practice")
    
    if not st.session_state.interview_active:
        st.subheader("Setup Your Interview Practice")
        
        col1, col2 = st.columns(2)
        
        with col1:
            job_role = st.text_input(
                "Job Role:",
                placeholder="e.g., Software Engineer, Data Scientist, Product Manager"
            )
            
        with col2:
            focus_areas = st.multiselect(
                "Focus Areas:",
                ["Behavioral", "Technical", "System Design", "Leadership", "Problem Solving"],
                default=["Behavioral"]
            )
        
        interview_type = st.radio(
            "Interview Type:",
            ["Mixed Questions", "Behavioral Only", "Technical Only"]
        )
        
        if st.button("🚀 Start Interview Practice", type="primary"):
            if job_role.strip() and focus_areas:
                # Create new interview session in database
                try:
                    interview_session_id = db_service.save_interview_session(
                        session_id=st.session_state.user_session_id,
                        job_role=job_role,
                        focus_areas=focus_areas,
                        interview_type=interview_type
                    )
                    st.session_state.interview_session_id = interview_session_id
                    st.info(f"Interview session started (ID: {interview_session_id})")
                except Exception as db_error:
                    st.warning(f"Failed to save interview session: {str(db_error)}")
                
                st.session_state.interview_active = True
                st.session_state.job_role = job_role
                st.session_state.focus_areas = focus_areas
                st.session_state.interview_type = interview_type
                st.session_state.chat_history = []
                st.session_state.current_question = None
                st.session_state.question_count = 0
                st.rerun()
            else:
                st.warning("Please provide a job role and select at least one focus area.")
    
    else:
        # Active interview session
        st.subheader(f"Interview Practice: {st.session_state.job_role}")
        st.markdown(f"**Focus Areas:** {', '.join(st.session_state.focus_areas)}")
        
        # Display chat history with custom styling
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.chat_history:
                if message["role"] == "interviewer":
                    st.markdown(f"""
                    <div class="chat-message interviewer-message">
                        <strong>🤖 Interviewer:</strong> {message['content']}
                    </div>
                    """, unsafe_allow_html=True)
                elif message["role"] == "candidate":
                    st.markdown(f"""
                    <div class="chat-message candidate-message">
                        <strong>👤 You:</strong> {message['content']}
                    </div>
                    """, unsafe_allow_html=True)
                elif message["role"] == "feedback":
                    score_color = "#2BAE66" if message.get("score", 0) >= 7 else "#FFC107" if message.get("score", 0) >= 5 else "#E01E5A"
                    st.markdown(f"""
                    <div class="chat-message feedback-message" style="border-left-color: {score_color};">
                        <strong>📊 Feedback:</strong> {message['content']}
                    </div>
                    """, unsafe_allow_html=True)
                    if "score" in message:
                        st.metric("Answer Score", f"{message['score']}/10")
        
        # Generate new question if none exists
        if st.session_state.current_question is None:
            with st.spinner("Generating interview question..."):
                try:
                    question = interview_coach.generate_question(
                        st.session_state.job_role,
                        st.session_state.focus_areas,
                        st.session_state.interview_type
                    )
                    st.session_state.current_question = question
                    st.session_state.chat_history.append({
                        "role": "interviewer",
                        "content": question
                    })
                    st.rerun()
                except Exception as e:
                    st.error(f"Error generating question: {str(e)}")
        
        # Answer input
        st.subheader("Your Answer")
        answer = st.text_area(
            "Type your answer here:",
            height=150,
            key="answer_input"
        )
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("Submit Answer", type="primary"):
                if answer.strip():
                    # Add answer to chat history
                    st.session_state.chat_history.append({
                        "role": "candidate",
                        "content": answer
                    })
                    
                    # Get feedback
                    with st.spinner("Analyzing your answer..."):
                        try:
                            feedback = interview_coach.evaluate_answer(
                                st.session_state.current_question,
                                answer,
                                st.session_state.job_role,
                                st.session_state.focus_areas
                            )
                            
                            # Add feedback to chat history
                            st.session_state.chat_history.append({
                                "role": "feedback",
                                "content": feedback.get("feedback", "Feedback not available"),
                                "score": feedback.get("score", 0)
                            })
                            
                            # Store question and answer in database
                            try:
                                st.session_state.question_count += 1
                                question_id = db_service.save_interview_question(
                                    session_id=st.session_state.user_session_id,
                                    interview_session_id=st.session_state.interview_session_id,
                                    question_text=st.session_state.current_question,
                                    answer_text=answer,
                                    feedback=feedback,
                                    score=feedback.get("score", 0),
                                    question_order=st.session_state.question_count
                                )
                            except Exception as db_error:
                                st.warning(f"Failed to save question to database: {str(db_error)}")
                            
                            # Reset for next question
                            st.session_state.current_question = None
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"Error evaluating answer: {str(e)}")
                else:
                    st.warning("Please provide an answer before submitting.")
        
        with col2:
            if st.button("Next Question"):
                st.session_state.current_question = None
                st.rerun()
        
        with col3:
            if st.button("End Interview", type="secondary"):
                # Update interview session completion in database
                try:
                    # Calculate average score from chat history
                    scores = [msg.get("score", 0) for msg in st.session_state.chat_history if msg.get("role") == "feedback" and msg.get("score")]
                    avg_score = sum(scores) / len(scores) if scores else 0
                    
                    db_service.update_interview_session_completion(
                        session_id=st.session_state.user_session_id,
                        total_questions=st.session_state.question_count,
                        average_score=avg_score
                    )
                    st.info(f"Interview completed! Questions: {st.session_state.question_count}, Average Score: {avg_score:.1f}/10")
                except Exception as db_error:
                    st.warning(f"Failed to update interview completion: {str(db_error)}")
                
                st.session_state.interview_active = False
                st.session_state.current_question = None
                st.session_state.interview_session_id = None
                st.success("Interview session ended. You can start a new session anytime!")
                st.rerun()

# Footer
st.markdown("---")
st.markdown("💡 **Tip:** Use this tool regularly to improve your job application success rate!")
