from dotenv import load_dotenv
load_dotenv()
import streamlit as st
import os
from PyPDF2 import PdfReader
import google.generativeai as genai
import time
import fitz
import docx
from datetime import datetime
import io
import re
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY

# Configure Gemini AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class ATSAnalyzer:
    @staticmethod
    def get_gemini_response(input_prompt, pdf_text, job_description):
        try:
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            response = model.generate_content([input_prompt, pdf_text, job_description])
            return response.text if response and response.text else "No response generated."
        except Exception as e:
            st.error(f"Error generating response: {str(e)}")
            return None

    @staticmethod
    def extract_text_from_pdf(uploaded_file):
        try:
            pdf_reader = PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text if text.strip() else None
        except Exception as e:
            st.error(f"Error extracting PDF text: {str(e)}")
            return None

class CVImprover:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')

    def extract_text_from_pdf(self, pdf_file):
        try:
            doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text if text.strip() else None
        except Exception as e:
            st.error(f"Error extracting PDF text: {str(e)}")
            return None

    def improve_cv_general(self, cv_text):
        if not cv_text or cv_text.strip() == "":
            return "Error: No CV text provided or CV text is empty."
        
        prompt = f"""
        As an ATS (Applicant Tracking System) and CV enhancement expert, please thoroughly review the following CV and optimize it for ATS compatibility. Pay special attention to any issues that could affect ATS parsing, including formatting, keyword relevance, and especially the use of quantifiable achievements in the experience section.

        ### Instructions for Optimization

        #### 1. **Correct Formatting and Layout for ATS Compatibility**
        - Ensure the CV has a simple, ATS-friendly layout (no tables, graphics, or complex formatting).
        - Use a consistent font and spacing style throughout the CV.
        - Organize sections clearly with appropriate headings like "Experience," "Education," and "Skills" for easy ATS reading.

        #### 2. **Experience Section - Quantitative Enhancements**
        - In the experience section, ensure each job description includes specific, measurable achievements or responsibilities.
        - If no quantifiable information is provided, revise descriptions to add quantitative aspects, using placeholders in brackets where necessary (e.g., [increased efficiency by 15%]).
        - Start bullet points with action verbs like "Developed," "Implemented," "Managed," "Optimized," and "Achieved."

        #### 3. **Error and Typo Correction**
        - Carefully proofread for any typographical errors, grammar issues, or inconsistent formatting.
        - Rephrase any awkward phrasing or ambiguous terms to improve clarity and readability.

        #### 4. **Keyword and Skill Integration**
        - Analyze the job role(s) the candidate is targeting to identify relevant keywords and integrate them naturally into the CV.
        - Emphasize high-demand skills and qualifications to increase ATS ranking.

        Please provide:
        1. **Improved CV**: A complete, optimized version of the CV
        2. **Summary of Key Improvements**: List all major improvements made
        3. **Additional Suggestions**: Recommend additional changes that could make the CV stand out

        ### Original CV:
        {cv_text}

        Please format your response clearly with the improved CV first, followed by the summary of improvements and suggestions.
        """

        try:
            response = self.model.generate_content(prompt)
            if response and response.text:
                return response.text
            else:
                return "Error: No response generated from the AI model."
        except Exception as e:
            return f"Error generating CV improvements: {str(e)}"

    def improve_cv_specific(self, cv_text, job_description, minimum_qualification):
        if not cv_text or cv_text.strip() == "":
            return "Error: No CV text provided or CV text is empty."
        
        if not job_description or not minimum_qualification:
            return "Error: Job description and minimum qualification are required."
        
        # First, improve the CV generally
        improved_cv_general = self.improve_cv_general(cv_text)
        
        if "Error:" in improved_cv_general:
            return improved_cv_general
        
        # Then, tailor it for the specific job description
        prompt = f"""
        As an ATS (Applicant Tracking System) and CV enhancement expert, please review the following improved CV and further optimize it for the specific job description provided. Ensure that the CV is tailored to match the job requirements while maintaining its ATS-friendly format.

        ### Job Description:
        {job_description}

        ### Minimum Qualification:
        {minimum_qualification}

        ### Previously Improved CV:
        {improved_cv_general}

        Please provide:
        1. **Job-Specific Tailored CV**: A version of the CV tailored specifically for this job description, highlighting relevant skills and experiences that match the job requirements.
        2. **Key Changes Made**: A list of key changes made to align the CV with the job description.
        3. **Job-Specific Suggestions**: Additional suggestions for making the CV stand out for this particular role.
        4. **Keyword Analysis**: Important keywords from the job description that should be emphasized in the CV.

        Format your response clearly with sections for each of the above points.
        """

        try:
            response = self.model.generate_content(prompt)
            if response and response.text:
                return response.text
            else:
                return "Error: No response generated from the AI model for job-specific improvements."
        except Exception as e:
            return f"Error generating job-specific CV improvements: {str(e)}"

class CoverLetterGenerator:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            st.error("❌ GOOGLE_API_KEY not found in environment variables!")
            st.stop()

    def extract_text_from_pdf(self, f):
        try:
            reader = PdfReader(f)
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception as e:
            st.error(f"Error extracting PDF text: {str(e)}")
            return ""

    def extract_text_from_docx(self, f):
        try:
            doc = docx.Document(f)
            return "\n".join(p.text for p in doc.paragraphs)
        except Exception as e:
            st.error(f"Error extracting DOCX text: {str(e)}")
            return ""

    def extract_text(self, f):
        try:
            t = ""
            if f.type == "application/pdf":
                t = self.extract_text_from_pdf(f)
            elif f.type.startswith("application/vnd.openxmlformats"):
                t = self.extract_text_from_docx(f)
            elif f.type == "text/plain":
                t = f.read().decode("utf-8")
            return t
        except Exception as e:
            st.error(f"Error extracting text: {str(e)}")
            return ""

    def strip_header(self, text):
        lines = text.splitlines()
        cleaned = []
        header_ended = False
        for line in lines:
            if not header_ended:
                if re.search(r"[\w\.-]+@[\w\.-]+", line) \
                   or re.search(r"(?<!\d)(\+62|08|62)[\d\s\-]{6,}(?!\d)", line) \
                   or re.search(r"\b\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)\b", line, re.IGNORECASE) \
                   or len(line.strip()) == 0:
                    continue
                else:
                    header_ended = True
            cleaned.append(line)
        return "\n".join(cleaned).strip()

    def generate_prompt(self, cv_text, job_title, company, job_desc, job_reqs, word_len, hr_name, hr_role, language):
        today   = datetime.now().strftime("%d %B %Y")
        hr_line = f"to {hr_name}, {hr_role}" if hr_name and hr_role else hr_name or "the Hiring Team"
        lang    = "Indonesian (Bahasa Indonesia)" if language == "Bahasa Indonesia" else "English"

        return f"""
    You are a professional cover letter writer. Create a clean, ready-to-use cover letter:

    Date: {today}

    Resume (achievements, skills, experiences):
    {cv_text}

    Job Info:
    - Position: {job_title}
    - Company: {company}
    - Description: {job_desc}
    - Requirements: {job_reqs}

    Instructions:
    - Language: {lang}
    - Length: approx. {word_len} words
    - Address to: {hr_line}

    Structure:
    📝 **Structure & Tone:**
    1. **Salutation:** Use specific name if given (e.g., \"Dear Mr./Ms. X\"), or \"Dear Hiring Manager\".
    2. **Intro:** Show enthusiasm and suitability for the role.
    3. **Body:**
        - Match top 2–3 job requirements with real achievements/skills from CV.
        - Use real examples and quantify (e.g., \"increased efficiency by 20%\").
        - Highlight what value you bring to {company}.
    4. **Motivation:** Optional — why you want to work at {company}.
    5. **Closing:** Reaffirm interest and politely invite follow-up.
    6. **Signature:** Full name

    *Critical Instruction*
        1. Do not include any placeholder text in square brackets like , [Date], [Company Name],, etc. 
        2. Use the actual provided information: {company}, etc.
        3. Do not include any metadata, instructions, or notes in square brackets in the final output.
        4. The output should be a clean, professional cover letter ready for immediate use.
        5. Remove any text that appears in square brackets [ ] completely from the final output.
        6. Always structure the paragrapgh and text allignment like professional cover letter
        7. Do not include any address and instruction to fill the address

    Do not include any personal contact details or headers in final output.
    """

    def export_pdf(self, letter_text):
        try:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4,
                                    leftMargin=40, rightMargin=40,
                                    topMargin=40, bottomMargin=40)
            styles = getSampleStyleSheet()
            style = ParagraphStyle(
                'Justify',
                parent=styles['Normal'],
                alignment=TA_JUSTIFY,
                fontName='Times-Roman',
                fontSize=12,
                leading=16,
                firstLineIndent=20  # indent first line
            )
            elements = []
            for para in letter_text.split("\n\n"):
                elements.append(Paragraph(para.strip().replace("\n", " "), style))
            doc.build(elements)
            buffer.seek(0)
            return buffer
        except Exception as e:
            st.error(f"Error generating PDF: {str(e)}")
            return None

def resume_analyzer_page():
    st.title("📄 ATS Resume Analyzer")
    st.markdown("""
        This tool helps you analyze your resume against job descriptions using AI. 
        Upload your resume and paste the job description to:
        - Get a detailed analysis of your resume
        - See the percentage match with job requirements
        - Identify missing keywords and areas for improvement
    """)

    # Custom CSS
    st.markdown("""
        <style>
        .stButton>button {
            width: 100%;
            background-color: #0066cc;
            color: white;
        }
        .stButton>button:hover {
            background-color: #0052a3;
        }
        .success-message {
            padding: 1rem;
            border-radius: 0.5rem;
            background-color: #d4edda;
            color: #155724;
        }
        </style>
    """, unsafe_allow_html=True)

    # Create two columns for input
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📝 Job Description")
        job_description = st.text_area(
            "Paste the job description here",
            height=200,
            placeholder="Paste the complete job description here..."
        )

    with col2:
        st.subheader("📎 Resume Upload")
        uploaded_file = st.file_uploader(
            "Upload your resume (PDF format)",
            type=["pdf"],
            help="Please ensure your resume is in PDF format"
        )

        if uploaded_file:
            st.markdown('<p class="success-message">✅ PDF uploaded successfully!</p>', unsafe_allow_html=True)

    # Analysis options
    if uploaded_file and job_description:
        st.subheader("🔍 Analysis Options")
        analysis_type = st.radio(
            "Choose analysis type:",
            ["Detailed Resume Review", "Match Percentage Analysis"]
        )

        if st.button("Analyze Resume"):
            with st.spinner("Analyzing your resume... Please wait"):
                # Extract PDF text
                pdf_text = ATSAnalyzer.extract_text_from_pdf(uploaded_file)
                
                if pdf_text:
                    # Select prompt based on analysis type
                    if analysis_type == "Detailed Resume Review":
                        prompt = """
                        As an experienced Technical Human Resource Manager, provide a detailed professional evaluation 
                        of the candidate's resume against the job description. Please analyze:
                        1. Overall alignment with the role
                        2. Key strengths and qualifications that match
                        3. Notable gaps or areas for improvement
                        4. Specific recommendations for enhancing the resume
                        5. Final verdict on suitability for the role
                        
                        Format the response with clear headings and professional language.
                        """
                    else:
                        prompt = """
                        As an ATS (Applicant Tracking System) expert, provide:
                        1. Overall match percentage (%)
                        2. Key matching keywords found
                        3. Important missing keywords
                        4. Skills gap analysis
                        5. Specific recommendations for improvement
                        
                        Start with the percentage match prominently displayed.
                        """

                    # Get and display response
                    response = ATSAnalyzer.get_gemini_response(prompt, pdf_text, job_description)
                    
                    if response:
                        st.markdown("### Analysis Results")
                        st.markdown(response)
                        
                        # Add export option
                        st.download_button(
                            label="📥 Export Analysis",
                            data=response,
                            file_name="resume_analysis.txt",
                            mime="text/plain"
                        )
                    else:
                        st.error("❌ Failed to generate analysis. Please try again.")
                else:
                    st.error("❌ Failed to extract text from PDF. Please ensure your PDF is readable.")
    else:
        st.info("👆 Please upload your resume and provide the job description to begin the analysis.")

    # Footer
    st.markdown("---")
    st.markdown(
        "Made with ❤️ using Google Gemini AI | "
        "This tool uses AI to analyze resumes but should be used as one of many factors in your job application process."
    )

def cv_improver_page():
    st.title("🔧 ATS-Friendly CV Improver")
    st.markdown("""
        This tool helps you optimize your CV for ATS (Applicant Tracking Systems) using AI. 
        Upload your CV to get:
        - ATS-friendly formatting suggestions
        - Quantifiable achievements enhancement
        - Keyword optimization
        - Error corrections and improvements
    """)
    
    # Custom CSS for better styling
    st.markdown("""
        <style>
        .stButton>button {
            width: 100%;
            background-color: #28a745;
            color: white;
        }
        .stButton>button:hover {
            background-color: #218838;
        }
        .success-message {
            padding: 1rem;
            border-radius: 0.5rem;
            background-color: #d4edda;
            color: #155724;
        }
        .warning-message {
            padding: 1rem;
            border-radius: 0.5rem;
            background-color: #fff3cd;
            color: #856404;
        }
        </style>
    """, unsafe_allow_html=True)
    
    cv_improver = CVImprover()

    st.subheader("📎 Upload your CV")
    pdf_file = st.file_uploader(
        "Choose a PDF file", 
        type="pdf", 
        key="cv_improver_upload",
        help="Please ensure your CV is in PDF format for best results"
    )

    if pdf_file is not None:
        st.markdown('<p class="success-message">✅ PDF uploaded successfully!</p>', unsafe_allow_html=True)
        
        with st.spinner("Extracting text from PDF..."):
            cv_text = cv_improver.extract_text_from_pdf(pdf_file)

        if cv_text:
            # Show extracted text preview
            with st.expander("📄 Preview of extracted text (first 500 characters)"):
                st.text(cv_text[:500] + "..." if len(cv_text) > 500 else cv_text)
            
            st.subheader("🛠️ Enhancement Options")
            option = st.selectbox(
                "Choose an enhancement option:", 
                ("General CV Enhancement", "Job-Specific Enhancement"),
                help="General enhancement improves overall ATS compatibility. Job-specific enhancement tailors your CV for a particular job."
            )

            if option == "General CV Enhancement":
                st.markdown("**General Enhancement** will optimize your CV for ATS compatibility with:")
                st.markdown("- ✅ Format optimization")
                st.markdown("- ✅ Quantifiable achievements")
                st.markdown("- ✅ Error corrections")
                st.markdown("- ✅ Keyword improvements")
                
                if st.button("🚀 Improve CV (General)", key="general_improve"):
                    with st.spinner("Analyzing and improving your CV... This may take a moment"):
                        improved_cv = cv_improver.improve_cv_general(cv_text)
                        
                        if improved_cv and not improved_cv.startswith("Error:"):
                            st.subheader("✨ Improved CV and Suggestions")
                            st.markdown(improved_cv)
                            
                            # Add download button
                            st.download_button(
                                label="📥 Download Improved CV Analysis",
                                data=improved_cv,
                                file_name="improved_cv_analysis.txt",
                                mime="text/plain"
                            )
                        else:
                            st.error(f"❌ {improved_cv}")
                            
            else:  # Job-Specific Enhancement
                st.markdown("**Job-Specific Enhancement** will tailor your CV for a particular job posting:")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    job_description = st.text_area(
                        "📋 Job Description:", 
                        height=150,
                        placeholder="Paste the full job description here..."
                    )
                
                with col2:
                    minimum_qualification = st.text_area(
                        "🎓 Minimum Qualifications:", 
                        height=150,
                        placeholder="List the minimum qualifications required..."
                    )
                
                if st.button("🎯 Improve CV for Specific Job", key="specific_improve"):
                    if job_description and minimum_qualification:
                        with st.spinner("Tailoring your CV for the specific job... This may take a moment"):
                            improved_cv = cv_improver.improve_cv_specific(cv_text, job_description, minimum_qualification)
                            
                            if improved_cv and not improved_cv.startswith("Error:"):
                                st.subheader("🎯 Job-Tailored CV and Suggestions")
                                st.markdown(improved_cv)
                                
                                # Add download button
                                st.download_button(
                                    label="📥 Download Job-Tailored CV Analysis",
                                    data=improved_cv,
                                    file_name="job_tailored_cv_analysis.txt",
                                    mime="text/plain"
                                )
                            else:
                                st.error(f"❌ {improved_cv}")
                    else:
                        st.markdown('<p class="warning-message">⚠️ Please provide both job description and minimum qualifications.</p>', unsafe_allow_html=True)
        else:
            st.error("❌ Failed to extract text from the PDF. Please ensure your PDF is readable and try again.")
    else:
        st.info("👆 Please upload your CV in PDF format to begin the improvement process.")

    # Additional tips section
    with st.expander("💡 Tips for Best Results"):
        st.markdown("""
        **To get the best CV improvements:**
        
        1. **PDF Quality**: Ensure your PDF is text-based (not scanned images)
        2. **Complete Information**: Include all sections (contact, experience, education, skills)
        3. **Job-Specific Mode**: Provide detailed job descriptions for better tailoring
        4. **Review Output**: Always review and customize the AI suggestions to match your voice
        5. **Multiple Iterations**: You can run the tool multiple times with different job descriptions
        """)

    # Footer
    st.markdown("---")
    st.markdown(
        "Made with ❤️ using Google Gemini AI | "
        "This tool provides AI-generated suggestions. Please review and customize the output to ensure accuracy."
    )

def cover_letter_generator_page():
    st.title("📝 Cover Letter Generator")
    st.markdown("Generate professional cover letters using **Gemini 2.0 Flash**")
    
    cover_letter_gen = CoverLetterGenerator()

    # File upload and inputs
    cv_file = st.file_uploader("📎 Upload your CV (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"], key="cover_letter_upload")

    with st.form("cover_letter_form"):
        job_title = st.text_input("Job Title")
        company   = st.text_input("Company Name")
        job_desc  = st.text_area("Job Description")
        job_reqs  = st.text_area("Job Requirements")
        word_len  = st.slider("Word Count Target", 40, 800, 100)
        hr_name   = st.text_input("HR Name (Optional)")
        hr_role   = st.text_input("HR Role (Optional)")
        language  = st.radio("Language", ["English", "Bahasa Indonesia"])
        submitted = st.form_submit_button("Generate Cover Letter")

    # Main logic
    if submitted and cv_file:
        if not (job_title and company and job_desc and job_reqs):
            st.warning("⚠️ Please fill all job fields.")
            st.stop()

        with st.spinner("Reading CV…"):
            raw_text = cover_letter_gen.extract_text(cv_file)
            if not raw_text:
                st.error("❌ Failed to extract text from CV. Please try again.")
                st.stop()
            clean_text = cover_letter_gen.strip_header(raw_text)

        with st.spinner("Generating letter…"):
            try:
                prompt = cover_letter_gen.generate_prompt(clean_text, job_title, company, job_desc, job_reqs, word_len, hr_name, hr_role, language)
                model = genai.GenerativeModel("gemini-2.0-flash-exp")
                resp = model.generate_content(prompt)
                
                if resp and resp.text:
                    letter = resp.text.strip()
                    
                    st.subheader("📄 Generated Cover Letter")
                    st.text_area("Preview", letter, height=350)

                    pdf = cover_letter_gen.export_pdf(letter)
                    if pdf:
                        st.download_button("📥 Download PDF", data=pdf,
                                           file_name="Cover_Letter.pdf", mime="application/pdf")
                    else:
                        st.error("❌ Failed to generate PDF. You can copy the text above.")
                else:
                    st.error("❌ Failed to generate cover letter. Please try again.")
            except Exception as e:
                st.error(f"❌ Error generating cover letter: {str(e)}")
    else:
        st.info("👆 Upload CV and fill the form to generate a cover letter.")

def main():
    # Page configuration
    st.set_page_config(
        page_title="ATS Resume & CV Tool",
        page_icon="📄",
        layout="wide"
    )

    # Check for API key
    if not os.getenv("GOOGLE_API_KEY"):
        st.error("❌ GOOGLE_API_KEY not found in environment variables!")
        st.info("Please add your Google API key to the .env file or environment variables.")
        st.stop()

    # Sidebar for navigation
    st.sidebar.title("🧭 Navigation")
    st.sidebar.markdown("---")
    page = st.sidebar.selectbox(
        "Choose a tool:", 
        ["ATS Resume Analyzer", "ATS CV Improver", "Cover Letter Generator"]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    ### 🔧 Tools Overview
    
    **📄 ATS Resume Analyzer**
    - Analyze resume-job fit
    - Get match percentages
    - Identify missing keywords
    
    **🔧 ATS CV Improver**
    - ATS-friendly formatting
    - Add quantifiable achievements
    - General & job-specific improvements
    
    **📝 Cover Letter Generator**
    - Professional cover letters
    - Tailored to job descriptions
    - Multiple language support
    """)

    # Route to appropriate page
    if page == "ATS Resume Analyzer":
        resume_analyzer_page()
    elif page == "ATS CV Improver":
        cv_improver_page()
    elif page == "Cover Letter Generator":
        cover_letter_generator_page()

if __name__ == "__main__":
    main()
