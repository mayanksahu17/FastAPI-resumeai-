from pydantic_settings import BaseSettings
from functools import lru_cache
import cloudinary
import cloudinary.uploader
import os
from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks, HTTPException
import platform
from openai import OpenAI



OPENAI_API_KEY="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"
CLOUD_NAME="doubpsp9q"
API_KEY="718428216941339"
API_SECRET="4_jbo9QF5j42ogVf-laaPh4y-zE"
DEEPSEEK_API_KEY="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"
DEEPSEEK_BASE_URL="https://openrouter.ai/api/v1"


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "FastAPI Server"

@lru_cache()
def get_settings():
    return Settings()




def get_pdflatex_path():
    """Get the appropriate pdflatex path based on the operating system"""
    system = platform.system().lower()
    
    if system == "windows":
        return "C:\\Program Files\\MiKTeX\\miktex\\bin\\x64\\pdflatex.exe"
    elif system == "linux":
        return "/usr/bin/pdflatex"  # Standard path on Ubuntu
    else:
        raise HTTPException(
            status_code=500,
            detail=f"Unsupported operating system: {system}"
        )
    
# Configure Cloudinary
cloudinary.config(
    cloud_name=CLOUD_NAME,
    api_key=API_KEY,
    api_secret=API_SECRET,
    secure=True
)

client = OpenAI(
            base_url=DEEPSEEK_BASE_URL,
    api_key=DEEPSEEK_API_KEY # This is the default and can be omitted
)

settings = get_settings()
