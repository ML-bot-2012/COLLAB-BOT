
import requests
import base64
from pathlib import Path
from picamera2 import Picamera2
import cv2
import time

# Load location summaries
locations = {}
for location_dir in Path(".").glob("[A-Z]*_[A-Z]*"):
    summary = location_dir / "summary.md"
    if summary.exists():
        with open(summary) as f:
            locations[location_dir.name] = f.read()

print(f"Loaded {len(locations)} locations\n")

# Capture 5 consecutive frames
picam2 = Picamera2()
picam2.start()
time.sleep(1)

frames_b64 = []
print("[CAPTURING 5 FRAMES]")
for i in range(5):
    frame = picam2.capture_array()
    _, buffer = cv2.imencode('.jpg', frame)
    frames_b64.append(base64.b64encode(buffer).decode())
    print(f"✓ Frame {i+1}")
    time.sleep(0.2)

picam2.stop()

# Send all frames to VLM
prompt = f"""You are seeing 5 consecutive camera frames (Frame 1 to Frame 5).

Analyze the SEQUENCE and CONSISTENCY across all frames to determine location.

Locations:
{chr(10).join([f'- {name}: {desc.split(chr(10))[5:8]}' for name, desc in list(locations.items())[:8]])}

What location is this? Rank top 3 with percentages. Consider:
- Frame-to-frame consistency
- Progressive changes in perspective
- Recurring features across frames
- Structural patterns (not single-frame anomalies)"""

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "minimax-m3:cloud",
        "prompt": prompt,
        "images": frames_b64,
        "stream": False
    },
    timeout=180
)

print("\n[MULTI-FRAME LOCALIZATION]")
print(response.json().get("response", ""))
(base) malharlabade@Malhars-MacBook-Air code % 
