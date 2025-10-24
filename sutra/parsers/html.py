"""
HTML Parser - Extract content from HTML files

Handles HTML files with support for:
- Clean text extraction from HTML tags
- Structure preservation (headings, paragraphs, lists)
- Table extraction from HTML tables
- Link extraction
- Metadata from HTML head
- Image detection and extraction

Requirements:
    pip install beautifulsoup4 lxml

Usage:
    parser = HTMLParser("document.html")
    result = await parser.parse()
    
    # Or streaming
    async for element in parser.parse_stream():
        process(element)
"""

import time
import re
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
    from bs4 import BeautifulSoup, Tag, NavigableString
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False


class HTMLParser(BaseParser):
    """
    HTML file parser using BeautifulSoup
    
    Extracts clean text content from HTML while preserving document structure.
    Handles tables, lists, headings, and metadata extraction.
    
    Args:
        file_path: Path to HTML file
        options: Parser options
            - encoding: Force specific encoding (default: auto-detect)
            - preserve_structure: Preserve HTML structure (default: True)
            - extract_links: Extract hyperlinks (default: True)
            - extract_images: Extract image references (default: True)
            - extract_tables: Extract HTML tables (default: True)
            - clean_whitespace: Clean extra whitespace (default: True)
    
    Example:
        >>> parser = HTMLParser("document.html", {
        ...     "preserve_structure": True,
        ...     "extract_tables": True,
        ...     "extract_links": True
        ... })
        >>> result = await parser.parse()
        >>> print(f"Extracted {len(result.document.pages)} sections")
    """
    
    def __init__(
        self,
        file_path: str | Path,
        options: Optional[Dict[str, Any]] = None
    ):
        if not BS4_AVAILABLE:
            raise ImportError(
                "beautifulsoup4 is required for HTML parsing.\n"
                "Install with: pip install beautifulsoup4 lxml"
            )
        
        super().__init__(file_path, options)
        
        # Parse options
        self.encoding = self.options.get("encoding", None)
        self.preserve_structure = self.options.get("preserve_structure", True)
        self.extract_links = self.options.get("extract_links", True)
        self.extract_images = self.options.get("extract_images", True)
        self.extract_tables = self.options.get("extract_tables", True)
        self.clean_whitespace = self.options.get("clean_whitespace", True)
        
        # Detect encoding if not specified
        if not self.encoding:
            self.encoding = self._detect_encoding()
        
        # Parse HTML
        try:
            with open(self.file_path, 'r', encoding=self.encoding) as f:
                html_content = f.read()
            
            self.soup = BeautifulSoup(html_content, 'html.parser')
        except Exception as e:
            raise CorruptedFileError(f"Failed to parse HTML: {e}")
    
    def _detect_encoding(self) -> str:
        """
        Detect HTML encoding from meta tags or BOM
        
        Returns:
            Detected encoding string
        """
        try:
            # Read raw bytes to check for encoding hints
            with open(self.file_path, 'rb') as f:
                raw_content = f.read(2048)  # Read first 2KB
            
            # Try to decode with different encodings to find meta charset
            for encoding in ['utf-8', 'ascii', 'latin1']:
                try:
                    content = raw_content.decode(encoding, errors='ignore')
                    
                    # Look for charset in meta tags
                    charset_match = re.search(
                        r'<meta[^>]*charset\s*=\s*["\']?([^"\'>]+)', 
                        content, 
                        re.IGNORECASE
                    )
                    if charset_match:
                        return charset_match.group(1).lower()
                    
                    # Look for XML encoding
                    xml_match = re.search(
                        r'<\?xml[^>]*encoding\s*=\s*["\']([^"\']+)', 
                        content, 
                        re.IGNORECASE
                    )
                    if xml_match:
                        return xml_match.group(1).lower()
                
                except (UnicodeDecodeError, AttributeError):
                    continue
            
            return 'utf-8'  # Default fallback
            
        except Exception:
            return 'utf-8'
    
    def get_page_count(self) -> int:
        """
        Get page count (HTML is typically single page)
        
        Returns:
            Page count (usually 1)
        """
        # HTML is typically a single document, but we can estimate
        # based on content sections
        if hasattr(self, 'soup'):
            sections = self.soup.find_all(['section', 'article', 'div', 'main'])
            if sections and len(sections) > 1:
                return len(sections)
        
        return 1
    
    async def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate HTML file
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check if HTML was parsed successfully
            if not hasattr(self, 'soup') or self.soup is None:
                return False, "Failed to parse HTML content"
            
            # Check for basic HTML structure
            if not self.soup.find(['html', 'body', 'div', 'p']):
                return False, "No recognizable HTML structure found"
            
            # Check if there's any text content
            text_content = self.soup.get_text(strip=True)
            if not text_content:
                return False, "HTML contains no text content"
            
            return True, None
            
        except Exception as e:
            return False, str(e)
    
    async def parse(self) -> ParserResult:
        """
        Parse entire HTML document
        
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
            
            # Parse content structure
            sections = []
            tables = []
            images = []
            links = []
            
            if self.preserve_structure:
                sections = self._parse_html_structure()
            else:
                # Extract plain text
                text_content = self._clean_text(self.soup.get_text())
                sections = [{
                    "text": text_content,
                    "heading": metadata.title,
                    "type": "document"
                }]
            
            # Extract tables
            if self.extract_tables:
                tables = self._extract_tables()
            
            # Extract images
            if self.extract_images:
                images = self._extract_images()
            
            # Extract links
            if self.extract_links:
                links = self._extract_links()
            
            # Create pages from sections
            pages = []
            full_text_parts = []
            
            for idx, section in enumerate(sections):
                page_info = PageInfo(
                    page_number=idx + 1,
                    text=section["text"],
                    width=800.0,  # Default width for HTML
                    height=600.0,  # Default height for HTML
                    images=[],
                    tables=[]
                )
                pages.append(page_info)
                full_text_parts.append(section["text"])
            
            # Create ParsedDocument
            document = ParsedDocument(
                file_path=str(self.file_path),
                file_type="text/html",
                file_size=self.file_size,
                text="\n\n".join(full_text_parts),
                pages=pages,
                images=images,
                tables=tables,
                metadata=metadata
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
        Parse HTML in streaming mode
        
        Yields document elements as they are parsed.
        """
        try:
            # Process body elements
            body = self.soup.find('body') or self.soup
            
            for element in body.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div', 'table', 'ul', 'ol', 'section', 'article']):
                if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    # Heading
                    text = self._clean_text(element.get_text())
                    if text:
                        yield DocumentElement(
                            type=ElementType.HEADER,
                            content=text,
                            metadata={
                                "tag": element.name,
                                "level": int(element.name[1])
                            }
                        )
                
                elif element.name == 'p':
                    # Paragraph
                    text = self._clean_text(element.get_text())
                    if text:
                        yield DocumentElement(
                            type=ElementType.PARAGRAPH,
                            content=text,
                            metadata={"tag": "p"}
                        )
                
                elif element.name in ['ul', 'ol']:
                    # List
                    items = []
                    for li in element.find_all('li', recursive=False):
                        item_text = self._clean_text(li.get_text())
                        if item_text:
                            items.append(item_text)
                    
                    if items:
                        yield DocumentElement(
                            type=ElementType.LIST,
                            content="\n".join(f"- {item}" for item in items),
                            metadata={
                                "tag": element.name,
                                "ordered": element.name == 'ol',
                                "item_count": len(items)
                            }
                        )
                
                elif element.name == 'table':
                    # Table
                    if self.extract_tables:
                        table_info = self._parse_html_table(element)
                        if table_info:
                            yield DocumentElement(
                                type=ElementType.TABLE,
                                content=None,
                                metadata={"table_info": table_info}
                            )
                
                else:
                    # Generic text content
                    text = self._clean_text(element.get_text())
                    if text and len(text.strip()) > 10:  # Avoid empty divs
                        yield DocumentElement(
                            type=ElementType.TEXT,
                            content=text,
                            metadata={"tag": element.name}
                        )
                
                await asyncio.sleep(0)  # Yield control
        
        except Exception as e:
            yield DocumentElement(
                type=ElementType.TEXT,
                content="",
                metadata={"error": str(e)}
            )
    
    def _parse_html_structure(self) -> List[Dict[str, Any]]:
        """
        Parse HTML structure preserving hierarchy
        
        Returns:
            List of section dictionaries
        """
        sections = []
        
        # Find main content area
        main_content = (
            self.soup.find('main') or 
            self.soup.find('article') or 
            self.soup.find('body') or 
            self.soup
        )
        
        current_section = []
        current_heading = None
        
        for element in main_content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div', 'section', 'article']):
            if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                # Save previous section
                if current_section:
                    section_text = "\n\n".join(current_section)
                    if section_text.strip():
                        sections.append({
                            "text": section_text,
                            "heading": current_heading,
                            "level": int(current_heading[1]) if current_heading else 1,
                            "type": "section"
                        })
                
                # Start new section
                current_heading = element.name
                heading_text = self._clean_text(element.get_text())
                current_section = [heading_text]
            
            else:
                # Add content to current section
                text = self._clean_text(element.get_text())
                if text and text.strip():
                    current_section.append(text)
        
        # Add final section
        if current_section:
            section_text = "\n\n".join(current_section)
            if section_text.strip():
                sections.append({
                    "text": section_text,
                    "heading": current_heading,
                    "level": int(current_heading[1]) if current_heading else 1,
                    "type": "section"
                })
        
        # If no sections found, use entire body text
        if not sections:
            body_text = self._clean_text(self.soup.get_text())
            if body_text:
                sections.append({
                    "text": body_text,
                    "heading": None,
                    "level": 0,
                    "type": "document"
                })
        
        return sections
    
    def _extract_tables(self) -> List[TableInfo]:
        """
        Extract HTML tables
        
        Returns:
            List of TableInfo objects
        """
        tables = []
        html_tables = self.soup.find_all('table')
        
        for idx, table in enumerate(html_tables):
            table_info = self._parse_html_table(table, idx)
            if table_info:
                tables.append(table_info)
        
        return tables
    
    def _parse_html_table(self, table_element, table_index: int = 0) -> Optional[TableInfo]:
        """
        Parse HTML table element
        
        Args:
            table_element: BeautifulSoup table element
            table_index: Index of table
        
        Returns:
            TableInfo object or None
        """
        try:
            rows = []
            headers = []
            
            # Look for header row
            thead = table_element.find('thead')
            if thead:
                header_row = thead.find('tr')
                if header_row:
                    headers = [self._clean_text(th.get_text()) for th in header_row.find_all(['th', 'td'])]
            
            # Get data rows
            tbody = table_element.find('tbody') or table_element
            for tr in tbody.find_all('tr'):
                cells = [self._clean_text(td.get_text()) for td in tr.find_all(['td', 'th'])]
                if cells:
                    # If no explicit headers and this is first row, use as headers
                    if not headers and not rows:
                        headers = cells
                    else:
                        rows.append(cells)
            
            if not headers and not rows:
                return None
            
            # Ensure consistent column count
            max_cols = max(len(headers) if headers else 0, 
                          max((len(row) for row in rows), default=0))
            
            if max_cols == 0:
                return None
            
            # Pad rows to consistent length
            if headers:
                headers.extend([''] * (max_cols - len(headers)))
            
            for row in rows:
                row.extend([''] * (max_cols - len(row)))
            
            # Combine headers and data rows for TableInfo
            all_rows = []
            if headers:
                all_rows.append(headers)
            all_rows.extend(rows)
            
            return TableInfo(
                id=f"table_{table_index}",
                rows=all_rows,
                page_number=1,  # HTML is single page
                caption=None
            )
        
        except Exception as e:
            print(f"Warning: Failed to parse table {table_index}: {e}")
            return None
    
    def _extract_images(self) -> List[ImageInfo]:
        """
        Extract image references from HTML
        
        Returns:
            List of ImageInfo objects (without actual image data)
        """
        images = []
        img_tags = self.soup.find_all('img')
        
        for idx, img in enumerate(img_tags):
            src = img.get('src', '')
            alt = img.get('alt', '')
            title = img.get('title', '')
            
            if src:
                # Determine format from extension
                format_ext = 'unknown'
                if '.' in src:
                    format_ext = src.split('.')[-1].lower()
                
                image_info = ImageInfo(
                    id=f"html_image_{idx}",
                    format=format_ext,
                    width=0,  # HTML doesn't provide actual dimensions easily
                    height=0,
                    page_number=1,
                    caption=alt or title or None,
                    data=None  # We don't fetch actual image data
                )
                images.append(image_info)
        
        return images
    
    def _extract_links(self) -> List[Dict[str, str]]:
        """
        Extract hyperlinks from HTML
        
        Returns:
            List of link dictionaries
        """
        links = []
        a_tags = self.soup.find_all('a', href=True)
        
        for link in a_tags:
            href = link['href']
            text = self._clean_text(link.get_text())
            title = link.get('title', '')
            
            if href and text:
                links.append({
                    "url": href,
                    "text": text,
                    "title": title
                })
        
        return links
    
    def _clean_text(self, text: str) -> str:
        """
        Clean extracted text
        
        Args:
            text: Raw text from HTML
        
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        if self.clean_whitespace:
            # Replace multiple whitespace with single space
            text = re.sub(r'\s+', ' ', text)
            text = text.strip()
        
        return text
    
    def _extract_metadata(self) -> DocumentMetadata:
        """
        Extract metadata from HTML head
        
        Returns:
            DocumentMetadata object
        """
        # Get title
        title = None
        title_tag = self.soup.find('title')
        if title_tag:
            title = self._clean_text(title_tag.get_text())
        
        # Get meta tags
        description = None
        author = None
        keywords = None
        
        # Description
        meta_desc = self.soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            description = meta_desc.get('content', '')
        
        # Author
        meta_author = self.soup.find('meta', attrs={'name': 'author'})
        if meta_author:
            author = meta_author.get('content', '')
        
        # Keywords
        meta_keywords = self.soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords:
            keywords = meta_keywords.get('content', '')
        
        # Content stats
        body_text = self.soup.get_text()
        word_count = len(body_text.split())
        char_count = len(body_text)
        
        return self._create_metadata(
            title=title or self.file_path.stem,
            author=author,
            page_count=self.get_page_count(),
            word_count=word_count,
            character_count=char_count,
            encoding=self.encoding,
            description=description,
            keywords=keywords
        )
    
    def get_supported_features(self) -> Dict[str, bool]:
        """Get supported features"""
        return {
            "text_extraction": True,
            "table_extraction": self.extract_tables,
            "image_extraction": self.extract_images,
            "metadata_extraction": True,
            "streaming": True,
            "structure_preservation": self.preserve_structure,
            "link_extraction": self.extract_links
        }


# Quick test function
async def test_html_parser():
    """Test HTML parser"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m sutra.parsers.html <html_file>")
        return
    
    html_file = sys.argv[1]
    
    print(f"\n{'='*70}")
    print(f"🧪 Testing HTML Parser")
    print(f"{'='*70}")
    print(f"File: {html_file}\n")
    
    try:
        # Create parser
        parser = HTMLParser(html_file)
        
        print(f"📄 Document Info:")
        print(f"   Type: {parser.document_type.value}")
        print(f"   Encoding: {parser.encoding}")
        print(f"   Size: {parser.file_size:,} bytes")
        print(f"   Pages: {parser.get_page_count()}")
        print(f"   Hash: {parser.file_hash[:16]}...")
        
        # Validate
        print(f"\n✓ Validating...")
        is_valid, error = await parser.validate()
        
        if not is_valid:
            print(f"❌ Validation failed: {error}")
            return
        
        print(f"✅ Valid HTML")
        
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
        print(f"   Sections: {len(doc.pages)}")
        print(f"   Tables: {len(doc.tables)}")
        print(f"   Images: {len(doc.images)}")
        print(f"   Total text: {len(doc.full_text):,} chars")
        
        if hasattr(doc.metadata, 'word_count'):
            print(f"   Words: {doc.metadata.word_count:,}")
        
        if doc.metadata.title:
            print(f"   Title: {doc.metadata.title}")
        if doc.metadata.author:
            print(f"   Author: {doc.metadata.author}")
        
        # Show first section preview
        if doc.pages:
            first_section = doc.pages[0]
            preview = first_section.text[:200].replace("\n", " ")
            print(f"\n📄 First section preview:")
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
    asyncio.run(test_html_parser())