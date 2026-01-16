import io
import sqlite3
import csv
import os
import logging
from typing import Callable, Dict

import pypdf
from docx import Document
from PIL import Image
import pytesseract

logger = logging.getLogger(__name__)


def extract_text_from_pdf(file_stream: io.BytesIO) -> str:
    """Extract text from a PDF file.
    
    Args:
        file_stream: BytesIO object containing PDF data
        
    Returns:
        Extracted text from all PDF pages
        
    Raises:
        ValueError: If PDF processing fails
    """
    try:
        logger.info("Extracting text from PDF")
        pdf_reader = pypdf.PdfReader(file_stream)
        text = "".join(page.extract_text() or "" for page in pdf_reader.pages)
        logger.debug(f"Successfully extracted {len(text)} characters from PDF")
        return text
    except Exception as e:
        error_message = f"PDF processing error: {str(e)}"
        logger.error(error_message)
        raise ValueError(error_message)


def extract_text_from_docx(file_stream: io.BytesIO) -> str:
    """Extract text from a DOCX file.
    
    Args:
        file_stream: BytesIO object containing DOCX data
        
    Returns:
        Extracted text from all paragraphs
        
    Raises:
        ValueError: If DOCX processing fails
    """
    try:
        logger.info("Extracting text from DOCX")
        document = Document(file_stream)
        text = "\n".join(para.text for para in document.paragraphs)
        logger.debug(f"Successfully extracted {len(text)} characters from DOCX")
        return text
    except Exception as e:
        error_message = f"DOCX processing error: {str(e)}"
        logger.error(error_message)
        raise ValueError(error_message)


def extract_text_from_txt(file_stream: io.BytesIO) -> str:
    """Extract text from a TXT file.
    
    Args:
        file_stream: BytesIO object containing text data
        
    Returns:
        Extracted text
        
    Raises:
        ValueError: If TXT processing fails
    """
    try:
        logger.info("Extracting text from TXT")
        text = file_stream.read().decode('utf-8')
        logger.debug(f"Successfully extracted {len(text)} characters from TXT")
        return text
    except Exception as e:
        error_message = f"TXT processing error: {str(e)}"
        logger.error(error_message)
        raise ValueError(error_message)


def extract_text_from_image(file_stream: io.BytesIO) -> str:
    """Extract text from an image file using OCR (Tesseract).
    
    Args:
        file_stream: BytesIO object containing image data
        
    Returns:
        Extracted text from image
        
    Raises:
        ValueError: If image processing fails or Tesseract is not installed
    """
    try:
        logger.info("Extracting text from image using OCR")
        image = Image.open(file_stream)
        text = pytesseract.image_to_string(image)
        logger.debug(f"Successfully extracted {len(text)} characters from image")
        return text
    except pytesseract.TesseractNotFoundError:
        error_message = "Tesseract OCR engine is not installed or not in your PATH"
        logger.error(error_message)
        raise ValueError(error_message)
    except Exception as e:
        error_message = f"Image processing error: {str(e)}"
        logger.error(error_message)
        raise ValueError(error_message)


def extract_text_from_csv(file_stream: io.BytesIO) -> str:
    """Extract text from a CSV file.
    
    Args:
        file_stream: BytesIO object containing CSV data
        
    Returns:
        Extracted CSV content as text
        
    Raises:
        ValueError: If CSV processing fails
    """
    try:
        logger.info("Extracting text from CSV")
        text = file_stream.read().decode('utf-8')
        logger.debug(f"Successfully extracted {len(text)} characters from CSV")
        return text
    except Exception as e:
        error_message = f"CSV processing error: {str(e)}"
        logger.error(error_message)
        raise ValueError(error_message)


def extract_text_from_sqlite(file_path: str) -> str:
    """Extract all text data from a SQLite database file.
    
    Args:
        file_path: Path to SQLite database file
        
    Returns:
        Extracted data from all tables as formatted text
        
    Raises:
        ValueError: If SQLite processing fails
    """
    try:
        logger.info(f"Extracting text from SQLite database: {file_path}")
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
        logger.debug(f"Successfully extracted {len(full_text)} characters from SQLite")
        return full_text
    except Exception as e:
        error_message = f"SQLite processing error: {str(e)}"
        logger.error(error_message)
        raise ValueError(error_message)
    finally:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.debug(f"Cleaned up temporary file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to remove temporary file {file_path}: {str(e)}")


# Mapping of file extensions to their extraction functions
FILE_EXTRACTORS: Dict[str, Callable[[io.BytesIO], str]] = {
    ".pdf": extract_text_from_pdf,
    ".docx": extract_text_from_docx,
    ".txt": extract_text_from_txt,
    ".jpg": extract_text_from_image,
    ".jpeg": extract_text_from_image,
    ".png": extract_text_from_image,
    ".csv": extract_text_from_csv,
}
