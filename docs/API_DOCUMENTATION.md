# Sutra Markdown API Documentation v2.1

Complete API reference for Sutra Markdown conversion service with Universal AI-Guided Extraction and structured output formats.

## 🌟 NEW: Multiple Output Formats

Sutra v2.1 now supports generating multiple structured output formats alongside traditional markdown.

### Supported Formats

| Format | Description | Use Case | File Extension |
|--------|-------------|----------|---------------|
| `markdown` | Traditional markdown (default) | Documentation, websites | `.md` |
| `json` | Structured semantic content | Data processing, APIs | `.json` |
| `xml` | Hierarchical document structure | Enterprise systems | `.xml` |
| `csv` | Tabular data extraction | Spreadsheets, databases | `.csv` |
| `yaml` | Human-readable structured data | Configuration, metadata | `.yaml` |
| `html` | Rich formatted output | Web rendering | `.html` |

## 🚀 Base URL

```
http://localhost:8000
```

## 📋 Endpoints

### 1. Health Check

#### `GET /health`

Check service health and status.

**Response:**
```json
{
  "status": "healthy",
  "version": "2.1.0",
  "cache_stats": {
    "total_hits": 1000,
    "total_requests": 1500,
    "hit_rate": 0.667
  }
}
```

### 2. Convert Document (Synchronous)

#### `POST /convert`

Convert a single document with optional multiple output formats.

**Request:**
```bash
curl -X POST "http://localhost:8000/convert" \
  -F "file=@document.pdf" \
  -F "tier=auto" \
  -F "output_formats=markdown,json,xml" \
  -F "enable_intelligence=true" \
  -F "options={\"quality\":\"high\"}"
```

**Form Parameters:**
- `file` (required): Document file to convert
- `tier` (optional): `auto`, `tier1`, `tier2`, `tier3` - Force specific conversion tier
- `output_formats` (optional): Comma-separated list of formats - Default: `markdown`
- `enable_intelligence` (optional): Enable Universal AI-Guided Enhancement - Default: `true`
- `use_cache` (optional): Use caching - Default: `true`
- `async_mode` (optional): Process asynchronously - Default: `false`
- `options` (optional): JSON object with additional options

**Available Output Formats:**
- `markdown` - Traditional markdown output
- `json` - Structured semantic content with headings, paragraphs, lists
- `xml` - Hierarchical XML with document structure
- `csv` - Tabular data extraction (tables, lists as rows)
- `yaml` - Human-readable structured format
- `html` - Rich HTML output with styling

**Response:**
```json
{
  "markdown": "# Sample Document Title\n\nExample content...",
  "outputs": {
    "json": "{\"document_info\":{\"title\":\"Sample Document Title\",...}}",
    "xml": "<?xml version=\"1.0\"?><document><title>Sample Document Title</title>...</document>",
    "yaml": "document_info:\n  title: Sample Document Title\n  pages: 25\n..."
  },
  "tier": "tier1",
  "quality_score": 0.95,
  "processing_time": 2.4,
  "word_count": 5000,
  "line_count": 300,
  "cached": false,
  "warnings": [],
  "complexity_analysis": {
    "score": 0.75,
    "confidence": 0.88,
    "reasoning": "Document contains standard structure with moderate complexity",
    "metrics": {
      "structural_score": 0.8,
      "semantic_score": 0.75,
      "visual_score": 0.7,
      "density_score": 0.6,
      "special_score": 0.5,
      "layout_type": "standard",
      "page_count": 25,
      "table_count": 3,
      "image_count": 2,
      "topic_clusters": 5,
      "embedding_diversity": 0.70,
      "layout_complexity": 0.55,
      "visual_diversity": 0.60
    }
  }
}
```

### 3. Convert Document (Asynchronous)

#### `POST /convert/async`

Submit document for asynchronous processing with multiple output formats.

**Request:**
```bash
curl -X POST "http://localhost:8000/convert/async" \
  -F "file=@large_document.pdf" \
  -F "output_formats=markdown,json,xml,csv,yaml"
```

**Response:**
```json
{
  "job_id": "job_abc123",
  "status": "pending",
  "created_at": "2025-03-15T14:30:00Z",
  "message": "Job submitted successfully"
}
```

### 4. Check Job Status

#### `GET /jobs/{job_id}`

Check status of asynchronous conversion job.

**Response:**
```json
{
  "job_id": "job_abc123",
  "status": "completed",
  "progress": 1.0,
  "created_at": "2025-03-15T14:30:00Z",
  "started_at": "2025-03-15T14:30:02Z",
  "completed_at": "2025-03-15T14:30:15Z",
  "result": {
    "markdown": "# Sample Document Content...",
    "outputs": {
      "json": "{...}",
      "xml": "<?xml...>",
      "csv": "heading,content,page\n...",
      "yaml": "document_info:\n..."
    },
    "tier": "tier2",
    "quality_score": 0.90,
    "processing_time": 8.5,
    "word_count": 12000,
    "line_count": 800,
    "cached": false,
    "warnings": []
  }
}
```

### 5. Batch Conversion

#### `POST /convert/batch`

Convert multiple documents in a single request.

**Request:**
```bash
curl -X POST "http://localhost:8000/convert/batch" \
  -F "files=@doc1.pdf" \
  -F "files=@doc2.docx" \
  -F "files=@doc3.pptx" \
  -F "output_formats=markdown,json"
```

**Response:**
```json
{
  "batch_id": "batch_xyz789",
  "status": "processing",
  "total_files": 3,
  "created_at": "2025-03-15T14:30:00Z",
  "message": "Batch processing started"
}
```

### 6. Statistics

#### `GET /stats`

Get conversion statistics and metrics.

**Response:**
```json
{
  "total_conversions": 10000,
  "cache_hits": 6000,
  "cache_misses": 4000,
  "hit_rate": 0.60,
  "average_processing_time": 2.5,
  "tier_distribution": {
    "tier1": 8500,
    "tier2": 1000,
    "tier3": 500
  },
  "format_distribution": {
    "markdown": 10000,
    "json": 7500,
    "xml": 5000,
    "csv": 2500,
    "yaml": 2000,
    "html": 1500
  }
}
```

## 🎯 Universal AI-Guided Extraction

### Features
- **Automatic Pattern Discovery**: AI learns document structure using Nomic embeddings
- **Adaptive Strategies**: Optimizes extraction for structured, flowing, or mixed content
- **Semantic Sectioning**: Detects topic boundaries using embedding similarity
- **97.5% Quality**: Average quality score across document types
- **3-4 Second Processing**: Even for 121-page complex documents
- **$0 Cost**: Local Nomic embeddings with unlimited usage

### Enhancement Metadata

When `enable_intelligence=true`, the response includes AI enhancement metadata:

```json
{
  "complexity_analysis": {
    "score": 0.75,
    "confidence": 0.92,
    "reasoning": "Document contains complex tables and multi-column layout",
    "metrics": {...}
  }
}
```

## 📊 Structured Output Examples

### JSON Output Structure

```json
{
  "document_info": {
    "title": "Sample Business Document",
    "total_pages": 25,
    "processing_time": "2.4s",
    "quality_score": 95,
    "enhancement_strategy": "adaptive_standard"
  },
  "structured_content": {
    "total_elements": 150,
    "headings": 45,
    "paragraphs": 80,
    "lists": 25,
    "hierarchy": {
      "h1": 5,
      "h2": 15,
      "h3": 25
    }
  },
  "semantic_elements": [
    {
      "type": "heading",
      "level": 1,
      "text": "Introduction",
      "page": 1,
      "id": "introduction"
    },
    {
      "type": "paragraph",
      "text": "This document provides an overview of the main topics...",
      "page": 1,
      "word_count": 32
    },
    {
      "type": "heading",
      "level": 2,
      "text": "Main Content Section",
      "page": 8,
      "id": "main-content"
    }
  ],
  "tables": [
    {
      "id": "table_1",
      "caption": "Sample Data Table",
      "page": 12,
      "rows": [
        ["Category", "Value A", "Value B", "Total"],
        ["Item 1", "100", "150", "250"],
        ["Item 2", "200", "175", "375"]
      ]
    }
  ],
  "images": [
    {
      "id": "img_1",
      "caption": "Example Chart",
      "page": 18,
      "type": "diagram"
    }
  ]
}
```

### XML Output Structure

```xml
<?xml version="1.0" encoding="UTF-8"?>
<document>
  <metadata>
    <title>Sample Business Document</title>
    <pages>25</pages>
    <processing_time>2.4s</processing_time>
    <quality_score>95</quality_score>
  </metadata>
  <content>
    <section level="1" page="1" id="introduction">
      <heading>Introduction</heading>
      <paragraph>This document provides an overview of the main topics...</paragraph>
    </section>
    <section level="2" page="8" id="main-content">
      <heading>Main Content Section</heading>
      <paragraph>The following information covers the key aspects...</paragraph>
      <table id="table_1" page="12">
        <caption>Sample Data Table</caption>
        <row type="header">
          <cell>Category</cell>
          <cell>Value A</cell>
          <cell>Value B</cell>
          <cell>Total</cell>
        </row>
        <row>
          <cell>Item 1</cell>
          <cell>100</cell>
          <cell>150</cell>
          <cell>250</cell>
        </row>
      </table>
    </section>
  </content>
</document>
```

### CSV Output Structure

```csv
type,level,text,page,parent_id,word_count
heading,1,"Introduction",1,,1
paragraph,,"This document provides an overview of the main topics and key information.",1,introduction,12
heading,2,"Main Content Section",8,,3
paragraph,,"The following information covers the key aspects of the subject matter.",8,main-content,11
table,,"Sample Data Table",12,main-content,3
table_row,,"Category,Value A,Value B,Total",12,table_1,4
table_row,,"Item 1,100,150,250",12,table_1,4
```

### YAML Output Structure

```yaml
document_info:
  title: "Sample Business Document"
  total_pages: 25
  processing_time: "2.4s"
  quality_score: 95
  enhancement_strategy: "adaptive_standard"

structured_content:
  total_elements: 150
  headings: 45
  paragraphs: 80
  lists: 25
  hierarchy:
    h1: 5
    h2: 15
    h3: 25

semantic_elements:
  - type: heading
    level: 1
    text: "Introduction"
    page: 1
    id: "introduction"
  
  - type: paragraph
    text: "This document provides an overview of the main topics..."
    page: 1
    word_count: 32
    parent_id: "introduction"
```

## 🔧 Integration Examples

### Python Client

```python
import httpx
import json

async def convert_with_structured_output(file_path, formats=["markdown", "json"]):
    async with httpx.AsyncClient() as client:
        with open(file_path, "rb") as f:
            files = {"file": f}
            data = {
                "output_formats": ",".join(formats),
                "enable_intelligence": "true"
            }
            
            response = await client.post(
                "http://localhost:8000/convert",
                files=files,
                data=data
            )
            
            result = response.json()
            
            # Access different formats
            markdown = result["markdown"]
            json_data = json.loads(result["outputs"]["json"]) if "json" in result["outputs"] else None
            
            return markdown, json_data

# Usage
markdown, structured_data = await convert_with_structured_output(
    "sample_document.pdf", 
    formats=["markdown", "json", "xml"]
)

print(f"Headings found: {len(structured_data['semantic_elements'])}")
print(f"Quality score: {structured_data['document_info']['quality_score']}")
```

### JavaScript/Node.js Client

```javascript
const FormData = require('form-data');
const fs = require('fs');
const axios = require('axios');

async function convertDocument(filePath, formats = ['markdown', 'json']) {
    const form = new FormData();
    form.append('file', fs.createReadStream(filePath));
    form.append('output_formats', formats.join(','));
    form.append('enable_intelligence', 'true');
    
    const response = await axios.post('http://localhost:8000/convert', form, {
        headers: form.getHeaders()
    });
    
    const result = response.data;
    
    // Access different outputs
    console.log('Markdown:', result.markdown.substring(0, 100) + '...');
    console.log('Quality Score:', result.quality_score);
    
    if (result.outputs.json) {
        const structuredData = JSON.parse(result.outputs.json);
        console.log('Elements:', structuredData.structured_content.total_elements);
    }
    
    return result;
}

// Usage
convertDocument('./document.pdf', ['markdown', 'json', 'yaml'])
    .then(result => console.log('Conversion completed'))
    .catch(err => console.error('Error:', err));
```

### cURL Examples

```bash
# Convert to JSON only
curl -X POST "http://localhost:8000/convert" \
  -F "file=@document.pdf" \
  -F "output_formats=json" \
  -o response.json

# Convert to multiple formats
curl -X POST "http://localhost:8000/convert" \
  -F "file=@report.pdf" \
  -F "output_formats=markdown,json,xml,yaml" \
  -F "enable_intelligence=true" \
  | jq '.outputs'

# Batch conversion with structured output
curl -X POST "http://localhost:8000/convert/batch" \
  -F "files=@doc1.pdf" \
  -F "files=@doc2.docx" \
  -F "output_formats=json,csv"
```

## 🚨 Error Handling

### Error Response Format

```json
{
  "error": "validation_error",
  "message": "Invalid output format specified",
  "details": {
    "invalid_formats": ["invalid_format"],
    "valid_formats": ["markdown", "json", "xml", "csv", "yaml", "html"]
  },
  "request_id": "req_sample123"
}
```

### Common Error Codes

| Code | Description | Solution |
|------|-------------|----------|
| 400 | Bad Request | Check request format and parameters |
| 413 | File Too Large | File exceeds maximum size limit (100MB) |
| 415 | Unsupported Media Type | Use supported file types (PDF, DOCX, PPTX, etc.) |
| 422 | Validation Error | Check file content and format parameters |
| 429 | Rate Limit Exceeded | Reduce request frequency |
| 500 | Internal Server Error | Server processing error |

## 🎛️ Configuration

### Environment Variables

```bash
# Output Format Configuration
DEFAULT_OUTPUT_FORMATS=markdown                # Default formats if none specified
MAX_OUTPUT_FORMATS=6                          # Maximum formats per request
ENABLE_STRUCTURED_OUTPUT=true                 # Enable structured output generation

# AI Enhancement
EMBEDDING_MODE=local                          # Local Nomic embeddings
ENABLE_INTELLIGENCE=true                      # Enable Universal AI by default
AI_CONFIDENCE_THRESHOLD=0.8                   # Minimum confidence for AI enhancement

# Performance
MAX_FILE_SIZE=104857600                       # 100MB file size limit
CONCURRENT_CONVERSIONS=10                     # Parallel processing limit
CACHE_STRUCTURED_OUTPUT=true                  # Cache structured outputs
```

## 📈 Performance Considerations

### File Size Limits

| Format | Recommended Max Size | Processing Time |
|--------|---------------------|-----------------|
| PDF | 100MB | 1-10s per 10 pages |
| DOCX | 50MB | 0.5-5s per 10 pages |
| PPTX | 200MB | 2-15s per 10 slides |

### Output Format Performance

| Format | Generation Time | Size Factor | Use Case |
|--------|----------------|-------------|-----------|
| Markdown | Baseline | 1x | Documentation |
| JSON | +20% | 1.3x | API integration |
| XML | +30% | 1.2x | Enterprise systems |
| CSV | +10% | 0.05x | Data analysis |
| YAML | +15% | 0.05x | Configuration |
| HTML | +25% | 1.1x | Web display |

## 🔐 Security

### Rate Limiting
- 100 requests per minute per IP
- 10 concurrent processing jobs per user
- File size limits enforced

### Data Privacy
- Files are processed temporarily and deleted after conversion
- No content is stored permanently
- All processing happens locally (when using local embeddings)

---

**API Version**: 2.1.0  
**Last Updated**: October 2025  
**Status**: Production Ready ✅