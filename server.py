from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from api import api_router
import os
import subprocess




def install_latex():
    """
    Installs LaTeX (texlive) if not already installed.
    """
    try:
        # Check if LaTeX is installed
        subprocess.run(["pdflatex", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("LaTeX is already installed.")
    except FileNotFoundError:
        print("LaTeX is not installed. Installing now...")
        os.system("sudo apt update && sudo apt install -y texlive texlive-latex-extra texlive-fonts-recommended")
        print("LaTeX installation completed.")

def run_fastapi_server():
    """
    Runs the FastAPI server.
    """
    print("Starting FastAPI server...")
    os.system("uvicorn main:app --host 0.0.0.0 --port 8000 --reload")


if __name__ == "__main__":
    install_latex()
    run_fastapi_server()
