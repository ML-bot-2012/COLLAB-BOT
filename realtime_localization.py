import requests
import base64
from pathlib import Path
from picamera2 import Picamera2
import cv2
import time

# Capture live
picam2 = Picamera2()
picam2.start()
time.sleep(0.2)
frame = picam2.capture_array()
picam2.stop()

frame = cv2.resize(frame, (320, 240))
_, buf = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 60])
live_b64 = base64.b64encode(buf).decode()

# Load 3 samples per location with explicit labels
images = [live_b64]
prompt_lines = ["IMAGE 0: LIVE CAMERA\n"]
idx = 1
loc_list = []

for loc_dir in sorted(Path(".").glob("*_*")):
    if not loc_dir.is_dir() or not (loc_dir / "summary.md").exists():
        continue
    loc_name = loc_dir.name
    loc_list.append(loc_name)
    samples = sorted(loc_dir.glob("*.jpg"))[:3]
    for i, sample in enumerate(samples):
        img = cv2.imread(str(sample))
        img = cv2.resize(img, (320, 240))
        _, buf = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 60])
        images.append(base64.b64encode(buf).decode())
    prompt_lines.append(f"IMAGES {idx}-{idx+2}: {loc_name} samples")
    idx += 3

prompt = "\n".join(prompt_lines) + "\n\nWhich location matches IMAGE 0? Name it. Top 3 with % confidence."

print(f"Sending {len(images)} images ({len(loc_list)} locations)...")
start = time.time()

response = requests.post(
    "http://localhost:11434/api/generate",
    json={"model": "minimax-m3:cloud", "prompt": prompt, "images": images, "stream": False},
    timeout=90
)

elapsed = time.time() - start
print(f"[{elapsed:.1f}s]\n")
print(response.json().get("response", "ERROR"))
(base) malharlabade@Malhars-MacBook-Air code % 
