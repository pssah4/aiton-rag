# 🚀 AITON-RAG Deployment Guide

Complete guide for deploying AITON-RAG to production environments with Custom GPT Actions integration.

## 📋 Prerequisites

### Local Development
- Python 3.8+ installed
- Git for version control
- OpenAI API key
- 4GB+ RAM recommended
- 2GB+ disk space

### Production Deployment
- Cloud platform account (Railway, Render, Heroku, or AWS)
- Domain name (optional, for custom URLs)
- SSL certificate (handled automatically by most platforms)
- OpenAI API key with sufficient credits

## 🛠️ Local Setup

### 1. Environment Preparation
```bash
# Clone or navigate to project
cd aiton-rag

# Run environment setup
python setup_environment.py

# Configure environment variables
cp .env.example .env
# Edit .env with your OpenAI API key and settings
```

### 2. Configuration
Edit `.env` file:
```env
# Required: OpenAI API Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here

# Server Configuration
FLASK_SECRET_KEY=your-secret-key-here
API_BASE_URL=http://localhost:5000

# File Processing Settings
MAX_FILE_SIZE_MB=100
DELETE_AFTER_PROCESSING=false

# Environment
FLASK_ENV=development
DEBUG=true
```

### 3. Testing
```bash
# Run comprehensive tests
python test_aiton_rag.py

# Start application
python run.py
```

## 🌐 Production Deployment Options

### Option 1: Railway (Recommended)

**Why Railway?**
- Automatic SSL certificates
- GitHub integration
- Environment variable management
- Persistent storage
- Custom domains
- Reasonable pricing

**Setup Steps:**

1. **Prepare Repository**
```bash
# Ensure all files are committed
git add .
git commit -m "Prepare for Railway deployment"
git push origin main
```

2. **Railway Configuration**
- Sign up at [railway.app](https://railway.app)
- Connect GitHub repository
- Deploy from `main` branch

3. **Environment Variables** (Set in Railway dashboard):
```
OPENAI_API_KEY=sk-your-openai-api-key-here
FLASK_SECRET_KEY=your-production-secret-key
API_BASE_URL=https://your-app.railway.app
FLASK_ENV=production
DEBUG=false
MAX_FILE_SIZE_MB=100
```

4. **Custom Domain** (Optional):
```
# In Railway dashboard:
# Settings → Domains → Add Custom Domain
# Configure DNS: CNAME record pointing to railway domain
```

### Option 2: Render

**Setup Steps:**

1. **Create render.yaml** (already included in project):
```yaml
services:
  - type: web
    name: aiton-rag
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "python app.py"
    envVars:
      - key: FLASK_ENV
        value: production
      - key: DEBUG
        value: false
```

2. **Deploy to Render**:
- Sign up at [render.com](https://render.com)
- Connect GitHub repository
- Configure environment variables
- Deploy

### Option 3: Heroku

**Setup Steps:**

1. **Install Heroku CLI**
```bash
# macOS
brew install heroku/brew/heroku

# Windows/Linux - download from heroku.com
```

2. **Heroku Deployment**
```bash
# Login to Heroku
heroku login

# Create app
heroku create your-aiton-rag-app

# Set environment variables
heroku config:set OPENAI_API_KEY=sk-your-key-here
heroku config:set FLASK_SECRET_KEY=your-secret-key
heroku config:set FLASK_ENV=production
heroku config:set DEBUG=false

# Deploy
git push heroku main
```

### Option 4: DigitalOcean App Platform

**Setup Steps:**

1. **Create app.yaml**:
```yaml
name: aiton-rag
services:
- name: web
  source_dir: /
  github:
    repo: your-username/aiton-rag
    branch: main
  run_command: python app.py
  environment_slug: python
  instance_count: 1
  instance_size_slug: professional-xs
  envs:
  - key: OPENAI_API_KEY
    value: sk-your-key-here
  - key: FLASK_ENV
    value: production
```

2. **Deploy via DigitalOcean dashboard**

## 🔧 Custom GPT Actions Integration

### 1. Deploy Application First
Ensure your AITON-RAG application is deployed and accessible via HTTPS.

### 2. Configure Custom GPT

**Step 1: Create Custom GPT**
- Go to [chat.openai.com](https://chat.openai.com)
- Click "Explore" → "Create a GPT"
- Name: "AITON-RAG Assistant"
- Description: "Document analysis and knowledge management assistant"

**Step 2: Instructions**
Copy the system prompt from `custom_gpt_config/system_prompts.md`:

```
You are AITON-RAG Assistant, an intelligent document analysis and knowledge management system. You have access to a curated knowledge base through specialized API actions...
[Full prompt from system_prompts.md]
```

**Step 3: Actions Configuration**
- Click "Create new action"
- Import schema from `custom_gpt_config/actions_schema.json`
- Set Authentication: None (for now)
- Test the actions

### 3. Schema Configuration

**Important URLs to Update:**
In `actions_schema.json`, replace `https://your-deployment-url.com` with your actual deployment URL:

```json
{
  "openapi": "3.0.0",
  "info": {
    "title": "AITON-RAG API",
    "version": "1.0.0"
  },
  "servers": [
    {
      "url": "https://your-actual-deployment-url.com"
    }
  ]
}
```

### 4. Testing Actions

Test each action in the Custom GPT interface:

1. **Health Check**: Should return system status
2. **Get Knowledge Base**: Should return structured content
3. **Search**: Should return relevant results
4. **Categories**: Should list content categories

## 🔒 Security Considerations

### API Security

1. **Rate Limiting** (Add to production):
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
```

2. **API Key Authentication** (Optional):
```python
# Add to actions_api.py
def require_api_key():
    api_key = request.headers.get('X-API-Key')
    if api_key != os.environ.get('API_KEY'):
        abort(401)
```

3. **CORS Configuration**:
Already configured in `actions_api.py` - restrict origins in production:
```python
CORS(app, origins=['https://chat.openai.com'])
```

### File Upload Security

1. **File Size Limits**: Already implemented
2. **File Type Validation**: Already implemented
3. **Virus Scanning** (Production):
```python
import clamd

def scan_file(file_path):
    cd = clamd.ClamdUnixSocket()
    return cd.scan(file_path)
```

## 📊 Monitoring & Maintenance

### Health Monitoring

**Built-in Health Check**:
- URL: `https://your-app.com/health`
- Returns system status and metrics

**External Monitoring**:
- Use services like Pingdom, UptimeRobot
- Monitor `/health` endpoint
- Set up alerts for downtime

### Log Management

**Production Logging**:
```python
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('logs/aiton-rag.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
```

### Database Backup

**Knowledge Base Backup**:
```python
import shutil
import datetime

def backup_knowledge_base():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"backups/kb_backup_{timestamp}"
    shutil.copytree("rag_data", backup_dir)
```

## 🚀 Performance Optimization

### File Processing

1. **Async Processing**: Already implemented
2. **Background Tasks**: Consider Celery for heavy workloads
3. **Caching**: Add Redis for frequently accessed data

### API Optimization

1. **Response Caching**:
```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/api/knowledge-base')
@cache.cached(timeout=300)  # 5 minutes
def get_knowledge_base():
    # ... existing code
```

2. **Database Indexing**: If using database instead of JSON
3. **CDN**: For static assets

## 📈 Scaling Considerations

### Horizontal Scaling

1. **Load Balancer**: Distribute traffic across multiple instances
2. **Shared Storage**: Use cloud storage for files
3. **Database**: Move from JSON to PostgreSQL/MongoDB

### Vertical Scaling

1. **Memory**: Increase for large document processing
2. **CPU**: Multiple cores for concurrent processing
3. **Storage**: SSD for better I/O performance

## 🎯 Deployment Checklist

### Pre-Deployment
- [ ] All tests pass (`python test_aiton_rag.py`)
- [ ] Environment variables configured
- [ ] OpenAI API key valid and funded
- [ ] File size limits appropriate
- [ ] Error handling tested

### Post-Deployment
- [ ] Health endpoint accessible
- [ ] File upload working
- [ ] API endpoints responding
- [ ] Custom GPT Actions configured
- [ ] SSL certificate active
- [ ] Monitoring set up
- [ ] Backup strategy implemented

### Custom GPT Configuration
- [ ] Actions schema imported
- [ ] System prompts configured
- [ ] All actions tested
- [ ] URLs updated to production
- [ ] Authentication configured (if needed)

## 🆘 Troubleshooting

### Common Issues

**1. OpenAI API Errors**
```
Error: Invalid API key
Solution: Check OPENAI_API_KEY in environment variables
```

**2. File Upload Failures**
```
Error: File too large
Solution: Check MAX_FILE_SIZE_MB setting
```

**3. Custom GPT Actions Not Working**
```
Error: Failed to fetch
Solution: Check CORS settings and URL configuration
```

**4. Memory Issues**
```
Error: Out of memory
Solution: Increase instance size or implement streaming
```

### Debug Mode

Enable debug logging:
```env
DEBUG=true
FLASK_ENV=development
```

### Support Resources

- **Documentation**: Check project README.md
- **Logs**: Review application logs in `/logs` directory
- **Health Check**: Monitor `/health` endpoint
- **API Testing**: Use `/api-docs` interface

## 🎉 Success Validation

Your deployment is successful when:

1. ✅ Web interface loads at your domain
2. ✅ File uploads process correctly
3. ✅ API endpoints return expected data
4. ✅ Custom GPT Actions work in ChatGPT
5. ✅ Health check returns "healthy" status
6. ✅ No critical errors in logs

**Congratulations! Your AITON-RAG system is now production-ready with Custom GPT Actions integration.**
