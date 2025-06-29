# 🚀 Pothole Detection Web App - Hosting Guide

This guide will help you deploy your pothole detection web app to various hosting platforms.

## 📋 Prerequisites

1. **Git** installed on your computer
2. **GitHub account** (for most hosting options)
3. **Python 3.9+** (for local testing)

## 🎯 Quick Start - Render (Recommended)

Render offers a free tier and is the easiest option for beginners.

### Step 1: Prepare Your Code
```bash
# Initialize git (if not already done)
git init
git add .
git commit -m "Initial commit"

# Create GitHub repository and push
git remote add origin https://github.com/YOUR_USERNAME/pothole-detector.git
git push -u origin main
```

### Step 2: Deploy to Render
1. Go to [Render.com](https://render.com) and sign up
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: `pothole-detection-app`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn web_app:app`
   - **Plan**: Free
5. Click "Create Web Service"
6. Wait 5-10 minutes for deployment
7. Your app will be live at: `https://your-app.onrender.com`

## 🚂 Railway Deployment

Railway is another excellent free option.

### Steps:
1. Go to [Railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Connect your repository
6. Railway will auto-detect Python and deploy
7. Get your live URL

## ⚡ Heroku Deployment

Heroku requires a credit card but offers good performance.

### Steps:
1. Install [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
2. Login: `heroku login`
3. Create app: `heroku create your-app-name`
4. Deploy: `git push heroku main`
5. Open: `heroku open`

## ☁️ Cloud Platform Deployment

### AWS (Amazon Web Services)

#### Option 1: AWS Elastic Beanstalk
```bash
# Install EB CLI
pip install awsebcli

# Initialize EB
eb init -p python-3.9 pothole-detector

# Create environment
eb create pothole-detector-env

# Deploy
eb deploy
```

#### Option 2: AWS EC2
1. Launch EC2 instance (Ubuntu recommended)
2. Install dependencies:
```bash
sudo apt update
sudo apt install python3-pip nginx
pip3 install -r requirements.txt
```
3. Configure nginx and gunicorn
4. Set up SSL with Let's Encrypt

### Google Cloud Platform (GCP)

#### Option 1: App Engine
1. Install [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
2. Create `app.yaml`:
```yaml
runtime: python39
entrypoint: gunicorn web_app:app
```
3. Deploy: `gcloud app deploy`

#### Option 2: Cloud Run
```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT_ID/pothole-detector
gcloud run deploy --image gcr.io/PROJECT_ID/pothole-detector --platform managed
```

### Microsoft Azure

#### Option 1: App Service
1. Install [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
2. Create app service:
```bash
az group create --name pothole-detector-rg --location eastus
az appservice plan create --name pothole-detector-plan --resource-group pothole-detector-rg --sku B1
az webapp create --name pothole-detector --resource-group pothole-detector-rg --plan pothole-detector-plan --runtime "PYTHON|3.9"
```
3. Deploy: `az webapp deployment source config-local-git --name pothole-detector --resource-group pothole-detector-rg`

## 🐳 Docker Deployment

### Local Docker
```bash
# Build image
docker build -t pothole-detector .

# Run container
docker run -p 5000:5000 pothole-detector
```

### Docker Hub
```bash
# Tag and push to Docker Hub
docker tag pothole-detector YOUR_USERNAME/pothole-detector
docker push YOUR_USERNAME/pothole-detector
```

## 🔧 Environment Variables

Set these environment variables on your hosting platform if needed:

- `FLASK_ENV=production`
- `MODEL_PATH=best.pt`
- `CONFIDENCE_THRESHOLD=0.5`
- `USE_GPU=false`

## 📁 File Structure for Deployment

Ensure your deployment includes:
```
├── web_app.py              # Main Flask app
├── requirements.txt         # Python dependencies
├── Procfile               # Heroku/Render config
├── runtime.txt            # Python version
├── Dockerfile             # Docker config
├── best.pt                # YOLO model file
├── simple_config_v2.py    # Configuration
├── templates/
│   └── index.html         # Frontend
├── uploads/               # Upload directory
├── output/                # Output directory
└── web_output/            # Web output directory
```

## 🚨 Common Issues & Solutions

### Issue: Model file not found
**Solution**: Ensure `best.pt` is in the root directory and committed to git.

### Issue: OpenCV installation fails
**Solution**: Use the provided `requirements.txt` with compatible versions.

### Issue: Memory limits on free tiers
**Solution**: 
- Reduce video processing quality
- Add file size limits
- Use smaller model variants

### Issue: Timeout on video processing
**Solution**: 
- Implement background processing
- Add progress indicators
- Use async processing

## 🔒 Security Considerations

1. **File Upload Limits**: Set maximum file sizes
2. **Input Validation**: Validate all uploaded files
3. **Rate Limiting**: Prevent abuse
4. **HTTPS**: Always use HTTPS in production
5. **Environment Variables**: Don't commit secrets

## 📊 Performance Optimization

1. **Caching**: Cache processed results
2. **CDN**: Use CDN for static files
3. **Database**: Add database for results storage
4. **Background Jobs**: Use Celery for video processing
5. **Load Balancing**: Scale horizontally

## 🆘 Support

If you encounter issues:

1. Check the hosting platform's logs
2. Verify all files are committed to git
3. Test locally first
4. Check environment variables
5. Review the platform's documentation

## 🎉 Success!

Once deployed, your pothole detection app will be accessible worldwide! Share the URL with others to test your AI-powered pothole detection system.

---

**Need help?** Check the platform-specific documentation or create an issue in your repository. 