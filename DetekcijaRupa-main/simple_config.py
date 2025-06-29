# Simple Pothole Detector Configuration

# Model Configuration
MODEL_PATH = 'best.pt'  # Path to your YOLO model

# Video Processing Configuration
INPUT_VIDEO = 'p.mp4'  # Input video file path
OUTPUT_VIDEO = 'output/pothole_detection_output.avi'  # Output video path
OUTPUT_CSV = 'output/pothole_measurements.csv'  # Output CSV path

# Processing Configuration
FRAME_SKIP = 3  # Process every nth frame (1 = process all frames)
SHOW_PREVIEW = True  # Show live preview (set to False for headless operation)

# Depth Estimation Configuration
# These parameters can be adjusted based on your camera setup
FOCAL_LENGTH = 1000  # Approximate focal length in pixels
KNOWN_WIDTH = 0.3    # Known width of reference object in meters

# Depth Categories and Colors (BGR format)
DEPTH_CATEGORIES = {
    'shallow': {
        'max_depth': 0.05,  # 5cm
        'color': (0, 255, 0),  # Green
        'description': 'Shallow potholes (< 5cm)'
    },
    'medium': {
        'max_depth': 0.10,  # 10cm
        'color': (0, 255, 255),  # Yellow
        'description': 'Medium potholes (5-10cm)'
    },
    'deep': {
        'max_depth': 0.15,  # 15cm
        'color': (0, 165, 255),  # Orange
        'description': 'Deep potholes (10-15cm)'
    },
    'critical': {
        'max_depth': float('inf'),  # No limit
        'color': (0, 0, 255),  # Red
        'description': 'Critical potholes (> 15cm)'
    }
}

# Detection Confidence Threshold
CONFIDENCE_THRESHOLD = 0.5  # Minimum confidence for detection

# Output Configuration
SAVE_VIDEO = True  # Save processed video
SAVE_CSV = True    # Save measurements to CSV
SAVE_IMAGES = False  # Save individual frames with detections

# Performance Configuration
USE_GPU = True  # Use GPU if available
BATCH_SIZE = 1  # Process frames in batches (1 for real-time) 