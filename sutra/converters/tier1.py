"""
Tier 1 Converter - Rule-based conversion for simple documents

Fast, deterministic conversion using pattern matching and templates.
Optimized for documents with:
- Simple structure (linear flow)
- Minimal formatting complexity
- Standard layouts
- Few tables and images

Target: 90% of documents
Cost: $0.001 per document
Speed: <1 second per document

Features:
- Pattern-based text extraction
- Template-driven formatting
- Heading detection and hierarchy
- List recognition (bullets, numbered)
- Basic table conversion
- Image placeholder generation
"""

import re
import time
from typing import List, Dict, Any, Optional

from ..models.document import ParsedDocument, DocumentElement, TableInfo, ImageInfo
from ..models.enums import ConversionTier, OutputFormat
from .base import BaseConverter, ConversionResult, ConversionError
from .outputs import StructuredOutputGenerator


class Tier1Converter(BaseConverter):
    """
    Rule-based converter for simple documents
    
    Uses deterministic patterns and templates to convert
    simple documents quickly and reliably.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize Tier 1 converter
        
        Args:
            config: Configuration options:
                - preserve_structure: True to preserve document structure
                - include_images: True to include image placeholders
                - include_tables: True to include tables
        """
        super().__init__(config)
        
        # Configuration
        self.preserve_structure = self.config.get('preserve_structure', True)
        self.include_images = self.config.get('include_images', True)
        self.include_tables = self.config.get('include_tables', True)
    
    @property
    def tier(self) -> ConversionTier:
        return ConversionTier.RULE_BASED
    
    def can_convert(self, document: ParsedDocument) -> bool:
        """
        Check if document is suitable for Tier 1 conversion
        
        Criteria:
        - Complexity score < 0.3
        - No complex tables
        - Few images
        - Simple structure
        """
        # Check if we have complexity metadata
        complexity = document.metadata.extra.get('complexity_score', 0.0)
        if complexity >= 0.3:
            return False
        
        # Check for complex tables
        if len(document.tables) > 5:
            return False
        
        for table in document.tables:
            if self._is_complex_table(table):
                return False
        
        # Too many images
        if len(document.images) > 10:
            return False
        
        return True
    
    async def convert(self, document: ParsedDocument, output_formats: Optional[List[OutputFormat]] = None) -> ConversionResult:
        """
        Convert document to multiple output formats using rule-based approach
        
        Args:
            document: Parsed document to convert
            output_formats: List of desired output formats (defaults to [OutputFormat.MARKDOWN])
            
        Returns:
            ConversionResult with generated content in all requested formats
        """
        if output_formats is None:
            output_formats = [OutputFormat.MARKDOWN]
            
        start_time = time.time()
        warnings: List[str] = []
        errors: List[str] = []
        stats = {
            'pages_processed': 0,
            'elements_processed': 0,
            'tables_found': len(document.tables),
            'images_found': len(document.images),
            'output_formats': [fmt.value for fmt in output_formats],
        }
        
        try:
            markdown_parts: List[str] = []
            
            # Add title if available
            if document.metadata.title:
                markdown_parts.append(f"# {document.metadata.title}\n")
            
            # Process by pages for structure preservation
            if self.preserve_structure and document.pages:
                for page in document.pages:
                    stats['pages_processed'] += 1
                    page_md = self._convert_page(page, stats)
                    if page_md:
                        markdown_parts.append(page_md)
            else:
                # Simple text extraction
                markdown_parts.append(self._format_text(document.text))
            
            # Add tables
            if self.include_tables and document.tables:
                markdown_parts.append("\n## Tables\n")
                for i, table in enumerate(document.tables, 1):
                    try:
                        table_md = self._convert_table(table, i)
                        markdown_parts.append(table_md)
                    except Exception as e:
                        warnings.append(f"Failed to convert table {i}: {str(e)}")
            
            # Add images
            if self.include_images and document.images:
                markdown_parts.append("\n## Images\n")
                for i, image in enumerate(document.images, 1):
                    image_md = self._convert_image(image, i)
                    markdown_parts.append(image_md)
            
            # Join and clean
            markdown = "\n\n".join(part for part in markdown_parts if part)
            markdown = self._clean_markdown(markdown)
            
            # Generate additional output formats
            outputs = {}
            if len(output_formats) > 1 or OutputFormat.MARKDOWN not in output_formats:
                generator = StructuredOutputGenerator()
                
                for format in output_formats:
                    if format == OutputFormat.MARKDOWN:
                        continue  # Already have markdown
                    elif format == OutputFormat.JSON:
                        outputs[format] = generator.generate_json(document)
                    elif format == OutputFormat.XML:
                        outputs[format] = generator.generate_xml(document)
                    elif format == OutputFormat.CSV:
                        outputs[format] = generator.generate_csv(document)
                    elif format == OutputFormat.YAML:
                        outputs[format] = generator.generate_yaml(document)
                    else:
                        warnings.append(f"Unsupported output format: {format.value}")
            
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
                outputs=outputs,
                metadata={
                    'converter': 'tier1',
                    'source_format': document.file_type,
                    'source_pages': document.num_pages,
                    'output_formats_generated': [fmt.value for fmt in output_formats],
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
            raise ConversionError(f"Tier 1 conversion failed: {str(e)}") from e
    
    def _convert_page(self, page: Any, stats: Dict[str, Any]) -> str:
        """Convert a single page to Markdown"""
        parts: List[str] = []
        
        # Add page marker (commented)
        parts.append(f"<!-- Page {page.page_number} -->\n")
        
        # Process elements if available
        if hasattr(page, 'elements') and page.elements:
            for element in page.elements:
                stats['elements_processed'] += 1
                element_md = self._convert_element(element)
                if element_md:
                    parts.append(element_md)
        else:
            # Fallback to page text
            parts.append(self._format_text(page.text))
        
        return "\n".join(parts)
    
    def _convert_element(self, element: DocumentElement) -> str:
        """Convert a document element to Markdown"""
        text = element.text.strip()
        
        if not text:
            return ""
        
        # Handle different element types
        if element.type == 'heading' or element.type == 'title':
            level = element.level or 2
            level = max(1, min(6, level))
            return f"{'#' * level} {text}\n"
        
        elif element.type == 'list_item':
            return f"- {text}\n"
        
        else:
            # Regular paragraph
            return f"{text}\n"
    
    def _format_text(self, text: str) -> str:
        """Format plain text into Markdown"""
        if not text:
            return ""
        
        lines = text.split('\n')
        formatted_lines: List[str] = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect headings (ALL CAPS or numbered)
            if line.isupper() and len(line) > 3:
                formatted_lines.append(f"## {line}\n")
            elif re.match(r'^\d+\.\s+[A-Z]', line):
                formatted_lines.append(f"## {line}\n")
            # Detect lists
            elif re.match(r'^\s*[•●○◦\-−]\s+', line):
                formatted_lines.append(f"- {line.lstrip('•●○◦-− ')}\n")
            # Regular paragraph
            else:
                formatted_lines.append(f"{line}\n")
        
        return "\n".join(formatted_lines)
    
    def _convert_table(self, table: TableInfo, index: int) -> str:
        """Convert table to Markdown pipe format"""
        if not table.rows:
            return ""
        
        lines: List[str] = []
        
        # Caption
        if table.caption:
            lines.append(f"### Table {index}: {table.caption}\n")
        else:
            lines.append(f"### Table {index}\n")
        
        # Header row
        header = table.rows[0]
        lines.append("| " + " | ".join(str(cell) for cell in header) + " |")
        lines.append("| " + " | ".join("---" for _ in header) + " |")
        
        # Data rows
        for row in table.rows[1:]:
            # Ensure same number of columns
            while len(row) < len(header):
                row.append("")
            lines.append("| " + " | ".join(str(cell) for cell in row[:len(header)]) + " |")
        
        return "\n".join(lines) + "\n"
    
    def _convert_image(self, image: ImageInfo, index: int) -> str:
        """Convert image to Markdown"""
        alt_text = image.caption or f"Image {index}"
        url = f"image_{image.id}.{image.format.lower()}"
        
        md = f"![{alt_text}]({url})"
        
        if image.caption:
            md += f"\n*{image.caption}*"
        
        return md + "\n"
    
    def _is_complex_table(self, table: TableInfo) -> bool:
        """Check if table is too complex for Tier 1"""
        # Too many rows
        if len(table.rows) > 20:
            return True
        
        # Too many columns
        if table.rows and len(table.rows[0]) > 10:
            return True
        
        return False
    
    def _clean_markdown(self, markdown: str) -> str:
        """Clean and format Markdown"""
        # Remove excessive blank lines
        while "\n\n\n" in markdown:
            markdown = markdown.replace("\n\n\n", "\n\n")
        
        # Trim whitespace
        lines = markdown.split('\n')
        lines = [line.rstrip() for line in lines]
        markdown = '\n'.join(lines)
        
        return markdown.strip() + "\n"
    
    def _calculate_quality(
        self,
        document: ParsedDocument,
        markdown: str,
        warnings: List[str],
        errors: List[str]
    ) -> float:
        """
        Calculate quality score for conversion
        
        Factors:
        - Content preservation (50%)
        - Structure preservation (30%)
        - Warnings/errors (20%)
        """
        quality = 1.0
        
        # Penalize for errors
        if errors:
            quality -= 0.3 * min(len(errors) / 5, 1.0)
        
        # Penalize for warnings
        if warnings:
            quality -= 0.2 * min(len(warnings) / 10, 1.0)
        
        # Check content preservation
        source_length = len(document.text)
        md_length = len(markdown)
        
        if source_length > 0:
            ratio = md_length / source_length
            # Should be roughly similar (0.7 - 1.5)
            if ratio < 0.5 or ratio > 2.0:
                quality -= 0.2
        
        return max(0.0, min(1.0, quality))
