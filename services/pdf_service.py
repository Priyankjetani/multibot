import PyPDF2
import io


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extracts all text from a PDF file given as bytes"""
    reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text