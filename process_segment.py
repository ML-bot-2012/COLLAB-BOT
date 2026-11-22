(base) malharlabade@Malhars-MacBook-Air code % cat process_segment.py
import sys
import requests
import base64
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

segment_name = "BL_to_BR"
segment_dir = Path(f"{segment_name}")

ground_truth = "DRAWER STORAGE FURNITURE. FLUSH WOODEN BASE/PLINTH at floor (NOT metal track). FIXED VERTICAL DIVIDERS between drawer sections (NOT overlapping sliding panels). MATTE FINISH surface with no glossy reflections. RECESSED DRAWER FACES inset within outer frame, creating visible recession/shadow lines at edges. MULTIPLE HORIZONTAL SEAMS visible - top edge line (drawer meets frame above) and bottom base line (drawer meets plinth) frame each drawer. FULL BUILT-IN FURNITURE CARCASS with substantial wooden frame, top rail, vertical stiles, bottom plinth all visible as separate structural elements. Mid-level angle, 25-35% floor."

print(f"Processing {segment_name}: {ground_truth}")
images = sorted(segment_dir.glob("img_*.jpg"))
total = len(images)
print(f"Found {total} images\n")

results = []
start_time = time.time()

def analyze_image(img_path, idx):
    try:
        with open(img_path, "rb") as f:
            img_base64 = base64.b64encode(f.read()).decode()
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "minimax-m3:cloud",
                "prompt": f"{segment_name}: {ground_truth}\n\nDescribe what you see.",
                "images": [img_base64],
                "stream": False
            },
            timeout=120
        )
        
        if response.status_code == 200:
            return response.json().get("response", "").strip()
    except:
        pass
    return None

print("[PROCESSING]")

with ThreadPoolExecutor(max_workers=8) as executor:
    futures = [executor.submit(analyze_image, img, i) for i, img in enumerate(images, 1)]
    
    for future in as_completed(futures):
        result = future.result()
        if result:
            results.append(result)
            print(f"✓ ({len(results)}/{total})")

elapsed = time.time() - start_time

md_content = f"""# {segment_name}
**Images:** {len(results)}/{total}  
**Time:** {elapsed:.1f}s  

## Landmark
{ground_truth}

## Analysis
{chr(10).join([r[:150] for r in results[:3]])}
"""

with open(segment_dir / "summary.md", "w") as f:
    f.write(md_content)

print(f"\n✓ Complete!")
(base) malharlabade@Malhars-MacBook-Air code % 
