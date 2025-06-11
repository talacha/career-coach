import json
import os
import google.generativeai as genai

class ResumeAnalyzer:
    def __init__(self):
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel('gemini-1.5-pro')
    
    def analyze_resume(self, resume_text, job_description):
        """
        Analyze resume against job description and provide comprehensive feedback
        """
        try:
            prompt = f"""
            You are an expert career coach and resume analyzer. Analyze the provided resume against the job description and provide comprehensive feedback.

            RESUME:
            {resume_text}

            JOB DESCRIPTION:
            {job_description}

            Please analyze and provide feedback in the following JSON format:
            {{
                "alignment_score": <score from 1-10>,
                "score_interpretation": "<brief explanation of the score>",
                "gaps": ["<gap1>", "<gap2>", ...],
                "suggestions": ["<suggestion1>", "<suggestion2>", ...],
                "keywords_analysis": {{
                    "missing_keywords": ["<keyword1>", "<keyword2>", ...],
                    "present_keywords": ["<keyword1>", "<keyword2>", ...]
                }},
                "strengths": ["<strength1>", "<strength2>", ...],
                "improvement_areas": ["<area1>", "<area2>", ...]
            }}

            Analysis Guidelines:
            1. alignment_score: Rate how well the resume matches the job requirements (1-10)
            2. score_interpretation: Explain what the score means
            3. gaps: Identify missing skills, experiences, or qualifications
            4. suggestions: Provide specific, actionable improvement recommendations
            5. keywords_analysis: Identify key terms from job description that are missing/present
            6. strengths: Highlight what the candidate does well
            7. improvement_areas: Areas that need enhancement

            Be specific, constructive, and actionable in your feedback. Focus on ATS optimization and recruiter appeal.
            """

            full_prompt = f"""You are an expert career coach specializing in resume analysis and optimization. Provide detailed, actionable feedback to help candidates improve their job application success rate.

{prompt}

Please ensure your response is valid JSON format."""

            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=2048,
                )
            )

            # Clean and parse JSON response
            response_text = response.text.strip()
            # Remove any markdown code block formatting if present
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            result = json.loads(response_text.strip())
            return result

        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse analysis results: {str(e)}")
        except Exception as e:
            raise Exception(f"Resume analysis failed: {str(e)}")

    def suggest_keywords(self, job_description):
        """
        Extract key terms and skills from job description for ATS optimization
        """
        try:
            prompt = f"""
            Extract the most important keywords, skills, and phrases from this job description that should be included in a resume for ATS optimization:

            JOB DESCRIPTION:
            {job_description}

            Return the results in JSON format:
            {{
                "technical_skills": ["<skill1>", "<skill2>", ...],
                "soft_skills": ["<skill1>", "<skill2>", ...],
                "tools_technologies": ["<tool1>", "<tool2>", ...],
                "certifications": ["<cert1>", "<cert2>", ...],
                "key_phrases": ["<phrase1>", "<phrase2>", ...]
            }}
            """

            full_prompt = f"""You are an ATS optimization expert. Extract the most important keywords and phrases that candidates should include in their resumes.

{prompt}

Please ensure your response is valid JSON format."""

            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.2,
                    max_output_tokens=1024,
                )
            )

            # Clean and parse JSON response
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            result = json.loads(response_text.strip())
            return result

        except Exception as e:
            raise Exception(f"Keyword extraction failed: {str(e)}")

    def generate_improvement_suggestions(self, resume_text, analysis_result):
        """
        Generate specific improvement suggestions based on analysis
        """
        try:
            gaps = analysis_result.get("gaps", [])
            missing_keywords = analysis_result.get("keywords_analysis", {}).get("missing_keywords", [])
            
            prompt = f"""
            Based on the resume analysis, provide specific, actionable suggestions for improvement:

            CURRENT GAPS: {gaps}
            MISSING KEYWORDS: {missing_keywords}

            Provide suggestions in JSON format:
            {{
                "content_improvements": ["<suggestion1>", "<suggestion2>", ...],
                "formatting_suggestions": ["<suggestion1>", "<suggestion2>", ...],
                "keyword_integration": ["<suggestion1>", "<suggestion2>", ...],
                "achievement_enhancements": ["<suggestion1>", "<suggestion2>", ...],
                "priority_actions": ["<action1>", "<action2>", ...]
            }}

            Make suggestions specific, actionable, and prioritized.
            """

            full_prompt = f"""You are a resume writing expert. Provide specific, actionable suggestions for resume improvement.

{prompt}

Please ensure your response is valid JSON format."""

            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=1536,
                )
            )

            # Clean and parse JSON response
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            result = json.loads(response_text.strip())
            return result

        except Exception as e:
            raise Exception(f"Failed to generate improvement suggestions: {str(e)}")
