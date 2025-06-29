import cv2
import numpy as np
import torch
from ultralytics import YOLO
import logging
from datetime import datetime
import os
import csv

# Import configuration
from simple_config import *

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        # Calculate area and aspect ratio
        area = bbox_width * bbox_height
        aspect_ratio = bbox_width / bbox_height if bbox_height > 0 else 1
        
        # Normalize area by frame size
        frame_area = frame_width * frame_height
        normalized_area = area / frame_area
        
        # Position-based depth estimation (objects closer to bottom of frame are closer)
        # This assumes camera is mounted on vehicle looking forward
        
        # Multiple depth estimation methods
        depth_methods = []
        
        # Method 1: Area-based (larger area = closer object)
        print(f"[DEBUG] bbox: {bbox_width}x{bbox_height}, normalized_area: {normalized_area:.4f}")
        depth_area = max(0.02, 0.22 - (normalized_area * 0.5))
        print(f"[DEBUG] depth_area: {depth_area*100:.1f}cm")
        depth_methods.append(depth_area)
        
        # Method 2: Width-based (using focal length formula)
        if bbox_width > 0:
            depth_width = (self.known_width * self.focal_length) / bbox_width
            depth_methods.append(depth_width)
        
        # Method 3: Height-based
        if bbox_height > 0:
            depth_height = (self.known_width * self.focal_length) / bbox_height
            depth_methods.append(depth_height)
        
        # Combine methods (weighted average)
        if len(depth_methods) > 1:
            # Give more weight to area-based method
            weights = [0.6] + [0.4 / (len(depth_methods) - 1)] * (len(depth_methods) - 1)
            depth = sum(d * w for d, w in zip(depth_methods, weights))
        else:
            depth = depth_methods[0]
        
        # Clamp depth to reasonable range (2cm to 25cm)
        depth = max(0.02, min(0.25, depth))
        
        return depth
    
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
        results = self.model(frame, verbose=False, conf=CONFIDENCE_THRESHOLD)
        
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
    
    def process_video(self, input_path=INPUT_VIDEO, output_path=OUTPUT_VIDEO, show_preview=SHOW_PREVIEW):
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
        
        # Setup video writer if output path is provided
        video_writer = None
        if output_path and SAVE_VIDEO:
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            video_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            logger.info(f"Output video will be saved to: {output_path}")
        
        # Setup CSV output for measurements
        csv_path = OUTPUT_CSV if SAVE_CSV else None
        csv_file = None
        if csv_path:
            csv_file = open(csv_path, 'w', newline='')
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
            if video_writer:
                video_writer.write(annotated_frame)
            
            # Progress update
            if processed_frames % 30 == 0:
                progress = (frame_count / total_frames) * 100
                logger.info(f"Progress: {progress:.1f}% - Detections: {self.total_detections}")
        
        # Cleanup
        cap.release()
        if video_writer:
            video_writer.release()
        if csv_file:
            csv_file.close()
        
        # Print final statistics
        self.print_statistics()
        
        logger.info(f"Processing complete!")
        if csv_path:
            logger.info(f"Measurements saved to: {csv_path}")
        if output_path and SAVE_VIDEO:
            logger.info(f"Output video saved to: {output_path}")
    
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
    """Main function to run the pothole detector"""
    # Create output directory
    os.makedirs('output', exist_ok=True)
    
    # Initialize detector
    detector = SimplePotholeDetectorV2()
    
    # Process video
    detector.process_video(
        input_path=INPUT_VIDEO,
        output_path=OUTPUT_VIDEO,
        show_preview=SHOW_PREVIEW
    )

if __name__ == '__main__':
    main() 