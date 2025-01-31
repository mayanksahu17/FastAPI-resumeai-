# Resume Optimizer using GPT-4o and LaTeX

## 📌 Project Overview

This project aims to generate **highly specific** and **ATS-optimized** resumes by processing a **LaTeX (.tex) resume template** and a given **job description**. The system ensures that the final resume follows the blueprint structure while aligning the content with job requirements using **GPT-4o**.

## 🏗️ Architecture Overview

1. **User Uploads**
   - A LaTeX (.tex) file (Resume Template)
   - A Job Description (Text format)
2. **Processing Layer**
   - **LaTeX Parser**: Extracts fields and structure.
   - **Job Description Analyzer** (GPT-4o): Extracts relevant skills & experience.
   - **Resume Generator** (GPT-4o): Adjusts content while keeping LaTeX structure intact.
3. **Resume Compilation**
   - Generates a `.tex` file with updated content.
   - Compiles it into a **PDF format**.
4. **Final Output**
   - Allows preview and download of the generated resume.

## 🚀 Tech Stack

- **Backend**: FastAPI (Python), GPT-4o API
- **Frontend**: Next.js (React.js)
- **Database**: PostgreSQL / MongoDB
- **LaTeX Processing**: pdflatex / Overleaf API

## 📂 Project Structure

```
project_root/
├── app/
│   ├── main.py  # FastAPI Application Entry Point
│   ├── core/  # Config and Security Modules
│   ├── api/  # API Endpoints
│   ├── models/  # Database Models
│   ├── schemas/  # Pydantic Schemas
│   ├── services/  # Business Logic
├── tests/  # Unit Tests
├── .env  # Environment Variables
├── requirements.txt  # Python Dependencies
├── README.md  # Project Documentation
```

## 🔧 Installation & Setup

1. **Clone the Repository**

   ```bash
   git clone <repo-url>
   cd project_root
   ```

2. **Create a Virtual Environment** (Optional but Recommended)

   ```bash
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   venv\Scripts\activate  # On Windows
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**

   - Rename `.env.example` to `.env`
   - Add your GPT-4o API key and database credentials

5. **Run the FastAPI Server**

   ```bash
   uvicorn app.main:app --reloadResume Optimizer using GPT-4o and LaTeX

   📌 Project Overview

   This project aims to generate highly specific and ATS-optimized resumes by processing a LaTeX (.tex) resume template and a given job description. The system ensures that the final resume follows the blueprint structure while aligning the content with job requirements using GPT-4o.

   🏗️ Architecture Overview

   User Uploads

   A LaTeX (.tex) file (Resume Template)

   A Job Description (Text format)

   Processing Layer

   LaTeX Parser: Extracts fields and structure.

   Job Description Analyzer (GPT-4o): Extracts relevant skills & experience.

   Resume Generator (GPT-4o): Adjusts content while keeping LaTeX structure intact.

   Resume Compilation

   Generates a .tex file with updated content.

   Compiles it into a PDF format.

   Final Output

   Allows preview and download of the generated resume.

   🚀 Tech Stack

   Backend: FastAPI (Python), GPT-4o API

   Frontend: Next.js (React.js)

   Database: PostgreSQL / MongoDB

   LaTeX Processing: pdflatex / Overleaf API

   📂 Project Structure

   project_root/
   ├── app/
   │   ├── main.py  # FastAPI Application Entry Point
   │   ├── core/  # Config and Security Modules
   │   ├── api/  # API Endpoints
   │   ├── models/  # Database Models
   │   ├── schemas/  # Pydantic Schemas
   │   ├── services/  # Business Logic
   ├── tests/  # Unit Tests
   ├── .env  # Environment Variables
   ├── requirements.txt  # Python Dependencies
   ├── README.md  # Project Documentation

   🔧 Installation & Setup

   Clone the Repository

   git clone <repo-url>
   cd project_root

   Create a Virtual Environment (Optional but Recommended)

   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   venv\Scripts\activate  # On Windows

   Install Dependencies

   pip install -r requirements.txt

   Set Up Environment Variables

   Rename .env.example to .env

   Add your GPT-4o API key and database credentials

   Run the FastAPI Server

   uvicorn app.main:app --reload

   Access API Docs

   Open http://127.0.0.1:8000/docs in your browser.

   📌 Features

   ✅ Upload LaTeX resume template & job description✅ GPT-4o-powered resume transformation✅ Preserves LaTeX formatting✅ Generates ATS-friendly resumes
   ```

6. **Access API Docs**

   - Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) in your browser.

## 📌 Features

✅ Upload **LaTeX resume template** & **job description**\
✅ **GPT-4o-powered** resume transformation\
✅ **Preserves LaTeX formatting**\
✅ Generates **ATS-friendly** resumes\
✅ Provides **LaTeX & PDF output**\
✅ **FastAPI-powered backend** for scalability

## 🤝 Contributions

Feel free to fork this repository and contribute! Open a PR if you have improvements.

## 📜 License

MIT License. See `LICENSE` for details.

