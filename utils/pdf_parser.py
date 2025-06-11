import pdfplumber
import io
import streamlit as st

class PDFParser:
    def __init__(self):
        pass
    
    def extract_text_from_pdf(self, uploaded_file):
        """
        Extract text content from uploaded PDF file
        """
        try:
            # Convert uploaded file to bytes
            pdf_bytes = uploaded_file.read()
            
            # Create a BytesIO object from the uploaded file
            pdf_file = io.BytesIO(pdf_bytes)
            
            # Extract text using pdfplumber
            text_content = ""
            
            with pdfplumber.open(pdf_file) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text_content += page_text + "\n\n"
                    except Exception as e:
                        st.warning(f"Could not extract text from page {page_num + 1}: {str(e)}")
                        continue
            
            if not text_content.strip():
                raise Exception("No readable text found in the PDF file")
            
            return text_content.strip()
            
        except Exception as e:
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
    
    def extract_structured_data(self, uploaded_file):
        """
        Extract structured data from resume PDF (sections, contact info, etc.)
        """
        try:
            text_content = self.extract_text_from_pdf(uploaded_file)
            
            # Basic structure identification
            structured_data = {
                "full_text": text_content,
                "sections": self._identify_sections(text_content),
                "contact_info": self._extract_contact_info(text_content),
                "skills": self._extract_skills_section(text_content),
                "experience": self._extract_experience_section(text_content),
                "education": self._extract_education_section(text_content)
            }
            
            return structured_data
            
        except Exception as e:
            raise Exception(f"Failed to extract structured data: {str(e)}")
    
    def _identify_sections(self, text):
        """
        Identify main sections in the resume
        """
        common_sections = [
            "summary", "objective", "experience", "work experience", "employment",
            "education", "skills", "technical skills", "projects", "certifications",
            "achievements", "awards", "publications", "languages", "interests"
        ]
        
        found_sections = []
        text_lower = text.lower()
        
        for section in common_sections:
            if section in text_lower:
                found_sections.append(section.title())
        
        return found_sections
    
    def _extract_contact_info(self, text):
        """
        Extract contact information from resume text
        """
        import re
        
        contact_info = {}
        
        # Email extraction
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            contact_info["email"] = emails[0]
        
        # Phone number extraction (basic pattern)
        phone_patterns = [
            r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        ]
        
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            if phones:
                contact_info["phone"] = phones[0]
                break
        
        # LinkedIn URL extraction
        linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        linkedin_matches = re.findall(linkedin_pattern, text.lower())
        if linkedin_matches:
            contact_info["linkedin"] = f"https://{linkedin_matches[0]}"
        
        return contact_info
    
    def _extract_skills_section(self, text):
        """
        Extract skills section from resume
        """
        lines = text.split('\n')
        skills_section = []
        
        # Look for skills section
        skills_started = False
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            
            # Identify skills section start
            if any(keyword in line_lower for keyword in ['skills', 'technical skills', 'core competencies']):
                skills_started = True
                continue
            
            # Stop at next major section
            if skills_started and any(keyword in line_lower for keyword in ['experience', 'education', 'projects', 'work']):
                break
            
            # Collect skills lines
            if skills_started and line.strip():
                skills_section.append(line.strip())
        
        return skills_section
    
    def _extract_experience_section(self, text):
        """
        Extract work experience section from resume
        """
        lines = text.split('\n')
        experience_section = []
        
        # Look for experience section
        exp_started = False
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            
            # Identify experience section start
            if any(keyword in line_lower for keyword in ['experience', 'work experience', 'employment', 'career']):
                exp_started = True
                continue
            
            # Stop at next major section
            if exp_started and any(keyword in line_lower for keyword in ['education', 'skills', 'projects', 'certifications']):
                break
            
            # Collect experience lines
            if exp_started and line.strip():
                experience_section.append(line.strip())
        
        return experience_section
    
    def _extract_education_section(self, text):
        """
        Extract education section from resume
        """
        lines = text.split('\n')
        education_section = []
        
        # Look for education section
        edu_started = False
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            
            # Identify education section start
            if any(keyword in line_lower for keyword in ['education', 'academic', 'degree']):
                edu_started = True
                continue
            
            # Stop at next major section
            if edu_started and any(keyword in line_lower for keyword in ['experience', 'skills', 'projects', 'certifications']):
                break
            
            # Collect education lines
            if edu_started and line.strip():
                education_section.append(line.strip())
        
        return education_section
    
    def validate_pdf_content(self, uploaded_file):
        """
        Validate that the PDF contains readable text content
        """
        try:
            text = self.extract_text_from_pdf(uploaded_file)
            
            # Check if text is meaningful
            word_count = len(text.split())
            has_common_resume_words = any(word in text.lower() for word in 
                                       ['experience', 'education', 'skills', 'work', 'university', 'company'])
            
            validation_result = {
                "is_valid": word_count > 50 and has_common_resume_words,
                "word_count": word_count,
                "has_resume_keywords": has_common_resume_words,
                "text_preview": text[:200] + "..." if len(text) > 200 else text
            }
            
            return validation_result
            
        except Exception as e:
            return {
                "is_valid": False,
                "error": str(e),
                "word_count": 0,
                "has_resume_keywords": False,
                "text_preview": ""
            }
