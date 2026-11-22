(base) malharlabade@Malhars-MacBook-Air code % cat identify_drawer_vs_door.py
import requests
import base64
from picamera2 import Picamera2
import cv2
import time

picam2 = Picamera2()
picam2.start()
time.sleep(1)
frame = picam2.capture_array()
picam2.stop()

_, buffer = cv2.imencode('.jpg', frame)
live_b64 = base64.b64encode(buffer).decode()

prompt = """Look at this image carefully.

IS THIS A DRAWER OR A SLIDING DOOR?

Drawer characteristics: Rectangular faces that PULL OUT horizontally, knobs for gripping, no vertical track/rail at floor, sits flush in a frame, dark knobs protruding from white faces, seams between drawer sections.

Sliding door characteristics: Panels that SLIDE horizontally along floor track, no knobs (push-to-open or edge grip), dark horizontal track/rail at floor, vertical seam where panels meet, glossy reflective surface, no interior drawer depth.

Which is it? DRAWER or SLIDING DOOR?"""

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "minimax-m3:cloud",
        "prompt": prompt,
        "images": [live_b64],
        "stream": False
    },
    timeout=120
)

print("DRAWER vs SLIDING DOOR classification:\n")
print(response.json().get("response", ""))
(base) malharlabade@Malhars-MacBook-Air code % 
