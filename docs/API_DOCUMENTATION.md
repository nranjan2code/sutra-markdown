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
    "total_hits": 1250,
    "total_requests": 2000,
    "hit_rate": 0.625
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
  "markdown": "# Document Title\n\nContent...",
  "outputs": {
    "json": "{\"document_info\":{\"title\":\"Document Title\",...}}",
    "xml": "<?xml version=\"1.0\"?><document><title>Document Title</title>...</document>",
    "yaml": "document_info:\n  title: Document Title\n  pages: 121\n..."
  },
  "tier": "tier1",
  "quality_score": 0.975,
  "processing_time": 3.86,
  "word_count": 15420,
  "line_count": 892,
  "cached": false,
  "warnings": [],
  "complexity_analysis": {
    "score": 0.65,
    "confidence": 0.92,
    "reasoning": "Complex document with tables and charts",
    "metrics": {
      "structural_score": 0.7,
      "semantic_score": 0.8,
      "visual_score": 0.6,
      "density_score": 0.5,
      "special_score": 0.4,
      "layout_type": "multi_column",
      "page_count": 121,
      "table_count": 15,
      "image_count": 8,
      "topic_clusters": 12,
      "embedding_diversity": 0.82,
      "layout_complexity": 0.65,
      "visual_diversity": 0.71
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
  "created_at": "2024-01-15T10:30:00Z",
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
  "created_at": "2024-01-15T10:30:00Z",
  "started_at": "2024-01-15T10:30:02Z",
  "completed_at": "2024-01-15T10:30:15Z",
  "result": {
    "markdown": "# Document content...",
    "outputs": {
      "json": "{...}",
      "xml": "<?xml...>",
      "csv": "heading,content,page\n...",
      "yaml": "document_info:\n..."
    },
    "tier": "tier2",
    "quality_score": 0.92,
    "processing_time": 13.2,
    "word_count": 45000,
    "line_count": 2500,
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
  "created_at": "2024-01-15T10:30:00Z",
  "message": "Batch processing started"
}
```

### 6. Statistics

#### `GET /stats`

Get conversion statistics and metrics.

**Response:**
```json
{
  "total_conversions": 15420,
  "cache_hits": 8950,
  "cache_misses": 6470,
  "hit_rate": 0.58,
  "average_processing_time": 2.3,
  "tier_distribution": {
    "tier1": 13878,
    "tier2": 770,
    "tier3": 772
  },
  "format_distribution": {
    "markdown": 15420,
    "json": 8950,
    "xml": 4230,
    "csv": 2110,
    "yaml": 1890,
    "html": 950
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
    "title": "Sustainability Report FY 2023-24",
    "total_pages": 121,
    "processing_time": "3.86s",
    "quality_score": 100,
    "enhancement_strategy": "adaptive_structured"
  },
  "structured_content": {
    "total_elements": 217,
    "headings": 95,
    "paragraphs": 122,
    "lists": 0,
    "hierarchy": {
      "h1": 12,
      "h2": 34,
      "h3": 49
    }
  },
  "semantic_elements": [
    {
      "type": "heading",
      "level": 1,
      "text": "Executive Summary",
      "page": 3,
      "id": "exec-summary"
    },
    {
      "type": "paragraph",
      "text": "We are committed to creating sustainable value...",
      "page": 3,
      "word_count": 45
    },
    {
      "type": "heading",
      "level": 2,
      "text": "Environmental Performance",
      "page": 15,
      "id": "env-performance"
    }
  ],
  "tables": [
    {
      "id": "table_1",
      "caption": "Carbon Emissions by Region",
      "page": 25,
      "rows": [
        ["Region", "2023", "2024", "Change"],
        ["North America", "1250", "1180", "-5.6%"],
        ["Europe", "890", "850", "-4.5%"]
      ]
    }
  ],
  "images": [
    {
      "id": "img_1",
      "caption": "Renewable Energy Growth",
      "page": 32,
      "type": "chart"
    }
  ]
}
```

### XML Output Structure

```xml
<?xml version="1.0" encoding="UTF-8"?>
<document>
  <metadata>
    <title>Sustainability Report FY 2023-24</title>
    <pages>121</pages>
    <processing_time>3.86s</processing_time>
    <quality_score>100</quality_score>
  </metadata>
  <content>
    <section level="1" page="3" id="exec-summary">
      <heading>Executive Summary</heading>
      <paragraph>We are committed to creating sustainable value...</paragraph>
    </section>
    <section level="2" page="15" id="env-performance">
      <heading>Environmental Performance</heading>
      <paragraph>Our environmental initiatives focus on...</paragraph>
      <table id="table_1" page="25">
        <caption>Carbon Emissions by Region</caption>
        <row type="header">
          <cell>Region</cell>
          <cell>2023</cell>
          <cell>2024</cell>
          <cell>Change</cell>
        </row>
        <row>
          <cell>North America</cell>
          <cell>1250</cell>
          <cell>1180</cell>
          <cell>-5.6%</cell>
        </row>
      </table>
    </section>
  </content>
</document>
```

### CSV Output Structure

```csv
type,level,text,page,parent_id,word_count
heading,1,"Executive Summary",3,,2
paragraph,,"We are committed to creating sustainable value through innovative practices and responsible business operations.",3,exec-summary,16
heading,2,"Environmental Performance",15,,2
paragraph,,"Our environmental initiatives focus on reducing carbon emissions and increasing renewable energy usage.",15,env-performance,15
table,,"Carbon Emissions by Region",25,env-performance,4
table_row,,"Region,2023,2024,Change",25,table_1,4
table_row,,"North America,1250,1180,-5.6%",25,table_1,4
```

### YAML Output Structure

```yaml
document_info:
  title: "Sustainability Report FY 2023-24"
  total_pages: 121
  processing_time: "3.86s"
  quality_score: 100
  enhancement_strategy: "adaptive_structured"

structured_content:
  total_elements: 217
  headings: 95
  paragraphs: 122
  lists: 0
  hierarchy:
    h1: 12
    h2: 34
    h3: 49

semantic_elements:
  - type: heading
    level: 1
    text: "Executive Summary"
    page: 3
    id: "exec-summary"
  
  - type: paragraph
    text: "We are committed to creating sustainable value..."
    page: 3
    word_count: 45
    parent_id: "exec-summary"
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
    "report.pdf", 
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
  "request_id": "req_123456"
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

## 📞 Support

- 📧 Email: api-support@sutra-markdown.com
- 📖 Full Documentation: [docs.sutra-markdown.com](https://docs.sutra-markdown.com)
- 🐛 Issues: [GitHub Issues](https://github.com/nranjan2code/sutra-markdown/issues)
- 💬 Discord: [Join our community](https://discord.gg/sutra)

---

**API Version**: 2.1.0  
**Last Updated**: January 2024  
**Status**: Production Ready ✅