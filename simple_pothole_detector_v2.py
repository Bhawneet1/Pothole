import cv2
import numpy as np
import torch
from ultralytics import YOLO
import logging
from datetime import datetime
import os
import csv
import glob

# Import configuration
from simple_config import *

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_next_video_number():
    """Find the next available video number for pothole_detection_X"""
    output_dir = 'output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Look for existing pothole_detection_X files
    pattern = os.path.join(output_dir, 'pothole_detection_*.avi')
    existing_files = glob.glob(pattern)
    
    if not existing_files:
        return 1
    
    # Extract numbers from existing filenames
    numbers = []
    for file in existing_files:
        try:
            # Extract number from filename like "pothole_detection_1.avi"
            filename = os.path.basename(file)
            number = int(filename.split('_')[-1].split('.')[0])
            numbers.append(number)
        except (ValueError, IndexError):
            continue
    
    if not numbers:
        return 1
    
    # Return next available number
    return max(numbers) + 1

def get_output_paths():
    """Generate output paths with incremented counter"""
    video_number = get_next_video_number()
    output_dir = 'output'
    
    video_filename = f'pothole_detection_{video_number}.avi'
    csv_filename = f'pothole_measurements_{video_number}.csv'
    
    video_path = os.path.join(output_dir, video_filename)
    csv_path = os.path.join(output_dir, csv_filename)
    
    return video_path, csv_path, video_number

class SimplePotholeDetectorV2:
    def __init__(self, model_path=MODEL_PATH):
        """Initialize the pothole detector"""
        self.device = 'cuda' if torch.cuda.is_available() and USE_GPU else 'cpu'
        logger.info(f"Using device: {self.device}")
        
        # Load YOLO model
        self.model = YOLO(model_path)
        logger.info("YOLO model loaded successfully")
        
        # Depth estimation parameters
        self.focal_length = FOCAL_LENGTH
        self.known_width = KNOWN_WIDTH
        
        # Color mapping for different depth ranges
        self.depth_colors = {category: config['color'] for category, config in DEPTH_CATEGORIES.items()}
        
        # Statistics
        self.total_detections = 0
        self.detection_stats = {category: 0 for category in DEPTH_CATEGORIES.keys()}
    
    def estimate_depth_improved(self, bbox_width, bbox_height, frame_width, frame_height):
        """Improved depth estimation using multiple factors"""
        area = bbox_width * bbox_height
        frame_area = frame_width * frame_height
        normalized_area = area / frame_area
        # Area-based: 0.22 - (normalized_area * 0.5)
        depth_area = max(0.02, 0.22 - (normalized_area * 0.5))
        return depth_area
    
    def get_depth_category(self, depth):
        """Categorize depth and return color"""
        for category, config in DEPTH_CATEGORIES.items():
            if depth <= config['max_depth']:
                return category, self.depth_colors[category]
        
        # Fallback to critical
        return 'critical', self.depth_colors['critical']
    
    def detect_potholes(self, frame):
        """Detect potholes in a frame and return annotated frame with measurements"""
        # Run YOLO detection with confidence threshold
        results = self.model(frame, verbose=False, conf=CONFIDENCE_THRESHOLD, show=False)
        
        annotated_frame = frame.copy()
        detections = []
        
        frame_height, frame_width = frame.shape[:2]
        
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    # Get bounding box coordinates
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    
                    # Get confidence score
                    confidence = float(box.conf[0].cpu().numpy())
                    
                    # Calculate dimensions
                    width = x2 - x1
                    height = y2 - y1
                    
                    # Estimate depth
                    depth = self.estimate_depth_improved(width, height, frame_width, frame_height)
                    
                    # Debug: Log depth values occasionally
                    if self.total_detections % 50 == 0:
                        logger.info(f"Sample depth: {depth*100:.1f}cm for bbox {width}x{height}")
                    
                    # Get depth category and color
                    depth_category, color = self.get_depth_category(depth)
                    
                    # Update statistics
                    self.detection_stats[depth_category] += 1
                    self.total_detections += 1
                    
                    # Draw bounding box
                    cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
                    
                    # Add text with measurements
                    text_lines = [
                        f"Depth: {depth*100:.1f}cm",
                        f"Width: {width}px",
                        f"Height: {height}px",
                        f"Category: {depth_category}",
                        f"Conf: {confidence:.2f}"
                    ]
                    
                    # Calculate text position
                    text_x = x1
                    text_y = y1 - 10
                    
                    # Draw text background
                    for i, line in enumerate(text_lines):
                        text_size = cv2.getTextSize(line, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
                        cv2.rectangle(annotated_frame, 
                                    (text_x, text_y - text_size[1] - 5),
                                    (text_x + text_size[0], text_y + 5),
                                    (0, 0, 0), -1)
                        cv2.putText(annotated_frame, line, 
                                  (text_x, text_y - i * 15),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    
                    # Store detection info
                    detections.append({
                        'bbox': (x1, y1, x2, y2),
                        'width': width,
                        'height': height,
                        'depth': depth,
                        'category': depth_category,
                        'color': color,
                        'confidence': confidence
                    })
        
        return annotated_frame, detections
    
    def add_overlay_info(self, frame, frame_count, total_frames, detections):
        """Add overlay information to the frame"""
        height, width = frame.shape[:2]
        
        # Add frame counter and detection count
        cv2.putText(frame, f"Frame: {frame_count}/{total_frames}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"Detections: {len(detections)}", 
                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"Total: {self.total_detections}", 
                   (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Add legend
        legend_y = height - 200
        for i, (category, config) in enumerate(DEPTH_CATEGORIES.items()):
            color = self.depth_colors[category]
            cv2.rectangle(frame, (10, legend_y + i * 25), (30, legend_y + i * 25 + 20), color, -1)
            cv2.putText(frame, f"{category.capitalize()}: {self.detection_stats[category]}", 
                       (35, legend_y + i * 25 + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Add processing info
        cv2.putText(frame, f"Device: {self.device.upper()}", 
                   (width - 200, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    def process_video(self, input_path=INPUT_VIDEO, show_preview=SHOW_PREVIEW):
        """Process a video file and detect potholes"""
        # Open video
        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            logger.error(f"Could not open video: {input_path}")
            return
        
        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        logger.info(f"Processing video: {input_path}")
        logger.info(f"Video properties: {width}x{height}, {fps} FPS, {total_frames} frames")

        # Find next available video number
        output_dir = 'output'
        
        # Check for both numbered files and default files
        numbered_pattern = os.path.join(output_dir, 'pothole_detection_*.avi')
        default_video_path = os.path.join(output_dir, 'pothole_detection_output.avi')
        
        existing_files = glob.glob(numbered_pattern)
        
        # If default files exist, count them as well
        if os.path.exists(default_video_path):
            existing_files.append(default_video_path)
        
        if not existing_files:
            video_number = 1
        else:
            numbers = []
            for f in existing_files:
                base = os.path.basename(f)
                # Handle both numbered and default filenames
                if base == 'pothole_detection_output.avi':
                    numbers.append(0)  # Count default as number 0
                else:
                    num = base.replace('pothole_detection_', '').replace('.avi', '')
                    if num.isdigit():
                        numbers.append(int(num))
            video_number = max(numbers) + 1 if numbers else 1
        
        output_video_path = os.path.join(output_dir, f'pothole_detection_{video_number}.avi')
        output_csv_path = os.path.join(output_dir, f'pothole_measurements_{video_number}.csv')
        
        logger.info(f"Video number: {video_number}")
        logger.info(f"Output video will be saved as: {output_video_path}")
        logger.info(f"Output CSV will be saved as: {output_csv_path}")

        # Create output video writer with slower playback (half speed)
        output_fps = max(1, fps // 2)  # Avoid zero FPS
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(output_video_path, fourcc, output_fps, (width, height))

        # Setup CSV output for measurements
        csv_file = None
        if output_csv_path:
            csv_file = open(output_csv_path, 'w', newline='')
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['Frame', 'Timestamp', 'Width_px', 'Height_px', 'Depth_cm', 
                               'Category', 'Confidence', 'X1', 'Y1', 'X2', 'Y2'])
        
        frame_count = 0
        processed_frames = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Process every nth frame for efficiency
            if frame_count % FRAME_SKIP != 0:
                continue
            
            processed_frames += 1
            
            # Detect potholes
            annotated_frame, detections = self.detect_potholes(frame)
            
            # Write detections to CSV
            if csv_file:
                timestamp = frame_count / fps
                for detection in detections:
                    x1, y1, x2, y2 = detection['bbox']
                    csv_writer.writerow([
                        frame_count, f"{timestamp:.2f}", detection['width'], detection['height'],
                        f"{detection['depth']*100:.1f}", detection['category'], 
                        f"{detection['confidence']:.3f}", x1, y1, x2, y2
                    ])
            
            # Add overlay information
            self.add_overlay_info(annotated_frame, frame_count, total_frames, detections)
            
            # Write frame to output video
            out.write(annotated_frame)
            
            # Show preview
            # (Removed cv2.imshow and cv2.waitKey for headless operation)
            # Progress update
            if processed_frames % 30 == 0:
                progress = (frame_count / total_frames) * 100
                logger.info(f"Progress: {progress:.1f}% - Detections: {self.total_detections}")
        
        # Cleanup
        cap.release()
        out.release()
        if csv_file:
            csv_file.close()
        # (Removed cv2.destroyAllWindows for headless operation)
        
        # Print final statistics
        self.print_statistics()
        
        logger.info(f"Measurements saved to: {output_csv_path}")
        logger.info(f"Output video saved to: {output_video_path}")
    
    def print_statistics(self):
        """Print detection statistics"""
        logger.info("\n" + "="*50)
        logger.info("DETECTION STATISTICS")
        logger.info("="*50)
        logger.info(f"Total detections: {self.total_detections}")
        logger.info("\nBreakdown by category:")
        for category, count in self.detection_stats.items():
            percentage = (count / self.total_detections * 100) if self.total_detections > 0 else 0
            logger.info(f"  {category.capitalize()}: {count} ({percentage:.1f}%)")
        logger.info("="*50)

def main():
    """Main function to run pothole detection."""
    # Create output directory
    os.makedirs('output', exist_ok=True)
    
    # Initialize detector
    detector = SimplePotholeDetectorV2()
    
    # Process video with file replacement and slower playback, using internal output path logic
    detector.process_video(
        input_path=INPUT_VIDEO,
        show_preview=SHOW_PREVIEW
    )

if __name__ == '__main__':
    main() 