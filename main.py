"""
AI-Powered Intelligent Border Surveillance - SIH Prototype
-----------------------------------------------------------
Runs with a webcam, video file, or a sample image.

Core demo:
1. YOLO detects people and vehicles.
2. A configurable virtual restricted zone is drawn.
3. If a person's center enters the zone, an intrusion alert is shown.
4. Intrusion events are logged to events.csv.

Install:
    python -m pip install -r requirements.txt

Run:
    python main.py

For a video file:
    python main.py --source test_video.mp4

For webcam:
    python main.py --source 0
"""

import argparse
import csv
import os
from datetime import datetime

import cv2
from ultralytics import YOLO

# YOLO model: downloads automatically the first time if internet is available.
MODEL_NAME = "yolo11n.pt"

# Restricted zone: x1, y1, x2, y2
ZONE = (180, 100, 620, 430)

# COCO classes useful for this prototype
PERSON = 0
VEHICLE_CLASSES = {
    2: "Car",
    3: "Motorcycle",
    5: "Bus",
    7: "Truck",
    1: "Bicycle",
}

LOG_FILE = "events.csv"


def ensure_log():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "event", "object", "confidence"])


def log_event(object_name, confidence):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(
            [now, "Restricted Zone Intrusion", object_name, f"{confidence:.2f}"]
        )


def inside_zone(cx, cy):
    x1, y1, x2, y2 = ZONE
    return x1 <= cx <= x2 and y1 <= cy <= y2


def main(source):
    ensure_log()
    model = YOLO(MODEL_NAME)

    # Convert webcam source "0" to integer.
    if str(source).isdigit():
        source = int(source)

    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        raise RuntimeError(
            f"Could not open source: {source}. "
            "Try --source 0 for webcam or provide a valid video path."
        )

    last_alert_second = None

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        # Keep a reasonable display size.
        h, w = frame.shape[:2]
        if w > 1100:
            scale = 1100 / w
            frame = cv2.resize(frame, (1100, int(h * scale)))

        results = model(frame, verbose=False)[0]

        person_count = 0
        vehicle_count = 0
        intrusion = False

        # Virtual restricted zone
        x1, y1, x2, y2 = ZONE
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
        cv2.putText(
            frame,
            "RESTRICTED ZONE",
            (x1 + 10, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 255),
            2,
        )

        if results.boxes is not None:
            for box in results.boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                if conf < 0.40:
                    continue

                bx1, by1, bx2, by2 = map(int, box.xyxy[0])
                cx = (bx1 + bx2) // 2
                cy = (by1 + by2) // 2

                if cls == PERSON:
                    person_count += 1
                    name = "Person"
                    if inside_zone(cx, cy):
                        intrusion = True
                        label = f"INTRUDER {conf:.0%}"
                    else:
                        label = f"Person {conf:.0%}"
                elif cls in VEHICLE_CLASSES:
                    vehicle_count += 1
                    name = VEHICLE_CLASSES[cls]
                    label = f"{name} {conf:.0%}"
                else:
                    continue

                # Detection box
                cv2.rectangle(frame, (bx1, by1), (bx2, by2), (0, 255, 0), 2)
                cv2.putText(
                    frame,
                    label,
                    (bx1, max(25, by1 - 8)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (0, 255, 0),
                    2,
                )
                cv2.circle(frame, (cx, cy), 4, (255, 255, 255), -1)

                if cls == PERSON and inside_zone(cx, cy):
                    cv2.line(frame, (cx, cy), ((x1 + x2)//2, (y1 + y2)//2), (0, 0, 255), 2)

        # Dashboard overlay
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (frame.shape[1], 88), (20, 20, 20), -1)
        frame = cv2.addWeighted(overlay, 0.78, frame, 0.22, 0)

        cv2.putText(
            frame, "AI-POWERED BORDER SURVEILLANCE",
            (18, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.78, (255, 255, 255), 2
        )
        cv2.putText(
            frame, "CAMERA: ONLINE   AI: ACTIVE",
            (18, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 2
        )
        cv2.putText(
            frame, f"PERSONS: {person_count}   VEHICLES: {vehicle_count}",
            (18, 82), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1
        )

        if intrusion:
            cv2.rectangle(
                frame, (0, frame.shape[0] - 72),
                (frame.shape[1], frame.shape[0]),
                (0, 0, 180), -1
            )
            cv2.putText(
                frame, "!!! INTRUSION ALERT: RESTRICTED ZONE !!!",
                (18, frame.shape[0] - 28),
                cv2.FONT_HERSHEY_SIMPLEX, 0.72, (255, 255, 255), 2
            )

            current_second = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if current_second != last_alert_second:
                log_event("Person", 1.0)
                last_alert_second = current_second

        cv2.imshow("SIH - Intelligent Border Surveillance Prototype", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source",
        default="0",
        help="0 for webcam, or path to a video file such as test_video.mp4",
    )
    args = parser.parse_args()
    main(args.source)
