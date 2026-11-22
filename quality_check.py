(base) malharlabade@Malhars-MacBook-Air code % cat quality_check.py
import requests
import base64
from pathlib import Path

fl_to_bl_desc = "Sliding door panels with white/pale surfaces. Dark seam at bottom. Vertical divider. Floor-level angle."

segment_dir = Path("FL_to_BL")
images = sorted(segment_dir.glob("img_*.jpg"))

print(f"Analyzing {len(images)} images\n")
outliers = []

for i, img_path in enumerate(images[:50], 1):  # Sample first 50
    with open(img_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
    
    prompt = f"""FL_to_BL landmark: {fl_to_bl_desc}

Does THIS image match this landmark? Rate 0-100%.
If NO MATCH, explain what's different about this image."""
    
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "minimax-m3:cloud",
            "prompt": prompt,
            "images": [img_b64],
            "stream": False
        },
        timeout=120
    )
    
    result = response.json().get("response", "").strip()
    
    # Check if low match
    if "0%" in result or "10%" in result or "20%" in result or "not match" in result.lower():
        outliers.append((img_path.name, result[:200]))
        print(f"❌ {img_path.name}: OUTLIER")
    else:
        print(f"✓ {i}: Match")

print(f"\n\nOUTLIERS FOUND: {len(outliers)}")
for name, reason in outliers:
    print(f"\n{name}:")
    print(reason)
(base) malharlabade@Malhars-MacBook-Air code % 
