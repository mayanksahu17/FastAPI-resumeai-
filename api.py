from fastapi import APIRouter, UploadFile, File, Form
import os
import subprocess
import re
from openai import OpenAI
from typing import Optional, Annotated
from fastapi import FastAPI, HTTPException, Query
import requests

# Constants
UPLOAD_DIR = "modified_tex"
UPLOAD_FOLDER = "uploads"
DOWNLOAD_FOLDER = "downloads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)
OPENAI_API_KEY="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"


client = OpenAI(
    api_key=OPENAI_API_KEY # This is the default and can be omitted
)
api_router = APIRouter()

# ✅ Test Route
@api_router.get("/test")
def test_route():
    return {"message": "API is working perfectly!"}

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
        model="gpt-3.5",
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
        modified_tex_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(modified_tex_path, "w", encoding="utf-8") as modified_tex:
            modified_tex.write(updated_latex)

        return {
            "message": "LaTeX file processed and modified successfully according to the job description.",
            "modified_tex_path": modified_tex_path
        }

    except Exception as e:
        return {"error": str(e)}





# ✅ API Endpoint to Compile LaTeX File from a URL
@api_router.get("/compile")
async def compile_latex(
    # url: str = Query(..., description="URL to the LaTeX (.tex) file")
    ):
    try:
        url = "https://github.com/mayanksahu17/FastAPI-resumeai-/blob/main/modified_tex/main(15).tex"
        # Define the LaTeX compilation service URL
        latex_compile_url = f"https://latexonline.cc/compile?url={url}"

        # ✅ Send request to compile LaTeX
        response =  requests.get(latex_compile_url, stream=True)
        print("response",response)

        # ✅ Handle errors from the LaTeX API
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to compile LaTeX file.")

        # ✅ Save the compiled PDF file
        pdf_filename = "compiled_resume.pdf"
        with open(pdf_filename, "wb") as pdf_file:
            for chunk in response.iter_content(chunk_size=1024):
                pdf_file.write(chunk)

        return {
            "message": "LaTeX file compiled successfully!",
            "download_url": f"http://localhost:8000/download/{pdf_filename}"
        }

    except requests.RequestException as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Request failed: {str(e)}")