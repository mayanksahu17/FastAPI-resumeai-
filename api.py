from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks
import os
import subprocess
import re
from openai import OpenAI
from fastapi.responses import FileResponse
from typing import Optional, Annotated
from fastapi import FastAPI, HTTPException, Query
import cloudinary
import cloudinary.uploader
from datetime import datetime 
from config import client , cloudinary , get_pdflatex_path


# Constants
UPLOAD_DIR = "modified_tex"
UPLOAD_FOLDER = "uploads"
DOWNLOAD_FOLDER = "downloads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

# client = OpenAI(
#     api_key="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" # This is the default and can be omitted
# )

api_router = APIRouter()

# ✅ Test Route
@api_router.get("/test")
def test_route():
    return {"message": "API is working perfectly!"}



ALLOWED_EXTENSIONS = {'pdf'}



def cleanup_files(file_paths: list[str]):
    """Background task to clean up generated files"""
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception:
            pass  # Ignore cleanup errors



def upload_to_cloudinary(file):
    """Uploads a file to Cloudinary and returns the secure URL and public ID."""
    try:
        upload_result = cloudinary.uploader.upload(
            file,
            resource_type="raw"  # Ensure PDFs are treated as raw files
        )
        print(upload_result)
        return upload_result.get("secure_url"), upload_result.get("public_id")
    except Exception as e:
        raise Exception(f"Error uploading to Cloudinary: {str(e)}")

def allowed_resume(filename):
    """Check if the uploaded file is of an allowed type."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def date_time_now():
    """Return the current date and time in a readable format."""
    now = datetime.now()
    return now.strftime("%d/%m/%Y %H:%M:%S")



# ✅ Function to Convert .tex to PDF
def convert_to_pdf(tex_filepath):
    pdf_filename = "resume.pdf"
    pdf_filepath = os.path.join(DOWNLOAD_FOLDER, pdf_filename)

    try:
        pdflatex_path = "C:\\Program Files\\MiKTeX\\miktex\\bin\\x64\\pdflatex.exe"  # Update for my  window
        subprocess.run([pdflatex_path, "-output-directory", DOWNLOAD_FOLDER, tex_filepath], check=True)
        print(f"✅ PDF successfully generated: {pdf_filepath}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error generating PDF: {e}")

    return pdf_filepath if os.path.exists(pdf_filepath) else None

# ✅ Function to Extract Work Experience
def extract_experience(latex_content):
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
    pattern = rf"{re.escape(start_marker)}(.*?){re.escape(end_marker)}"
    match = re.search(pattern, latex_content, re.DOTALL)

    return match.group(1).strip() if match else "Section not found."

# ✅ Function to Extract Technical Skills
def extract_skills(latex_content):
    start_marker_skills = r"""
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% SKILLS
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
    end_marker_skills = r"""
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% PROFESSIONAL EXPERIENCE
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
    pattern = rf"{re.escape(start_marker_skills)}(.*?){re.escape(end_marker_skills)}"
    match = re.search(pattern, latex_content, re.DOTALL)

    return match.group(1).strip() if match else "Section not found."

# ✅ Function to Modify Section with OpenAI GPT
def modify_section(section_content, job_description, section_type):
    if not section_content or not job_description:
        return section_content  # Return original if modification is not possible

    messages = [
        {"role": "system", "content": "You are an expert assistant for modifying LaTeX resumes."},
        {"role": "user", "content": (
            f"Here is the {section_type} section of a LaTeX resume: {section_content}. "
            f"Here is the job description: {job_description}. "
            "Identify key skills from the job description and integrate them into the section, ensuring they are applied in relevant contexts. "
            "Maintain bullet points, structure, and LaTeX formatting. "
            "Return only the modified LaTeX content, without explanations or introductions. "
            "DO NOT wrap the output in triple backticks (```latex). Just return the pure LaTeX code."
        )}
    ]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=1500
    )

    modified_text = response.choices[0].message.content if response.choices else "Error: No response from OpenAI"

    # ✅ Remove Markdown-style code blocks (```latex ... ```)
    modified_text = re.sub(r"```latex\n(.*?)\n```", r"\1", modified_text, flags=re.DOTALL)
    modified_text = re.sub(r"```(.*?)```", r"\1", modified_text, flags=re.DOTALL)  # Catch any remaining cases

    # ✅ Remove unwanted introductory phrases
    unwanted_phrases = [
        "Based on the job description",
        "Here is the modified",
        "Remember, the goal of a resume",
        "So in the above LaTeX code"
    ]
    for phrase in unwanted_phrases:
        modified_text = modified_text.replace(phrase, "").strip()

    return modified_text



# ✅ Function to Replace Section in LaTeX Content
def replace_section(original_content, old_section, new_section):
    return original_content.replace(old_section, new_section)

# ✅ API Endpoint to Process LaTeX File and Modify Work Experience & Skills

@api_router.post("/process_tex")
async def process_tex(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    job_description: Optional[str] = Form(None)
):
    try:
        # Read LaTeX file
        latex_content = await file.read()
        latex_content = latex_content.decode("utf-8")

        # Extract Sections
        extracted_skills = extract_skills(latex_content)
        extracted_work_experience = extract_experience(latex_content)

        # Modify Sections
        modified_work_experience = modify_section(extracted_work_experience, job_description, "work experience")
        modified_skills = modify_section(extracted_skills, job_description, "skills")

        # Replace Sections in Original LaTeX
        updated_latex = replace_section(latex_content, extracted_work_experience, modified_work_experience)
        updated_latex = replace_section(updated_latex, extracted_skills, modified_skills)

        # Save Modified LaTeX File
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        tex_filename = f"resume_{timestamp}.tex"
        modified_tex_path = os.path.join(UPLOAD_DIR, tex_filename)
        
        with open(modified_tex_path, "w", encoding="utf-8") as modified_tex:
            modified_tex.write(updated_latex)

        # Compile LaTeX to PDF
        try:

               # Get the appropriate pdflatex path
            pdflatex_path = get_pdflatex_path()
            
            # Check if pdflatex exists
            if not os.path.exists(pdflatex_path):
                raise HTTPException(
                    status_code=500,
                    detail="pdflatex not found. Please install TeX Live on Ubuntu using: sudo apt-get install texlive-full"
                )
            
            process = subprocess.run(
                [pdflatex_path, "-output-directory", UPLOAD_DIR, modified_tex_path],
                check=True,
                capture_output=True,
                text=True,
                timeout=30
            )
        
            # Get the generated PDF path
            pdf_filename = tex_filename.replace('.tex', '.pdf')
            pdf_path = os.path.join(UPLOAD_DIR, pdf_filename)
            
            if not os.path.exists(pdf_path):
                raise HTTPException(status_code=500, detail="PDF generation failed")

            # Prepare list of files to cleanup
            cleanup_file_paths = [
                os.path.join(UPLOAD_DIR, f"{os.path.splitext(tex_filename)[0]}.aux"),
                os.path.join(UPLOAD_DIR, f"{os.path.splitext(tex_filename)[0]}.log"),
                os.path.join(UPLOAD_DIR, f"{os.path.splitext(tex_filename)[0]}.out"),
                modified_tex_path,
                pdf_path  # Add PDF to cleanup after sending
            ]
            
            # Add cleanup task to background tasks
            background_tasks.add_task(cleanup_files, cleanup_file_paths)
            
            return FileResponse(
                path=pdf_path,
                filename=pdf_filename,
                media_type="application/pdf"
            )

        except subprocess.CalledProcessError as e:
            raise HTTPException(
                status_code=500,
                detail=f"LaTeX compilation failed: {e.stderr}"
            )
            
    except Exception as e:
        # Clean up any files that might have been created before the error
        if 'tex_filename' in locals():
            cleanup_paths = [
                os.path.join(UPLOAD_DIR, f"{os.path.splitext(tex_filename)[0]}.aux"),
                os.path.join(UPLOAD_DIR, f"{os.path.splitext(tex_filename)[0]}.log"),
                os.path.join(UPLOAD_DIR, f"{os.path.splitext(tex_filename)[0]}.pdf"),
                os.path.join(UPLOAD_DIR, tex_filename)
            ]
            cleanup_files(cleanup_paths)
            
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )