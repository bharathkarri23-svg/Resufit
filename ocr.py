import os
import platform
import fitz
from PIL import Image
import pytesseract

# Configure Tesseract path depending on platform.
if platform.system() == "Windows":
    win_tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    if os.path.exists(win_tesseract_path):
        pytesseract.pytesseract.tesseract_cmd = win_tesseract_path
else:
    # On Render/Linux, check if we have a portable static tesseract binary in the project.
    project_bin_path = os.path.join(os.path.dirname(__file__), "bin", "tesseract")
    if os.path.exists(project_bin_path):
        pytesseract.pytesseract.tesseract_cmd = project_bin_path
        # Point Tesseract to the local tessdata directory in the project
        tessdata_dir = os.path.join(os.path.dirname(__file__), "bin", "tessdata")
        os.environ["TESSDATA_PREFIX"] = tessdata_dir

def is_likely_resume(text):
    if not text:
        return False
    resume_keywords = [
        "experience", "education", "skills", "projects", "certifications",
        "linkedin", "github", "objective", "summary", "intern",
        "university", "bachelor", "master", "work", "profile",
        "contact", "email", "phone", "academic", "achievement",
        "languages", "technologies", "tools", "developer", "engineer"
    ]
    text_lower = text.lower()
    score = sum(1 for word in resume_keywords if word in text_lower)
    return score >= 3

def extract_text(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    links = []
    for page in doc:
        text += page.get_text()
        for link in page.get_links():
            if "uri" in link and link["uri"] not in links:
                links.append(link["uri"])
                
    if links:
        text += "\n\nExtracted Links:\n" + "\n".join(links)
    
    # If the text is empty or lacks resume keywords, fallback to OCR
    if not is_likely_resume(text):
        print("Scanned/empty PDF detected, falling back to OCR extraction.")
        ocr_text = ""
        for page in doc:
            pix = page.get_pixmap(dpi=150)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            ocr_text += pytesseract.image_to_string(img) + "\n"
        
        # Use OCR text if it retrieved more content
        if len(ocr_text.strip()) > len(text.strip()):
            text = ocr_text
            
    return text

def ocr_image(image_path):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return text