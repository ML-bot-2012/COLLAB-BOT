<img width="696" height="228" alt="image" src="https://github.com/user-attachments/assets/dc034617-7aa7-4644-979b-eae3cd3c26c9" />

A robot swarm project. Raspberry Pi robots use a camera and a vision-language model (VLM) to recognize where they are in a room, and drive with a web UI or WASD keys.

<img width="1000" height="841" alt="image" src="https://github.com/user-attachments/assets/304ab34a-4a49-4584-81b9-5072f22a9f41" />


## Table of Contents

- [How it works](#how-it-works)
- [Scripts](#scripts)
- [Hardware](#hardware)
- [Software](#software)
- [Running](#running)
- [Status](#status)

## How it works

1. **Collect reference images.** `mvlmnav.py` drives the robot and saves room images to `mvlmnav_room/` through its `/collect` route.
2. **Describe and label segments.** `process_segment.py` and `quality_check.py` send images of wall segments (for example `FL_to_BL`, `BL_to_BR`) to the VLM and write a `summary.md` for each segment.
3. **Localize live.** `realtime_localization.py` and `realtime_localization_multiframe.py` capture a live frame and ask the VLM which known location it matches, with top-3 confidence scores.
4. **Classify landmarks.** `identify_drawer_vs_door.py` and `refine_door_vs_drawer.py` ask the VLM to tell sliding doors from drawer storage.

## Scripts

| File | Purpose |
|------|---------|
| `mvlmnav.py` | Flask app with camera stream, motor control, and image capture (`/collect`) |
| `web_control.py` | Flask app with camera stream and directional buttons |
| `wasd_control.py` | Keyboard (WASD) motor control |
| `camera_describe.py` | Describes camera images with the VLM and rates how much they look like a room corner |
| `realtime_localization.py` | Single-frame location matching |
| `realtime_localization_multiframe.py` | Multi-frame location matching |
| `process_segment.py` | Describes a wall segment and writes `summary.md` |
| `quality_check.py` | Checks segment descriptions against expected landmarks |
| `identify_drawer_vs_door.py` | Classifies drawer vs. sliding door |
| `refine_door_vs_drawer.py` | Refined drawer vs. sliding door classification |

## Hardware

- Raspberry Pi with a Picamera2-compatible camera
- Motor driver on BCM pins 17, 27, 23, 24 (direction) and 18, 25 (PWM)

## Software

- Python 3
- `picamera2`, `opencv-python` (`cv2`), `flask`, `requests`
- `RPi.GPIO` or `gpiozero`
- [Ollama](https://ollama.com) running locally on `localhost:11434` with the `minimax-m3:cloud` model

## Running

```bash
# Web control on the robot (port 5000)
python3 web_control.py

# Localize against saved segments
python3 realtime_localization.py
```

Run localization from the folder that holds the segment directories (`*_*/` with a `summary.md`).

## Status

Early work in progress. Scripts are drafts and paths are hardcoded.
