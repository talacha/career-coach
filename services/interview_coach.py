import json
import os
import random
import google.generativeai as genai

class InterviewCoach:
    def __init__(self):
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel('gemini-1.5-pro')
        
        # Question categories for different interview types
        self.question_types = {
            "Behavioral": [
                "Tell me about a time when you had to work under pressure.",
                "Describe a situation where you had to resolve a conflict with a team member.",
                "Give me an example of when you had to learn something new quickly.",
                "Tell me about a time you failed and how you handled it.",
                "Describe a situation where you had to persuade someone to see your point of view."
            ],
            "Technical": [
                "Explain the difference between synchronous and asynchronous programming.",
                "How would you optimize a slow database query?",
                "What are the key principles of object-oriented programming?",
                "Explain the concept of API rate limiting and how you would implement it.",
                "How would you handle error handling in a distributed system?"
            ],
            "System Design": [
                "Design a URL shortening service like bit.ly.",
                "How would you design a chat application like WhatsApp?",
                "Design a recommendation system for an e-commerce platform.",
                "How would you design a file storage system like Google Drive?",
                "Design a real-time notification system."
            ],
            "Leadership": [
                "Tell me about a time you had to lead a team through a difficult project.",
                "How do you handle underperforming team members?",
                "Describe your approach to giving feedback to team members.",
                "Tell me about a time you had to make a difficult decision as a leader.",
                "How do you motivate your team during challenging times?"
            ],
            "Problem Solving": [
                "Walk me through your problem-solving process.",
                "Tell me about the most complex problem you've solved recently.",
                "How do you approach debugging a system that's failing?",
                "Describe a time when you had to think outside the box to solve a problem.",
                "How do you prioritize multiple competing problems?"
            ]
        }

    def generate_question(self, job_role, focus_areas, interview_type):
        """
        Generate an interview question based on job role and focus areas
        """
        try:
            # Select question type based on focus areas
            if interview_type == "Behavioral Only":
                selected_focus = ["Behavioral"]
            elif interview_type == "Technical Only":
                selected_focus = [area for area in focus_areas if area in ["Technical", "System Design"]]
                if not selected_focus:
                    selected_focus = ["Technical"]
            else:
                selected_focus = focus_areas

            # Generate AI-powered question
            prompt = f"""
            Generate a thoughtful interview question for a {job_role} position.
            
            Focus areas: {', '.join(selected_focus)}
            Interview type: {interview_type}
            
            The question should be:
            1. Relevant to the {job_role} position
            2. Focused on {', '.join(selected_focus)} skills
            3. Designed to assess the candidate's experience and problem-solving abilities
            4. Clear and specific enough to allow for a structured response
            
            Return only the question, no additional text or formatting.
            """

            full_prompt = f"""You are an expert interviewer who creates insightful, role-specific interview questions. Generate questions that help assess a candidate's skills, experience, and fit for the position.

{prompt}"""

            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=200,
                )
            )

            question = response.text.strip()
            return question

        except Exception as e:
            # Fallback to predefined questions if AI generation fails
            focus_area = random.choice(focus_areas)
            if focus_area in self.question_types:
                return random.choice(self.question_types[focus_area])
            else:
                return "Tell me about your experience and what makes you a good fit for this role."

    def evaluate_answer(self, question, answer, job_role, focus_areas):
        """
        Evaluate the candidate's answer and provide feedback
        """
        try:
            # Determine if this is a behavioral question for STAR format coaching
            is_behavioral = any(word in question.lower() for word in ['tell me about', 'describe a time', 'give me an example'])
            
            prompt = f"""
            You are an expert interview coach. Evaluate this candidate's answer and provide constructive feedback.

            POSITION: {job_role}
            FOCUS AREAS: {', '.join(focus_areas)}
            QUESTION: {question}
            CANDIDATE'S ANSWER: {answer}

            Evaluate the answer and provide feedback in JSON format:
            {{
                "score": <score from 1-10>,
                "feedback": "<detailed constructive feedback>",
                "strengths": ["<strength1>", "<strength2>", ...],
                "areas_for_improvement": ["<area1>", "<area2>", ...],
                "suggested_improvements": "<specific suggestions for better answer>",
                "star_format_feedback": "<feedback on STAR format if applicable>",
                "example_improvement": "<example of how to improve the answer>"
            }}

            Evaluation Criteria:
            1. Relevance to the question and role
            2. Specificity and concrete examples
            3. Structure and clarity
            4. Demonstration of skills/experience
            5. STAR format usage (for behavioral questions)
            
            {'Focus on STAR format (Situation, Task, Action, Result) for this behavioral question.' if is_behavioral else 'Focus on technical accuracy and problem-solving approach.'}
            
            Be constructive, specific, and encouraging in your feedback.
            """

            full_prompt = f"""You are an expert interview coach and evaluator. Provide detailed, constructive feedback to help candidates improve their interview performance. Be encouraging but honest about areas for improvement.

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
            
            # Format the feedback for display
            feedback_text = result.get("feedback", "")
            
            # Add STAR format guidance for behavioral questions
            if is_behavioral and result.get("star_format_feedback"):
                feedback_text += f"\n\n**STAR Format Feedback:** {result.get('star_format_feedback')}"
            
            # Add improvement suggestions
            if result.get("suggested_improvements"):
                feedback_text += f"\n\n**Suggestions:** {result.get('suggested_improvements')}"
            
            return {
                "score": max(1, min(10, result.get("score", 5))),
                "feedback": feedback_text,
                "strengths": result.get("strengths", []),
                "areas_for_improvement": result.get("areas_for_improvement", []),
                "example_improvement": result.get("example_improvement", "")
            }

        except json.JSONDecodeError as e:
            return {
                "score": 5,
                "feedback": f"I had trouble analyzing your answer, but I appreciate your response. Try to be more specific and provide concrete examples. {str(e)}",
                "strengths": [],
                "areas_for_improvement": ["Provide more specific examples", "Structure your answer more clearly"],
                "example_improvement": ""
            }
        except Exception as e:
            return {
                "score": 5,
                "feedback": f"I encountered an error while evaluating your answer. Please try again. Error: {str(e)}",
                "strengths": [],
                "areas_for_improvement": [],
                "example_improvement": ""
            }

    def provide_star_coaching(self, question, answer):
        """
        Provide specific STAR format coaching for behavioral questions
        """
        try:
            prompt = f"""
            Help the candidate improve their answer using the STAR format (Situation, Task, Action, Result).

            QUESTION: {question}
            CURRENT ANSWER: {answer}

            Provide coaching in JSON format:
            {{
                "star_analysis": {{
                    "situation": "<what situation elements are present/missing>",
                    "task": "<what task elements are present/missing>",
                    "action": "<what action elements are present/missing>",
                    "result": "<what result elements are present/missing>"
                }},
                "improved_structure": "<suggested structure for the answer>",
                "example_phrases": ["<phrase1>", "<phrase2>", ...],
                "coaching_tips": ["<tip1>", "<tip2>", ...]
            }}
            """

            full_prompt = f"""You are a STAR format coaching expert. Help candidates structure their behavioral interview answers using Situation, Task, Action, Result framework.

{prompt}

Please ensure your response is valid JSON format."""

            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
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
            return {
                "star_analysis": {
                    "situation": "Could not analyze situation",
                    "task": "Could not analyze task",
                    "action": "Could not analyze action",
                    "result": "Could not analyze result"
                },
                "improved_structure": "Try to structure your answer with: What was the situation? What was your task? What actions did you take? What were the results?",
                "example_phrases": ["In this situation...", "My task was to...", "I took the following actions...", "As a result..."],
                "coaching_tips": ["Be specific with examples", "Quantify your results when possible", "Focus on your individual contributions"]
            }

    def generate_follow_up_question(self, previous_question, previous_answer, job_role):
        """
        Generate a follow-up question based on the candidate's previous answer
        """
        try:
            prompt = f"""
            Based on the candidate's previous answer, generate a thoughtful follow-up question for a {job_role} interview.

            PREVIOUS QUESTION: {previous_question}
            CANDIDATE'S ANSWER: {previous_answer}

            Generate a follow-up question that:
            1. Digs deeper into their experience
            2. Clarifies or expands on their previous answer
            3. Is relevant to the {job_role} position
            4. Helps assess their skills and problem-solving abilities

            Return only the follow-up question, no additional text.
            """

            full_prompt = f"""You are an expert interviewer who asks insightful follow-up questions to better understand candidates' experiences and abilities.

{prompt}"""

            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.6,
                    max_output_tokens=150,
                )
            )

            return response.text.strip()

        except Exception as e:
            return "Can you tell me more about the specific challenges you faced in that situation and how you overcame them?"
