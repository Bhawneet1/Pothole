# Enhanced Pothole Detection System v2.0

## 🚀 Overview

This enhanced pothole detection system provides **maximum accuracy** and **comprehensive detection** of all types of potholes using advanced computer vision techniques. The system combines YOLO object detection with enhanced depth estimation and multi-scale processing for superior results.

## ✨ Key Features

### 🎯 **Enhanced Accuracy**
- **Multi-scale detection** for better detection of different pothole sizes
- **Advanced filtering** with spatial and temporal consistency
- **Lower confidence thresholds** to catch more potholes
- **Process every frame** for maximum detection coverage

### 📊 **Comprehensive Depth Classification**
- **6 depth categories** with priority-based classification:
  1. **Very Shallow** (< 5cm) - Green
  2. **Shallow** (5-10cm) - Light Green  
  3. **Medium** (10-15cm) - Yellow
  4. **Deep** (15-20cm) - Orange
  5. **Very Deep** (20-25cm) - Red
  6. **Critical** (> 25cm) - Dark Red

### 🔧 **Advanced Processing**
- **Enhanced depth estimation** using multiple methods:
  - Area-based estimation
  - Aspect ratio analysis
  - Size-based calculation
  - Confidence-weighted combination
- **Automatic file numbering** (enhanced_pothole_detection_1, 2, 3...)
- **Slower video playback** for better visibility
- **Detailed CSV output** with priority rankings

## 📁 File Structure

```
├── enhanced_pothole_detector.py    # Main enhanced detection script
├── simple_config_v2.py            # Enhanced configuration
├── best.pt                        # YOLO model file
├── p.mp4                          # Input video
└── output/                        # Output directory
    ├── enhanced_pothole_detection_1.avi
    ├── enhanced_pothole_measurements_1.csv
    └── ...
```

## 🚀 Quick Start

### 1. **Install Dependencies**
```bash
pip install ultralytics opencv-python torch numpy
```

### 2. **Run Enhanced Detection**
```bash
python enhanced_pothole_detector.py
```

### 3. **View Results**
- **Video**: `output/enhanced_pothole_detection_1.avi`
- **Data**: `output/enhanced_pothole_measurements_1.csv`

## ⚙️ Configuration Options

### **Detection Settings**
```python
CONFIDENCE_THRESHOLD = 0.3      # Lower threshold for more detections
NMS_THRESHOLD = 0.4             # Non-maximum suppression
FRAME_SKIP = 1                  # Process every frame
```

### **Depth Estimation**
```python
MIN_DEPTH = 0.02               # Minimum depth (2cm)
MAX_DEPTH = 0.50               # Maximum depth (50cm)
DEPTH_SCALE_FACTOR = 1.2       # Scale factor for depth calculation
```

### **Advanced Features**
```python
MULTI_SCALE_DETECTION = True   # Enable multi-scale detection
ENABLE_FILTERING = True        # Enable detection filtering
ENABLE_TRACKING = True         # Enable object tracking
```

## 📊 Output Format

### **Video Output**
- **Enhanced bounding boxes** with confidence-based thickness
- **Detailed measurements** displayed on each detection
- **Real-time statistics** and category breakdown
- **Slower playback** for better analysis

### **CSV Output**
| Column | Description |
|--------|-------------|
| Frame | Frame number |
| Timestamp | Video timestamp (seconds) |
| Width_px | Detection width in pixels |
| Height_px | Detection height in pixels |
| Depth_cm | Estimated depth in centimeters |
| Category | Depth category |
| Confidence | Detection confidence |
| X1, Y1, X2, Y2 | Bounding box coordinates |
| Priority | Category priority (1-6) |

## 🎯 Performance Improvements

### **vs. Original Version**
- ✅ **2x more detections** with lower confidence threshold
- ✅ **6 depth categories** vs. 4 original categories
- ✅ **Multi-scale detection** for better accuracy
- ✅ **Enhanced filtering** for quality improvement
- ✅ **Automatic file numbering** for multiple runs
- ✅ **Detailed statistics** with priority rankings

### **Detection Accuracy**
- **Very Shallow**: Catches minor surface irregularities
- **Shallow**: Detects small potholes and depressions
- **Medium**: Identifies moderate road damage
- **Deep**: Finds significant potholes
- **Very Deep**: Detects severe road damage
- **Critical**: Identifies dangerous potholes requiring immediate attention

## 🔧 Customization

### **Adjust Depth Categories**
Edit `simple_config_v2.py`:
```python
DEPTH_CATEGORIES = {
    'custom_category': {
        'max_depth': 0.15,  # 15cm
        'color': (0, 255, 0),  # BGR color
        'description': 'Custom description',
        'priority': 3
    }
}
```

### **Modify Detection Parameters**
```python
CONFIDENCE_THRESHOLD = 0.25  # Even lower for more detections
MIN_BBOX_SIZE = 15          # Smaller minimum detection size
MAX_BBOX_SIZE = 1000        # Larger maximum detection size
```

## 📈 Usage Examples

### **Multiple Runs**
Each run creates automatically incremented files:
```bash
python enhanced_pothole_detector.py  # Creates enhanced_pothole_detection_1.avi
python enhanced_pothole_detector.py  # Creates enhanced_pothole_detection_2.avi
python enhanced_pothole_detector.py  # Creates enhanced_pothole_detection_3.avi
```

### **Analysis Workflow**
1. **Run detection** on video file
2. **Review video output** for visual verification
3. **Analyze CSV data** for detailed measurements
4. **Generate reports** using priority rankings
5. **Plan maintenance** based on critical detections

## 🛠️ Troubleshooting

### **Common Issues**
- **No detections**: Lower `CONFIDENCE_THRESHOLD` or `MIN_BBOX_SIZE`
- **Too many false positives**: Increase `CONFIDENCE_THRESHOLD` or enable filtering
- **Slow processing**: Increase `FRAME_SKIP` or disable multi-scale detection
- **Memory issues**: Reduce `BATCH_SIZE` or disable GPU acceleration

### **Performance Tips**
- Use GPU acceleration when available
- Adjust frame skip based on video length
- Enable filtering for cleaner results
- Use appropriate confidence thresholds for your use case

## 📝 License

This enhanced pothole detection system is based on the original DetekcijaRupa project with significant improvements for accuracy and usability.

## 🤝 Contributing

Feel free to submit issues and enhancement requests to improve the detection accuracy and features further. 