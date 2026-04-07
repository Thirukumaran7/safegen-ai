import os

def extract_text_from_file(file_content: bytes, filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()

    if ext == ".pdf":
        try:
            import fitz  # pymupdf
            doc = fitz.open(stream=file_content, filetype="pdf")
            text = ""
            for page in doc:
                text += page.get_text()
            return text
        except Exception as e:
            return f"PDF extraction error: {str(e)}"

    elif ext in [".docx", ".doc"]:
        try:
            import docx
            import io
            document = docx.Document(io.BytesIO(file_content))
            text = "\n".join([para.text for para in document.paragraphs])
            return text
        except Exception as e:
            return f"DOCX extraction error: {str(e)}"

    else:
        # Plain text
        try:
            return file_content.decode("utf-8")
        except:
            return file_content.decode("latin-1")