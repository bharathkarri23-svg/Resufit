# ResuFit - AI Resume Intelligence & ATS Optimizer

ResuFit is a premium, AI-powered Resume Analyzer, Job Description Matcher, and Interactive Resume Builder designed to help job seekers bypass Applicant Tracking Systems (ATS) and instantly impress recruiters. By combining modern LLM parsing, real-time keyword analysis, and dynamic layout template rendering, ResuFit shifts resume building from a guess-work chore into a streamlined, data-driven workflow.

![ResuFit Dashboard Mockup](resufit_mockup.png)

---

## 🚀 Key Features

* **AI-Powered ATS Score Analysis**: Extracts layout nodes, text flow, and structure to grade your resume on readability, formatting, and keyword density.
* **Smart Job Description Matcher**: Paste your target job description to run a direct gap analysis. Isolate matched and missing industry-specific keywords, and receive tailored certification recommendations.
* **Interactive Resume Builder Wizard**: Step-by-step wizard to build a clean, A4 single-page resume with character-by-character live typing previews.
* **Multi-Template Layout Gallery**: Instantly toggle between **8 distinct professional templates** (Slate, Modern Corporate, Executive Minimalist, Monospace, Academic, etc.) and see formatting update in real-time.
* **Instant Resume Tailoring**: Leverage Llama 3 / 3.3 models via Groq to rewrite professional summaries and experience bullet points to match your target job description automatically.
* **Scanned Resume OCR Fallback**: Integrated OCR parser using PyMuPDF and Tesseract to extract readable text even from image-only scan PDFs.

---

## 🛠️ Tech Stack

* **Backend Framework**: Python 3.13 / Flask
* **Artificial Intelligence**: Groq API (Llama-3.3-70b-versatile, Llama-3.1-8b-instant)
* **Text & Image Parsing (OCR)**: PyMuPDF (fitz), Pillow (PIL), and Tesseract OCR
* **Frontend**: HTML5, Vanilla CSS3 (modern glassmorphic styling, CSS Grid, Flexbox, custom variables), and Vanilla JavaScript
* **Database**: SQLite3 (user records, session caching)
* **Video/Automation Testing**: Playwright (Python implementation)

---

## 📦 Installation & Setup

Follow these steps to run ResuFit locally on your machine:

### 1. Prerequisites
Ensure you have **Python 3.13+** installed. If you plan on using the scanned OCR fallback, download and install [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) and ensure it is added to your environment path.

### 2. Clone & Setup Environment
Open your shell in the project folder and create a virtual environment:
```powershell
python -m venv env
.\env\Scripts\activate
```

### 3. Install Dependencies
Install all the required python libraries listed in `requirements.txt`:
```powershell
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a file named `.env` in the root directory and configure your keys:
```env
secret_key = YourFlaskSecretKey
groq_api_key = YourGroqApiKeyHere
OAUTHLIB_INSECURE_TRANSPORT = 1

# Email credentials for verification (optional)
EMAIL_USER = your_email@gmail.com
EMAIL_PASS = your_email_app_password

# Google OAuth credentials (optional)
client_id = your_google_client_id
project_id = your_google_project_id
auth_uri = https://accounts.google.com/o/oauth2/auth
token_uri = https://oauth2.googleapis.com/token
auth_provider_x509_cert_url = https://www.googleapis.com/oauth2/v1/certs
client_secret = your_google_client_secret
redirect_uri = http://localhost:5000/callback
```

### 5. Launch the Server
Start the Flask application:
```powershell
python app.py
```
Open your browser and navigate to `http://localhost:5000` to access the application.

---

## 📖 How to Use Guide

1. **Scan Your Current Resume**: Click "Choose File" on the Landing Page simulator or click "Sign In" (credentials: `test@example.com` / `Password123!`) to open the main **Dashboard**. Upload a PDF to view your ATS score, strengths, and suggestions.
2. **Scan Job Description Gaps**: Navigate to the **Job Fit Analysis** tab, paste the target job description, select your resume file, and click "Submit". Review missing keywords and recommendations.
3. **Build from Scratch**: Go to the **Resume Builder** tab and click "Create New Resume". Use the step-by-step wizard on the left. Watch the A4 template preview on the right update dynamically as you type.
4. **Tailor to Job Description**: In the builder finish tab, paste a job description into the tailoring input box and click "Tailor Resume". The AI will rewrite achievements and descriptions directly in the live A4 preview.
5. **Cycle Templates**: Use the layout selector sidebar to cycle between Templates 1 to 8 to find the visual format that fits your industry.

---

## 🎥 Video Walkthrough Demo

A full-screen, high-definition (Full HD, 1080p, High-DPI) video demo of the entire application workflow has been recorded using Playwright automation. It showcases the landing page scrolling, user login, ATS score analysis, Job Fit comparison, builder typing animations, and template cycles.

* **File Location**: `resufit_walkthrough.webm` in the project root folder.
* **Previewing**: Double-click [resufit_walkthrough.webm](resufit_walkthrough.webm) or open it in a compatible browser/media player (such as Windows Media Player or VLC) to watch the walkthrough.


