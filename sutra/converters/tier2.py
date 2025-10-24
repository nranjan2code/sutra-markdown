"""
Tier 2 Converter - Spatial-aware conversion for moderately complex documents

Layout-aware conversion using spatial analysis and positioning.
Optimized for documents with:
- Multi-column layouts
- Complex formatting
- Spatial relationships
- Multiple tables and images

Target: 5% of documents
Cost: $0.005 per document
Speed: 1-3 seconds per document

Features:
- Layout analysis and column detection
- Spatial positioning awareness
- Complex table handling
- Image placement optimization
- Reading order detection
- Format preservation
"""

import time
from typing import List, Dict, Any, Optional, Tuple

from ..models.document import ParsedDocument, DocumentElement, TableInfo, ImageInfo, PageInfo
from ..models.enums import ConversionTier
from .base import BaseConverter, ConversionResult, ConversionError
from .tier1 import Tier1Converter


class Tier2Converter(BaseConverter):
    """
    Spatial-aware converter for moderately complex documents
    
    Uses layout analysis and spatial positioning to handle
    documents with complex structures.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize Tier 2 converter
        
        Args:
            config: Configuration options:
                - detect_columns: True to detect multi-column layouts
                - preserve_layout: True to preserve spatial relationships
                - group_elements: True to group related elements
        """
        super().__init__(config)
        
        # Configuration
        self.detect_columns = self.config.get('detect_columns', True)
        self.preserve_layout = self.config.get('preserve_layout', True)
        self.group_elements = self.config.get('group_elements', True)
        
        # Fallback to Tier 1 for simple elements
        self.tier1_converter = Tier1Converter(config)
    
    @property
    def tier(self) -> ConversionTier:
        return ConversionTier.SPATIAL_AWARE
    
    def can_convert(self, document: ParsedDocument) -> bool:
        """
        Check if document is suitable for Tier 2 conversion
        
        Criteria:
        - Complexity score 0.3 - 0.7
        - Multi-column layout OR complex tables OR many images
        """
        # Check complexity score
        complexity = document.metadata.extra.get('complexity_score', 0.0)
        if complexity < 0.3 or complexity >= 0.7:
            return False
        
        # Check for moderate complexity indicators
        has_many_tables = len(document.tables) > 3
        has_many_images = len(document.images) > 5
        has_multi_column = document.metadata.extra.get('has_multi_column', False)
        
        return has_many_tables or has_many_images or has_multi_column
    
    async def convert(self, document: ParsedDocument) -> ConversionResult:
        """
        Convert document to Markdown using spatial-aware approach
        
        Args:
            document: Parsed document to convert
            
        Returns:
            ConversionResult with generated Markdown
        """
        start_time = time.time()
        warnings: List[str] = []
        errors: List[str] = []
        stats = {
            'pages_processed': 0,
            'columns_detected': 0,
            'elements_grouped': 0,
            'tables_found': len(document.tables),
            'images_found': len(document.images),
        }
        
        try:
            markdown_parts: List[str] = []
            
            # Add title
            if document.metadata.title:
                markdown_parts.append(f"# {document.metadata.title}\n")
            
            # Process pages with spatial awareness
            for page in document.pages:
                stats['pages_processed'] += 1
                
                try:
                    page_md = await self._convert_page_spatial(page, stats)
                    if page_md:
                        markdown_parts.append(page_md)
                except Exception as e:
                    warnings.append(f"Failed to convert page {page.page_number}: {str(e)}")
                    # Fallback to simple conversion
                    page_md = self.tier1_converter._format_text(page.text)
                    markdown_parts.append(page_md)
            
            # Join and clean
            markdown = "\n\n".join(part for part in markdown_parts if part)
            markdown = self._clean_markdown(markdown)
            
            # Calculate quality score
            quality_score = self._calculate_quality(
                document, markdown, warnings, errors
            )
            
            processing_time = time.time() - start_time
            
            result = ConversionResult(
                markdown=markdown,
                tier=self.tier,
                success=True,
                quality_score=quality_score,
                processing_time=processing_time,
                metadata={
                    'converter': 'tier2',
                    'source_format': document.file_type,
                    'source_pages': document.num_pages,
                    'columns_detected': stats['columns_detected'],
                },
                warnings=warnings,
                errors=errors,
                stats=stats,
            )
            
            self._update_stats(result)
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            errors.append(str(e))
            
            result = ConversionResult(
                markdown="",
                tier=self.tier,
                success=False,
                quality_score=0.0,
                processing_time=processing_time,
                warnings=warnings,
                errors=errors,
                stats=stats,
            )
            
            self._update_stats(result)
            raise ConversionError(f"Tier 2 conversion failed: {str(e)}") from e
    
    async def _convert_page_spatial(self, page: PageInfo, stats: Dict[str, Any]) -> str:
        """Convert page with spatial awareness"""
        parts: List[str] = []
        
        # Add page marker
        parts.append(f"<!-- Page {page.page_number} -->\n")
        
        if not page.elements:
            # Fallback to simple text
            return self.tier1_converter._format_text(page.text)
        
        # Detect columns if enabled
        if self.detect_columns:
            columns = self._detect_columns(page)
            stats['columns_detected'] += len(columns)
            
            if len(columns) > 1:
                # Multi-column layout
                for col_idx, column in enumerate(columns, 1):
                    parts.append(f"\n### Column {col_idx}\n")
                    column_md = self._convert_elements(column)
                    parts.append(column_md)
            else:
                # Single column
                elements_md = self._convert_elements(page.elements)
                parts.append(elements_md)
        else:
            # No column detection
            elements_md = self._convert_elements(page.elements)
            parts.append(elements_md)
        
        # Add tables for this page
        page_tables = [t for t in page.tables if t.page_number == page.page_number]
        for i, table in enumerate(page_tables, 1):
            table_md = self.tier1_converter._convert_table(table, i)
            parts.append(table_md)
        
        # Add images for this page
        page_images = [img for img in page.images if img.page_number == page.page_number]
        for i, image in enumerate(page_images, 1):
            image_md = self.tier1_converter._convert_image(image, i)
            parts.append(image_md)
        
        return "\n".join(parts)
    
    def _detect_columns(self, page: PageInfo) -> List[List[DocumentElement]]:
        """
        Detect multi-column layout
        
        Uses x-coordinates (bbox) to group elements into columns.
        """
        if not page.elements:
            return []
        
        # Get elements with bounding boxes
        elements_with_bbox = [
            e for e in page.elements 
            if e.bbox and len(e.bbox) >= 4
        ]
        
        if not elements_with_bbox:
            # No bbox info, return all as single column
            return [page.elements]
        
        # Sort by x-coordinate (left position)
        elements_with_bbox.sort(key=lambda e: e.bbox[0])
        
        # Simple column detection: group by x-coordinate ranges
        page_width = page.width if hasattr(page, 'width') else 612  # Default letter width
        mid_point = page_width / 2
        
        left_column = []
        right_column = []
        
        for element in elements_with_bbox:
            x_left = element.bbox[0]
            if x_left < mid_point - 50:  # Left column (with tolerance)
                left_column.append(element)
            elif x_left > mid_point + 50:  # Right column (with tolerance)
                right_column.append(element)
            else:
                # In the middle - could be spanning both
                if len(left_column) > len(right_column):
                    left_column.append(element)
                else:
                    right_column.append(element)
        
        # Return non-empty columns
        columns = []
        if left_column:
            columns.append(left_column)
        if right_column:
            columns.append(right_column)
        
        return columns if columns else [page.elements]
    
    def _convert_elements(self, elements: List[DocumentElement]) -> str:
        """Convert list of elements to Markdown"""
        parts: List[str] = []
        
        # Sort by reading order (top to bottom)
        sorted_elements = sorted(
            elements,
            key=lambda e: (e.bbox[1] if e.bbox and len(e.bbox) >= 2 else 0)
        )
        
        for element in sorted_elements:
            element_md = self.tier1_converter._convert_element(element)
            if element_md:
                parts.append(element_md)
        
        return "\n".join(parts)
    
    def _clean_markdown(self, markdown: str) -> str:
        """Clean and format Markdown"""
        return self.tier1_converter._clean_markdown(markdown)
    
    def _calculate_quality(
        self,
        document: ParsedDocument,
        markdown: str,
        warnings: List[str],
        errors: List[str]
    ) -> float:
        """Calculate quality score"""
        # Base quality from Tier 1
        quality = self.tier1_converter._calculate_quality(
            document, markdown, warnings, errors
        )
        
        # Bonus for successful spatial analysis
        if not errors:
            quality = min(1.0, quality + 0.1)
        
        return quality
