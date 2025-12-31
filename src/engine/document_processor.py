"""
Document processor for Logos.

This module provides text extraction and document processing capabilities
for various file formats, enabling Logos to build knowledge from documents.
Adapted from fellow project's modular text extraction system.
"""

import io
import mimetypes
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

from ..logging_config import get_logger

logger = get_logger(__name__)


class DocumentProcessorError(Exception):
    """Base exception for document processing errors."""


class BaseTextExtractor(ABC):
    """
    Abstract base class for text extractors.
    Simplified version focused on Logos requirements.
    """

    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)

    @abstractmethod
    def extract_text(self, content: bytes) -> str:
        """
        Extract text from file content.

        Args:
            content: Raw file content as bytes

        Returns:
            Extracted text as string

        Raises:
            DocumentProcessorError: If extraction fails
        """

    def get_supported_formats(self) -> List[str]:
        """Get supported file formats for this extractor."""
        return []

    def clean_text(self, text: str) -> str:
        """Clean extracted text."""
        if text is None:
            return ""

        # Replace NULL bytes with spaces
        text = text.replace('\x00', ' ').replace('\u0000', ' ')

        # Remove other control characters (except newlines and tabs)
        text = ''.join(c if (ord(c) >= 32 or c in '\n\t\r') else ' ' for c in text)

        # Normalize whitespace
        import re
        text = re.sub(r'\s+', ' ', text).strip()

        return text


class PlainTextExtractor(BaseTextExtractor):
    """Text extractor for plain text files."""

    def extract_text(self, content: bytes) -> str:
        """Extract text from plain text content."""
        try:
            # Try UTF-8 first
            text = content.decode('utf-8', errors='replace')
            return self.clean_text(text)
        except Exception as e:
            raise DocumentProcessorError(f"Plain text extraction failed: {str(e)}")

    def get_supported_formats(self) -> List[str]:
        return ["TXT", "CSV", "MD"]


class PDFTextExtractor(BaseTextExtractor):
    """Text extractor for PDF files."""

    def __init__(self):
        super().__init__()
        self._pdfplumber_available = False
        self._pypdf_available = False
        try:
            import pdfplumber
            self._pdfplumber_available = True
        except ImportError:
            pass
        try:
            import pypdf
            self._pypdf_available = True
        except ImportError:
            pass

    def extract_text(self, content: bytes) -> str:
        """Extract text from PDF content."""
        if self._pdfplumber_available:
            return self._extract_with_pdfplumber(content)
        elif self._pypdf_available:
            return self._extract_with_pypdf(content)
        else:
            raise DocumentProcessorError("PDF extraction requires pdfplumber or pypdf")

    def _extract_with_pdfplumber(self, content: bytes) -> str:
        """Extract text using pdfplumber."""
        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                return self.clean_text(text)
        except Exception as e:
            raise DocumentProcessorError(f"pdfplumber extraction failed: {str(e)}")

    def _extract_with_pypdf(self, content: bytes) -> str:
        """Extract text using pypdf."""
        try:
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(content))
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            return self.clean_text(text)
        except Exception as e:
            raise DocumentProcessorError(f"pypdf extraction failed: {str(e)}")

    def get_supported_formats(self) -> List[str]:
        return ["PDF"]


class DOCXTextExtractor(BaseTextExtractor):
    """Text extractor for DOCX files."""

    def __init__(self):
        super().__init__()
        self._docx_available = False
        try:
            import docx
            self._docx_available = True
        except ImportError:
            pass

    def extract_text(self, content: bytes) -> str:
        """Extract text from DOCX content."""
        if not self._docx_available:
            raise DocumentProcessorError("DOCX extraction requires python-docx")

        try:
            import docx
            from io import BytesIO

            doc = docx.Document(BytesIO(content))
            text = ""
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text += paragraph.text + "\n"
            return self.clean_text(text)
        except Exception as e:
            raise DocumentProcessorError(f"DOCX extraction failed: {str(e)}")

    def get_supported_formats(self) -> List[str]:
        return ["DOCX"]


class HTMLTextExtractor(BaseTextExtractor):
    """Text extractor for HTML files."""

    def __init__(self):
        super().__init__()
        self._bs4_available = False
        try:
            import bs4
            self._bs4_available = True
        except ImportError:
            pass

    def extract_text(self, content: bytes) -> str:
        """Extract text from HTML content."""
        if not self._bs4_available:
            raise DocumentProcessorError("HTML extraction requires beautifulsoup4")

        try:
            from bs4 import BeautifulSoup

            html = content.decode('utf-8', errors='ignore')
            soup = BeautifulSoup(html, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            text = soup.get_text(separator='\n')
            return self.clean_text(text)
        except Exception as e:
            raise DocumentProcessorError(f"HTML extraction failed: {str(e)}")

    def get_supported_formats(self) -> List[str]:
        return ["HTML", "HTM"]


class DocumentProcessorRegistry:
    """Registry for managing document processors."""

    def __init__(self):
        self._extractors: Dict[str, BaseTextExtractor] = {}
        self._register_extractors()

    def _register_extractors(self):
        """Register all available extractors."""
        extractors = [
            (PlainTextExtractor(), ["TXT", "CSV", "MD"]),
            (PDFTextExtractor(), ["PDF"]),
            (DOCXTextExtractor(), ["DOCX"]),
            (HTMLTextExtractor(), ["HTML", "HTM"]),
        ]

        for extractor, formats in extractors:
            for fmt in formats:
                try:
                    self._extractors[fmt.upper()] = extractor
                    logger.debug(f"Registered extractor for {fmt}")
                except Exception as e:
                    logger.warning(f"Failed to register {fmt} extractor: {str(e)}")

    def get_extractor(self, file_format: str) -> Optional[BaseTextExtractor]:
        """Get extractor for file format."""
        return self._extractors.get(file_format.upper())

    def get_supported_formats(self) -> List[str]:
        """Get all supported formats."""
        return list(self._extractors.keys())

    def is_supported(self, file_format: str) -> bool:
        """Check if format is supported."""
        return file_format.upper() in self._extractors


@dataclass
class DocumentMetadata:
    """Metadata for processed documents."""
    filename: str
    file_format: str
    mimetype: str
    size_bytes: int
    text_length: int
    processing_timestamp: str
    checksum: Optional[str] = None


class DocumentProcessor:
    """
    Main document processor for Logos.

    Handles file format detection, text extraction, and document processing
    for building knowledge bases from various file types.
    """

    def __init__(self):
        self.registry = DocumentProcessorRegistry()
        logger.info(f"Document processor initialized with formats: {', '.join(sorted(self.registry.get_supported_formats()))}")

    def detect_file_format(self, filename: str, mimetype: Optional[str] = None) -> str:
        """
        Detect file format from filename and mimetype.

        Args:
            filename: Name of the file
            mimetype: MIME type if available

        Returns:
            Detected file format (e.g., 'PDF', 'DOCX', 'TXT')
        """
        # Get extension
        path = Path(filename)
        extension = path.suffix.lower().lstrip('.') if path.suffix else ""

        # Try to detect by mimetype first
        if mimetype:
            if mimetype.startswith('application/pdf'):
                return "PDF"
            elif mimetype.startswith('application/vnd.openxmlformats-officedocument.wordprocessingml.document'):
                return "DOCX"
            elif mimetype.startswith('text/html'):
                return "HTML"
            elif mimetype.startswith('text/plain'):
                return "TXT"

        # Fall back to extension
        if extension in ['pdf']:
            return "PDF"
        elif extension in ['docx']:
            return "DOCX"
        elif extension in ['doc']:
            return "DOC"
        elif extension in ['html', 'htm']:
            return "HTML"
        elif extension in ['txt', 'md', 'csv']:
            return "TXT"
        elif extension in ['xlsx', 'xls']:
            return "XLSX"
        elif extension in ['pptx']:
            return "PPTX"
        elif extension in ['odt']:
            return "ODT"
        elif extension in ['rtf']:
            return "RTF"
        elif extension in ['msg']:
            return "MSG"
        else:
            return "BINARY"

    def extract_text(self, content: bytes, file_format: str) -> str:
        """
        Extract text from file content.

        Args:
            content: Raw file content as bytes
            file_format: File format (PDF, DOCX, etc.)

        Returns:
            Extracted text

        Raises:
            DocumentProcessorError: If extraction fails
        """
        extractor = self.registry.get_extractor(file_format)
        if not extractor:
            raise DocumentProcessorError(f"No extractor available for format: {file_format}")

        try:
            text = extractor.extract_text(content)
            logger.info(f"Extracted {len(text)} characters from {file_format}")
            return text
        except Exception as e:
            logger.error(f"Text extraction failed for {file_format}: {str(e)}")
            raise DocumentProcessorError(f"Failed to extract text from {file_format}: {str(e)}")

    def process_document(self, content: bytes, filename: str, mimetype: Optional[str] = None) -> tuple[str, DocumentMetadata]:
        """
        Process a document and return extracted text with metadata.

        Args:
            content: Raw file content as bytes
            filename: Original filename
            mimetype: MIME type if known

        Returns:
            Tuple of (extracted_text, metadata)

        Raises:
            DocumentProcessorError: If processing fails
        """
        import hashlib
        from datetime import datetime, timezone

        # Detect format
        file_format = self.detect_file_format(filename, mimetype)

        # Calculate checksum
        checksum = hashlib.md5(content).hexdigest()

        # Extract text
        text = self.extract_text(content, file_format)

        # Create metadata
        metadata = DocumentMetadata(
            filename=filename,
            file_format=file_format,
            mimetype=mimetype or mimetypes.guess_type(filename)[0] or "application/octet-stream",
            size_bytes=len(content),
            text_length=len(text),
            processing_timestamp=datetime.now(timezone.utc).isoformat(),
            checksum=checksum
        )

        return text, metadata

    def get_supported_formats(self) -> List[str]:
        """Get list of supported file formats."""
        return self.registry.get_supported_formats()

    def is_format_supported(self, file_format: str) -> bool:
        """Check if a file format is supported."""
        return self.registry.is_supported(file_format)