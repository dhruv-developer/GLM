# GLM Vision API Integration - Complete Documentation

## Overview

This document describes the complete integration of GLM Vision API (GLM-4.6V) into the ZIEL-MAS multi-agent system, providing powerful image and video analysis capabilities.

## Table of Contents

1. [Features](#features)
2. [Architecture](#architecture)
3. [Backend Implementation](#backend-implementation)
4. [Frontend Implementation](#frontend-implementation)
5. [API Endpoints](#api-endpoints)
6. [Usage Examples](#usage-examples)
7. [Configuration](#configuration)
8. [Troubleshooting](#troubleshooting)

---

## Features

### Vision Analysis Types

1. **General Image Analysis**
   - Detailed image description and understanding
   - Object detection and recognition
   - Scene interpretation

2. **Text Extraction (OCR)**
   - Extract text from screenshots
   - Parse code snippets with syntax preservation
   - Handle documents with structured output

3. **Error Diagnosis**
   - Analyze error screenshots
   - Root cause analysis
   - Actionable fix recommendations
   - Code examples when applicable

4. **UI to Code**
   - Convert UI designs to code
   - Support for multiple frameworks (React, Vue, Angular)
   - Generate responsive, accessible components
   - Include styling and usage examples

5. **Diagram Understanding**
   - Technical diagrams (architecture, flowcharts, UML, ER)
   - Component relationships
   - Flow and interactions
   - Implementation recommendations

6. **Chart Analysis**
   - Data visualization understanding
   - Trend identification
   - Anomaly detection
   - Actionable insights

7. **Video Analysis**
   - Scene description
   - Moment identification
   - Entity recognition
   - Up to 8MB video support

---

## Architecture

### Backend Components

```
backend/
├── agents/
│   ├── vision_agent.py          # Main vision agent implementation
│   └── base_agent.py            # Base agent class
├── models/
│   ├── agent.py                 # Agent type enums and configs
│   └── task.py                  # Task models with VISION agent type
├── core/
│   └── execution.py             # Updated to include vision agent
└── api/
    └── main.py                  # Vision API endpoints
```

### Frontend Components

```
frontend/
├── components/
│   ├── VisionImageUpload.tsx    # Image upload component
│   └── VisionResultDisplay.tsx  # Results display component
├── app/
│   └── vision/
│       └── page.tsx             # Vision demo page
├── lib/
│   └── api.ts                   # Vision API client functions
└── types/
    └── index.ts                 # Vision types and interfaces
```

---

## Backend Implementation

### Vision Agent

The `VisionAgent` class extends `BaseAgent` and implements all vision analysis capabilities:

```python
class VisionAgent(BaseAgent):
    """
    Vision Agent - Analyzes images and videos using GLM Vision API
    """

    def __init__(self):
        super().__init__("Vision Agent", "vision")
        self.zai_api_key = os.getenv("ZAI_API_KEY", "")
        self.zai_api_url = os.getenv("ZAI_API_URL", "https://open.bigmodel.cn/api/paas/v4")
```

### Agent Actions

```python
async def execute(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    actions = {
        "analyze_image": self._analyze_image,
        "analyze_video": self._analyze_video,
        "extract_text": self._extract_text,
        "diagnose_error": self._diagnose_error,
        "ui_to_code": self._ui_to_code,
        "understand_diagram": self._understand_diagram,
        "analyze_chart": self._analyze_chart,
        "compare_ui": self._compare_ui,
    }
```

### API Endpoints

#### 1. Analyze Image (File Upload)

```http
POST /api/v1/vision/analyze
Content-Type: multipart/form-data

Parameters:
- file: Image file (required)
- prompt: Analysis prompt (optional)
- analysis_type: Analysis type (optional, default: "general")
- context: Additional context (optional)
```

#### 2. Analyze Image (Base64)

```http
POST /api/v1/vision/analyze-base64
Content-Type: application/json

{
  "image_base64": "data:image/png;base64,...",
  "prompt": "Describe this image",
  "analysis_type": "general",
  "context": "",
  "framework": "React",
  "language": "TypeScript"
}
```

#### 3. Analyze Video

```http
POST /api/v1/vision/analyze-video
Content-Type: multipart/form-data

Parameters:
- file: Video file (required, max 8MB)
- prompt: Analysis prompt (optional)
```

#### 4. Compare UI

```http
POST /api/v1/vision/compare-ui
Content-Type: multipart/form-data

Parameters:
- image1: First image (required)
- image2: Second image (required)
```

---

## Frontend Implementation

### Image Upload Component

The `VisionImageUpload` component provides:

- **Drag & Drop Interface**: Easy file upload
- **Analysis Type Selection**: Choose from 6 analysis types
- **Custom Prompts**: Override default prompts
- **Context Input**: Add context for error diagnosis
- **Preview**: See the uploaded image before analysis

```tsx
<VisionImageUpload
  onAnalysisComplete={(result) => console.log(result)}
  onError={(error) => console.error(error)}
/>
```

### Result Display Component

The `VisionResultDisplay` component shows:

- **Analysis Type Badge**: Clear indication of analysis type
- **Success/Error States**: Different styling for results
- **Copy to Clipboard**: Easy result copying
- **Download Result**: Save as text file
- **Metadata Display**: Duration, timestamp, model info
- **Original Image**: Show the analyzed image

```tsx
<VisionResultDisplay
  result={analysisResult}
  image={previewImage}
/>
```

### Vision Demo Page

Access at `/vision` - Complete vision analysis interface with:

- Feature showcase
- Upload interface
- Results display
- Error handling
- Responsive design

---

## Usage Examples

### Example 1: General Image Analysis

```bash
# Using curl
curl -X POST http://localhost:8000/api/v1/vision/analyze \
  -F "file=@image.png" \
  -F "prompt=Describe this image in detail" \
  -F "analysis_type=general"
```

```typescript
// Using frontend
import { analyzeImage } from '@/lib/api'

const result = await analyzeImage(
  file,
  "Describe this image in detail",
  "general"
)
```

### Example 2: Text Extraction (OCR)

```bash
curl -X POST http://localhost:8000/api/v1/vision/analyze \
  -F "file=@screenshot.png" \
  -F "analysis_type=extract_text"
```

```typescript
const result = await analyzeImage(
  file,
  "Extract all text from this image",
  "extract_text"
)
```

### Example 3: Error Diagnosis

```bash
curl -X POST http://localhost:8000/api/v1/vision/analyze \
  -F "file=@error.png" \
  -F "analysis_type=diagnose_error" \
  -F "context=Trying to connect to database"
```

```typescript
const result = await analyzeImage(
  file,
  "Analyze this error and provide fixes",
  "diagnose_error",
  "Trying to connect to database"
)
```

### Example 4: UI to Code

```bash
curl -X POST http://localhost:8000/api/v1/vision/analyze \
  -F "file=@design.png" \
  -F "analysis_type=ui_to_code" \
  -F "framework=React" \
  -F "language=TypeScript"
```

```typescript
const result = await analyzeImage(
  file,
  "Convert this UI to React code",
  "ui_to_code"
)
```

---

## Configuration

### Backend Environment Variables

Add to your `.env` file:

```env
# Z.AI GLM Vision API
ZAI_API_KEY=your_zai_api_key_here
ZAI_API_URL=https://open.bigmodel.cn/api/paas/v4
```

### Getting Your API Key

1. Visit [Z.AI Open Platform](https://z.ai/manage-apikey/apikey-list)
2. Sign up or log in
3. Generate a new API key
4. Copy the key to your `.env` file

### Testing Without API Key

The system will return mock results when `ZAI_API_KEY` is not configured:

```json
{
  "mock": true,
  "analysis": "This is a mock result. Configure ZAI_API_KEY to use real GLM Vision API.",
  "prompt": "Describe this image",
  "analysis_type": "general"
}
```

---

## Troubleshooting

### Issue 1: "Invalid API Key"

**Solution:**
1. Verify your API key is correct
2. Check the key is activated
3. Ensure sufficient balance
4. Confirm platform matches (`Z_AI_MODE=ZAI`)

### Issue 2: "Failed to analyze image"

**Possible Causes:**
- Invalid image format
- Corrupted image file
- File size too large
- Network timeout

**Solutions:**
- Use supported formats: PNG, JPG, GIF, WebP
- Check file integrity
- Compress large images
- Check network connection

### Issue 3: "Video file exceeds limit"

**Solution:**
- GLM Vision API limits videos to 8MB
- Compress video before upload
- Use lower resolution
- Shorter duration

### Issue 4: Mock results returned

**Solution:**
- Configure `ZAI_API_KEY` in `.env`
- Restart the backend server
- Verify API key is valid

### Issue 5: Frontend can't connect to backend

**Solution:**
```env
# In frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000

# Ensure CORS is configured in backend
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```

---

## Performance Considerations

### Optimization Tips

1. **Image Compression**: Compress images before upload
2. **Caching**: Cache results for repeated analyses
3. **Async Processing**: Use background tasks for large files
4. **Rate Limiting**: Implement rate limiting for API calls

### Scalability

- **Horizontal Scaling**: Deploy multiple backend instances
- **Load Balancing**: Use load balancer for API requests
- **Queue Management**: Implement job queues for heavy workloads
- **CDN**: Use CDN for static assets

---

## Security

### Best Practices

1. **API Key Storage**: Never commit API keys to git
2. **Input Validation**: Validate all uploaded files
3. **File Size Limits**: Enforce maximum file sizes
4. **Content Type Verification**: Verify actual file content
5. **Rate Limiting**: Prevent abuse with rate limiting
6. **Sanitization**: Sanitize all user inputs

### File Upload Security

```python
# Backend validation
ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def validate_upload(file):
    # Check extension
    # Check file size
    # Verify content type
    # Scan for malware
```

---

## Future Enhancements

### Planned Features

- [ ] Batch image processing
- [ ] Real-time video analysis
- [ ] Custom model fine-tuning
- [ ] Advanced OCR with formatting
- [ ] Image comparison and diff
- [ ] Object detection and bounding boxes
- [ ] Face detection and recognition
- [ ] Text-to-image generation
- [ ] Image editing and manipulation
- [ ] Multi-modal analysis (image + text)

### Integration Ideas

- **Document Scanner**: Scan and extract text from documents
- **Code Review Tool**: Analyze code screenshots
- **Design System**: Convert designs to component libraries
- **Accessibility Checker**: Analyze UI for accessibility issues
- **Chart Generator**: Create charts from descriptions
- **Error Reporter**: Automatic error analysis from screenshots

---

## API Reference

### Response Format

#### Success Response

```json
{
  "success": true,
  "analysis_type": "general",
  "result": {
    "success": true,
    "analysis": "Detailed image analysis...",
    "model": "glm-4v",
    "usage": {
      "prompt_tokens": 100,
      "completion_tokens": 500,
      "total_tokens": 600
    }
  },
  "timestamp": "2026-04-05T12:00:00Z"
}
```

#### Error Response

```json
{
  "success": false,
  "analysis_type": "general",
  "result": {
    "success": false,
    "error": "Failed to process image",
    "details": "Invalid image format"
  },
  "timestamp": "2026-04-05T12:00:00Z"
}
```

---

## Support

For issues and questions:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review the [GLM Vision Documentation](https://docs.z.ai/llms.txt)
3. Check API status at [Z.AI Platform](https://z.ai)
4. Open an issue in the repository

---

**Last Updated**: April 5, 2026
**Version**: 1.0.0
**Status**: ✅ Production Ready
