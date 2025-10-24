"""
Structured Output Generators

Convert parsed documents directly to structured formats alongside markdown.
"""

import json
import csv
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional
from io import StringIO
from datetime import datetime

from ..models.document import ParsedDocument, DocumentElement, PageInfo, ImageInfo, TableInfo
from ..models.enums import OutputFormat


class StructuredOutputGenerator:
    """Generate structured output formats from parsed documents"""
    
    def __init__(self):
        pass
    
    def generate_json(self, document: ParsedDocument) -> str:
        """Generate JSON representation of document structure"""
        doc_dict = {
            "document_id": document.id,
            "metadata": {
                "file_path": document.file_path,
                "file_type": document.file_type,
                "file_size": document.file_size,
                "title": document.metadata.title,
                "author": document.metadata.author,
                "created_date": document.metadata.created_date,
                "page_count": document.metadata.page_count,
                "word_count": document.metadata.word_count,
                "language": document.metadata.language,
            },
            "content": {
                "full_text": document.text,
                "pages": []
            },
            "structure": {
                "images": [],
                "tables": [],
                "elements": []
            },
            "generated_at": datetime.now().isoformat()
        }
        
        # Add pages
        for page in document.pages:
            page_dict = {
                "page_number": page.page_number,
                "text": page.text,
                "dimensions": {
                    "width": page.width,
                    "height": page.height
                },
                "elements": [self._element_to_dict(elem) for elem in page.elements],
                "images": [self._image_to_dict(img) for img in page.images],
                "tables": [self._table_to_dict(table) for table in page.tables]
            }
            doc_dict["content"]["pages"].append(page_dict)
        
        # Add global images and tables
        doc_dict["structure"]["images"] = [self._image_to_dict(img) for img in document.images]
        doc_dict["structure"]["tables"] = [self._table_to_dict(table) for table in document.tables]
        
        return json.dumps(doc_dict, indent=2, ensure_ascii=False)
    
    def generate_xml(self, document: ParsedDocument) -> str:
        """Generate XML representation of document structure"""
        root = ET.Element("document")
        root.set("id", document.id)
        root.set("generated_at", datetime.now().isoformat())
        
        # Metadata
        metadata_elem = ET.SubElement(root, "metadata")
        ET.SubElement(metadata_elem, "file_path").text = document.file_path
        ET.SubElement(metadata_elem, "file_type").text = document.file_type
        ET.SubElement(metadata_elem, "file_size").text = str(document.file_size)
        if document.metadata.title:
            ET.SubElement(metadata_elem, "title").text = document.metadata.title
        if document.metadata.author:
            ET.SubElement(metadata_elem, "author").text = document.metadata.author
        
        # Content
        content_elem = ET.SubElement(root, "content")
        ET.SubElement(content_elem, "full_text").text = document.text
        
        # Pages
        pages_elem = ET.SubElement(content_elem, "pages")
        for page in document.pages:
            page_elem = ET.SubElement(pages_elem, "page")
            page_elem.set("number", str(page.page_number))
            page_elem.set("width", str(page.width))
            page_elem.set("height", str(page.height))
            ET.SubElement(page_elem, "text").text = page.text
            
            # Page elements
            if page.elements:
                elements_elem = ET.SubElement(page_elem, "elements")
                for elem in page.elements:
                    elem_xml = ET.SubElement(elements_elem, "element")
                    elem_xml.set("type", elem.type)
                    elem_xml.set("page", str(elem.page_number))
                    if elem.level:
                        elem_xml.set("level", str(elem.level))
                    elem_xml.text = elem.text
        
        # Structure
        structure_elem = ET.SubElement(root, "structure")
        
        # Images
        if document.images:
            images_elem = ET.SubElement(structure_elem, "images")
            for img in document.images:
                img_elem = ET.SubElement(images_elem, "image")
                img_elem.set("id", img.id)
                img_elem.set("format", img.format)
                img_elem.set("width", str(img.width))
                img_elem.set("height", str(img.height))
                if img.page_number:
                    img_elem.set("page", str(img.page_number))
                if img.caption:
                    ET.SubElement(img_elem, "caption").text = img.caption
        
        # Tables
        if document.tables:
            tables_elem = ET.SubElement(structure_elem, "tables")
            for table in document.tables:
                table_elem = ET.SubElement(tables_elem, "table")
                table_elem.set("id", table.id)
                if table.page_number:
                    table_elem.set("page", str(table.page_number))
                if table.caption:
                    ET.SubElement(table_elem, "caption").text = table.caption
                
                # Table rows
                for i, row in enumerate(table.rows):
                    row_elem = ET.SubElement(table_elem, "row")
                    row_elem.set("index", str(i))
                    for j, cell in enumerate(row):
                        cell_elem = ET.SubElement(row_elem, "cell")
                        cell_elem.set("index", str(j))
                        cell_elem.text = cell
        
        return ET.tostring(root, encoding='unicode', xml_declaration=True)
    
    def generate_csv(self, document: ParsedDocument) -> str:
        """Generate CSV representation focusing on tabular data"""
        output = StringIO()
        writer = csv.writer(output)
        
        # Write metadata header
        writer.writerow(["Document Metadata"])
        writer.writerow(["File Path", document.file_path])
        writer.writerow(["File Type", document.file_type])
        writer.writerow(["File Size", document.file_size])
        writer.writerow(["Pages", len(document.pages)])
        writer.writerow(["Tables", len(document.tables)])
        writer.writerow(["Images", len(document.images)])
        writer.writerow([])  # Empty row
        
        # Write tables
        for i, table in enumerate(document.tables):
            writer.writerow([f"Table {i+1} (ID: {table.id})"])
            if table.caption:
                writer.writerow(["Caption", table.caption])
            if table.page_number:
                writer.writerow(["Page", table.page_number])
            writer.writerow([])  # Empty row
            
            # Write table data
            for row in table.rows:
                writer.writerow(row)
            writer.writerow([])  # Empty row
        
        return output.getvalue()
    
    def generate_yaml(self, document: ParsedDocument) -> str:
        """Generate YAML representation of document structure"""
        try:
            import yaml
        except ImportError:
            # Fallback to simple YAML-like format
            return self._generate_simple_yaml(document)
        
        doc_dict = {
            "document_id": document.id,
            "metadata": {
                "file_path": document.file_path,
                "file_type": document.file_type,
                "file_size": document.file_size,
                "title": document.metadata.title,
                "author": document.metadata.author,
                "page_count": len(document.pages),
                "table_count": len(document.tables),
                "image_count": len(document.images),
            },
            "content_summary": {
                "total_text_length": len(document.text),
                "word_count": len(document.text.split()) if document.text else 0,
            },
            "structure": {
                "pages": [
                    {
                        "page_number": page.page_number,
                        "text_length": len(page.text),
                        "element_count": len(page.elements),
                        "image_count": len(page.images),
                        "table_count": len(page.tables),
                    }
                    for page in document.pages
                ],
                "tables": [
                    {
                        "id": table.id,
                        "rows": len(table.rows),
                        "cols": len(table.rows[0]) if table.rows else 0,
                        "page": table.page_number,
                        "caption": table.caption,
                    }
                    for table in document.tables
                ],
                "images": [
                    {
                        "id": img.id,
                        "format": img.format,
                        "width": img.width,
                        "height": img.height,
                        "page": img.page_number,
                        "caption": img.caption,
                    }
                    for img in document.images
                ]
            },
            "generated_at": datetime.now().isoformat()
        }
        
        return yaml.dump(doc_dict, default_flow_style=False, allow_unicode=True, indent=2)
    
    def _generate_simple_yaml(self, document: ParsedDocument) -> str:
        """Generate simple YAML-like format without yaml library"""
        lines = [
            f"document_id: {document.id}",
            "metadata:",
            f"  file_path: {document.file_path}",
            f"  file_type: {document.file_type}",
            f"  file_size: {document.file_size}",
            f"  page_count: {len(document.pages)}",
            f"  table_count: {len(document.tables)}",
            f"  image_count: {len(document.images)}",
            "",
            "content_summary:",
            f"  total_text_length: {len(document.text)}",
            f"  word_count: {len(document.text.split()) if document.text else 0}",
            "",
            "structure:",
            "  pages:",
        ]
        
        for page in document.pages:
            lines.extend([
                f"    - page_number: {page.page_number}",
                f"      text_length: {len(page.text)}",
                f"      element_count: {len(page.elements)}",
            ])
        
        if document.tables:
            lines.append("  tables:")
            for table in document.tables:
                lines.extend([
                    f"    - id: {table.id}",
                    f"      rows: {len(table.rows)}",
                    f"      cols: {len(table.rows[0]) if table.rows else 0}",
                ])
        
        lines.append(f"generated_at: {datetime.now().isoformat()}")
        return "\n".join(lines)
    
    def _element_to_dict(self, element: DocumentElement) -> Dict[str, Any]:
        """Convert DocumentElement to dictionary"""
        return {
            "type": element.type,
            "text": element.text,
            "level": element.level,
            "page_number": element.page_number,
            "bbox": element.bbox,
            "metadata": element.metadata
        }
    
    def _image_to_dict(self, image: ImageInfo) -> Dict[str, Any]:
        """Convert ImageInfo to dictionary"""
        return {
            "id": image.id,
            "format": image.format,
            "width": image.width,
            "height": image.height,
            "bbox": image.bbox,
            "page_number": image.page_number,
            "caption": image.caption,
            "has_data": image.data is not None
        }
    
    def _table_to_dict(self, table: TableInfo) -> Dict[str, Any]:
        """Convert TableInfo to dictionary"""
        return {
            "id": table.id,
            "rows": table.rows,
            "page_number": table.page_number,
            "bbox": table.bbox,
            "caption": table.caption,
            "row_count": len(table.rows),
            "col_count": len(table.rows[0]) if table.rows else 0
        }