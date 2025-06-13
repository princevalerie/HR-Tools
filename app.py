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
            return response.text
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
            return text
        except Exception as e:
            st.error(f"Error extracting PDF text: {str(e)}")
            return None

class CVImprover:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.0-flash-lite')

    def extract_text_from_pdf(self, pdf_file):
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text

    def improve_cv_general(self, cv_text):
        prompt = f"""
        As an ATS (Applicant Tracking System) and CV enhancement expert, please thoroughly review the following CV and optimize it for ATS compatibility. Pay special attention to any issues that could affect ATS parsing, including formatting, keyword relevance, and especially the use of quantifiable achievements in the experience section. If any job descriptions lack quantifiable data, modify them to include quantifiable achievements or responsibilities, indicating estimated metrics with brackets, e.g., [5%].

        ### Instructions for Optimization

        #### 1. **Correct Formatting and Layout for ATS Compatibility**
        - Ensure the CV has a simple, ATS-friendly layout (no tables, graphics, or complex formatting).
        - Use a consistent font and spacing style throughout the CV. Recommended fonts include Arial, Calibri, or Times New Roman, with a font size between 10 and 12 points.
        - Organize sections clearly with appropriate headings like "Experience," "Education," and "Skills" for easy ATS reading. Use bold or larger font for these headings to enhance readability.

        #### 2. **Experience Section - Quantitative Enhancements**
        - In the experience section, ensure each job description includes specific, measurable achievements or responsibilities reflecting the candidate's impact. If no quantifiable information is provided, revise descriptions to add quantitative aspects, using placeholders in brackets where necessary (e.g., [5%]).
        - Ensure that every job description in the experience section is either a quantifiable achievement or a quantifiable responsibility.
        - Start bullet points with action verbs like "Developed," "Implemented," "Managed," "Optimized," and "Achieved" to make the resume more engaging and ATS-readable.
        - Examples of quantitative achievements to use or adapt:
        - "Identification and implementation of [5%] cost-saving measures, resulting in increased efficiency and reduced expenses."
        - "Development and execution of [20%] increase in sales strategy, leading to significant revenue growth."
        - "Redesign of [30%] more efficient workflow process, resulting in improved productivity and reduced errors."

        #### 3. **Error and Typo Correction**
        - Carefully proofread for any typographical errors, grammar issues, or inconsistent formatting that may affect professionalism.
        - Rephrase any awkward phrasing or ambiguous terms to improve clarity and readability. Use grammar-checking tools to catch any mistakes.
        - Common errors to look out for:
        - Spelling mistakes (e.g., "managment" instead of "management")
        - Grammatical errors (e.g., "I have been working at the company for 5 years ago" instead of "I have been working at the company for 5 years")
        - Formatting inconsistencies (e.g., using inconsistent fonts or spacing)

        #### 4. **Keyword and Skill Integration**
        - Analyze the job role(s) the candidate is targeting to identify relevant keywords and integrate them naturally into the CV.
        - Emphasize high-demand skills and qualifications to increase ATS ranking, including both hard and soft skills relevant to the role. Ensure to include both long-form versions and acronym versions of keywords (e.g., "certified public accountant" and "CPA").
        - Tailor the CV to each job application by incorporating relevant keywords from the job description. This may involve tweaking existing keywords to match those in the job description exactly.

        #### 5. **Final Optimized Version of the CV**
        - Provide an improved, finalized ATS-friendly version of the CV.
        - Ensure the CV maintains a clean, minimalistic style that enhances readability while highlighting key achievements.

        #### 6. **Summary of Key Improvements Made**
        - List all major improvements, such as formatting changes, keyword additions, quantifiable results, typo corrections, or any other updates that enhance ATS compatibility and readability.

        #### 7. **Additional Suggestions**
        - Recommend additional changes that could make the CV stand out, such as adding certifications, clarifying job titles to align with industry norms, or updating project descriptions to reflect the latest relevant skills.
        - Suggest a professional email address and ensure contact information is easily visible and up-to-date.
        - For the personal projects section, provide detailed descriptions that emphasize the candidate's quantify technical skills, problem-solving abilities, and the impact of their contributions.

        #### 8. **ATS-Friendly Section Headings**
        - Use ATS-friendly section headings, such as "Experience," "Education," "Skills," and "Certifications," to help the ATS system accurately parse and categorize the CV.
        - Avoid using creative or non-standard section headings, as they may confuse the ATS system.

        #### 9. **Keyword Density and Placement**
        - Analyze the keyword density and placement throughout the CV to ensure that relevant keywords appear frequently enough to pass the ATS filter.
        - Use keywords strategically in the CV, particularly in the experience section, to increase the chances of passing the ATS filter.

        #### 10. **ATS Simulator Testing**
        - Test the CV through an ATS simulator or an online resume parser to ensure it performs well in an automated screening process.
        - Make necessary adjustments based on the results to improve compatibility and performance.

        #### 11. **Use of Bullet Points**
        - Consistently use bullet points to list responsibilities and achievements under each job title. This makes it easier for the ATS to parse and for human readers to scan quickly.

        #### 12. **Contact Information**
        - Place contact information at the top of the CV, including full name, phone number, email address, and LinkedIn profile if applicable. Ensure this information is accurate and professional.

        #### 13. **File Format**
        - Save the CV in a format that is widely accepted and ATS-friendly, such as .docx or .pdf. Avoid using .jpg or .png formats.

        #### 14. **Avoid Special Characters**
        - Avoid using special characters, symbols, or non-standard fonts that may confuse the ATS. Stick to standard characters and symbols.

        #### 15. **Consistent Date Formatting**
        - Use a consistent date format throughout the CV, such as MM/YYYY or Month YYYY, to ensure the ATS can properly read and parse the dates.

        #### 16. **Professional Summary**
        - Include a professional summary or objective statement at the beginning of the CV. This should be a brief paragraph that highlights key skills, experience, and career objectives.

        #### 17. **Relevant Courses and Training**
        - List relevant courses, certifications, and professional development activities in a specific section to show continuous learning and development.

        #### 18. **Technical Skills Section**
        - Create a dedicated section for technical skills, listing programming languages, software tools, and other technical competencies that are relevant to the job.

        #### 19. **Use of Acronyms**
        - Spell out acronyms the first time they are used, followed by the acronym in parentheses. For example, "Certified Public Accountant (CPA)."

        #### 20. **Avoid Industry Jargon**
        - Avoid excessive use of industry jargon that may not be recognized by the ATS. Use clear and straightforward language.

        #### 21. **Use of Hyperlinks**
        - Include hyperlinks to professional profiles, such as LinkedIn, but ensure they are text-based (e.g., "linkedin.com/in/yourprofile") to avoid issues with ATS parsing.

        #### 22. **Education Section**
        - List educational institutions in reverse chronological order, including the degree earned, institution name, and graduation date.

        #### 23. **Professional Development**
        - Highlight any professional development activities, such as conferences, workshops, or webinars, that demonstrate continuous learning and growth.

        #### 24. **Volunteer Work**
        - Include relevant volunteer work in a separate section, emphasizing skills and experiences that are transferable to the job.

        #### 25. **Achievements and Awards**
        - Create a section for achievements and awards, listing any recognition, scholarships, or honors received.

        #### 26. **Publications and Presentations**
        - If applicable, include a section for publications and presentations, highlighting any articles, papers, or presentations that demonstrate expertise in the field.

        #### 27. **Languages**
        - List any additional languages spoken and the level of proficiency in a separate section.

        #### 29. **Customization for Each Job**
        - Tailor the CV for each job application by customizing the summary, keywords, and experiences to match the specific job description.

        #### 30. **Final Review**
        - Conduct a final review of the CV to ensure all sections are complete, formatted consistently, and free of errors. Use spell-check and grammar-check tools for accuracy.

        ### Final Check
        Before submitting the CV, test it through an ATS simulator or an online resume parser to ensure it performs well in an automated screening process. Make necessary adjustments based on the results to improve compatibility and performance.

        ### Original CV
        {cv_text}
        """

class CoverLetterGenerator:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            st.error("❌ GOOGLE_API_KEY not found in environment variables!")
            st.stop()

    def extract_text_from_pdf(self, f):
        reader = PdfReader(f)
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    def extract_text_from_docx(self, f):
        doc = docx.Document(f)
        return "\n".join(p.text for p in doc.paragraphs)

    def extract_text(self, f):
        t = ""
        if f.type == "application/pdf":
            t = self.extract_text_from_pdf(f)
        elif f.type.startswith("application/vnd.openxmlformats"):
            t = self.extract_text_from_docx(f)
        elif f.type == "text/plain":
            t = f.read().decode("utf-8")
        return t

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

    def improve_cv_specific(self, cv_text, job_description, minimum_qualification):
        # First, improve the CV generally
        improved_cv = self.improve_cv_general(cv_text)
        
        # Then, tailor it for the specific job description
        prompt = f"""
        As an ATS (Applicant Tracking System) and CV enhancement expert, please review the following improved CV and further optimize it for the specific job description provided. Ensure that the CV is tailored to match the job requirements while maintaining its ATS-friendly format.

        ### Job Description:
        {job_description}

        ### Minimum Qualification:
        {minimum_qualification}

        ### Improved CV:
        {improved_cv}

        Please provide:
        1. A version of the CV tailored specifically for this job description, highlighting relevant skills and experiences.
        2. A list of key changes made to align the CV with the job description.
        3. Additional suggestions for making the CV stand out for this particular role.
        """

        response = self.model.generate_content(prompt)
        return response.text

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
        st.info("👆 Please upload your resume and provide the job description to begin the analysis.")

    # Footer
    st.markdown("---")
    st.markdown(
        "Made with ❤️ by Your Company Name | "
        "This tool uses AI to analyze resumes but should be used as one of many factors in your job application process."
    )

def cv_improver_page():
    st.title("ATS-Friendly CV Improver")
    
    cv_improver = CVImprover()

    st.subheader("Upload your CV (PDF format):")
    pdf_file = st.file_uploader("Choose a PDF file", type="pdf", key="cv_improver_upload")

    if pdf_file is not None:
        with st.spinner("Extracting text from PDF..."):
            cv_text = cv_improver.extract_text_from_pdf(pdf_file)

        option = st.selectbox("Choose an option:", ("General CV Enhancement", "Specific Job Description Enhancement"))

        if option == "General CV Enhancement":
            if st.button("Improve CV"):
                with st.spinner("Improving your CV..."):
                    improved_cv = cv_improver.improve_cv_general(cv_text)
                    st.subheader("Improved CV and Suggestions:")
                    st.write(improved_cv)
        else:
            job_description = st.text_area("Enter the job description:", height=150)
            minimum_qualification = st.text_area("Enter the minimum qualification:", height=50)
            if st.button("Improve CV for Specific Job"):
                if job_description and minimum_qualification:
                    with st.spinner("Improving your CV for the specific job..."):
                        improved_cv = cv_improver.improve_cv_specific(cv_text, job_description, minimum_qualification)
                        st.subheader("Improved CV and Suggestions for Specific Job:")
                        st.write(improved_cv)
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
            clean_text = cover_letter_gen.strip_header(raw_text)

        with st.spinner("Generating letter…"):
            prompt = cover_letter_gen.generate_prompt(clean_text, job_title, company, job_desc, job_reqs, word_len, hr_name, hr_role, language)
            model = genai.GenerativeModel("gemini-2.0-flash")
            resp = model.generate_content(prompt)
            letter = resp.text.strip()

        st.subheader("📄 Generated Cover Letter")
        st.text_area("Preview", letter, height=350)

        pdf = cover_letter_gen.export_pdf(letter)
        st.download_button("📥 Download PDF", data=pdf,
                           file_name="Cover_Letter.pdf", mime="application/pdf")
    else:
        st.info("👆 Upload CV and fill the form to generate a cover letter.")

def main():
    # Page configuration
    st.set_page_config(
        page_title="ATS Resume & CV Tool",
        page_icon="📄",
        layout="wide"
    )

    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Choose a tool:", ["ATS Resume Analyzer", "ATS CV Improver", "Cover Letter Generator"])

    if page == "ATS Resume Analyzer":
        resume_analyzer_page()
    elif page == "ATS CV Improver":
        cv_improver_page()
    elif page == "Cover Letter Generator":
        cover_letter_generator_page()

if __name__ == "__main__":
    main()
