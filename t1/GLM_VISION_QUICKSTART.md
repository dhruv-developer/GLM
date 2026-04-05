# GLM Vision API - Quick Start Guide

Get started with GLM Vision API integration in your ZIEL-MAS system in 5 minutes!

## 🚀 Quick Setup

### Step 1: Get Your API Key

1. Visit [Z.AI Open Platform](https://z.ai/manage-apikey/apikey-list)
2. Sign up or log in to your account
3. Generate a new API key
4. Copy the API key

### Step 2: Configure Backend

Add to your `backend/.env` file:

```env
ZAI_API_KEY=your_actual_api_key_here
ZAI_API_URL=https://open.bigmodel.cn/api/paas/v4
```

### Step 3: Start the Backend

```bash
cd backend
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 4: Start the Frontend

```bash
cd frontend
npm run dev
```

### Step 5: Access Vision Features

Open your browser and navigate to:
```
http://localhost:3000/vision
```

## 🎯 Try It Out

### Option 1: Use the Web Interface

1. Go to `http://localhost:3000/vision`
2. Select an analysis type (General, OCR, Error Diagnosis, etc.)
3. Upload an image
4. Click "Analyze Image"
5. View the results!

### Option 2: Use the API Directly

```bash
# Analyze an image
curl -X POST http://localhost:8000/api/v1/vision/analyze \
  -F "file=@your-image.png" \
  -F "prompt=Describe this image" \
  -F "analysis_type=general"
```

### Option 3: Use in Your Code

```typescript
import { analyzeImage } from '@/lib/api'

// Analyze an image
const result = await analyzeImage(
  file,
  "Describe this image in detail",
  "general"
)

console.log(result.result.analysis)
```

## 🎨 Available Analysis Types

| Type | Description | Use Case |
|------|-------------|----------|
| `general` | General image analysis | Understand any image |
| `extract_text` | OCR text extraction | Extract text from screenshots |
| `diagnose_error` | Error diagnosis | Fix errors from screenshots |
| `ui_to_code` | UI to code conversion | Convert designs to code |
| `understand_diagram` | Diagram understanding | Interpret technical diagrams |
| `analyze_chart` | Chart analysis | Extract insights from charts |

## 📸 Example Images to Try

### 1. General Analysis
- Any photo or image
- Screenshot of a webpage
- Product photo

### 2. Text Extraction
- Screenshot of code
- Document scan
- Receipt or invoice

### 3. Error Diagnosis
- Error message screenshot
- Stack trace image
- Bug report screenshot

### 4. UI to Code
- UI design mockup
- Figma/sketch screenshot
- Website screenshot

### 5. Diagram Understanding
- Flowchart
- Architecture diagram
- UML diagram

### 6. Chart Analysis
- Bar chart
- Line graph
- Pie chart

## 🔧 Testing Without API Key

The system works in "mock mode" without an API key:

```json
{
  "mock": true,
  "analysis": "This is a mock result. Configure ZAI_API_KEY to use real GLM Vision API.",
  "prompt": "Describe this image",
  "analysis_type": "general"
}
```

**Note**: Mock mode is great for testing but won't provide real analysis.

## 🐛 Troubleshooting

### "Invalid API Key"
- Check your API key is correct
- Verify the key is activated
- Ensure sufficient balance

### "Failed to analyze image"
- Check image format (PNG, JPG, GIF, WebP)
- Verify file size (< 10MB)
- Check network connection

### "Backend disconnected"
- Ensure backend is running on port 8000
- Check CORS configuration
- Verify API URL is correct

## 📚 Next Steps

1. **Read the full documentation**: [GLM_VISION_INTEGRATION.md](./GLM_VISION_INTEGRATION.md)
2. **Explore the demo**: Visit `http://localhost:3000/vision`
3. **Check the API docs**: Go to `http://localhost:8000/docs`
4. **Build your own**: Use components in your app

## 💡 Tips

- **Start simple**: Try general analysis first
- **Use custom prompts**: Be specific in your requests
- **Provide context**: Add context for better results
- **Check results**: Review and verify analysis output
- **Optimize images**: Compress large images for faster processing

## 🎉 You're Ready!

You now have full GLM Vision API integration in your ZIEL-MAS system. Start analyzing images and videos with AI-powered vision capabilities!

---

**Need Help?**
- Check the [full documentation](./GLM_VISION_INTEGRATION.md)
- Visit [Z.AI docs](https://docs.z.ai/llms.txt)
- Open an issue in the repository

**Happy Analyzing! 🚀**
