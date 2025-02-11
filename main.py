from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from api import api_router
import os
import subprocess
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
app = FastAPI(title=settings.PROJECT_NAME)

templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

app.include_router(api_router, prefix=settings.API_V1_STR)
