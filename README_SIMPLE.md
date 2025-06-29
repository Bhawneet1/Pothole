# Simple Pothole Detection System

A streamlined pothole detection system that processes video input and outputs depth, height, and width measurements with colored bounding boxes based on depth.

## Features

- **Video Processing**: Process any video file for pothole detection
- **Depth Estimation**: Estimate pothole depth using multiple methods
- **Colored Bounding Boxes**: Different colors based on depth severity
- **Measurements**: Width, height, and depth measurements for each detection
- **CSV Export**: Detailed measurements saved to CSV file
- **Video Output**: Annotated video with detections and measurements
- **Statistics**: Comprehensive detection statistics

## Color Coding

- **🟢 Green**: Shallow potholes (< 5cm depth)
- **🟡 Yellow**: Medium potholes (5-10cm depth)
- **🟠 Orange**: Deep potholes (10-15cm depth)
- **🔴 Red**: Critical potholes (> 15cm depth)

## Requirements

```bash
pip install opencv-python torch torchvision ultralytics numpy
```

## Quick Start

1. **Place your video file** in the project directory (default: `p.mp4`)
2. **Ensure your YOLO model** is available (default: `best.pt`)
3. **Run the detector**:

```bash
python simple_pothole_detector_v2.py
```

## Configuration

Edit `simple_config.py` to customize:

- **Input/Output paths**
- **Depth categories and thresholds**
- **Processing parameters**
- **Color schemes**

### Key Configuration Options

```python
# Video paths
INPUT_VIDEO = 'p.mp4'  # Your input video
OUTPUT_VIDEO = 'output/pothole_detection_output.avi'  # Output video
OUTPUT_CSV = 'output/pothole_measurements.csv'  # Measurements CSV

# Processing
FRAME_SKIP = 3  # Process every 3rd frame for speed
SHOW_PREVIEW = True  # Show live preview

# Depth categories
DEPTH_CATEGORIES = {
    'shallow': {'max_depth': 0.05, 'color': (0, 255, 0)},  # < 5cm
    'medium': {'max_depth': 0.10, 'color': (0, 255, 255)}, # 5-10cm
    'deep': {'max_depth': 0.15, 'color': (0, 165, 255)},   # 10-15cm
    'critical': {'max_depth': float('inf'), 'color': (0, 0, 255)} # > 15cm
}
```

## Output Files

### 1. Annotated Video (`output/pothole_detection_output.avi`)
- Original video with colored bounding boxes
- Depth, width, height measurements displayed
- Frame counter and detection statistics
- Color legend

### 2. Measurements CSV (`output/pothole_measurements.csv`)
Contains detailed data for each detection:
- Frame number and timestamp
- Bounding box dimensions (width, height in pixels)
- Estimated depth (in centimeters)
- Depth category
- Confidence score
- Bounding box coordinates

### 3. Console Statistics
Real-time and final statistics showing:
- Total detections
- Breakdown by depth category
- Processing progress

## Usage Examples

### Basic Usage
```python
from simple_pothole_detector_v2 import SimplePotholeDetectorV2

detector = SimplePotholeDetectorV2()
detector.process_video('my_video.mp4')
```

### Custom Configuration
```python
# Modify config before running
from simple_config import *
INPUT_VIDEO = 'my_custom_video.mp4'
FRAME_SKIP = 1  # Process every frame
SHOW_PREVIEW = False  # Headless mode

detector = SimplePotholeDetectorV2()
detector.process_video()
```

### Single Frame Processing
```python
import cv2
from simple_pothole_detector_v2 import SimplePotholeDetectorV2

detector = SimplePotholeDetectorV2()
frame = cv2.imread('pothole_image.jpg')
annotated_frame, detections = detector.detect_potholes(frame)

print(f"Found {len(detections)} potholes")
for detection in detections:
    print(f"Depth: {detection['depth']*100:.1f}cm, Category: {detection['category']}")
```

## Depth Estimation

The system uses multiple methods for depth estimation:

1. **Area-based**: Larger bounding boxes indicate closer objects
2. **Focal length formula**: Using known object width and focal length
3. **Position-based**: Objects closer to bottom of frame are assumed closer

The final depth is a weighted combination of these methods.

## Performance Tips

- **GPU Usage**: Set `USE_GPU = True` in config for faster processing
- **Frame Skipping**: Increase `FRAME_SKIP` for faster processing
- **Headless Mode**: Set `SHOW_PREVIEW = False` for server environments
- **Confidence Threshold**: Adjust `CONFIDENCE_THRESHOLD` to filter detections

## Troubleshooting

### Common Issues

1. **Model not found**: Ensure `best.pt` is in the project directory
2. **Video not found**: Check the `INPUT_VIDEO` path in config
3. **OpenCV errors**: Install opencv-python: `pip install opencv-python`
4. **CUDA errors**: Set `USE_GPU = False` in config for CPU-only processing

### Performance Issues

- Use GPU if available
- Reduce frame resolution
- Increase frame skip rate
- Lower confidence threshold

## File Structure

```
project/
├── simple_pothole_detector_v2.py  # Main detector
├── simple_config.py               # Configuration
├── best.pt                        # YOLO model
├── p.mp4                          # Input video
├── output/                        # Output directory
│   ├── pothole_detection_output.avi
│   └── pothole_measurements.csv
└── README_SIMPLE.md              # This file
```

## License

This simplified version is based on the original pothole detection system. Use according to the original project's license terms. 