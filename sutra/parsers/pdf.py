"""
PDF Parser - Extract content from PDF documents

Uses PyMuPDF (fitz) for high-performance PDF parsing with support for:
- Text extraction with positioning
- Table detection and extraction
- Image extraction
- Metadata extraction
- Page-by-page processing
- OCR support (optional)

Requirements:
    pip install PyMuPDF

Usage:
    parser = PDFParser("document.pdf")
    result = await parser.parse()
    
    # Or streaming
    async for element in parser.parse_stream():
        process(element)
"""

import time
from pathlib import Path
from typing import List, Optional, Dict, Any, AsyncIterator
from datetime import datetime
import asyncio

from ..models.document import (
    ParsedDocument,
    PageInfo,
    ImageInfo,
    TableInfo,
    DocumentElement,
    DocumentMetadata
)
from ..models.enums import ElementType, DocumentType
from .base import BaseParser, ParserResult, ParserError, CorruptedFileError

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False


class PDFParser(BaseParser):
    """
    PDF document parser using PyMuPDF
    
    Extracts text, tables, images, and metadata from PDF files.
    Supports both full document parsing and streaming mode.
    
    Args:
        file_path: Path to PDF file
        options: Parser options
            - extract_images: Extract images (default: True)
            - extract_tables: Extract tables (default: True)
            - ocr: Use OCR for scanned PDFs (default: False)
            - dpi: DPI for image extraction (default: 150)
            - max_pages: Limit number of pages to parse (default: None)
    
    Example:
        >>> parser = PDFParser("report.pdf", {
        ...     "extract_images": True,
        ...     "extract_tables": True
        ... })
        >>> result = await parser.parse()
        >>> print(f"Extracted {len(result.document.pages)} pages")
    """
    
    def __init__(
        self,
        file_path: str | Path,
        options: Optional[Dict[str, Any]] = None
    ):
        if not PYMUPDF_AVAILABLE:
            raise ImportError(
                "PyMuPDF is required for PDF parsing.\n"
                "Install with: pip install PyMuPDF"
            )
        
        super().__init__(file_path, options)
        
        # Parse options
        self.extract_images = self.options.get("extract_images", True)
        self.extract_tables = self.options.get("extract_tables", True)
        self.use_ocr = self.options.get("ocr", False)
        self.dpi = self.options.get("dpi", 150)
        self.max_pages = self.options.get("max_pages", None)
        
        # Open PDF document
        try:
            self.doc = fitz.open(str(self.file_path))
        except Exception as e:
            raise CorruptedFileError(f"Failed to open PDF: {e}")
    
    def __del__(self):
        """Close PDF document on cleanup"""
        if hasattr(self, 'doc'):
            self.doc.close()
    
    def get_page_count(self) -> int:
        """Get number of pages in PDF"""
        return len(self.doc)
    
    async def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate PDF file
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check if PDF can be opened
            if not hasattr(self, 'doc'):
                return False, "Failed to open PDF document"
            
            # Check if PDF is encrypted
            if self.doc.is_encrypted:
                return False, "PDF is encrypted (password required)"
            
            # Check if has pages
            if len(self.doc) == 0:
                return False, "PDF has no pages"
            
            # Try to read first page
            try:
                page = self.doc[0]
                _ = page.get_text()
            except Exception as e:
                return False, f"Failed to read PDF content: {e}"
            
            return True, None
            
        except Exception as e:
            return False, str(e)
    
    async def parse(self) -> ParserResult:
        """
        Parse entire PDF document
        
        Returns:
            ParserResult with parsed content
        """
        start_time = time.time()
        warnings = []
        
        try:
            # Validate first
            is_valid, error = await self.validate()
            if not is_valid:
                return ParserResult(
                    document=None,
                    success=False,
                    error=error,
                    file_size=self.file_size
                )
            
            # Extract metadata
            metadata = self._extract_metadata()
            
            # Parse pages
            pages = []
            images = []
            tables = []
            
            page_count = min(len(self.doc), self.max_pages) if self.max_pages else len(self.doc)
            
            for page_num in range(page_count):
                page_data = await self._parse_page(page_num)
                pages.append(page_data["page_info"])
                images.extend(page_data["images"])
                tables.extend(page_data["tables"])
            
            # Create ParsedDocument
            document = ParsedDocument(
                file_path=str(self.file_path),
                file_type="application/pdf",
                file_size=self.file_size,
                text="\n\n".join(page.text for page in pages if page.text),
                metadata=metadata,
                pages=pages,
                images=images,
                tables=tables
            )
            
            parse_time = time.time() - start_time
            
            return ParserResult(
                document=document,
                success=True,
                warnings=warnings,
                parse_time=parse_time,
                file_size=self.file_size
            )
            
        except Exception as e:
            return ParserResult(
                document=None,
                success=False,
                error=str(e),
                parse_time=time.time() - start_time,
                file_size=self.file_size
            )
    
    async def parse_stream(self) -> AsyncIterator[DocumentElement]:
        """
        Parse PDF in streaming mode
        
        Yields document elements as they are parsed.
        """
        page_count = min(len(self.doc), self.max_pages) if self.max_pages else len(self.doc)
        
        for page_num in range(page_count):
            page_data = await self._parse_page(page_num)
            
            # Yield page text as element
            if page_data["page_info"].text:
                yield DocumentElement(
                    type=ElementType.TEXT,
                    content=page_data["page_info"].text,
                    metadata={
                        "page_number": page_num + 1,
                        "bounds": page_data["page_info"].bounds
                    }
                )
            
            # Yield images
            for image in page_data["images"]:
                yield DocumentElement(
                    type=ElementType.IMAGE,
                    content=None,
                    metadata={
                        "page_number": page_num + 1,
                        "image_info": image
                    }
                )
            
            # Yield tables
            for table in page_data["tables"]:
                yield DocumentElement(
                    type=ElementType.TABLE,
                    content=None,
                    metadata={
                        "page_number": page_num + 1,
                        "table_info": table
                    }
                )
            
            # Yield control to event loop
            await asyncio.sleep(0)
    
    async def _parse_page(self, page_num: int) -> Dict[str, Any]:
        """
        Parse a single page
        
        Args:
            page_num: Page number (0-indexed)
        
        Returns:
            Dict with page_info, images, and tables
        """
        page = self.doc[page_num]
        
        # Extract text with better paragraph structure
        text = self._extract_structured_text(page)
        
        # Get page dimensions
        rect = page.rect
        bounds = {
            "x0": rect.x0,
            "y0": rect.y0,
            "x1": rect.x1,
            "y1": rect.y1,
            "width": rect.width,
            "height": rect.height
        }
        
        # Create PageInfo
        page_info = PageInfo(
            page_number=page_num + 1,
            text=text,
            width=rect.width,
            height=rect.height
        )
        
        # Extract images
        images = []
        if self.extract_images:
            images = await self._extract_images_from_page(page, page_num)
        
        # Extract tables
        tables = []
        if self.extract_tables:
            tables = await self._extract_tables_from_page(page, page_num)
        
        return {
            "page_info": page_info,
            "images": images,
            "tables": tables
        }
    
    def _extract_structured_text(self, page) -> str:
        """
        Extract text with better paragraph structure preservation
        
        Uses PyMuPDF's dictionary format to maintain proper paragraph flow
        instead of the basic text extraction that breaks lines arbitrarily.
        """
        try:
            # Get text in dictionary format with positioning
            text_dict = page.get_text("dict")
            
            if not isinstance(text_dict, dict) or "blocks" not in text_dict:
                # Fallback to basic extraction
                return page.get_text("text")
            
            blocks = text_dict["blocks"]
            structured_text = []
            
            for block in blocks:
                if not isinstance(block, dict) or "lines" not in block:
                    continue
                    
                # Text block - extract lines and spans
                block_text = []
                for line in block["lines"]:
                    if not isinstance(line, dict) or "spans" not in line:
                        continue
                        
                    line_text = ""
                    for span in line["spans"]:
                        if isinstance(span, dict) and "text" in span:
                            line_text += span["text"]
                    
                    # Add line if it has content
                    if line_text.strip():
                        block_text.append(line_text.strip())
                
                # Join lines in a block with spaces (natural flow)
                # Separate blocks with double newlines (paragraphs)
                if block_text:
                    structured_text.append(" ".join(block_text))
            
            # Join all blocks with paragraph breaks
            result = "\n\n".join(structured_text)
            
            # Clean up excessive whitespace
            import re
            result = re.sub(r'\n{3,}', '\n\n', result)  # Max 2 newlines
            result = re.sub(r' {2,}', ' ', result)     # Max 1 space
            
            return result.strip()
            
        except Exception:
            # Fallback to basic extraction if structured parsing fails
            return page.get_text("text")
    
    async def _extract_images_from_page(
        self,
        page: Any,
        page_num: int
    ) -> List[ImageInfo]:
        """
        Extract images from page
        
        Args:
            page: PyMuPDF page object
            page_num: Page number (0-indexed)
        
        Returns:
            List of ImageInfo objects
        """
        images = []
        
        try:
            image_list = page.get_images(full=True)
            
            for img_index, img in enumerate(image_list):
                xref = img[0]
                
                try:
                    # Get image info
                    base_image = self.doc.extract_image(xref)
                    
                    if base_image:
                        image_info = ImageInfo(
                            id=f"pdf_page{page_num + 1}_image{img_index}",
                            format=base_image.get("ext", "unknown"),
                            width=base_image.get("width", 0),
                            height=base_image.get("height", 0),
                            page_number=page_num + 1,
                            # Store image bytes (could be saved to file later)
                            data=base_image.get("image")
                        )
                        images.append(image_info)
                
                except Exception as e:
                    # Skip problematic images
                    print(f"Warning: Failed to extract image {img_index} from page {page_num + 1}: {e}")
                    continue
        
        except Exception as e:
            print(f"Warning: Failed to get images from page {page_num + 1}: {e}")
        
        return images
    
    async def _extract_tables_from_page(
        self,
        page: Any,
        page_num: int
    ) -> List[TableInfo]:
        """
        Extract tables from page
        
        Note: Basic table detection. For better results, consider using
        libraries like camelot-py or tabula-py.
        
        Args:
            page: PyMuPDF page object
            page_num: Page number (0-indexed)
        
        Returns:
            List of TableInfo objects
        """
        tables = []
        
        # TODO: Implement table extraction
        # This is a placeholder for future table extraction logic
        # Options:
        # 1. Use page.find_tables() if available in newer PyMuPDF
        # 2. Integrate camelot-py or tabula-py
        # 3. Implement custom table detection based on text blocks
        
        return tables
    
    def _extract_metadata(self) -> DocumentMetadata:
        """
        Extract PDF metadata
        
        Returns:
            DocumentMetadata object
        """
        # Get PDF metadata
        meta = self.doc.metadata
        
        # Parse dates
        created_date = None
        modified_date = None
        
        if meta.get("creationDate"):
            try:
                # PDF date format: D:YYYYMMDDHHmmSSOHH'mm'
                date_str = meta["creationDate"]
                if date_str.startswith("D:"):
                    date_str = date_str[2:16]  # Get YYYYMMDDHHmmSS
                    created_date = datetime.strptime(date_str, "%Y%m%d%H%M%S")
            except:
                pass
        
        if meta.get("modDate"):
            try:
                date_str = meta["modDate"]
                if date_str.startswith("D:"):
                    date_str = date_str[2:16]
                    modified_date = datetime.strptime(date_str, "%Y%m%d%H%M%S")
            except:
                pass
        
        return self._create_metadata(
            title=meta.get("title"),
            author=meta.get("author"),
            created_date=created_date,
            modified_date=modified_date,
            page_count=len(self.doc),
            producer=meta.get("producer"),
            subject=meta.get("subject"),
            keywords=meta.get("keywords"),
            is_encrypted=self.doc.is_encrypted,
            is_ocr_needed=self._needs_ocr()
        )
    
    def _needs_ocr(self) -> bool:
        """
        Check if PDF needs OCR (is scanned/image-based)
        
        Returns:
            True if OCR is needed
        """
        if not hasattr(self, 'doc') or len(self.doc) == 0:
            return False
        
        # Check first few pages
        pages_to_check = min(3, len(self.doc))
        
        for page_num in range(pages_to_check):
            page = self.doc[page_num]
            text = page.get_text("text").strip()
            
            # If page has substantial text, OCR not needed
            if len(text) > 100:
                return False
        
        # If no text found in first pages, likely needs OCR
        return True
    
    def get_supported_features(self) -> Dict[str, bool]:
        """Get supported features"""
        return {
            "text_extraction": True,
            "table_extraction": self.extract_tables,
            "image_extraction": self.extract_images,
            "metadata_extraction": True,
            "streaming": True,
            "page_by_page": True,
            "ocr": self.use_ocr,
            "formatting": False
        }


# Quick test function
async def test_pdf_parser():
    """Test PDF parser"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m sutra.parsers.pdf <pdf_file>")
        return
    
    pdf_file = sys.argv[1]
    
    print(f"\n{'='*70}")
    print(f"🧪 Testing PDF Parser")
    print(f"{'='*70}")
    print(f"File: {pdf_file}\n")
    
    try:
        # Create parser
        parser = PDFParser(pdf_file)
        
        print(f"📄 Document Info:")
        print(f"   Type: {parser.document_type.value}")
        print(f"   Size: {parser.file_size:,} bytes")
        print(f"   Pages: {parser.get_page_count()}")
        print(f"   Hash: {parser.file_hash[:16]}...")
        
        # Validate
        print(f"\n✓ Validating...")
        is_valid, error = await parser.validate()
        
        if not is_valid:
            print(f"❌ Validation failed: {error}")
            return
        
        print(f"✅ Valid PDF")
        
        # Parse
        print(f"\n⏳ Parsing...")
        result = await parser.parse()
        
        if not result.success:
            print(f"❌ Parse failed: {result.error}")
            return
        
        print(f"✅ Parsed in {result.parse_time:.2f}s")
        
        # Show results
        doc = result.document
        print(f"\n📊 Results:")
        print(f"   Pages: {len(doc.pages)}")
        print(f"   Images: {len(doc.images)}")
        print(f"   Tables: {len(doc.tables)}")
        print(f"   Total text: {len(doc.full_text):,} chars")
        
        if doc.metadata.title:
            print(f"   Title: {doc.metadata.title}")
        if doc.metadata.author:
            print(f"   Author: {doc.metadata.author}")
        
        # Show first page preview
        if doc.pages:
            first_page = doc.pages[0]
            preview = first_page.text[:200].replace("\n", " ")
            print(f"\n📄 First page preview:")
            print(f"   {preview}...")
        
        print(f"\n{'='*70}")
        print(f"✅ Test complete!")
        print(f"{'='*70}\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_pdf_parser())
