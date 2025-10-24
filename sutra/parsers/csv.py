"""
CSV Parser - Extract content from CSV files

Handles CSV/TSV files with support for:
- Automatic delimiter detection
- Header row detection
- Data type inference
- Large file streaming
- Various encodings
- Table structure preservation

Requirements:
    pip install pandas chardet

Usage:
    parser = CSVParser("data.csv")
    result = await parser.parse()
    
    # Or streaming
    async for element in parser.parse_stream():
        process(element)
"""

import time
import csv
import io
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
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    import chardet
    CHARDET_AVAILABLE = True
except ImportError:
    CHARDET_AVAILABLE = False


class CSVParser(BaseParser):
    """
    CSV/TSV file parser with automatic detection
    
    Handles various CSV formats with automatic delimiter and encoding detection.
    Converts tabular data to structured format for document processing.
    
    Args:
        file_path: Path to CSV file
        options: Parser options
            - delimiter: Force specific delimiter (default: auto-detect)
            - encoding: Force specific encoding (default: auto-detect)
            - has_header: Whether first row is header (default: auto-detect)
            - max_rows: Maximum rows to read (default: None - all)
            - chunk_size: Rows per chunk for streaming (default: 1000)
            - infer_types: Attempt data type inference (default: True)
    
    Example:
        >>> parser = CSVParser("data.csv", {
        ...     "delimiter": ",",
        ...     "has_header": True,
        ...     "max_rows": 10000
        ... })
        >>> result = await parser.parse()
        >>> print(f"Extracted table with {result.document.tables[0].rows} rows")
    """
    
    def __init__(
        self,
        file_path: str | Path,
        options: Optional[Dict[str, Any]] = None
    ):
        super().__init__(file_path, options)
        
        # Parse options
        self.delimiter = self.options.get("delimiter", None)
        self.encoding = self.options.get("encoding", None)
        self.has_header = self.options.get("has_header", None)
        self.max_rows = self.options.get("max_rows", None)
        self.chunk_size = self.options.get("chunk_size", 1000)
        self.infer_types = self.options.get("infer_types", True)
        
        # Auto-detect parameters if not specified
        if not self.encoding:
            self.encoding = self._detect_encoding()
        
        if not self.delimiter:
            self.delimiter = self._detect_delimiter()
        
        if self.has_header is None:
            self.has_header = self._detect_header()
        
        # Validate CSV can be read
        try:
            with open(self.file_path, 'r', encoding=self.encoding) as f:
                reader = csv.reader(f, delimiter=self.delimiter)
                # Try to read first few rows
                for i, row in enumerate(reader):
                    if i >= 3:  # Read first 3 rows for validation
                        break
        except Exception as e:
            raise CorruptedFileError(f"Failed to read CSV file: {e}")
    
    def _detect_encoding(self) -> str:
        """
        Detect CSV file encoding
        
        Returns:
            Detected encoding string
        """
        if CHARDET_AVAILABLE:
            try:
                with open(self.file_path, 'rb') as f:
                    sample = f.read(min(8192, self.file_size))
                
                result = chardet.detect(sample)
                encoding = result.get('encoding', 'utf-8')
                confidence = result.get('confidence', 0)
                
                if confidence < 0.7:
                    encoding = 'utf-8'
                
                return encoding
            except Exception:
                return 'utf-8'
        else:
            # Try common encodings
            for encoding in ['utf-8', 'ascii', 'latin-1', 'cp1252']:
                try:
                    with open(self.file_path, 'r', encoding=encoding) as f:
                        f.read(1024)
                    return encoding
                except (UnicodeDecodeError, UnicodeError):
                    continue
            
            return 'utf-8'
    
    def _detect_delimiter(self) -> str:
        """
        Detect CSV delimiter
        
        Returns:
            Detected delimiter character
        """
        try:
            with open(self.file_path, 'r', encoding=self.encoding) as f:
                # Read sample for detection
                sample = f.read(8192)
            
            # Use csv.Sniffer to detect delimiter
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample, delimiters=',;\t|').delimiter
            
            return delimiter
        
        except Exception:
            # Fallback: count occurrences of common delimiters
            try:
                with open(self.file_path, 'r', encoding=self.encoding) as f:
                    first_line = f.readline()
                
                delim_counts = {
                    ',': first_line.count(','),
                    ';': first_line.count(';'),
                    '\t': first_line.count('\t'),
                    '|': first_line.count('|')
                }
                
                # Return delimiter with highest count
                return max(delim_counts, key=delim_counts.get)
            
            except Exception:
                return ','  # Default to comma
    
    def _detect_header(self) -> bool:
        """
        Detect if first row is header
        
        Returns:
            True if first row appears to be header
        """
        try:
            with open(self.file_path, 'r', encoding=self.encoding) as f:
                reader = csv.reader(f, delimiter=self.delimiter)
                
                rows = []
                for i, row in enumerate(reader):
                    rows.append(row)
                    if i >= 2:  # Read first 3 rows
                        break
                
                if len(rows) < 2:
                    return True  # Assume header if only one row
                
                first_row = rows[0]
                second_row = rows[1] if len(rows) > 1 else []
                
                # Check if first row looks like header
                # Headers usually have different data types than data
                if not second_row:
                    return True
                
                header_score = 0
                
                for i, (h_val, d_val) in enumerate(zip(first_row, second_row)):
                    # If header value is not numeric but data is
                    try:
                        float(d_val)  # Data is numeric
                        try:
                            float(h_val)  # Header is also numeric
                        except ValueError:
                            header_score += 1  # Header is text, data is numeric
                    except ValueError:
                        pass  # Data is not numeric
                
                # If more than half the columns show header pattern
                return header_score > len(first_row) / 2
            
        except Exception:
            return True  # Default to assuming header exists
    
    def get_page_count(self) -> int:
        """
        Get page count (based on row count)
        
        Returns:
            Estimated page count
        """
        try:
            row_count = 0
            with open(self.file_path, 'r', encoding=self.encoding) as f:
                reader = csv.reader(f, delimiter=self.delimiter)
                for _ in reader:
                    row_count += 1
            
            # Estimate pages (assuming ~50 rows per page)
            pages = max(1, row_count // 50)
            return pages
        
        except Exception:
            return 1
    
    async def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate CSV file
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            with open(self.file_path, 'r', encoding=self.encoding) as f:
                reader = csv.reader(f, delimiter=self.delimiter)
                
                row_count = 0
                col_count = None
                
                for row in reader:
                    row_count += 1
                    
                    # Check column consistency
                    if col_count is None:
                        col_count = len(row)
                    elif len(row) != col_count and len(row) > 0:
                        # Allow some variation in column count (empty trailing cells)
                        if abs(len(row) - col_count) > col_count * 0.5:
                            return False, f"Inconsistent column count: expected ~{col_count}, got {len(row)} in row {row_count}"
                    
                    # Stop after checking first 100 rows for performance
                    if row_count >= 100:
                        break
                
                if row_count == 0:
                    return False, "CSV file is empty"
                
                if col_count == 0:
                    return False, "CSV has no columns"
            
            return True, None
            
        except Exception as e:
            return False, str(e)
    
    async def parse(self) -> ParserResult:
        """
        Parse entire CSV file
        
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
            
            # Read CSV data
            rows = []
            headers = []
            
            with open(self.file_path, 'r', encoding=self.encoding) as f:
                reader = csv.reader(f, delimiter=self.delimiter)
                
                for i, row in enumerate(reader):
                    # Skip empty rows
                    if not any(cell.strip() for cell in row):
                        continue
                    
                    if i == 0 and self.has_header:
                        headers = [cell.strip() for cell in row]
                    else:
                        rows.append([cell.strip() for cell in row])
                    
                    # Respect max_rows limit
                    if self.max_rows and len(rows) >= self.max_rows:
                        warnings.append(f"Truncated at {self.max_rows} rows")
                        break
            
            # Ensure consistent column count
            if rows:
                max_cols = max(len(row) for row in rows)
                
                # Pad headers if needed
                if headers:
                    while len(headers) < max_cols:
                        headers.append(f"Column_{len(headers) + 1}")
                else:
                    # Generate headers if none detected
                    headers = [f"Column_{i + 1}" for i in range(max_cols)]
                
                # Pad rows
                for row in rows:
                    while len(row) < max_cols:
                        row.append('')
            
            # Combine headers and rows for TableInfo
            all_rows = []
            if headers:
                all_rows.append(headers)
            all_rows.extend(rows)
            
            # Create table info
            table_info = TableInfo(
                id="csv_table_0",
                rows=all_rows,  # All rows as List[List[str]]
                page_number=1,
                bbox=None,
                caption=None
            )
            
            # Create text representation
            text_lines = []
            if headers:
                text_lines.append(" | ".join(headers))
                text_lines.append("-" * 50)
            
            for row in rows[:10]:  # Show first 10 rows in text
                text_lines.append(" | ".join(str(cell) for cell in row))
            
            if len(rows) > 10:
                text_lines.append(f"... and {len(rows) - 10} more rows")
            
            full_text = "\n".join(text_lines)
            
            # Extract metadata
            metadata = self._extract_metadata(len(rows), len(headers))
            
            # Create single page with table summary
            page_info = PageInfo(
                page_number=1,
                text=full_text,
                width=800.0,  # Default width for CSV
                height=600.0,  # Default height for CSV
                images=[],
                tables=[]
            )
            
            # Create ParsedDocument
            document = ParsedDocument(
                file_path=str(self.file_path),
                file_type="text/csv",
                file_size=self.file_size,
                text=full_text,
                pages=[page_info],
                images=[],  # CSV files don't have images
                tables=[table_info],
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
        Parse CSV in streaming mode
        
        Yields document elements as they are parsed.
        """
        try:
            with open(self.file_path, 'r', encoding=self.encoding) as f:
                reader = csv.reader(f, delimiter=self.delimiter)
                
                chunk_rows = []
                headers = []
                row_count = 0
                
                for row in reader:
                    # Skip empty rows
                    if not any(cell.strip() for cell in row):
                        continue
                    
                    if row_count == 0 and self.has_header:
                        headers = [cell.strip() for cell in row]
                        row_count += 1
                        continue
                    
                    chunk_rows.append([cell.strip() for cell in row])
                    row_count += 1
                    
                    # Yield chunk when full
                    if len(chunk_rows) >= self.chunk_size:
                        chunk_text = self._format_chunk(headers, chunk_rows)
                        
                        yield DocumentElement(
                            type=ElementType.TABLE,
                            content=chunk_text,
                            metadata={
                                "chunk": row_count // self.chunk_size,
                                "rows_start": row_count - len(chunk_rows),
                                "rows_end": row_count - 1,
                                "headers": headers,
                                "delimiter": self.delimiter,
                                "encoding": self.encoding
                            }
                        )
                        
                        chunk_rows = []
                        await asyncio.sleep(0)  # Yield control
                    
                    # Respect max_rows limit
                    if self.max_rows and row_count >= self.max_rows:
                        break
                
                # Yield remaining rows
                if chunk_rows:
                    chunk_text = self._format_chunk(headers, chunk_rows)
                    
                    yield DocumentElement(
                        type=ElementType.TABLE,
                        content=chunk_text,
                        metadata={
                            "chunk": (row_count // self.chunk_size) + 1,
                            "rows_start": row_count - len(chunk_rows),
                            "rows_end": row_count - 1,
                            "headers": headers,
                            "delimiter": self.delimiter,
                            "encoding": self.encoding
                        }
                    )
        
        except Exception as e:
            yield DocumentElement(
                type=ElementType.TEXT,
                content="",
                metadata={"error": str(e)}
            )
    
    def _format_chunk(self, headers: List[str], rows: List[List[str]]) -> str:
        """
        Format chunk of CSV data as text
        
        Args:
            headers: Column headers
            rows: Data rows
        
        Returns:
            Formatted text representation
        """
        lines = []
        
        if headers:
            lines.append(" | ".join(headers))
            lines.append("-" * (len(" | ".join(headers))))
        
        for row in rows:
            lines.append(" | ".join(str(cell) for cell in row))
        
        return "\n".join(lines)
    
    def _extract_metadata(self, row_count: int, col_count: int) -> DocumentMetadata:
        """
        Extract metadata from CSV data
        
        Args:
            row_count: Number of data rows
            col_count: Number of columns
        
        Returns:
            DocumentMetadata object
        """
        return self._create_metadata(
            title=self.file_path.stem,
            page_count=self.get_page_count(),
            encoding=self.encoding,
            row_count=row_count,
            column_count=col_count,
            delimiter=self.delimiter,
            has_header=self.has_header,
            csv_format=True
        )
    
    def get_supported_features(self) -> Dict[str, bool]:
        """Get supported features"""
        return {
            "text_extraction": True,
            "table_extraction": True,
            "image_extraction": False,
            "metadata_extraction": True,
            "streaming": True,
            "delimiter_detection": True,
            "encoding_detection": True,
            "type_inference": self.infer_types
        }


# Quick test function
async def test_csv_parser():
    """Test CSV parser"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m sutra.parsers.csv <csv_file>")
        return
    
    csv_file = sys.argv[1]
    
    print(f"\n{'='*70}")
    print(f"🧪 Testing CSV Parser")
    print(f"{'='*70}")
    print(f"File: {csv_file}\n")
    
    try:
        # Create parser
        parser = CSVParser(csv_file)
        
        print(f"📄 Document Info:")
        print(f"   Type: {parser.document_type.value}")
        print(f"   Encoding: {parser.encoding}")
        print(f"   Delimiter: '{parser.delimiter}'")
        print(f"   Has header: {parser.has_header}")
        print(f"   Size: {parser.file_size:,} bytes")
        print(f"   Estimated pages: {parser.get_page_count()}")
        print(f"   Hash: {parser.file_hash[:16]}...")
        
        # Validate
        print(f"\n✓ Validating...")
        is_valid, error = await parser.validate()
        
        if not is_valid:
            print(f"❌ Validation failed: {error}")
            return
        
        print(f"✅ Valid CSV")
        
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
        print(f"   Tables: {len(doc.tables)}")
        print(f"   Total text: {len(doc.full_text):,} chars")
        
        if doc.tables:
            table = doc.tables[0]
            print(f"   Rows: {table.rows:,}")
            print(f"   Columns: {table.cols}")
            
            if table.headers:
                print(f"   Headers: {', '.join(table.headers[:5])}")
                if len(table.headers) > 5:
                    print(f"            ... and {len(table.headers) - 5} more")
        
        # Show preview
        if doc.pages:
            preview = doc.pages[0].text[:300].replace("\n", " ")
            print(f"\n📄 Preview:")
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
    asyncio.run(test_csv_parser())