import sys
import os
sys.path.append('.')

from simple_pothole_detector_v2 import SimplePotholeDetectorV2

# Create detector instance
detector = SimplePotholeDetectorV2()

# Test different bounding box sizes
test_cases = [
    (100, 50, 1280, 720),   # Small bbox
    (200, 100, 1280, 720),  # Medium bbox
    (400, 200, 1280, 720),  # Large bbox
    (50, 25, 1280, 720),    # Very small bbox
    (600, 300, 1280, 720),  # Very large bbox
]

print("Testing depth estimation:")
print("=" * 50)

for width, height, frame_width, frame_height in test_cases:
    depth = detector.estimate_depth_improved(width, height, frame_width, frame_height)
    category, color = detector.get_depth_category(depth)
    
    print(f"Bbox: {width}x{height} -> Depth: {depth*100:.1f}cm -> Category: {category}")

print("\n" + "=" * 50)
print("Depth categories:")
for category, config in detector.depth_colors.items():
    print(f"  {category}: {config}") 