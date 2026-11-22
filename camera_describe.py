(base) malharlabade@Malhars-MacBook-Air code % cat camera_describe.py
from picamera2 import Picamera2
import subprocess
import os
import cv2
import time

picam2 = Picamera2()
picam2.start()

while True:
    frame = picam2.capture_array()
    timestamp = os.urandom(4).hex()
    img_path = f"/tmp/cam_{timestamp}.jpg"
    
    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    cv2.imwrite(img_path, frame_bgr)
    
    print("\n" + "="*60)
    print("Processing image...")
    time.sleep(0.5)
    
    print("\n[DESCRIPTION]")
    result = subprocess.run(
        ["ollama", "run", "minimax-m3:cloud", 
         f"Describe image in 1 sentence: {img_path}"],
        capture_output=True, text=True, timeout=30
    )
    desc = result.stdout.strip().split('\n')[-1]
    print(desc)
    time.sleep(0.5)
    
    print("\n[CORNER CONFIDENCE]")
    conf_prompt = f"Rate 0-100 how much this looks like a room corner. Reply: CONFIDENCE: XX\n{img_path}"
    conf_result = subprocess.run(
        ["ollama", "run", "minimax-m3:cloud", conf_prompt],
        capture_output=True, text=True, timeout=30
    )
    
    conf_text = conf_result.stdout.strip().split('\n')[-1]
    digits = ''.join(c for c in conf_text if c.isdigit())
    conf = int(digits[:2] if len(digits) >= 2 else digits if digits else "0")
    
    print(f"{conf}%")
    time.sleep(0.5)
    
    print("\n[RESULT]")
    if conf >= 90:
        print("✓ CORNER DETECTED")
    else:
        print("✗ NOT A CORNER")
    
    print("\n" + "="*60)
    
    os.remove(img_path)
    
    input("\nPress Enter for next image...")
(base) malharlabade@Malhars-MacBook-Air code % 
