# AI-Powered Intelligent Border Surveillance — SIH Prototype

## What this prototype demonstrates

- Person and vehicle detection using YOLO
- Virtual restricted-zone / virtual-fence monitoring
- Automated intrusion alert
- Basic event logging to `events.csv`
- Works with a webcam or recorded CCTV-style video

## Quick start

### 1. Install Python
Use Python 3.10–3.13 if possible for the smoothest package compatibility.

### 2. Open this folder in VS Code

### 3. Install dependencies

Windows PowerShell:

```powershell
python -m pip install -r requirements.txt
```

If `python` is unavailable, try:

```powershell
py -m pip install -r requirements.txt
```

### 4. Run with webcam

```powershell
python main.py
```

Press `q` to quit.

### 5. Run with a recorded video

Put your video in this folder and run:

```powershell
python main.py --source test_video.mp4
```

The first run downloads the YOLO model automatically when internet access is available.

## Important

This is an academic demonstration prototype, not a production border-security system.

The virtual zone coordinates are defined near the top of `main.py`:

```python
ZONE = (180, 100, 620, 430)
```

If the zone does not fit your video, change these four numbers.

## Demo story

1. Start the video.
2. Show normal detections.
3. A person enters the red restricted zone.
4. The label changes to `INTRUDER`.
5. The bottom banner shows `INTRUSION ALERT`.
6. The event is added to `events.csv`.

## SIH positioning

Core innovation:

**Passive CCTV → Proactive Security Intelligence**

The prototype is intentionally small so the team can demonstrate the core concept first and extend it later with multi-camera support, tracking, authentication, maps, analytics, notifications, and a web dashboard.
