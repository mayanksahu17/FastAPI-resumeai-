from main import app
import os
import subprocess


ALLOWED_EXTENSIONS = {'tex'}


# Function to convert .tex file to PDF using pdflatex
def convert_to_pdf(tex_file):
    pdf_filename = 'resume.pdf'
    pdf_filepath = os.path.join(app.config['DOWNLOAD_FOLDER'], pdf_filename)
    
    try:
        # Provide the full path to pdflatex
        pdflatex_path = '/Library/TeX/texbin/pdflatex'
        subprocess.run([pdflatex_path, '-output-directory', app.config['DOWNLOAD_FOLDER'], tex_file], check=True)
        print(f"PDF successfully generated: {pdf_filepath}")
    except subprocess.CalledProcessError as e:
        print(f"Error generating PDF: {e}")
    
    return pdf_filename


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
