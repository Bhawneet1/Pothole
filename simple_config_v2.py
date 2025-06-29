# Enhanced Pothole Detector Configuration v2.0
# Optimized for maximum accuracy and detection of all pothole types

# Model Configuration
MODEL_PATH = 'best.pt'  # Path to your YOLO model

# Video Processing Configuration
INPUT_VIDEO = 'p.mp4'  # Input video file path
OUTPUT_VIDEO = 'output/pothole_detection_output.avi'  # Output video path
OUTPUT_CSV = 'output/pothole_measurements.csv'  # Output CSV path

# Processing Configuration - Optimized for accuracy
FRAME_SKIP = 1  # Process every frame for maximum accuracy (was 3)
SHOW_PREVIEW = False  # Show live preview (set to False for headless operation)

# Enhanced Detection Configuration
CONFIDENCE_THRESHOLD = 0.3  # Lower threshold to catch more potholes (was 0.5)
NMS_THRESHOLD = 0.4  # Non-maximum suppression threshold
MIN_BBOX_SIZE = 20  # Minimum bounding box size in pixels
MAX_BBOX_SIZE = 800  # Maximum bounding box size in pixels

# Depth Estimation Configuration - Enhanced for accuracy
FOCAL_LENGTH = 1000  # Approximate focal length in pixels
KNOWN_WIDTH = 0.3    # Known width of reference object in meters
DEPTH_SCALE_FACTOR = 0.8  # Reduced scale factor for more realistic depths
MIN_DEPTH = 0.02     # Minimum depth in meters (2cm)
MAX_DEPTH = 0.30     # Reduced maximum depth in meters (30cm)

# Enhanced Depth Categories with more realistic thresholds
DEPTH_CATEGORIES = {
    'very_shallow': {
        'max_depth': 0.08,  # 8cm (was 5cm)
        'color': (0, 255, 0),  # Green
        'description': 'Very shallow potholes (< 8cm)',
        'priority': 1
    },
    'shallow': {
        'max_depth': 0.12,  # 12cm (was 10cm)
        'color': (0, 255, 128),  # Light green
        'description': 'Shallow potholes (8-12cm)',
        'priority': 2
    },
    'medium': {
        'max_depth': 0.16,  # 16cm (was 15cm)
        'color': (0, 255, 255),  # Yellow
        'description': 'Medium potholes (12-16cm)',
        'priority': 3
    },
    'deep': {
        'max_depth': 0.20,  # 20cm (was 20cm)
        'color': (0, 165, 255),  # Orange
        'description': 'Deep potholes (16-20cm)',
        'priority': 4
    },
    'very_deep': {
        'max_depth': 0.25,  # 25cm (was 25cm)
        'color': (0, 0, 255),  # Red
        'description': 'Very deep potholes (20-25cm)',
        'priority': 5
    },
    'critical': {
        'max_depth': float('inf'),  # No limit
        'color': (0, 0, 128),  # Dark red
        'description': 'Critical potholes (> 25cm)',
        'priority': 6
    }
}

# Advanced Detection Parameters
MULTI_SCALE_DETECTION = True  # Enable multi-scale detection
SCALE_FACTORS = [0.8, 1.0, 1.2]  # Different scales for detection
ASPECT_RATIO_RANGE = (0.5, 2.0)  # Acceptable aspect ratios for potholes

# Performance Configuration
USE_GPU = True  # Use GPU if available
BATCH_SIZE = 1  # Process frames in batches (1 for real-time)
ENABLE_TRACKING = True  # Enable object tracking for consistency
TRACKING_BUFFER = 5  # Number of frames to maintain tracking

# Output Configuration
SAVE_VIDEO = True  # Save processed video
SAVE_CSV = True    # Save measurements to CSV
SAVE_IMAGES = False  # Save individual frames with detections
SAVE_DETAILED_STATS = True  # Save detailed statistics

# Quality Assurance
ENABLE_FILTERING = True  # Enable detection filtering
MIN_DETECTION_CONFIDENCE = 0.25  # Minimum confidence for final detection
SPATIAL_FILTERING = True  # Filter detections based on spatial consistency
TEMPORAL_FILTERING = True  # Filter detections based on temporal consistency

# Logging Configuration
LOG_LEVEL = 'INFO'  # Logging level (DEBUG, INFO, WARNING, ERROR)
SAVE_DETECTION_LOGS = True  # Save detailed detection logs 