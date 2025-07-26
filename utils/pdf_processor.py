import PyPDF2
from io import BytesIO

def extract_text_from_pdf(pdf_file):
    """
    Extract text content from uploaded PDF file
    """
    try:
        # Read the PDF file
        pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_file.read()))
        
        # Extract text from all pages
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        return text.strip()
    
    except Exception as e:
        raise Exception(f"Failed to process PDF: {str(e)}")
