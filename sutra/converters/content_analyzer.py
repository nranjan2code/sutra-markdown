"""
Enhanced Structured Content Analyzer

Analyzes and extracts structured content elements from document text:
- Headings hierarchy (H1, H2, H3...)
- Paragraphs
- Lists (bullets, numbered)
- Tables (if present in text)
- Document sections
- Content relationships
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass


@dataclass
class StructuredElement:
    """A structured content element"""
    type: str  # 'heading', 'paragraph', 'list', 'table', 'section'
    level: Optional[int] = None  # For headings (1-6)
    content: str = ""
    children: List['StructuredElement'] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.children is None:
            self.children = []
        if self.metadata is None:
            self.metadata = {}


class StructuredContentAnalyzer:
    """Analyzes document text and extracts structured content elements"""
    
    def __init__(self):
        # Patterns for detecting content types
        self.heading_patterns = [
            r'^#{1,6}\s+(.+)$',  # Markdown headings
            r'^([A-Z][A-Z\s]{2,})\s*$',  # ALL CAPS headings
            r'^(\d+\.?\s+[A-Z][^.]*)\s*$',  # Numbered headings
            r'^([A-Z][a-z].*?)\s*$'  # Title case (when isolated)
        ]
        
        self.list_patterns = [
            r'^\s*[•●○◦\-\*\+]\s+(.+)$',  # Bullet lists
            r'^\s*\d+[\.\)]\s+(.+)$',  # Numbered lists
            r'^\s*[a-zA-Z][\.\)]\s+(.+)$',  # Lettered lists
        ]
        
        self.table_patterns = [
            r'^\s*\|.*\|\s*$',  # Markdown table rows
            r'^.*\t.*\t.*$',  # Tab-separated data
        ]
    
    def analyze_document_structure(self, text: str) -> Dict[str, Any]:
        """Analyze entire document and return structured content"""
        lines = text.split('\n')
        elements = self._parse_lines_to_elements(lines)
        hierarchy = self._build_hierarchy(elements)
        
        return {
            'elements': [self._element_to_dict(elem) for elem in elements],
            'hierarchy': hierarchy,
            'stats': self._calculate_structure_stats(elements),
            'outline': self._generate_outline(elements)
        }
    
    def analyze_page_structure(self, page_text: str, page_number: int) -> Dict[str, Any]:
        """Analyze single page structure"""
        lines = page_text.split('\n')
        elements = self._parse_lines_to_elements(lines, page_number)
        
        return {
            'page_number': page_number,
            'elements': [self._element_to_dict(elem) for elem in elements],
            'stats': self._calculate_structure_stats(elements),
            'content_types': self._get_content_types(elements)
        }
    
    def _parse_lines_to_elements(self, lines: List[str], page_number: Optional[int] = None) -> List[StructuredElement]:
        """Parse lines of text into structured elements"""
        elements = []
        current_paragraph = []
        current_list = []
        current_list_type = None
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                # Empty line - finish current elements
                if current_paragraph:
                    elements.append(StructuredElement(
                        type='paragraph',
                        content=' '.join(current_paragraph),
                        metadata={'line_start': i - len(current_paragraph), 'page': page_number}
                    ))
                    current_paragraph = []
                
                if current_list:
                    elements.append(StructuredElement(
                        type='list',
                        content='\n'.join(current_list),
                        metadata={'list_type': current_list_type, 'items': len(current_list), 'page': page_number}
                    ))
                    current_list = []
                    current_list_type = None
                continue
            
            # Check for headings
            heading_match = self._detect_heading(line)
            if heading_match:
                # Finish previous elements
                if current_paragraph:
                    elements.append(StructuredElement(
                        type='paragraph',
                        content=' '.join(current_paragraph),
                        metadata={'line_start': i - len(current_paragraph), 'page': page_number}
                    ))
                    current_paragraph = []
                
                level, content = heading_match
                elements.append(StructuredElement(
                    type='heading',
                    level=level,
                    content=content,
                    metadata={'line': i, 'page': page_number}
                ))
                continue
            
            # Check for list items
            list_match = self._detect_list_item(line)
            if list_match:
                list_type, content = list_match
                if current_list_type != list_type:
                    # Different list type, finish previous
                    if current_list:
                        elements.append(StructuredElement(
                            type='list',
                            content='\n'.join(current_list),
                            metadata={'list_type': current_list_type, 'items': len(current_list), 'page': page_number}
                        ))
                    current_list = []
                    current_list_type = list_type
                
                current_list.append(content)
                continue
            
            # Check for table rows
            if self._detect_table_row(line):
                elements.append(StructuredElement(
                    type='table_row',
                    content=line,
                    metadata={'line': i, 'page': page_number}
                ))
                continue
            
            # Regular text - add to paragraph
            if current_list:
                # Finish list first
                elements.append(StructuredElement(
                    type='list',
                    content='\n'.join(current_list),
                    metadata={'list_type': current_list_type, 'items': len(current_list), 'page': page_number}
                ))
                current_list = []
                current_list_type = None
            
            current_paragraph.append(line)
        
        # Finish remaining elements
        if current_paragraph:
            elements.append(StructuredElement(
                type='paragraph',
                content=' '.join(current_paragraph),
                metadata={'page': page_number}
            ))
        
        if current_list:
            elements.append(StructuredElement(
                type='list',
                content='\n'.join(current_list),
                metadata={'list_type': current_list_type, 'items': len(current_list), 'page': page_number}
            ))
        
        return elements
    
    def _detect_heading(self, line: str) -> Optional[Tuple[int, str]]:
        """Detect if line is a heading and return (level, content)"""
        # Markdown style headings
        if line.startswith('#'):
            level = len(line) - len(line.lstrip('#'))
            content = line.lstrip('#').strip()
            return (min(level, 6), content)
        
        # ALL CAPS short lines (likely headings)
        if len(line) < 100 and line.isupper() and len(line.split()) >= 2:
            return (2, line)
        
        # Title case isolated lines
        if (len(line) < 80 and 
            line[0].isupper() and 
            not line.endswith('.') and 
            len(line.split()) <= 10):
            return (3, line)
        
        return None
    
    def _detect_list_item(self, line: str) -> Optional[Tuple[str, str]]:
        """Detect list items and return (type, content)"""
        # Bullet lists
        for pattern in [r'^\s*[•●○◦]\s+(.+)$', r'^\s*[\-\*\+]\s+(.+)$']:
            match = re.match(pattern, line)
            if match:
                return ('bullet', match.group(1))
        
        # Numbered lists
        match = re.match(r'^\s*(\d+)[\.\)]\s+(.+)$', line)
        if match:
            return ('numbered', match.group(2))
        
        # Lettered lists
        match = re.match(r'^\s*([a-zA-Z])[\.\)]\s+(.+)$', line)
        if match:
            return ('lettered', match.group(2))
        
        return None
    
    def _detect_table_row(self, line: str) -> bool:
        """Detect table rows"""
        # Markdown tables
        if '|' in line and line.count('|') >= 2:
            return True
        
        # Tab-separated
        if '\t' in line and line.count('\t') >= 2:
            return True
        
        return False
    
    def _build_hierarchy(self, elements: List[StructuredElement]) -> Dict[str, Any]:
        """Build hierarchical structure from flat list of elements"""
        hierarchy = {'sections': []}
        current_section = None
        
        for element in elements:
            if element.type == 'heading':
                if element.level == 1:
                    current_section = {
                        'title': element.content,
                        'level': 1,
                        'content': [],
                        'subsections': []
                    }
                    hierarchy['sections'].append(current_section)
                elif current_section:
                    current_section['subsections'].append({
                        'title': element.content,
                        'level': element.level,
                        'content': []
                    })
            elif current_section:
                if current_section['subsections']:
                    current_section['subsections'][-1]['content'].append(element)
                else:
                    current_section['content'].append(element)
        
        return hierarchy
    
    def _calculate_structure_stats(self, elements: List[StructuredElement]) -> Dict[str, int]:
        """Calculate statistics about document structure"""
        stats = {
            'total_elements': len(elements),
            'headings': 0,
            'paragraphs': 0,
            'lists': 0,
            'table_rows': 0,
        }
        
        heading_levels = {}
        
        for element in elements:
            if element.type in stats:
                stats[element.type] += 1
            
            if element.type == 'heading':
                level = element.level or 0
                heading_levels[level] = heading_levels.get(level, 0) + 1
        
        stats['heading_levels'] = heading_levels
        return stats
    
    def _get_content_types(self, elements: List[StructuredElement]) -> List[str]:
        """Get list of content types present"""
        return list(set(elem.type for elem in elements))
    
    def _generate_outline(self, elements: List[StructuredElement]) -> List[Dict[str, Any]]:
        """Generate document outline from headings"""
        outline = []
        
        for element in elements:
            if element.type == 'heading':
                outline.append({
                    'level': element.level,
                    'title': element.content,
                    'metadata': element.metadata
                })
        
        return outline
    
    def _element_to_dict(self, element: StructuredElement) -> Dict[str, Any]:
        """Convert StructuredElement to dictionary"""
        return {
            'type': element.type,
            'level': element.level,
            'content': element.content,
            'metadata': element.metadata or {},
            'children_count': len(element.children)
        }