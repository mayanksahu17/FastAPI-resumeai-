from fastapi import APIRouter
import os
from fastapi import APIRouter, UploadFile, File, Form
from typing import Annotated
import subprocess
from typing import Optional
import re
import openai


UPLOAD_DIR = "modified_tex"
UPLOAD_FOLDER = "uploads"
DOWNLOAD_FOLDER = "downloads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Set OpenAI API key
openai.api_key = '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'


api_router = APIRouter()

@api_router.get("/test")
def test_route():
    return {"message": "API is working perfectly!"}


@api_router.post("/upload")
async def upload_job_description(
    job_description: Annotated[str, Form()],  
    file: UploadFile = File(...) 
):
    
    jd_path = os.path.join(UPLOAD_FOLDER, "job_description.txt")
    with open(jd_path, "w", encoding="utf-8") as jd_file:
        jd_file.write(job_description)

    
    tex_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(tex_path, "wb") as tex_file:
        tex_file.write(await file.read())
    pfd_path = convert_to_pdf(tex_path)
    return {
        "message": "File uploaded successfully!",
        "job_description_path": jd_path,
        "tex_file_path": pfd_path
    }



# ✅ Function to Convert .tex to PDF
def convert_to_pdf(tex_filepath):
    pdf_filename = "resume.pdf"
    pdf_filepath = os.path.join(DOWNLOAD_FOLDER, pdf_filename)
    
    try:
        # pdflatex का पूरा path (Linux/macOS/Windows के हिसाब से एडिट करो)
        pdflatex_path = "C:\\Program Files\\MiKTeX\\miktex\\bin\\x64\\pdflatex.exe"
        # pdflatex_path = "C:\\Program Files\\MiKTeX\\miktex\\bin\\pdflatex.exe"  # Windows (Example)

        # LaTeX को PDF में कन्वर्ट करना
        subprocess.run([pdflatex_path, "-output-directory", DOWNLOAD_FOLDER, tex_filepath], check=True)
        print(f"✅ PDF successfully generated: {pdf_filepath}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error generating PDF: {e}")
    
    return pdf_filepath if os.path.exists(pdf_filepath) else None



def extract_experience(latex_content):
    # Define correct LaTeX section markers
     
    # Define markers
    start_marker = r"""
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% PROFESSIONAL EXPERIENCE
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
    end_marker = r"""
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% PROJECTS & OUTSIDE EXPERIENCE
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
    # Regex pattern to extract content between markers
    pattern = rf"{re.escape(start_marker)}(.*?){re.escape(end_marker)}"
    match = re.search(pattern, latex_content, re.DOTALL)

    if match:
        return match.group(1).strip()
    else:
        return "Section not found."
    
def extract_skills(latex_content):

    # Define markers for the Technical Skills section
    # start_marker_skills = r"\noindent \textbf{{SKILLS}}"
    start_marker_skills = r"""
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% SKILLS
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
    # end_marker_skills = r"\noindent \textbf{{WORK EXPERIENCE}}"
    end_marker_skills = r"""
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% PROFESSIONAL EXPERIENCE
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""

     # Regex pattern to extract content between markers
    pattern = rf"{re.escape(start_marker_skills)}(.*?){re.escape(end_marker_skills)}"
    match = re.search(pattern, latex_content, re.DOTALL)

    if match:
        return match.group(1).strip()
    else:
        return "Section not found."




@api_router.post("/process_tex")
async def process_tex(file: UploadFile = File(...),
                       job_description: Optional[str] = Form(None)):
    try:
        latex_content = await file.read()
        latex_content = latex_content.decode("utf-8")
        extracted_skills = extract_skills(latex_content)
        extracted_work_experience = extract_experience(latex_content)
        # Refined prompt to modify work experience section with relevant keywords
        messages = [
            {"role": "system", "content": "You are an expert assistant for modifying LaTeX resumes."},
            {"role": "user", "content": (
                f"Here is the work experience section of a LaTeX resume: {extracted_work_experience}. "
                f"Here is the job description: {job_description}. "
                "I want you to **identify key skills** from the job description and **explicitly integrate them** into the work experience. "
                "Show how these skills were applied or demonstrated in the responsibilities and achievements listed in the work experience. "
                "Ensure each skill from the job description is reflected in a specific context (e.g., technical challenges, achievements, or responsibilities) within the work experience. "
                "Preserve the original structure and bullet points, but enhance them by showcasing the use of those skills. "
                "Ensure no bullet point exceeds two lines in length, and maintain formatting, alignment, and consistency throughout the section. "
                "Return only the modified LaTeX content without any explanations, introductions, or notes."
            )}
        ]

        # Get the modified work experience section from GPT
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            max_tokens=1500
        )
        modified_work_experience = response['choices'][0]['message']['content']
            # Sanitize: Remove unwanted prompts or explanatory text
        unwanted_phrases = [
            "Here is your modified work experience", 
            "Note:", 
            "Incorporating", 
            "Here’s the result",
        ]
        for phrase in unwanted_phrases:
            modified_work_experience = modified_work_experience.replace(phrase, '')

        # TODO :Replace the work experience section with the modified content in the latex file
        # TODO : Repeate the same process for the skills seection and replace the modified  skills latex code 
        # TODO : and return the entire latex code 
        return {
            "message": "LaTeX file processed ACCORDING TO THE JOB DESCRIPTION  successfully.",
            # "extracted_work_experience" : extracted_work_experience,
            # "extracted_skills" : extracted_skills,
            # "job_description": job_description  # Return job description in the response

        }

    except Exception as e:
        return {"error": str(e)}