# 🚧 Pothole Detection Web App

An AI-powered web application for detecting potholes in images and videos using YOLO deep learning model.

## 🌟 Features

- **Image Processing**: Upload and detect potholes in images
- **Video Processing**: Process videos with pothole detection overlay
- **Depth Estimation**: Estimate pothole depth and categorize severity
- **Modern Web Interface**: Drag-and-drop upload with progress indicators
- **Download Results**: Get processed images, videos, and CSV reports

## 🚀 Live Demo

**Coming Soon**: Deployed on Render with auto-deploy enabled!

## 🛠️ Technology Stack

- **Backend**: Flask (Python)
- **AI Model**: YOLO (Ultralytics)
- **Frontend**: HTML5, CSS3, JavaScript
- **Computer Vision**: OpenCV
- **Hosting**: Render (Auto-deploy enabled)

## 📁 Project Structure

```
├── web_app.py              # Main Flask application
├── templates/
│   └── index.html         # Web interface
├── best.pt                # YOLO model (23MB)
├── simple_config_v2.py    # Configuration
├── requirements.txt       # Python dependencies
├── Procfile              # Render deployment
├── Dockerfile            # Container deployment
└── HOSTING_GUIDE.md      # Deployment guide
```

## 🎯 Auto-Deploy Features

- ✅ **Automatic deployment** on every GitHub push
- ✅ **No manual intervention** required
- ✅ **Build and deploy** in 5-10 minutes
- ✅ **Rollback capability** if needed
- ✅ **Deployment logs** for monitoring

## 🔧 Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python web_app.py

# Access at: http://127.0.0.1:5000
```

## 📊 Detection Categories

- **Minor**: 0-5cm depth
- **Moderate**: 5-10cm depth  
- **Major**: 10-15cm depth
- **Critical**: 15+cm depth

## 🌍 Deployment

This app is configured for easy deployment on:
- **Render** (Recommended - Free tier)
- **Railway** (Free tier)
- **Heroku** (Paid)
- **AWS/Azure/GCP** (Enterprise)

## 📝 License

MIT License - Feel free to use and modify!

---

**Auto-deploy enabled**: Every push to main branch triggers automatic deployment! 🚀 