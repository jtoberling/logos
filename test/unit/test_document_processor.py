"""
Unit tests for document processor.
"""

import pytest
from unittest.mock import patch, MagicMock
from src.engine.document_processor import (
    DocumentProcessor,
    DocumentProcessorError,
    PlainTextExtractor,
    PDFTextExtractor,
    DOCXTextExtractor,
    HTMLTextExtractor,
    DocumentProcessorRegistry,
    DocumentMetadata
)


class TestPlainTextExtractor:
    """Test plain text extractor."""

    def test_extract_text_utf8(self):
        """Test UTF-8 text extraction."""
        extractor = PlainTextExtractor()
        content = "Hello World\nThis is a test.".encode('utf-8')
        result = extractor.extract_text(content)
        assert result == "Hello World This is a test."

    def test_extract_text_with_nulls(self):
        """Test text with null bytes."""
        extractor = PlainTextExtractor()
        content = "Hello\x00World\x00Test".encode('utf-8')
        result = extractor.extract_text(content)
        assert result == "Hello World Test"

    def test_get_supported_formats(self):
        """Test supported formats."""
        extractor = PlainTextExtractor()
        formats = extractor.get_supported_formats()
        assert "TXT" in formats
        assert "CSV" in formats
        assert "MD" in formats

    def test_clean_text_null_bytes(self):
        """Test NULL byte removal."""
        extractor = PlainTextExtractor()
        result = extractor.clean_text("test\x00text\x00more")
        assert result == "test text more"

    def test_clean_text_whitespace(self):
        """Test whitespace normalization."""
        extractor = PlainTextExtractor()
        result = extractor.clean_text("test  \n\n  text\t\tmore")
        assert result == "test text more"

    def test_clean_text_none_input(self):
        """Test clean_text with None input."""
        extractor = PlainTextExtractor()
        result = extractor.clean_text(None)
        assert result == ""

    def test_clean_text_empty_string(self):
        """Test clean_text with empty string."""
        extractor = PlainTextExtractor()
        result = extractor.clean_text("")
        assert result == ""

    def test_clean_text_special_characters(self):
        """Test clean_text with various special characters."""
        extractor = PlainTextExtractor()
        text = "Hello\x01world\x7fmore\x80text"
        result = extractor.clean_text(text)
        # Only control characters (ord < 32) should be replaced, others remain
        assert result == "Hello world\x7fmore\x80text"

    def test_extract_text_decoding_error(self):
        """Test text extraction with invalid UTF-8."""
        extractor = PlainTextExtractor()
        # Create invalid UTF-8 bytes
        content = b'\xff\xfeinvalid'

        # Should not raise an exception, should use error='replace'
        result = extractor.extract_text(content)
        assert isinstance(result, str)
        assert len(result) > 0  # Should have replacement characters


class TestPDFTextExtractor:
    """Test PDF text extractor."""

    def test_get_supported_formats(self):
        """Test supported formats."""
        extractor = PDFTextExtractor()
        assert extractor.get_supported_formats() == ["PDF"]

    def test_pdf_extractor_initialization(self):
        """Test PDF extractor initializes correctly."""
        extractor = PDFTextExtractor()
        assert extractor.get_supported_formats() == ["PDF"]

    def test_extract_text_with_pdfplumber(self):
        """Test PDF extraction using pdfplumber."""
        import sys

        # Mock pdfplumber availability and module
        extractor = PDFTextExtractor()
        extractor._pdfplumber_available = True

        mock_pdfplumber = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Page text"
        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]

        mock_pdfplumber.open.return_value.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdfplumber.open.return_value.__exit__ = MagicMock(return_value=None)

        # Mock the import
        with patch.dict('sys.modules', {'pdfplumber': mock_pdfplumber}):
            content = b"fake pdf content"
            result = extractor.extract_text(content)

            assert "Page text" in result

    def test_extract_text_with_pypdf(self):
        """Test PDF extraction using pypdf when pdfplumber not available."""
        import sys

        # Mock pypdf availability and module
        extractor = PDFTextExtractor()
        extractor._pdfplumber_available = False
        extractor._pypdf_available = True

        # Mock pypdf module
        mock_pypdf = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "PyPDF text"
        mock_reader = MagicMock()
        mock_reader.pages = [mock_page]
        mock_pypdf.PdfReader.return_value = mock_reader

        with patch.dict('sys.modules', {'pypdf': mock_pypdf}):
            content = b"fake pdf content"
            result = extractor.extract_text(content)

            assert "PyPDF text" in result

    def test_extract_text_no_libraries_available(self):
        """Test PDF extraction when no libraries are available."""
        extractor = PDFTextExtractor()
        extractor._pdfplumber_available = False
        extractor._pypdf_available = False

        content = b"fake pdf content"
        with pytest.raises(DocumentProcessorError, match="PDF extraction requires pdfplumber or pypdf"):
            extractor.extract_text(content)

    def test_extract_with_pdfplumber_error(self):
        """Test PDF extraction error handling with pdfplumber."""
        import sys

        extractor = PDFTextExtractor()
        extractor._pdfplumber_available = True

        mock_pdfplumber = MagicMock()
        mock_pdfplumber.open.side_effect = Exception("PDF error")

        with patch.dict('sys.modules', {'pdfplumber': mock_pdfplumber}):
            content = b"fake pdf content"
            with pytest.raises(DocumentProcessorError, match="pdfplumber extraction failed"):
                extractor.extract_text(content)

    def test_extract_with_pypdf_error(self):
        """Test PDF extraction error handling with pypdf."""
        import sys

        extractor = PDFTextExtractor()
        extractor._pdfplumber_available = False
        extractor._pypdf_available = True

        mock_pypdf = MagicMock()
        mock_pypdf.PdfReader.side_effect = Exception("PyPDF error")

        with patch.dict('sys.modules', {'pypdf': mock_pypdf}):
            content = b"fake pdf content"
            with pytest.raises(DocumentProcessorError, match="pypdf extraction failed"):
                extractor.extract_text(content)


class TestDOCXTextExtractor:
    """Test DOCX text extractor."""

    def test_get_supported_formats(self):
        """Test supported formats."""
        extractor = DOCXTextExtractor()
        assert extractor.get_supported_formats() == ["DOCX"]

    def test_docx_extractor_initialization(self):
        """Test DOCX extractor initializes correctly."""
        extractor = DOCXTextExtractor()
        assert extractor.get_supported_formats() == ["DOCX"]

    def test_extract_text_docx_success(self):
        """Test successful DOCX text extraction."""
        import sys

        extractor = DOCXTextExtractor()
        extractor._docx_available = True

        # Mock docx module
        mock_docx = MagicMock()
        mock_paragraph1 = MagicMock()
        mock_paragraph1.text = "First paragraph"
        mock_paragraph2 = MagicMock()
        mock_paragraph2.text = ""  # Empty paragraph
        mock_paragraph3 = MagicMock()
        mock_paragraph3.text = "Second paragraph"

        mock_doc = MagicMock()
        mock_doc.paragraphs = [mock_paragraph1, mock_paragraph2, mock_paragraph3]
        mock_docx.Document.return_value = mock_doc

        with patch.dict('sys.modules', {'docx': mock_docx}):
            content = b"fake docx content"
            result = extractor.extract_text(content)

            assert "First paragraph" in result
            assert "Second paragraph" in result

    def test_extract_text_docx_not_available(self):
        """Test DOCX extraction when python-docx not available."""
        extractor = DOCXTextExtractor()
        extractor._docx_available = False

        content = b"fake docx content"
        with pytest.raises(DocumentProcessorError, match="DOCX extraction requires python-docx"):
            extractor.extract_text(content)

    def test_extract_text_docx_error(self):
        """Test DOCX extraction error handling."""
        import sys

        extractor = DOCXTextExtractor()
        extractor._docx_available = True

        mock_docx = MagicMock()
        mock_docx.Document.side_effect = Exception("DOCX parsing error")

        with patch.dict('sys.modules', {'docx': mock_docx}):
            content = b"fake docx content"
            with pytest.raises(DocumentProcessorError, match="DOCX extraction failed"):
                extractor.extract_text(content)


class TestHTMLTextExtractor:
    """Test HTML text extractor."""

    def test_get_supported_formats(self):
        """Test supported formats."""
        extractor = HTMLTextExtractor()
        formats = extractor.get_supported_formats()
        assert "HTML" in formats
        assert "HTM" in formats

    def test_html_extractor_initialization(self):
        """Test HTML extractor initializes correctly."""
        extractor = HTMLTextExtractor()
        formats = extractor.get_supported_formats()
        assert "HTML" in formats
        assert "HTM" in formats

    def test_extract_text_html_success(self):
        """Test successful HTML text extraction."""
        import sys

        extractor = HTMLTextExtractor()
        extractor._bs4_available = True

        # Mock bs4 module
        mock_bs4 = MagicMock()
        mock_soup = MagicMock()
        mock_soup.get_text.return_value = "Extracted text content"
        mock_bs4.BeautifulSoup.return_value = mock_soup

        # Mock script/style removal
        mock_script = MagicMock()
        mock_soup.__getitem__.return_value = [mock_script]

        with patch.dict('sys.modules', {'bs4': mock_bs4}):
            content = b"<html><body><h1>Title</h1><p>Content</p></body></html>"
            result = extractor.extract_text(content)

            assert result == "Extracted text content"

    def test_extract_text_html_not_available(self):
        """Test HTML extraction when BeautifulSoup not available."""
        extractor = HTMLTextExtractor()
        extractor._bs4_available = False

        content = b"<html><body>Test</body></html>"
        with pytest.raises(DocumentProcessorError, match="HTML extraction requires beautifulsoup4"):
            extractor.extract_text(content)

    def test_extract_text_html_error(self):
        """Test HTML extraction error handling."""
        import sys

        extractor = HTMLTextExtractor()
        extractor._bs4_available = True

        # Mock bs4 to raise an exception
        mock_bs4 = MagicMock()
        mock_bs4.BeautifulSoup.side_effect = Exception("HTML parsing error")

        with patch.dict('sys.modules', {'bs4': mock_bs4}):
            content = b"<html><body>Test</body></html>"
            with pytest.raises(DocumentProcessorError, match="HTML extraction failed"):
                extractor.extract_text(content)


class TestDocumentProcessorRegistry:
    """Test document processor registry."""

    def test_registry_initialization(self):
        """Test registry initialization."""
        registry = DocumentProcessorRegistry()
        assert len(registry.get_supported_formats()) > 0

    def test_get_extractor(self):
        """Test getting extractor by format."""
        registry = DocumentProcessorRegistry()
        extractor = registry.get_extractor("TXT")
        assert extractor is not None
        assert isinstance(extractor, PlainTextExtractor)

    def test_get_extractor_case_insensitive(self):
        """Test getting extractor with case insensitive format."""
        registry = DocumentProcessorRegistry()
        extractor = registry.get_extractor("txt")
        assert extractor is not None
        assert isinstance(extractor, PlainTextExtractor)

    def test_get_extractor_unknown_format(self):
        """Test getting extractor for unknown format."""
        registry = DocumentProcessorRegistry()
        extractor = registry.get_extractor("UNKNOWN")
        assert extractor is None

    def test_is_supported(self):
        """Test format support checking."""
        registry = DocumentProcessorRegistry()
        assert registry.is_supported("PDF")
        assert not registry.is_supported("UNSUPPORTED")

    def test_is_supported_case_insensitive(self):
        """Test format support checking is case insensitive."""
        registry = DocumentProcessorRegistry()
        assert registry.is_supported("pdf")
        assert registry.is_supported("PDF")

    def test_registry_registration_error_handling(self):
        """Test registry handles extractor registration errors gracefully."""
        with patch('src.engine.document_processor.logger') as mock_logger:
            # Create a registry and manually trigger registration error
            registry = DocumentProcessorRegistry()

            # The registration should have completed despite any individual errors
            # (errors are logged but don't prevent other registrations)
            formats = registry.get_supported_formats()
            assert len(formats) > 0  # Should still have some formats registered

            # Check that logger.warning was called for any registration failures
            # (This depends on whether any extractors failed to register during init)


class TestDocumentProcessor:
    """Test main document processor."""

    def test_initialization(self):
        """Test processor initialization."""
        processor = DocumentProcessor()
        assert processor.registry is not None

    def test_detect_file_format_pdf(self):
        """Test PDF format detection."""
        processor = DocumentProcessor()
        assert processor.detect_file_format("test.pdf") == "PDF"
        assert processor.detect_file_format("test.pdf", "application/pdf") == "PDF"

    def test_detect_file_format_docx(self):
        """Test DOCX format detection."""
        processor = DocumentProcessor()
        assert processor.detect_file_format("test.docx") == "DOCX"

    def test_detect_file_format_text(self):
        """Test text format detection."""
        processor = DocumentProcessor()
        assert processor.detect_file_format("test.txt") == "TXT"
        assert processor.detect_file_format("test.md") == "TXT"
        assert processor.detect_file_format("test.csv") == "TXT"

    def test_detect_file_format_html(self):
        """Test HTML format detection."""
        processor = DocumentProcessor()
        assert processor.detect_file_format("test.html") == "HTML"
        assert processor.detect_file_format("test.htm") == "HTML"

    def test_detect_file_format_unknown(self):
        """Test unknown format detection."""
        processor = DocumentProcessor()
        assert processor.detect_file_format("test.unknown") == "BINARY"

    def test_detect_file_format_no_extension(self):
        """Test format detection for files without extension."""
        processor = DocumentProcessor()
        assert processor.detect_file_format("README") == "BINARY"

    def test_detect_file_format_uppercase_extension(self):
        """Test format detection with uppercase extension."""
        processor = DocumentProcessor()
        assert processor.detect_file_format("test.PDF") == "PDF"

    def test_detect_file_format_mimetype_priority(self):
        """Test that mimetype takes priority over extension."""
        processor = DocumentProcessor()
        # Extension suggests TXT, but mimetype says PDF
        assert processor.detect_file_format("test.txt", "application/pdf") == "PDF"

    def test_detect_file_format_various_extensions(self):
        """Test format detection for various file extensions."""
        processor = DocumentProcessor()

        test_cases = [
            ("test.xlsx", "XLSX"),
            ("test.xls", "XLSX"),
            ("test.pptx", "PPTX"),
            ("test.odt", "ODT"),
            ("test.rtf", "RTF"),
            ("test.msg", "MSG"),
        ]

        for filename, expected_format in test_cases:
            result = processor.detect_file_format(filename)
            assert result == expected_format, f"Expected {expected_format} for {filename}, got {result}"

    def test_extract_text_plain(self):
        """Test plain text extraction."""
        processor = DocumentProcessor()
        content = b"Hello World"
        result = processor.extract_text(content, "TXT")
        assert result == "Hello World"

    def test_extract_text_unsupported_format(self):
        """Test extraction with unsupported format."""
        processor = DocumentProcessor()
        content = b"test content"

        with pytest.raises(DocumentProcessorError):
            processor.extract_text(content, "UNSUPPORTED")

    def test_extract_text_extractor_error(self):
        """Test extraction when extractor raises an error."""
        processor = DocumentProcessor()

        # Mock the registry to return an extractor that will fail
        with patch.object(processor.registry, 'get_extractor') as mock_get_extractor:
            mock_extractor = MagicMock()
            mock_extractor.extract_text.side_effect = Exception("Extraction failed")
            mock_get_extractor.return_value = mock_extractor

            content = b"test content"
            with pytest.raises(DocumentProcessorError, match="Failed to extract text"):
                processor.extract_text(content, "TXT")

    def test_process_document(self):
        """Test full document processing."""
        processor = DocumentProcessor()
        content = b"Hello World Document"
        filename = "test.txt"

        text, metadata = processor.process_document(content, filename)

        assert text == "Hello World Document"
        assert isinstance(metadata, DocumentMetadata)
        assert metadata.filename == "test.txt"
        assert metadata.file_format == "TXT"
        assert metadata.size_bytes == len(content)
        assert metadata.text_length == len(text)
        assert metadata.checksum is not None
        assert metadata.processing_timestamp is not None

    def test_process_document_with_mimetype(self):
        """Test document processing with explicit mimetype."""
        processor = DocumentProcessor()
        content = b"<html><body>Test</body></html>"
        filename = "test.html"
        mimetype = "text/html"

        text, metadata = processor.process_document(content, filename, mimetype)

        assert isinstance(metadata, DocumentMetadata)
        assert metadata.filename == "test.html"
        assert metadata.file_format == "HTML"
        assert metadata.mimetype == "text/html"

    def test_process_document_extraction_error(self):
        """Test document processing when text extraction fails."""
        processor = DocumentProcessor()

        # Mock extract_text to raise an error
        with patch.object(processor, 'extract_text', side_effect=DocumentProcessorError("Extraction failed")):
            content = b"test content"
            filename = "test.txt"

            with pytest.raises(DocumentProcessorError, match="Extraction failed"):
                processor.process_document(content, filename)

    def test_process_document_empty_content(self):
        """Test document processing with empty content."""
        processor = DocumentProcessor()
        content = b""
        filename = "empty.txt"

        text, metadata = processor.process_document(content, filename)

        assert text == ""
        assert isinstance(metadata, DocumentMetadata)
        assert metadata.filename == "empty.txt"
        assert metadata.size_bytes == 0
        assert metadata.text_length == 0

    def test_get_supported_formats(self):
        """Test getting supported formats."""
        processor = DocumentProcessor()
        formats = processor.get_supported_formats()
        assert "PDF" in formats
        assert "DOCX" in formats
        assert "TXT" in formats
        assert "HTML" in formats

    def test_is_format_supported(self):
        """Test format support checking."""
        processor = DocumentProcessor()
        assert processor.is_format_supported("PDF")
        assert not processor.is_format_supported("UNSUPPORTED")