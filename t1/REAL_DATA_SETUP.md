# Getting Real Data Instead of Mock Results

## 🚨 Important: Why You're Getting Mock Results

By default, ZIEL-MAS falls back to mock/sample data when API keys are not configured. This is to ensure the system works out of the box for testing, but it means you're not getting real AI-powered results.

## 🔑 Required API Keys for Real Functionality

### 1. GLM API Key (REQUIRED)
- **Purpose**: Main AI model for intent parsing, task planning, and code generation
- **Get it here**: https://open.bigmodel.cn/
- **Cost**: Free tier available
- **Without it**: System uses pattern matching and mock responses

### 2. Optional API Keys
- **Email**: Gmail SMTP for sending emails
- **WhatsApp**: Twilio for WhatsApp messages
- **Others**: Various service-specific APIs

## 🛠️ Quick Setup

### Method 1: Use the Setup Script (Recommended)

```bash
# Run the interactive setup
python setup_api_keys.py

# Check your current configuration
python setup_api_keys.py check
```

### Method 2: Manual Setup

1. Copy the template:
```bash
cp .env.template .env
```

2. Edit `.env` and add your GLM API key:
```bash
# Replace this line:
GLM_API_KEY=your-glm-api-key-here

# With your actual key:
GLM_API_KEY=your-actual-glm-api-key-from-bigmodel-cn
```

## 🧪 Test the Difference

### Before (Mock Data)
```bash
# Start server
python -m backend.main

# Test - you'll see mock/sample results
python test.py
```

### After (Real AI Data)
```bash
# Restart server after configuring API keys
python -m backend.main

# Test - you'll see real AI-powered results
python test.py
```

## 📊 What Changes With Real API Keys

| Feature | Without GLM API | With GLM API |
|---------|------------------|-------------|
| Intent Parsing | Pattern matching | AI understanding |
| Task Planning | Rule-based | Intelligent planning |
| Code Generation | Mock templates | Real AI code |
| Web Search | Fallback results | Enhanced results |
| Error Messages | "Mock response" | Actual AI responses |

## 🔍 How to Check if You're Using Real Data

### 1. Check Logs
```bash
# Look for these messages:
✅ "Parsing intent with GLM API"
✅ "Generated task graph with GLM API"
❌ "Falling back to pattern matching"
❌ "Using fallback task graph generation"
```

### 2. Check Response Quality
- **Real AI**: Contextual, varied, intelligent responses
- **Mock**: Generic, template-based responses

### 3. Run Configuration Check
```bash
python setup_api_keys.py check
```

## 🚀 Getting Your GLM API Key

1. **Visit**: https://open.bigmodel.cn/
2. **Sign up**: Create a free account
3. **Get API key**: Find it in your dashboard
4. **Configure**: Add it to your `.env` file
5. **Restart**: Stop and restart the server

## 💡 Troubleshooting

### Still Getting Mock Results?
1. Check that `.env` file exists
2. Verify GLM_API_KEY is correctly set
3. Restart the server after changes
4. Check logs for API connection errors

### API Key Errors?
1. Verify the key is correct (no extra spaces)
2. Check if the key has expired
3. Ensure you have API credits remaining

### Connection Issues?
1. Check internet connection
2. Verify GLM API is accessible
3. Check firewall/proxy settings

## 🎯 Best Practices

1. **Never commit API keys** to version control
2. **Use environment variables** in production
3. **Monitor API usage** to avoid limits
4. **Keep backup** of your API keys
5. **Rotate keys** periodically for security

## 🆘 Need Help?

- **GLM API Issues**: https://open.bigmodel.cn/support
- **System Issues**: Check the logs in the console
- **Configuration**: Run `python setup_api_keys.py check`

---

**Remember**: The mock data is just for testing. Real AI-powered functionality requires proper API key configuration!
