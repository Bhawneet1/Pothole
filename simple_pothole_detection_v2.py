import cv2
import csv
import os
import glob
import logging

logger = logging.getLogger(__name__)

class PotholeDetection:
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
        default_csv_path = os.path.join(output_dir, 'pothole_measurements.csv')
        
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