"""
Base Parser - Abstract interface for all document parsers

Defines the common interface that all parsers must implement.
Provides shared utilities for error handling, validation, and metadata extraction.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional, Dict, Any, AsyncIterator
from dataclasses import dataclass, field
import hashlib
import mimetypes
import logging
from datetime import datetime

from ..models.document import (
    ParsedDocument,
    PageInfo,
    ImageInfo,
    TableInfo,
    DocumentElement,
    DocumentMetadata
)
from ..models.enums import DocumentType

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class ParserResult:
    """
    Result from document parsing
    
    Contains the parsed document and metadata about the parsing process.
    """
    document: ParsedDocument
    success: bool = True
    error: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    parse_time: float = 0.0
    file_size: int = 0


class BaseParser(ABC):
    """
    Abstract base class for all document parsers
    
    All parsers must implement:
    - parse(): Main parsing method
    - parse_stream(): Streaming parser for large files
    - validate(): Validate file before parsing
    
    Attributes:
        file_path: Path to document
        document_type: Type of document (PDF, DOCX, etc.)
        options: Parser-specific options
    """
    
    def __init__(
        self,
        file_path: str | Path,
        options: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize parser
        
        Args:
            file_path: Path to document file
            options: Parser-specific options
        """
        self.file_path = Path(file_path)
        self.options = options or {}
        
        # Validate file exists
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")
        
        # Detect document type
        self.document_type = self._detect_document_type()
        
        # Extract basic metadata
        self.file_size = self.file_path.stat().st_size
        self.file_hash = self._compute_file_hash()
    
    def _detect_document_type(self) -> DocumentType:
        """
        Detect document type from file extension and MIME type
        
        Returns:
            DocumentType enum value
        """
        # Get MIME type
        mime_type, _ = mimetypes.guess_type(str(self.file_path))
        
        # Check by extension
        ext = self.file_path.suffix.lower()
        
        if ext == '.pdf' or mime_type == 'application/pdf':
            return DocumentType.PDF
        elif ext in ['.doc', '.docx'] or mime_type in [
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        ]:
            return DocumentType.WORD
        elif ext in ['.ppt', '.pptx'] or mime_type in [
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        ]:
            return DocumentType.POWERPOINT
        elif ext in ['.xls', '.xlsx'] or mime_type in [
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ]:
            return DocumentType.SPREADSHEET
        elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'] or \
             (mime_type and mime_type.startswith('image/')):
            return DocumentType.IMAGE
        elif ext in ['.txt', '.md', '.rst'] or mime_type == 'text/plain':
            return DocumentType.TEXT
        elif ext in ['.html', '.htm'] or mime_type == 'text/html':
            return DocumentType.HTML
        elif ext == '.csv' or mime_type == 'text/csv':
            return DocumentType.CSV
        else:
            return DocumentType.OTHER
    
    def _compute_file_hash(self, algorithm: str = 'sha256') -> str:
        """
        Compute hash of file for caching and deduplication
        
        Args:
            algorithm: Hash algorithm (default: sha256)
        
        Returns:
            Hex string of file hash
        """
        hash_obj = hashlib.new(algorithm)
        
        # Read file in chunks for memory efficiency
        with open(self.file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hash_obj.update(chunk)
        
        return hash_obj.hexdigest()
    
    def _create_metadata(
        self,
        title: Optional[str] = None,
        author: Optional[str] = None,
        created_date: Optional[datetime] = None,
        modified_date: Optional[datetime] = None,
        **kwargs
    ) -> DocumentMetadata:
        """
        Create DocumentMetadata object
        
        Args:
            title: Document title
            author: Document author
            created_date: Creation date
            modified_date: Last modified date
            **kwargs: Additional metadata fields
        
        Returns:
            DocumentMetadata instance
        """
        # Use file stats if dates not provided
        stat = self.file_path.stat()
        
        # Convert dates to ISO format strings
        if created_date is None:
            created_date = datetime.fromtimestamp(stat.st_ctime)
        if modified_date is None:
            modified_date = datetime.fromtimestamp(stat.st_mtime)
        
        # Format dates as strings
        created_str = created_date.isoformat() if created_date else None
        modified_str = modified_date.isoformat() if modified_date else None
        
        return DocumentMetadata(
            title=title or self.file_path.stem,
            author=author,
            created_date=created_str,
            modified_date=modified_str,
            page_count=kwargs.get('page_count', 1),
            word_count=kwargs.get('word_count', 0),
            language=kwargs.get('language'),
            extra=kwargs
        )
    
    @abstractmethod
    async def parse(self) -> ParserResult:
        """
        Parse the document
        
        This is the main parsing method that must be implemented by all parsers.
        
        Returns:
            ParserResult containing parsed document and metadata
        
        Raises:
            Exception: If parsing fails
        """
        pass
    
    @abstractmethod
    async def parse_stream(self) -> AsyncIterator[DocumentElement]:
        """
        Parse document in streaming mode
        
        Yields document elements as they are parsed, useful for large files.
        
        Yields:
            DocumentElement instances
        """
        pass
    
    @abstractmethod
    async def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate that file can be parsed
        
        Checks file format, corruption, etc. before attempting full parse.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        pass
    
    @abstractmethod
    def get_page_count(self) -> int:
        """
        Get number of pages/slides in document
        
        Returns:
            Page count
        """
        pass
    
    def get_supported_features(self) -> Dict[str, bool]:
        """
        Get list of features supported by this parser
        
        Returns:
            Dict mapping feature names to support status
        """
        return {
            "text_extraction": True,
            "table_extraction": False,
            "image_extraction": False,
            "metadata_extraction": True,
            "streaming": True,
            "page_by_page": False,
            "ocr": False,
            "formatting": False
        }
    
    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"file={self.file_path.name}, "
            f"type={self.document_type.value}, "
            f"size={self.file_size:,} bytes)"
        )
    
    # ========== SAFE CREATION HELPERS ==========
    
    def _create_table_info_safe(
        self,
        rows: List[List[str]],
        table_id: str,
        page_number: Optional[int] = None,
        bbox: Optional[List[float]] = None,
        caption: Optional[str] = None,
        max_rows: int = 10000
    ) -> Optional[TableInfo]:
        """
        Safely create TableInfo with validation and normalization
        
        Args:
            rows: Table rows as List[List[str]]
            table_id: Unique identifier
            page_number: Optional page number
            bbox: Optional bounding box
            caption: Optional caption
            max_rows: Maximum rows to keep (default: 10000)
        
        Returns:
            TableInfo object or None if invalid
        """
        try:
            # Skip empty tables
            if not rows:
                logger.debug(f"Skipping empty table {table_id}")
                return None
            
            # Skip tables with all empty cells
            if all(not any(cell.strip() for cell in row) for row in rows):
                logger.debug(f"Skipping table {table_id} with all empty cells")
                return None
            
            # Normalize row lengths (pad with empty strings)
            max_cols = max(len(row) for row in rows) if rows else 0
            if max_cols == 0:
                return None
            
            for row in rows:
                while len(row) < max_cols:
                    row.append('')
            
            # Limit table size
            if len(rows) > max_rows:
                logger.warning(f"Table {table_id} truncated from {len(rows)} to {max_rows} rows")
                rows = rows[:max_rows]
            
            # Create TableInfo
            return TableInfo(
                id=table_id,
                rows=rows,
                page_number=page_number,
                bbox=bbox,
                caption=caption
            )
        
        except Exception as e:
            logger.error(f"Failed to create TableInfo for {table_id}: {e}")
            return None
    
    def _create_image_info_safe(
        self,
        image_id: str,
        format: str,
        width: int,
        height: int,
        page_number: Optional[int] = None,
        bbox: Optional[List[float]] = None,
        caption: Optional[str] = None,
        data: Optional[bytes] = None,
        max_image_size: int = 10 * 1024 * 1024  # 10MB
    ) -> Optional[ImageInfo]:
        """
        Safely create ImageInfo with validation
        
        Args:
            image_id: Unique identifier
            format: Image format (jpg, png, etc.)
            width: Image width in pixels
            height: Image height in pixels
            page_number: Optional page number
            bbox: Optional bounding box
            caption: Optional caption
            data: Optional raw image bytes
            max_image_size: Max size to store in memory (default: 10MB)
        
        Returns:
            ImageInfo object or None if invalid
        """
        try:
            # Skip invalid images
            if width <= 0 or height <= 0:
                logger.debug(f"Skipping image {image_id} with invalid dimensions: {width}x{height}")
                return None
            
            # Don't store large images in memory
            if data and len(data) > max_image_size:
                logger.debug(f"Image {image_id} too large ({len(data)} bytes), not storing data")
                data = None
            
            # Validate format
            valid_formats = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp', 'svg', 'ico']
            if format.lower() not in valid_formats:
                logger.debug(f"Unknown image format: {format}, using 'unknown'")
                format = 'unknown'
            
            # Create ImageInfo
            return ImageInfo(
                id=image_id,
                format=format,
                width=width,
                height=height,
                page_number=page_number,
                bbox=bbox,
                caption=caption,
                data=data
            )
        
        except Exception as e:
            logger.error(f"Failed to create ImageInfo for {image_id}: {e}")
            return None


class ParserError(Exception):
    """Base exception for parser errors"""
    pass


class UnsupportedFormatError(ParserError):
    """Raised when document format is not supported"""
    pass


class CorruptedFileError(ParserError):
    """Raised when document file is corrupted"""
    pass


class ParseTimeoutError(ParserError):
    """Raised when parsing takes too long"""
    pass
