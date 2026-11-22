(base) malharlabade@Malhars-MacBook-Air code % cat      refine_door_vs_drawer.py 
import requests
import base64
from pathlib import Path

# Load FL_to_BL samples
fl_to_bl_imgs = sorted(Path("FL_to_BL").glob("img_*.jpg"))
fl_to_bl_indices = [0, 50, 100, 150]

fl_to_bl_samples = []
for idx in fl_to_bl_indices:
    if idx < len(fl_to_bl_imgs):
        with open(fl_to_bl_imgs[idx], "rb") as f:
            fl_to_bl_samples.append(base64.b64encode(f.read()).decode())

# Load BL_to_BR samples
bl_to_br_imgs = sorted(Path("BL_to_BR").glob("img_*.jpg"))
bl_to_br_indices = [0, 100, 200, 300]

bl_to_br_samples = []
for idx in bl_to_br_indices:
    if idx < len(bl_to_br_imgs):
        with open(bl_to_br_imgs[idx], "rb") as f:
            bl_to_br_samples.append(base64.b64encode(f.read()).decode())

images_to_compare = fl_to_bl_samples + bl_to_br_samples

prompt = """Images 1-4: FL_to_BL (sliding doors)
Images 5-8: BL_to_BR (drawer storage)

IGNORE knobs - focus on structural differences:

1. Floor detail: Track/rail at base vs flush frame with baseboard?
2. Seam type: Vertical seam where PANELS meet vs vertical divider between DRAWER SECTIONS?
3. Surface finish: Glossy/reflective vs matte?
4. Interior depth: Any visible depth inside (drawer recession) vs flat plane?
5. Horizontal lines: Seams between drawer faces vs smooth panel surface?
6. Frame structure: Minimalist sliding system vs built-in furniture frame?

What are the STRUCTURAL differences that don't depend on knobs?"""

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "minimax-m3:cloud",
        "prompt": prompt,
        "images": images_to_compare,
        "stream": False
    },
    timeout=240
)

print("Refined FL_to_BL vs BL_to_BR structural differences:\n")
print(response.json().get("response", ""))
(base) malharlabade@Malhars-MacBook-Air code % 
