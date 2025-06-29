import cv2
import numpy as np
import torch
from ultralytics import YOLO
import logging
from datetime import datetime
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimplePotholeDetector:
    def __init__(self, model_path='best.pt'):
        """Initialize the pothole detector"""
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        logger.info(f"Using device: {self.device}")
        
        # Load YOLO model
        self.model = YOLO(model_path)
        logger.info("YOLO model loaded successfully")
        
        # Depth estimation parameters
        self.focal_length = 1000  # Approximate focal length in pixels
        self.known_width = 0.3    # Known width of reference object in meters
        
        # Color mapping for different depth ranges
        self.depth_colors = {
            'shallow': (0, 255, 0),    # Green for shallow potholes (< 5cm)
            'medium': (0, 255, 255),   # Yellow for medium potholes (5-10cm)
            'deep': (0, 165, 255),     # Orange for deep potholes (10-15cm)
            'critical': (0, 0, 255)    # Red for critical potholes (> 15cm)
        }
    
    def estimate_depth(self, bbox_width, bbox_height):
        """Estimate depth using bounding box dimensions"""
        # Simple depth estimation based on bounding box size
        # Larger bounding boxes indicate closer objects (shallower depth)
        # Smaller bounding boxes indicate farther objects (deeper depth)
        
        # Calculate area of bounding box
        area = bbox_width * bbox_height
        
        # Normalize area (assuming typical pothole sizes)
        normalized_area = area / (640 * 480)  # Normalize by frame size
        
        # Estimate depth (inverse relationship: larger area = shallower depth)
        # This is a simplified estimation - in real applications, you'd use stereo vision or LiDAR
        depth = max(0.02, 0.5 - (normalized_area * 0.4))  # Depth in meters (2cm to 50cm range)
        
        return depth
    
    def get_depth_category(self, depth):
        """Categorize depth and return color"""
        if depth < 0.05:  # Less than 5cm
            return 'shallow', self.depth_colors['shallow']
        elif depth < 0.10:  # 5-10cm
            return 'medium', self.depth_colors['medium']
        elif depth < 0.15:  # 10-15cm
            return 'deep', self.depth_colors['deep']
        else:  # More than 15cm
            return 'critical', self.depth_colors['critical']
    
    def detect_potholes(self, frame):
        """Detect potholes in a frame and return annotated frame with measurements"""
        # Run YOLO detection
        results = self.model(frame, verbose=False)
        
        annotated_frame = frame.copy()
        detections = []
        
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    # Get bounding box coordinates
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    
                    # Calculate dimensions
                    width = x2 - x1
                    height = y2 - y1
                    
                    # Estimate depth
                    depth = self.estimate_depth(width, height)
                    
                    # Get depth category and color
                    depth_category, color = self.get_depth_category(depth)
                    
                    # Draw bounding box
                    cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
                    
                    # Add text with measurements
                    text_lines = [
                        f"Depth: {depth*100:.1f}cm",
                        f"Width: {width}px",
                        f"Height: {height}px",
                        f"Category: {depth_category}"
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
                        'color': color
                    })
        
        return annotated_frame, detections
    
    def process_video(self, input_path, output_path=None, show_preview=True):
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
        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            video_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            logger.info(f"Output video will be saved to: {output_path}")
        
        # Setup CSV output for measurements
        csv_path = output_path.replace('.avi', '_measurements.csv') if output_path else 'pothole_measurements.csv'
        csv_file = open(csv_path, 'w')
        csv_file.write("Frame,Timestamp,Width_px,Height_px,Depth_cm,Category,X1,Y1,X2,Y2\n")
        
        frame_count = 0
        total_detections = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Process every 3rd frame for efficiency (adjust as needed)
            if frame_count % 3 != 0:
                continue
            
            # Detect potholes
            annotated_frame, detections = self.detect_potholes(frame)
            
            # Write detections to CSV
            timestamp = frame_count / fps
            for detection in detections:
                x1, y1, x2, y2 = detection['bbox']
                csv_file.write(f"{frame_count},{timestamp:.2f},{detection['width']},{detection['height']},"
                             f"{detection['depth']*100:.1f},{detection['category']},{x1},{y1},{x2},{y2}\n")
                total_detections += 1
            
            # Add frame counter and detection count
            cv2.putText(annotated_frame, f"Frame: {frame_count}/{total_frames}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(annotated_frame, f"Detections: {len(detections)}", 
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Add legend
            legend_y = height - 150
            for i, (category, color) in enumerate(self.depth_colors.items()):
                cv2.rectangle(annotated_frame, (10, legend_y + i * 25), (30, legend_y + i * 25 + 20), color, -1)
                cv2.putText(annotated_frame, f"{category.capitalize()}", 
                           (35, legend_y + i * 25 + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Write frame to output video
            if video_writer:
                video_writer.write(annotated_frame)
            
            # Show preview
            if show_preview:
                cv2.imshow('Pothole Detection', annotated_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            
            # Progress update
            if frame_count % 30 == 0:
                progress = (frame_count / total_frames) * 100
                logger.info(f"Progress: {progress:.1f}% - Detections: {total_detections}")
        
        # Cleanup
        cap.release()
        if video_writer:
            video_writer.release()
        csv_file.close()
        if show_preview:
            cv2.destroyAllWindows()
        
        logger.info(f"Processing complete! Total detections: {total_detections}")
        logger.info(f"Measurements saved to: {csv_path}")
        if output_path:
            logger.info(f"Output video saved to: {output_path}")

def main():
    """Main function to run the pothole detector"""
    # Initialize detector
    detector = SimplePotholeDetector()
    
    # Input video path
    input_video = 'p.mp4'  # Change this to your video file
    
    # Output paths
    output_video = 'output/pothole_detection_output.avi'
    output_csv = 'output/pothole_measurements.csv'
    
    # Create output directory
    os.makedirs('output', exist_ok=True)
    
    # Process video
    detector.process_video(
        input_path=input_video,
        output_path=output_video,
        show_preview=True  # Set to False for headless operation
    )

if __name__ == '__main__':
    main() 