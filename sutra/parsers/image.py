"""
Image Parser - Extract content from image files using OCR

Handles image files with support for:
- OCR text extraction
- Multiple image formats (PNG, JPEG, GIF, BMP, TIFF)
- Metadata extraction
- Basic image analysis
- Tesseract OCR integration

Requirements:
    pip install pillow pytesseract
    System: tesseract-ocr installation

Usage:
    parser = ImageParser("document.png")
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
    from PIL import Image, ExifTags
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False


class ImageParser(BaseParser):
    """
    Image file parser using OCR
    
    Extracts text from images using Tesseract OCR engine.
    Supports common image formats and provides metadata extraction.
    
    Args:
        file_path: Path to image file
        options: Parser options
            - ocr_language: OCR language code (default: 'eng')
            - ocr_config: Custom OCR configuration
            - extract_metadata: Extract EXIF metadata (default: True)
            - preprocess: Apply image preprocessing (default: True)
            - min_confidence: Minimum OCR confidence (default: 30)
    
    Example:
        >>> parser = ImageParser("scanned_doc.png", {
        ...     "ocr_language": "eng",
        ...     "extract_metadata": True,
        ...     "min_confidence": 50
        ... })
        >>> result = await parser.parse()
        >>> print(f"Extracted text: {len(result.document.full_text)} chars")
    """
    
    def __init__(
        self,
        file_path: str | Path,
        options: Optional[Dict[str, Any]] = None
    ):
        if not PIL_AVAILABLE:
            raise ImportError(
                "Pillow is required for image parsing.\n"
                "Install with: pip install pillow"
            )
        
        super().__init__(file_path, options)
        
        # Parse options
        self.ocr_language = self.options.get("ocr_language", "eng")
        self.ocr_config = self.options.get("ocr_config", "--psm 3")
        self.extract_metadata = self.options.get("extract_metadata", True)
        self.preprocess = self.options.get("preprocess", True)
        self.min_confidence = self.options.get("min_confidence", 30)
        
        # Check tesseract availability
        if TESSERACT_AVAILABLE:
            try:
                pytesseract.get_tesseract_version()
            except Exception:
                self.ocr_available = False
        else:
            self.ocr_available = False
        
        # Load and validate image
        try:
            self.image = Image.open(self.file_path)
            
            # Convert to RGB if necessary
            if self.image.mode not in ['RGB', 'L']:
                self.image = self.image.convert('RGB')
        
        except Exception as e:
            raise CorruptedFileError(f"Failed to load image: {e}")
    
    def get_page_count(self) -> int:
        """
        Get page count (images are single page)
        
        Returns:
            Always 1 for images
        """
        return 1
    
    async def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate image file
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check if image was loaded successfully
            if not hasattr(self, 'image') or self.image is None:
                return False, "Failed to load image"
            
            # Check image dimensions
            width, height = self.image.size
            if width <= 0 or height <= 0:
                return False, "Invalid image dimensions"
            
            # Check if image is too small for meaningful OCR
            if width < 50 or height < 50:
                return False, "Image too small for text extraction"
            
            # Warn if OCR not available
            if not self.ocr_available:
                return True, "OCR not available - will extract basic metadata only"
            
            return True, None
            
        except Exception as e:
            return False, str(e)
    
    async def parse(self) -> ParserResult:
        """
        Parse image using OCR
        
        Returns:
            ParserResult with extracted text and metadata
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
            
            # Extract text using OCR if available
            extracted_text = ""
            
            if self.ocr_available:
                try:
                    # Preprocess image if requested
                    ocr_image = self.image
                    if self.preprocess:
                        ocr_image = self._preprocess_image(self.image)
                    
                    # Perform OCR
                    extracted_text = pytesseract.image_to_string(
                        ocr_image,
                        lang=self.ocr_language,
                        config=self.ocr_config
                    ).strip()
                    
                    # Filter by confidence if available
                    if self.min_confidence > 0:
                        try:
                            data = pytesseract.image_to_data(
                                ocr_image,
                                lang=self.ocr_language,
                                config=self.ocr_config,
                                output_type=pytesseract.Output.DICT
                            )
                            
                            # Filter words by confidence
                            filtered_words = []
                            for i, conf in enumerate(data['conf']):
                                if int(conf) >= self.min_confidence:
                                    word = data['text'][i].strip()
                                    if word:
                                        filtered_words.append(word)
                            
                            if filtered_words:
                                extracted_text = ' '.join(filtered_words)
                        
                        except Exception as e:
                            warnings.append(f"Confidence filtering failed: {e}")
                
                except Exception as e:
                    warnings.append(f"OCR failed: {e}")
                    extracted_text = ""
            
            else:
                warnings.append("OCR not available - no text extracted")
            
            # Extract metadata
            metadata = self._extract_metadata()
            
            # Create image info
            image_info = ImageInfo(
                id="image_0",
                format=self.file_path.suffix[1:].lower(),
                width=self.image.size[0],
                height=self.image.size[1],
                page_number=1,
                data=None  # Don't store raw data to save memory
            )
            
            # Create page info
            page_info = PageInfo(
                page_number=1,
                text=extracted_text,
                bounds={}
            )
            
            # Create ParsedDocument
            document = ParsedDocument(
                metadata=metadata,
                pages=[page_info] if extracted_text else [],
                images=[image_info],
                tables=[],
                full_text=extracted_text
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
        Parse image in streaming mode
        
        Yields document elements as they are extracted.
        """
        try:
            # Yield image metadata first
            yield DocumentElement(
                type=ElementType.IMAGE,
                content=None,
                metadata={
                    "width": self.image.size[0],
                    "height": self.image.size[1],
                    "format": self.file_path.suffix[1:].lower(),
                    "mode": self.image.mode
                }
            )
            
            # Extract text if OCR available
            if self.ocr_available:
                try:
                    # Preprocess image
                    ocr_image = self.image
                    if self.preprocess:
                        ocr_image = self._preprocess_image(self.image)
                    
                    # Perform OCR
                    text = pytesseract.image_to_string(
                        ocr_image,
                        lang=self.ocr_language,
                        config=self.ocr_config
                    ).strip()
                    
                    if text:
                        yield DocumentElement(
                            type=ElementType.TEXT,
                            content=text,
                            metadata={
                                "source": "ocr",
                                "language": self.ocr_language,
                                "confidence_threshold": self.min_confidence
                            }
                        )
                
                except Exception as e:
                    yield DocumentElement(
                        type=ElementType.TEXT,
                        content="",
                        metadata={"ocr_error": str(e)}
                    )
            
            await asyncio.sleep(0)  # Yield control
        
        except Exception as e:
            yield DocumentElement(
                type=ElementType.TEXT,
                content="",
                metadata={"error": str(e)}
            )
    
    def _preprocess_image(self, image: Any) -> Any:
        """
        Preprocess image for better OCR results
        
        Args:
            image: PIL Image object
        
        Returns:
            Preprocessed PIL Image
        """
        try:
            # Convert to grayscale if not already
            if image.mode != 'L':
                image = image.convert('L')
            
            # Basic preprocessing could include:
            # - Noise reduction
            # - Contrast enhancement
            # - Deskewing
            # For now, just return the grayscale image
            
            return image
        
        except Exception:
            return image
    
    def _extract_metadata(self) -> DocumentMetadata:
        """
        Extract image metadata including EXIF data
        
        Returns:
            DocumentMetadata object
        """
        # Basic image info
        width, height = self.image.size
        mode = self.image.mode
        format_name = self.image.format or "Unknown"
        
        # Extract EXIF data if available
        exif_data = {}
        
        if self.extract_metadata and hasattr(self.image, '_getexif'):
            try:
                exif = self.image._getexif()
                if exif:
                    for tag_id, value in exif.items():
                        tag = ExifTags.TAGS.get(tag_id, tag_id)
                        exif_data[tag] = str(value)
            except Exception:
                pass
        
        # Get creation date from EXIF or file stats
        created_date = None
        if 'DateTime' in exif_data:
            try:
                created_date = datetime.strptime(
                    exif_data['DateTime'], 
                    '%Y:%m:%d %H:%M:%S'
                )
            except ValueError:
                pass
        
        if not created_date:
            # Use file creation time
            stat = self.file_path.stat()
            created_date = datetime.fromtimestamp(stat.st_ctime)
        
        # Extract camera info
        camera_make = exif_data.get('Make', '')
        camera_model = exif_data.get('Model', '')
        camera_info = f"{camera_make} {camera_model}".strip()
        
        return self._create_metadata(
            title=self.file_path.stem,
            created_date=created_date,
            page_count=1,
            image_width=width,
            image_height=height,
            image_mode=mode,
            image_format=format_name,
            camera_info=camera_info if camera_info else None,
            exif_data=exif_data if exif_data else None
        )
    
    def get_supported_features(self) -> Dict[str, bool]:
        """Get supported features"""
        return {
            "text_extraction": self.ocr_available,
            "table_extraction": False,
            "image_extraction": True,
            "metadata_extraction": self.extract_metadata,
            "streaming": True,
            "ocr": self.ocr_available,
            "preprocessing": self.preprocess
        }


# Quick test function
async def test_image_parser():
    """Test image parser"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m sutra.parsers.image <image_file>")
        return
    
    image_file = sys.argv[1]
    
    print(f"\n{'='*70}")
    print(f"🧪 Testing Image Parser")
    print(f"{'='*70}")
    print(f"File: {image_file}\n")
    
    try:
        # Create parser
        parser = ImageParser(image_file)
        
        print(f"📄 Document Info:")
        print(f"   Type: {parser.document_type.value}")
        print(f"   Size: {parser.file_size:,} bytes")
        print(f"   Dimensions: {parser.image.size[0]} x {parser.image.size[1]}")
        print(f"   Mode: {parser.image.mode}")
        print(f"   OCR available: {parser.ocr_available}")
        print(f"   Hash: {parser.file_hash[:16]}...")
        
        # Validate
        print(f"\n✓ Validating...")
        is_valid, error = await parser.validate()
        
        if not is_valid:
            print(f"❌ Validation failed: {error}")
            return
        
        print(f"✅ Valid image")
        
        # Parse
        print(f"\n⏳ Parsing...")
        result = await parser.parse()
        
        if not result.success:
            print(f"❌ Parse failed: {result.error}")
            return
        
        print(f"✅ Parsed in {result.parse_time:.2f}s")
        
        if result.warnings:
            print(f"⚠️  Warnings:")
            for warning in result.warnings:
                print(f"   - {warning}")
        
        # Show results
        doc = result.document
        print(f"\n📊 Results:")
        print(f"   Images: {len(doc.images)}")
        print(f"   Text extracted: {len(doc.full_text):,} chars")
        
        if doc.images:
            img = doc.images[0]
            print(f"   Image size: {img.width} x {img.height}")
            print(f"   Format: {img.format}")
        
        # Show text preview
        if doc.full_text:
            preview = doc.full_text[:300].replace("\n", " ")
            print(f"\n📄 Extracted text preview:")
            print(f"   {preview}...")
        else:
            print(f"\n📄 No text extracted")
        
        print(f"\n{'='*70}")
        print(f"✅ Test complete!")
        print(f"{'='*70}\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_image_parser())