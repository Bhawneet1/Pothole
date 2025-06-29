from flask import Flask, render_template, request, jsonify, send_file, url_for
import os
import cv2
import numpy as np
import torch
from ultralytics import YOLO
import logging
from datetime import datetime
import csv
import glob
from collections import deque
import random
import base64
import io
from PIL import Image
import tempfile
import zipfile
from werkzeug.utils import secure_filename

from simple_config_v2 import *

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'web_output'

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WebPotholeDetector:
    def __init__(self, model_path=MODEL_PATH):
        self.model_path = model_path
        self.device = 'cuda' if torch.cuda.is_available() and USE_GPU else 'cpu'
        try:
            self.model = YOLO(model_path)
            logger.info(f"Model loaded successfully from {model_path}")
            logger.info(f"Using device: {self.device}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
        self.detection_stats = {category: 0 for category in DEPTH_CATEGORIES.keys()}
        self.total_detections = 0
        self.depth_colors = {category: config['color'] for category, config in DEPTH_CATEGORIES.items()}
        logger.info("Web Pothole Detector initialized successfully")

    def estimate_depth_enhanced(self, bbox_width, bbox_height, frame_width, frame_height, confidence):
        frame_area = frame_width * frame_height
        bbox_area = bbox_width * bbox_height
        normalized_area = bbox_area / frame_area
        
        # Method 1: Area-based depth estimation
        depth_area = max(MIN_DEPTH, MAX_DEPTH - (normalized_area * DEPTH_SCALE_FACTOR * 0.3))
        
        # Method 2: Aspect ratio based depth estimation
        aspect_ratio = bbox_width / bbox_height if bbox_height > 0 else 1.0
        depth_aspect = max(MIN_DEPTH, 0.25 - (aspect_ratio * 0.05))
        
        # Method 3: Size-based depth estimation
        avg_size = (bbox_width + bbox_height) / 2
        depth_size = max(MIN_DEPTH, 0.28 - (avg_size / frame_width * 0.2))
        
        # Method 4: Confidence-based depth adjustment
        confidence_adjustment = 1.0 - (confidence * 0.3)
        
        # Weighted combination
        depth_combined = (
            depth_area * 0.4 +
            depth_aspect * 0.2 +
            depth_size * 0.4
        ) * confidence_adjustment
        
        # Apply depth constraints
        depth_final = max(MIN_DEPTH, min(MAX_DEPTH, depth_combined))
        
        # Add randomization
        random_factor = random.uniform(0.9, 1.1)
        depth_final = depth_final * random_factor
        
        # Ensure final depth is within bounds
        depth_final = max(MIN_DEPTH, min(MAX_DEPTH, depth_final))
        
        return depth_final

    def get_depth_category_enhanced(self, depth):
        for category, config in sorted(DEPTH_CATEGORIES.items(), key=lambda x: x[1]['priority']):
            if depth <= config['max_depth']:
                return category, self.depth_colors[category]
        return 'critical', self.depth_colors['critical']

    def filter_detections(self, detections, frame_shape):
        if not ENABLE_FILTERING:
            return detections
        filtered_detections = []
        for detection in detections:
            if detection['confidence'] < MIN_DETECTION_CONFIDENCE:
                continue
            bbox_width = detection['width']
            bbox_height = detection['height']
            if bbox_width < MIN_BBOX_SIZE or bbox_height < MIN_BBOX_SIZE:
                continue
            if bbox_width > MAX_BBOX_SIZE or bbox_height > MAX_BBOX_SIZE:
                continue
            aspect_ratio = bbox_width / bbox_height if bbox_height > 0 else 1.0
            if not (ASPECT_RATIO_RANGE[0] <= aspect_ratio <= ASPECT_RATIO_RANGE[1]):
                continue
            filtered_detections.append(detection)
        return filtered_detections

    def detect_potholes_image(self, image_path):
        """Detect potholes in a single image"""
        frame = cv2.imread(image_path)
        if frame is None:
            raise ValueError("Could not read image")
        
        annotated_frame = frame.copy()
        detections = []
        frame_height, frame_width = frame.shape[:2]
        
        results = self.model(frame, verbose=False, conf=CONFIDENCE_THRESHOLD, iou=NMS_THRESHOLD, show=False)
        
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    confidence = float(box.conf[0].cpu().numpy())
                    width = x2 - x1
                    height = y2 - y1
                    depth = self.estimate_depth_enhanced(width, height, frame_width, frame_height, confidence)
                    depth_category, color = self.get_depth_category_enhanced(depth)
                    
                    detection_info = {
                        'bbox': (x1, y1, x2, y2),
                        'width': width,
                        'height': height,
                        'depth': depth,
                        'category': depth_category,
                        'color': color,
                        'confidence': confidence,
                        'center': ((x1 + x2) // 2, (y1 + y2) // 2)
                    }
                    detections.append(detection_info)
        
        filtered_detections = self.filter_detections(detections, frame.shape)
        
        # Draw detections on frame
        for detection in filtered_detections:
            self.detection_stats[detection['category']] += 1
            self.total_detections += 1
            x1, y1, x2, y2 = detection['bbox']
            color = detection['color']
            thickness = max(1, int(detection['confidence'] * 5))
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, thickness)
            
            text_lines = [
                f"Depth: {detection['depth']*100:.1f}cm",
                f"Size: {detection['width']}x{detection['height']}px",
                f"Category: {detection['category']}",
                f"Conf: {detection['confidence']:.2f}"
            ]
            text_x = x1
            text_y = y1 - 10
            for i, line in enumerate(text_lines):
                text_size = cv2.getTextSize(line, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
                cv2.rectangle(annotated_frame, (text_x, text_y - text_size[1] - 5), 
                             (text_x + text_size[0], text_y + 5), (0, 0, 0), -1)
                cv2.putText(annotated_frame, line, (text_x, text_y - i * 15), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return annotated_frame, filtered_detections

    def detect_potholes_video(self, video_path, output_path):
        """Detect potholes in video and save results"""
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video: {video_path}")
        
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        output_fps = max(1, fps // 2)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(output_path, fourcc, output_fps, (width, height))
        
        csv_path = output_path.replace('.avi', '.csv')
        csv_file = open(csv_path, 'w', newline='')
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Frame', 'Timestamp', 'Width_px', 'Height_px', 'Depth_cm', 'Category', 'Confidence', 'X1', 'Y1', 'X2', 'Y2', 'Priority'])
        
        frame_count = 0
        processed_frames = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            if frame_count % FRAME_SKIP != 0:
                continue
            
            processed_frames += 1
            annotated_frame, detections = self.detect_potholes_image_from_frame(frame)
            
            # Write to CSV
            timestamp = frame_count / fps
            for detection in detections:
                x1, y1, x2, y2 = detection['bbox']
                priority = DEPTH_CATEGORIES[detection['category']]['priority']
                csv_writer.writerow([
                    frame_count, f"{timestamp:.2f}", detection['width'], detection['height'],
                    f"{detection['depth']*100:.1f}", detection['category'], 
                    f"{detection['confidence']:.3f}", x1, y1, x2, y2, priority
                ])
            
            out.write(annotated_frame)
        
        cap.release()
        out.release()
        csv_file.close()
        
        return csv_path

    def detect_potholes_image_from_frame(self, frame):
        """Detect potholes in a frame (for video processing)"""
        annotated_frame = frame.copy()
        detections = []
        frame_height, frame_width = frame.shape[:2]
        
        results = self.model(frame, verbose=False, conf=CONFIDENCE_THRESHOLD, iou=NMS_THRESHOLD, show=False)
        
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    confidence = float(box.conf[0].cpu().numpy())
                    width = x2 - x1
                    height = y2 - y1
                    depth = self.estimate_depth_enhanced(width, height, frame_width, frame_height, confidence)
                    depth_category, color = self.get_depth_category_enhanced(depth)
                    
                    detection_info = {
                        'bbox': (x1, y1, x2, y2),
                        'width': width,
                        'height': height,
                        'depth': depth,
                        'category': depth_category,
                        'color': color,
                        'confidence': confidence,
                        'center': ((x1 + x2) // 2, (y1 + y2) // 2)
                    }
                    detections.append(detection_info)
        
        filtered_detections = self.filter_detections(detections, frame.shape)
        
        # Draw detections on frame
        for detection in filtered_detections:
            self.detection_stats[detection['category']] += 1
            self.total_detections += 1
            x1, y1, x2, y2 = detection['bbox']
            color = detection['color']
            thickness = max(1, int(detection['confidence'] * 5))
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, thickness)
            
            text_lines = [
                f"Depth: {detection['depth']*100:.1f}cm",
                f"Size: {detection['width']}x{detection['height']}px",
                f"Category: {detection['category']}",
                f"Conf: {detection['confidence']:.2f}"
            ]
            text_x = x1
            text_y = y1 - 10
            for i, line in enumerate(text_lines):
                text_size = cv2.getTextSize(line, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
                cv2.rectangle(annotated_frame, (text_x, text_y - text_size[1] - 5), 
                             (text_x + text_size[0], text_y + 5), (0, 0, 0), -1)
                cv2.putText(annotated_frame, line, (text_x, text_y - i * 15), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return annotated_frame, filtered_detections

    def get_statistics(self):
        """Get detection statistics"""
        stats = {
            'total_detections': self.total_detections,
            'categories': {}
        }
        
        for category, config in sorted(DEPTH_CATEGORIES.items(), key=lambda x: x[1]['priority']):
            count = self.detection_stats[category]
            percentage = (count / self.total_detections * 100) if self.total_detections > 0 else 0
            stats['categories'][category] = {
                'count': count,
                'percentage': percentage,
                'description': config['description'],
                'priority': config['priority']
            }
        
        return stats

# Initialize the detector
detector = WebPotholeDetector()

def allowed_file(filename):
    """Check if file extension is allowed"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'mp4', 'avi', 'mov', 'mkv'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        if not file or not allowed_file(file.filename):
            return jsonify({'error': f'Invalid file type. Allowed: png, jpg, jpeg, gif, bmp, mp4, avi, mov, mkv'}), 400
        
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Reset detector stats
        detector.detection_stats = {category: 0 for category in DEPTH_CATEGORIES.keys()}
        detector.total_detections = 0
        
        file_ext = filename.rsplit('.', 1)[1].lower()
        
        if file_ext in ['mp4', 'avi', 'mov', 'mkv']:
            # Process video
            output_video = os.path.join(app.config['OUTPUT_FOLDER'], f"processed_{filename}.avi")
            csv_path = detector.detect_potholes_video(filepath, output_video)
            
            # Create zip file with results
            zip_path = os.path.join(app.config['OUTPUT_FOLDER'], f"results_{filename}.zip")
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                zipf.write(output_video, os.path.basename(output_video))
                zipf.write(csv_path, os.path.basename(csv_path))
            
            stats = detector.get_statistics()
            
            return jsonify({
                'success': True,
                'message': 'Video processed successfully',
                'results': {
                    'video_url': url_for('download_file', filename=f"processed_{filename}.avi"),
                    'csv_url': url_for('download_file', filename=os.path.basename(csv_path)),
                    'zip_url': url_for('download_file', filename=f"results_{filename}.zip"),
                    'statistics': stats
                }
            })
        
        else:
            # Process image
            annotated_image, detections = detector.detect_potholes_image(filepath)
            
            # Save annotated image
            output_image = os.path.join(app.config['OUTPUT_FOLDER'], f"processed_{filename}")
            cv2.imwrite(output_image, annotated_image)
            
            # Convert to base64 for display
            _, buffer = cv2.imencode('.jpg', annotated_image)
            img_base64 = base64.b64encode(buffer).decode('utf-8')
            
            stats = detector.get_statistics()
            
            return jsonify({
                'success': True,
                'message': 'Image processed successfully',
                'results': {
                    'image_data': f"data:image/jpeg;base64,{img_base64}",
                    'download_url': url_for('download_file', filename=f"processed_{filename}"),
                    'detections': [
                        {
                            'depth': f"{d['depth']*100:.1f}cm",
                            'category': d['category'],
                            'confidence': f"{d['confidence']:.2f}",
                            'size': f"{d['width']}x{d['height']}px"
                        } for d in detections
                    ],
                    'statistics': stats
                }
            })
    
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        return jsonify({'error': f'Error processing file: {str(e)}'}), 500
    
    finally:
        # Clean up uploaded file
        if 'filepath' in locals() and os.path.exists(filepath):
            os.remove(filepath)

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join(app.config['OUTPUT_FOLDER'], filename), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 