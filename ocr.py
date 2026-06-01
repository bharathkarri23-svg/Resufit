import fitz
from PIL import Image
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

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