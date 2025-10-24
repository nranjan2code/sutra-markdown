# Quick Reference: Pydantic Model Construction

## TableInfo Model

### Definition
```python
class TableInfo(BaseModel):
    id: str                          # REQUIRED
    rows: List[List[str]]           # REQUIRED - All rows as 2D list
    page_number: Optional[int] = None
    bbox: Optional[List[float]] = None
    caption: Optional[str] = None
```

### Correct Usage
```python
# Example: Extract table with headers and data
table_rows = [
    ["Name", "Age", "City"],           # Header row
    ["Alice", "30", "NYC"],            # Data row 1
    ["Bob", "25", "LA"]                # Data row 2
]

table_info = TableInfo(
    id=f"table_{index}",               # Unique identifier
    rows=table_rows,                    # ALL rows (headers + data)
    page_number=1,                      # Optional
    bbox=None,                          # Optional [x1, y1, x2, y2]
    caption="Employee Data"             # Optional
)
```

### Common Mistakes ❌
```python
# ❌ WRONG: Passing row count instead of rows
TableInfo(rows=5)  # TypeError!

# ❌ WRONG: Using non-existent fields
TableInfo(
    rows=rows,
    cols=3,          # Field doesn't exist
    headers=headers, # Field doesn't exist
    data=data_rows   # Field doesn't exist
)

# ❌ WRONG: Missing required 'id' field
TableInfo(rows=rows, page_number=1)  # ValidationError!
```

---

## ImageInfo Model

### Definition
```python
class ImageInfo(BaseModel):
    id: str                          # REQUIRED
    format: str                      # REQUIRED (e.g., "jpg", "png")
    width: int                       # REQUIRED
    height: int                      # REQUIRED
    bbox: Optional[List[float]] = None
    page_number: Optional[int] = None
    caption: Optional[str] = None
    data: Optional[bytes] = None
```

### Correct Usage
```python
image_info = ImageInfo(
    id=f"image_{page}_{index}",      # Unique identifier
    format="jpg",                     # Image format
    width=1920,                       # Width in pixels
    height=1080,                      # Height in pixels
    page_number=1,                    # Optional
    bbox=[100, 200, 300, 400],       # Optional [x1, y1, x2, y2]
    caption="Company Logo",           # Optional
    data=image_bytes                  # Optional raw image data
)
```

### Common Mistakes ❌
```python
# ❌ WRONG: Using 'image_index' instead of 'id'
ImageInfo(
    image_index=0,    # Field doesn't exist
    format="jpg",
    width=100,
    height=100
)

# ❌ WRONG: Using 'image_data' instead of 'data'
ImageInfo(
    id="img_0",
    format="jpg",
    width=100,
    height=100,
    image_data=bytes  # Wrong field name!
)

# ❌ WRONG: Missing required fields
ImageInfo(id="img_0")  # ValidationError! Missing format, width, height
```

---

## Parser-Specific ID Patterns

### Recommended ID Formats

| Parser | TableInfo ID | ImageInfo ID |
|--------|--------------|--------------|
| DOCX | `table_{index}` | `docx_image_{index}` |
| PPTX | `pptx_table_{slide}_{index}` | `pptx_image_{slide}_{index}` |
| XLSX | `xlsx_sheet_{index}` | N/A |
| CSV | `csv_table_0` | N/A |
| PDF | N/A | `pdf_page{page}_image{index}` |
| HTML | `table_{index}` | `html_image_{index}` |
| IMAGE | N/A | `image_0` |

---

## Full Examples

### Example 1: DOCX Table
```python
def _parse_table(self, table, table_index: int) -> TableInfo:
    # Extract all rows
    rows = []
    for row in table.rows:
        cells = [cell.text.strip() for cell in row.cells]
        rows.append(cells)
    
    # Create TableInfo (all rows as-is)
    return TableInfo(
        id=f"table_{table_index}",
        rows=rows,  # List[List[str]]
        page_number=table_index + 1,
        bbox=None,
        caption=None
    )
```

### Example 2: PDF Image
```python
def _extract_image(self, page, img_index: int, page_num: int) -> ImageInfo:
    base_image = self.doc.extract_image(xref)
    
    return ImageInfo(
        id=f"pdf_page{page_num + 1}_image{img_index}",
        format=base_image.get("ext", "unknown"),
        width=base_image.get("width", 0),
        height=base_image.get("height", 0),
        page_number=page_num + 1,
        data=base_image.get("image")  # Note: 'data' not 'image_data'
    )
```

### Example 3: XLSX Sheet (Table)
```python
def _process_sheet(self, sheet, sheet_index: int) -> TableInfo:
    headers = ["Col1", "Col2", "Col3"]
    data_rows = [
        ["val1", "val2", "val3"],
        ["val4", "val5", "val6"]
    ]
    
    # Combine headers and data
    all_rows = [headers] + data_rows
    
    return TableInfo(
        id=f"xlsx_sheet_{sheet_index}",
        rows=all_rows,  # Headers + data combined
        page_number=sheet_index + 1,
        bbox=None,
        caption=sheet.title
    )
```

---

## Validation Tips

### 1. Test with Pydantic Directly
```python
# This will raise ValidationError if incorrect
table = TableInfo(
    id="test",
    rows=[["A", "B"], ["1", "2"]]
)

image = ImageInfo(
    id="test",
    format="jpg",
    width=100,
    height=100
)
```

### 2. Check Field Names
```python
# Use model_fields to see what's available
print(TableInfo.model_fields.keys())
# dict_keys(['id', 'rows', 'page_number', 'bbox', 'caption'])

print(ImageInfo.model_fields.keys())
# dict_keys(['id', 'format', 'width', 'height', 'bbox', 
#            'page_number', 'caption', 'data'])
```

### 3. Validate Before Appending
```python
try:
    table_info = TableInfo(
        id=f"table_{idx}",
        rows=extracted_rows
    )
    tables.append(table_info)
except ValidationError as e:
    print(f"Invalid TableInfo: {e}")
```

---

## Migration Checklist

When updating parser code:

- [ ] Replace `image_index` with `id` (unique string)
- [ ] Replace `image_data` with `data`
- [ ] Change `rows=len(rows)` to `rows=actual_rows_list`
- [ ] Remove `cols`, `headers`, `data` fields from TableInfo
- [ ] Add `id` field to all TableInfo constructions
- [ ] Add `id` field to all ImageInfo constructions
- [ ] Combine headers and data into single `rows` list
- [ ] Test with actual files to verify Pydantic validation

---

## See Also

- [API Documentation](./API_DOCUMENTATION.md) - Complete API reference
- [Migration Guide](./MIGRATION_GUIDE.md) - V2.1 to V2.2 upgrade guide
- [sutra/models/](../sutra/models/) - Model source code
