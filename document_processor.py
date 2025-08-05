# document_processor.py
import io
import sqlite3
import csv
import os
from fastapi import HTTPException

import pypdf
from docx import Document
from PIL import Image
import pytesseract

def extract_text_from_pdf(file_stream: io.BytesIO) -> str:
    """Extracts text from a PDF file."""
    try:
        pdf_reader = pypdf.PdfReader(file_stream)
        text = "".join(page.extract_text() or "" for page in pdf_reader.pages)
        return text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF processing error: {e}")

def extract_text_from_docx(file_stream: io.BytesIO) -> str:
    """Extracts text from a DOCX file."""
    try:
        document = Document(file_stream)
        text = "\n".join(para.text for para in document.paragraphs)
        return text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DOCX processing error: {e}")

def extract_text_from_txt(file_stream: io.BytesIO) -> str:
    """Extracts text from a TXT file."""
    try:
        return file_stream.read().decode('utf-8')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TXT processing error: {e}")

def extract_text_from_image(file_stream: io.BytesIO) -> str:
    """Extracts text from an image file using OCR (Tesseract)."""
    try:
        image = Image.open(file_stream)
        text = pytesseract.image_to_string(image)
        return text
    except pytesseract.TesseractNotFoundError:
        raise HTTPException(status_code=500, detail="Tesseract OCR engine is not installed or not in your PATH.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image processing error: {e}")

def extract_text_from_csv(file_stream: io.BytesIO) -> str:
    """Extracts text from a CSV file."""
    try:
        return file_stream.read().decode('utf-8')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CSV processing error: {e}")

def extract_text_from_sqlite(file_path: str) -> str:
    """Extracts all text data from a SQLite database file."""
    try:
        conn = sqlite3.connect(file_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        full_text = ""
        for table_name in tables:
            table_name = table_name[0]
            full_text += f"Table '{table_name}':\n"
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            col_names = [description[0] for description in cursor.description]
            
            writer = io.StringIO()
            csv_writer = csv.writer(writer)
            csv_writer.writerow(col_names)
            csv_writer.writerows(rows)
            full_text += writer.getvalue() + "\n\n"
            
        conn.close()
        return full_text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SQLite processing error: {e}")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

FILE_EXTRACTORS = {
    ".pdf": extract_text_from_pdf,
    ".docx": extract_text_from_docx,
    ".txt": extract_text_from_txt,
    ".jpg": extract_text_from_image,
    ".jpeg": extract_text_from_image,
    ".png": extract_text_from_image,
    ".csv": extract_text_from_csv,
}