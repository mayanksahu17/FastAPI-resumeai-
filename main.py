from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from api import api_router

app = FastAPI(title=settings.PROJECT_NAME)

# CORS मिडलवेयर सेटअप
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# होम रूट चेक करने के लिए
@app.get("/")
def read_root():
    return {"message": "Server is up and running 🚀"}

# API राउटर इन्क्लूड करना
app.include_router(api_router, prefix=settings.API_V1_STR)
