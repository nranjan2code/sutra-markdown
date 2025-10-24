"""
Text Parser - Production-Grade Implementation

A robust, production-ready text file parser that properly integrates with the Sutra system.
Handles various text formats with comprehensive error handling, validation, and security.

Features:
- Comprehensive encoding detection and handling
- Robust error handling and validation  
- Memory-efficient streaming for large files
- Security checks for malicious content
- Full BaseParser interface compliance
- Proper ParsedDocument structure generation
- Extensive logging and monitoring support

Author: Sutra Development Team
Version: 2.0.0
"""

import time
import logging
from pathlib import Path
from typing import Optional, Dict, Any, AsyncIterator, List, Tuple
import uuid
import mimetypes
from datetime import datetime
import asyncio

from ..models.document import (
    ParsedDocument,
    DocumentMetadata, 
    PageInfo,
    ImageInfo,
    TableInfo,
    DocumentElement
)
from ..models.enums import DocumentType
from .base import BaseParser, ParserResult, ParserError, CorruptedFileError

# Configure logging
logger = logging.getLogger(__name__)

# Constants
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB limit
ENCODING_DETECTION_SAMPLE = 8192   # 8KB for encoding detection
CHUNK_SIZE = 1000                  # Lines per chunk for streaming
SUSPICIOUS_PATTERNS = [            # Security patterns to detect
    b'\x00', b'\xff\xfe', b'\xfe\xff',  # Binary markers
    b'<script', b'javascript:',          # Script content
]


class TextParser(BaseParser):
    """
    Production-grade text file parser
    
    Implements comprehensive text parsing with robust error handling,
    security validation, and proper integration with the Sutra system.
    
    Args:
        file_path: Path to text file
        options: Parser configuration options
            - max_file_size: Maximum file size in bytes (default: 100MB)
            - encoding: Force specific encoding (default: auto-detect)
            - validate_content: Enable content validation (default: True)
            - chunk_size: Lines per streaming chunk (default: 1000)
            - detect_structure: Attempt structure detection (default: True)
            - security_scan: Enable security scanning (default: True)
    
    Raises:
        ParserError: For parser-specific errors
        CorruptedFileError: For file corruption issues
        ValueError: For invalid arguments
        SecurityError: For security violations
    
    Example:
        >>> parser = TextParser("document.txt", {
        ...     "encoding": "utf-8",
        ...     "validate_content": True,
        ...     "security_scan": True
        ... })
        >>> result = await parser.parse()
        >>> if result.success:
        ...     print(f"Parsed {len(result.document.text)} characters")
    """
    
    def __init__(
        self,
        file_path: str | Path,
        options: Optional[Dict[str, Any]] = None
    ):
        """Initialize text parser with comprehensive validation"""
        
        # Initialize parent parser
        super().__init__(file_path, options)
        
        # Parse and validate options
        self.max_file_size = self.options.get("max_file_size", MAX_FILE_SIZE)
        self.encoding = self.options.get("encoding", None)
        self.validate_content = self.options.get("validate_content", True)
        self.chunk_size = self.options.get("chunk_size", CHUNK_SIZE)
        self.detect_structure = self.options.get("detect_structure", True)
        self.security_scan = self.options.get("security_scan", True)
        
        # Validate option parameters
        if self.max_file_size <= 0:
            raise ValueError("max_file_size must be positive")
        if self.chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        
        # Security validation
        if self.file_size > self.max_file_size:
            raise ParserError(
                f"File size {self.file_size:,} bytes exceeds limit of {self.max_file_size:,} bytes"
            )
        
        # Detect and validate encoding
        if not self.encoding:
            self.encoding = self._detect_encoding_robust()
        
        # Validate file accessibility and basic security
        self._perform_security_validation()
        
        # Detect text format
        self.text_format = self._detect_text_format()
        
        logger.info(
            f"Initialized TextParser for {self.file_path.name} "
            f"(size: {self.file_size:,} bytes, encoding: {self.encoding}, "
            f"format: {self.text_format})"
        )
    
    def _detect_encoding_robust(self) -> str:
        """
        Robust encoding detection with multiple fallback strategies
        
        Returns:
            Detected encoding string
            
        Raises:
            CorruptedFileError: If no valid encoding found
        """
        logger.debug(f"Detecting encoding for {self.file_path}")
        
        # Strategy 1: Try chardet if available
        try:
            import chardet
            
            with open(self.file_path, 'rb') as f:
                sample = f.read(min(ENCODING_DETECTION_SAMPLE, self.file_size))
            
            if sample:
                result = chardet.detect(sample)
                if result and result.get('confidence', 0) > 0.7:
                    encoding = result['encoding'].lower()
                    logger.debug(f"Chardet detected {encoding} with confidence {result['confidence']}")
                    
                    # Validate detection by attempting decode
                    if self._validate_encoding(encoding, sample):
                        return encoding
        
        except ImportError:
            logger.debug("Chardet not available, using fallback detection")
        except Exception as e:
            logger.warning(f"Chardet detection failed: {e}")
        
        # Strategy 2: Common encoding attempts
        common_encodings = ['utf-8', 'ascii', 'latin-1', 'cp1252', 'iso-8859-1']
        
        with open(self.file_path, 'rb') as f:
            sample = f.read(min(ENCODING_DETECTION_SAMPLE, self.file_size))
        
        for encoding in common_encodings:
            if self._validate_encoding(encoding, sample):
                logger.debug(f"Successfully validated encoding: {encoding}")
                return encoding
        
        # Strategy 3: BOM detection
        if sample.startswith(b'\xef\xbb\xbf'):
            return 'utf-8-sig'
        elif sample.startswith(b'\xff\xfe'):
            return 'utf-16-le'  
        elif sample.startswith(b'\xfe\xff'):
            return 'utf-16-be'
        
        # Final fallback
        logger.warning(f"Could not detect encoding for {self.file_path}, using utf-8 with error handling")
        return 'utf-8'
    
    def _validate_encoding(self, encoding: str, sample: bytes) -> bool:
        """
        Validate encoding by attempting to decode sample
        
        Args:
            encoding: Encoding to test
            sample: Byte sample to decode
            
        Returns:
            True if encoding is valid
        """
        try:
            sample.decode(encoding)
            return True
        except (UnicodeDecodeError, LookupError):
            return False
    
    def _detect_text_format(self) -> str:
        """
        Detect text file format from extension and content
        
        Returns:
            Detected format string
        """
        ext = self.file_path.suffix.lower()
        
        # Format mapping
        format_map = {
            '.md': 'markdown',
            '.markdown': 'markdown', 
            '.rst': 'restructuredtext',
            '.rest': 'restructuredtext',
            '.txt': 'plain',
            '.log': 'log',
            '.json': 'json',
            '.xml': 'xml',
            '.html': 'html',
            '.htm': 'html',
            '.csv': 'csv',
            '.tsv': 'tsv'
        }
        
        detected_format = format_map.get(ext, 'plain')
        
        # Content-based detection for extensionless files
        if detected_format == 'plain' and self.detect_structure:
            try:
                with open(self.file_path, 'r', encoding=self.encoding, errors='ignore') as f:
                    first_lines = [f.readline().strip() for _ in range(5)]
                
                content_sample = '\n'.join(first_lines)
                
                # Simple heuristics
                if content_sample.startswith('#') or '##' in content_sample:
                    detected_format = 'markdown'
                elif content_sample.startswith('{') or content_sample.startswith('['):
                    detected_format = 'json'
                elif '<' in content_sample and '>' in content_sample:
                    detected_format = 'xml'
                    
            except Exception as e:
                logger.debug(f"Content-based format detection failed: {e}")
        
        return detected_format
    
    def _perform_security_validation(self) -> None:
        """
        Perform security validation on the file
        
        Raises:
            ParserError: If security violations detected
        """
        if not self.security_scan:
            return
        
        logger.debug(f"Performing security validation on {self.file_path}")
        
        try:
            # Check MIME type
            mime_type, _ = mimetypes.guess_type(str(self.file_path))
            if mime_type and not mime_type.startswith('text/'):
                logger.warning(f"Unexpected MIME type: {mime_type}")
            
            # Scan for suspicious binary content
            with open(self.file_path, 'rb') as f:
                sample = f.read(min(4096, self.file_size))
            
            for pattern in SUSPICIOUS_PATTERNS:
                if pattern in sample:
                    raise ParserError(
                        f"Security violation: Suspicious pattern detected in file"
                    )
            
            # Check for excessive null bytes (binary content)
            null_count = sample.count(b'\x00')
            if null_count > len(sample) * 0.1:  # More than 10% null bytes
                raise CorruptedFileError("File appears to contain binary data")
        
        except (OSError, IOError) as e:
            raise CorruptedFileError(f"Security validation failed: {e}")
    
    def get_page_count(self) -> int:
        """
        Get estimated page count based on content length
        
        Returns:
            Estimated page count
        """
        try:
            # Estimate based on line count (50 lines per page)
            with open(self.file_path, 'r', encoding=self.encoding, errors='ignore') as f:
                line_count = sum(1 for _ in f)
            
            return max(1, (line_count + 49) // 50)  # Ceiling division
        
        except Exception as e:
            logger.warning(f"Could not count lines for {self.file_path}: {e}")
            return 1
    
    async def validate(self) -> Tuple[bool, Optional[str]]:
        """
        Comprehensive file validation
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Basic accessibility check
            if not self.file_path.exists():
                return False, f"File not found: {self.file_path}"
            
            if not self.file_path.is_file():
                return False, f"Path is not a file: {self.file_path}"
            
            # Permission check
            if not self.file_path.stat().st_mode & 0o444:  # Read permission
                return False, "File is not readable"
            
            # Size validation
            if self.file_size == 0:
                return False, "File is empty"
            
            if self.file_size > self.max_file_size:
                return False, f"File too large: {self.file_size:,} > {self.max_file_size:,} bytes"
            
            # Content validation
            if self.validate_content:
                try:
                    with open(self.file_path, 'r', encoding=self.encoding, errors='strict') as f:
                        # Try to read first chunk
                        chunk = f.read(1024)
                        if not chunk.strip():
                            return False, "File contains only whitespace"
                
                except UnicodeDecodeError as e:
                    return False, f"Encoding error with {self.encoding}: {e}"
            
            logger.debug(f"Validation successful for {self.file_path}")
            return True, None
        
        except Exception as e:
            logger.error(f"Validation failed for {self.file_path}: {e}")
            return False, str(e)
    
    async def parse(self) -> ParserResult:
        """
        Parse text file with comprehensive error handling
        
        Returns:
            ParserResult containing ParsedDocument or error information
        """
        start_time = time.time()
        warnings: List[str] = []
        
        logger.info(f"Starting parse of {self.file_path}")
        
        try:
            # Validation
            is_valid, error_msg = await self.validate()
            if not is_valid:
                logger.error(f"Validation failed: {error_msg}")
                return ParserResult(
                    document=None,
                    success=False,
                    error=error_msg,
                    warnings=warnings,
                    parse_time=0.0,
                    file_size=self.file_size
                )
            
            # Read file content with proper error handling
            try:
                with open(self.file_path, 'r', encoding=self.encoding, errors='replace') as f:
                    content = f.read()
            
            except Exception as e:
                logger.error(f"Failed to read file content: {e}")
                return ParserResult(
                    document=None,
                    success=False,
                    error=f"Failed to read file: {e}",
                    warnings=warnings,
                    parse_time=time.time() - start_time,
                    file_size=self.file_size
                )
            
            # Content processing
            content = content.strip()
            if not content:
                warnings.append("File content is empty after stripping whitespace")
            
            # Generate metadata
            try:
                metadata = self._create_comprehensive_metadata(content)
            except Exception as e:
                logger.warning(f"Metadata generation failed: {e}")
                warnings.append(f"Could not generate full metadata: {e}")
                
                # Create minimal metadata
                metadata = DocumentMetadata(
                    title=self.file_path.stem,
                    created_date=None,
                    modified_date=None,
                    page_count=1,
                    word_count=len(content.split()) if content else 0,
                    language="en",
                    extra={"parser_warnings": ["Metadata generation failed"]}
                )
            
            # Create page structure
            page = PageInfo(
                page_number=1,
                text=content,
                width=0.0,
                height=0.0,
                elements=[],
                images=[],
                tables=[]
            )
            
            # Create ParsedDocument with proper structure
            document = ParsedDocument(
                id=uuid.uuid4().hex,
                file_path=str(self.file_path),
                file_type=self.text_format,
                file_size=self.file_size,
                text=content,
                pages=[page],
                images=[],
                tables=[],
                metadata=metadata,
                document_type=None,  # Will be determined later
                layout_type=None,
                embedding=None
            )
            
            processing_time = time.time() - start_time
            
            logger.info(
                f"Successfully parsed {self.file_path} in {processing_time:.3f}s "
                f"({len(content):,} chars, {len(warnings)} warnings)"
            )
            
            return ParserResult(
                document=document,
                success=True,
                error=None,
                warnings=warnings,
                parse_time=processing_time,
                file_size=self.file_size
            )
        
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Parse failed for {self.file_path}: {e}", exc_info=True)
            
            return ParserResult(
                document=None,
                success=False,
                error=f"Unexpected error during parsing: {e}",
                warnings=warnings,
                parse_time=processing_time,
                file_size=self.file_size
            )
    
    async def parse_stream(self) -> AsyncIterator[DocumentElement]:
        """
        Stream parse text file in chunks
        
        Yields:
            DocumentElement instances for each chunk
        """
        logger.debug(f"Starting streaming parse of {self.file_path}")
        
        try:
            with open(self.file_path, 'r', encoding=self.encoding, errors='replace') as f:
                chunk_lines: List[str] = []
                line_number = 0
                chunk_number = 0
                
                async for line in self._async_readline(f):
                    line_number += 1
                    chunk_lines.append(line.rstrip('\n\r'))
                    
                    # Yield chunk when full
                    if len(chunk_lines) >= self.chunk_size:
                        chunk_text = '\n'.join(chunk_lines)
                        
                        yield DocumentElement(
                            type="text",
                            text=chunk_text,
                            level=None,
                            page_number=1,
                            bbox=None,
                            metadata={
                                "chunk_number": chunk_number,
                                "line_start": line_number - len(chunk_lines) + 1,
                                "line_end": line_number,
                                "encoding": self.encoding,
                                "format": self.text_format
                            }
                        )
                        
                        chunk_lines.clear()
                        chunk_number += 1
                        
                        # Yield control to event loop
                        await asyncio.sleep(0)
                
                # Yield remaining lines
                if chunk_lines:
                    chunk_text = '\n'.join(chunk_lines)
                    
                    yield DocumentElement(
                        type="text",
                        text=chunk_text,
                        level=None,
                        page_number=1,
                        bbox=None,
                        metadata={
                            "chunk_number": chunk_number,
                            "line_start": line_number - len(chunk_lines) + 1,
                            "line_end": line_number,
                            "encoding": self.encoding,
                            "format": self.text_format,
                            "final_chunk": True
                        }
                    )
        
        except Exception as e:
            logger.error(f"Streaming parse failed: {e}")
            # Yield error element
            yield DocumentElement(
                type="error",
                text="",
                level=None,
                page_number=1,
                bbox=None,
                metadata={"error": str(e)}
            )
    
    async def _async_readline(self, file_obj) -> AsyncIterator[str]:
        """
        Async wrapper for file readline to allow proper yielding
        
        Args:
            file_obj: Open file object
            
        Yields:
            File lines
        """
        while True:
            line = file_obj.readline()
            if not line:
                break
            yield line
            await asyncio.sleep(0)  # Allow other coroutines to run
    
    def _create_comprehensive_metadata(self, content: str) -> DocumentMetadata:
        """
        Create comprehensive metadata from file and content analysis
        
        Args:
            content: File content
            
        Returns:
            DocumentMetadata instance
        """
        # File statistics
        stat = self.file_path.stat()
        created_date = datetime.fromtimestamp(stat.st_ctime).isoformat()
        modified_date = datetime.fromtimestamp(stat.st_mtime).isoformat()
        
        # Content analysis
        lines = content.split('\n')
        line_count = len(lines)
        word_count = len(content.split()) if content else 0
        char_count = len(content)
        
        # Detect title from content
        title = self._extract_title_from_content(lines) or self.file_path.stem
        
        # Language detection (basic)
        language = self._detect_language_simple(content)
        
        # Additional metadata
        extra_metadata = {
            "encoding": self.encoding,
            "text_format": self.text_format,
            "line_count": line_count,
            "character_count": char_count,
            "file_extension": self.file_path.suffix,
            "parser_version": "2.0.0",
            "processing_timestamp": datetime.utcnow().isoformat(),
            "security_validated": self.security_scan
        }
        
        return DocumentMetadata(
            title=title,
            author=None,  # Not available for text files
            created_date=created_date,
            modified_date=modified_date,
            page_count=self.get_page_count(),
            word_count=word_count,
            language=language,
            extra=extra_metadata
        )
    
    def _extract_title_from_content(self, lines: List[str]) -> Optional[str]:
        """
        Extract title from content based on format
        
        Args:
            lines: Content lines
            
        Returns:
            Extracted title or None
        """
        if not lines:
            return None
        
        # Try first non-empty line
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            if not line:
                continue
            
            # Markdown heading
            if line.startswith('#'):
                return line.lstrip('#').strip()
            
            # RestructuredText title (underlined)
            if len(lines) > lines.index(line) + 1:
                next_line = lines[lines.index(line) + 1].strip()
                if len(next_line) >= len(line) and len(set(next_line)) == 1:
                    if next_line[0] in '=-~`#*+^':
                        return line
            
            # Use first substantial line if short enough
            if len(line) < 100 and not line.lower().startswith(('the ', 'a ', 'an ')):
                return line
        
        return None
    
    def _detect_language_simple(self, content: str) -> str:
        """
        Simple language detection
        
        Args:
            content: Text content
            
        Returns:
            Language code
        """
        # Very basic English detection
        english_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        
        if content:
            words = set(word.lower().strip('.,!?;:"()[]{}') for word in content.split()[:100])
            english_matches = len(words.intersection(english_words))
            
            if english_matches >= 3:
                return "en"
        
        return "unknown"
    
    def get_supported_features(self) -> Dict[str, bool]:
        """
        Get list of features supported by this parser
        
        Returns:
            Feature support mapping
        """
        return {
            "text_extraction": True,
            "metadata_extraction": True,
            "streaming": True,
            "encoding_detection": True,
            "security_validation": self.security_scan,
            "structure_detection": self.detect_structure,
            "error_recovery": True,
            "async_processing": True,
            "content_validation": self.validate_content,
            # Not supported for text files
            "table_extraction": False,
            "image_extraction": False,
            "ocr": False,
            "formatting_preservation": False
        }
    
    def __repr__(self) -> str:
        """String representation for debugging"""
        return (
            f"TextParser(file='{self.file_path.name}', "
            f"size={self.file_size:,}, encoding='{self.encoding}', "
            f"format='{self.text_format}')"
        )


# Production testing and validation
async def validate_text_parser():
    """
    Comprehensive validation of TextParser implementation
    
    This function tests various scenarios to ensure production readiness.
    """
    import tempfile
    import os
    
    print(f"\n{'='*70}")
    print(f"🧪 Production Validation: TextParser")
    print(f"{'='*70}")
    
    test_cases = [
        ("UTF-8 Text", "Hello, World! 🌍\nThis is a test file."),
        ("ASCII Text", "Simple ASCII content\nLine 2\nLine 3"),
        ("Empty File", ""),
        ("Whitespace Only", "   \n\t\n   "),
        ("Large Content", "Line {}\n" * 1000),
        ("Markdown", "# Title\n\n## Section\n\nContent here."),
        ("Mixed Content", "Title\n" + "Word " * 500)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, content in test_cases:
        try:
            print(f"\n🔍 Testing: {test_name}")
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                f.write(content.format(*range(1000)) if '{}' in content else content)
                temp_path = f.name
            
            try:
                # Test parser
                parser = TextParser(temp_path)
                result = await parser.parse()
                
                if result.success:
                    print(f"   ✅ SUCCESS - {len(result.document.text):,} chars parsed")
                    if result.warnings:
                        print(f"   ⚠️  {len(result.warnings)} warnings: {result.warnings}")
                    passed += 1
                else:
                    print(f"   ❌ FAILED - {result.error}")
                    failed += 1
                    
            finally:
                # Cleanup
                os.unlink(temp_path)
                
        except Exception as e:
            print(f"   💥 EXCEPTION - {e}")
            failed += 1
    
    print(f"\n{'='*70}")
    print(f"📊 Results: {passed} passed, {failed} failed")
    print(f"{'='*70}")
    
    return failed == 0


if __name__ == "__main__":
    """Run production validation when executed directly"""
    asyncio.run(validate_text_parser())