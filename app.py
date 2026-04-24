'''import streamlit as st
from ultralytics import YOLO
import cv2
import tempfile

st.title("🚗 Smart Driver Assistance System")

model = YOLO("yolov8n.pt")

uploaded_file = st.file_uploader("Upload Image or Video", type=["jpg","png","mp4","avi"])

if uploaded_file is not None:

    # Save file temporarily
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(uploaded_file.read())

    if uploaded_file.type.startswith("image"):
        img = cv2.imread(tfile.name)
        results = model(img)

        for r in results:
            output = r.plot()

        st.image(output, caption="Detected Image")

    else:
        cap = cv2.VideoCapture(tfile.name)

        stframe = st.empty()

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            results = model(frame)

            for r in results:
                frame = r.plot()

            stframe.image(frame)

        cap.release()
       
import streamlit as st
from ultralytics import YOLO
import cv2
import tempfile
import numpy as np

st.title("🚗 Smart Driver Assistance System")

model = YOLO("yolov8n.pt")

# ---------------- CLEAN LANE DETECTION ----------------
def detect_lanes(frame):
    height, width = frame.shape[:2]

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    edges = cv2.Canny(blur, 50, 150)

    mask = np.zeros_like(edges)

    polygon = np.array([[
        (0, height),
        (width, height),
        (width, int(height*0.6)),
        (0, int(height*0.6))
    ]], np.int32)

    cv2.fillPoly(mask, polygon, 255)
    cropped_edges = cv2.bitwise_and(edges, mask)

    lines = cv2.HoughLinesP(cropped_edges, 1, np.pi/180, 50,
                            minLineLength=100, maxLineGap=50)

    left_lines = []
    right_lines = []

    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]

            # avoid vertical & small lines
            if x2 == x1:
                continue

            slope = (y2 - y1) / (x2 - x1)

            # filter noise
            if abs(slope) < 0.5:
                continue

            if slope < 0:
                left_lines.append(line[0])
            else:
                right_lines.append(line[0])

    # function to average lines
    def average_line(lines):
        if len(lines) == 0:
            return None

        x1 = int(np.mean([l[0] for l in lines]))
        y1 = int(np.mean([l[1] for l in lines]))
        x2 = int(np.mean([l[2] for l in lines]))
        y2 = int(np.mean([l[3] for l in lines]))

        return x1, y1, x2, y2

    left_avg = average_line(left_lines)
    right_avg = average_line(right_lines)

    if left_avg:
        cv2.line(frame, (left_avg[0], left_avg[1]),
                 (left_avg[2], left_avg[3]), (0,255,0), 5)

    if right_avg:
        cv2.line(frame, (right_avg[0], right_avg[1]),
                 (right_avg[2], right_avg[3]), (0,255,0), 5)

    return frame
# ------------------------------------------------------

uploaded_file = st.file_uploader("Upload Image or Video", type=["jpg","png","mp4","avi"])

if uploaded_file is not None:

    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(uploaded_file.read())

    # ---------------- IMAGE ----------------
    if uploaded_file.type.startswith("image"):
        img = cv2.imread(tfile.name)
        results = model(img)

        for r in results:
            output = r.plot()

        st.image(output, caption="Detected Image")

    # ---------------- VIDEO ----------------
    else:
        cap = cv2.VideoCapture(tfile.name)
        stframe = st.empty()

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # YOLO Detection
            results = model(frame)

            # ✅ SHOW LABELS + CONFIDENCE
            for r in results:
                frame = r.plot()

                # -------- COLLISION WARNING --------
                for box in r.boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])

                    w = x2 - x1
                    h = y2 - y1
                    box_area = w * h
                    frame_area = frame.shape[0] * frame.shape[1]

                    ratio = box_area / frame_area

                    if ratio > 0.15:
                        cv2.putText(frame, "WARNING: OBJECT TOO CLOSE!",
                                    (50,50),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    1,
                                    (0,0,255),
                                    3)
import streamlit as st
from ultralytics import YOLO
import cv2
import tempfile
import numpy as np

st.title("🚗 Smart Driver Assistance System")

model = YOLO("yolov8n.pt")

# ---------------- CLEAN LANE DETECTION ----------------
def detect_lanes(frame):
    height, width = frame.shape[:2]

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    edges = cv2.Canny(blur, 50, 150)

    mask = np.zeros_like(edges)

    polygon = np.array([[
        (0, height),
            # -------- LANE DETECTION --------
            frame = detect_lanes(frame)

            # Show frame
            stframe.image(frame, channels="BGR")

        cap.release()
        


import streamlit as st
from ultralytics import YOLO
import cv2
import tempfile
import numpy as np
import time

st.title("🚗 Smart Driver Assistance System")

# 🔥 Use better model (change to yolov8l.pt if system supports)
model = YOLO("yolov8m.pt")

# ---------------- LANE DETECTION ----------------
def detect_lanes(frame):
    height, width = frame.shape[:2]

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # Improved edge detection
    edges = cv2.Canny(blur, 100, 200)

    mask = np.zeros_like(edges)

    # 🔥 Trapezium ROI (better accuracy)
    polygon = np.array([[
        (200, height),
        (width - 200, height),
        (width // 2 + 100, int(height * 0.6)),
        (width // 2 - 100, int(height * 0.6))
    ]], np.int32)

    cv2.fillPoly(mask, polygon, 255)
    cropped_edges = cv2.bitwise_and(edges, mask)

    lines = cv2.HoughLinesP(
        cropped_edges,
        1,
        np.pi / 180,
        50,
        minLineLength=100,
        maxLineGap=50
    )

    left_lines = []
    right_lines = []

    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]

            if x2 == x1:
                continue

            slope = (y2 - y1) / (x2 - x1)

            if abs(slope) < 0.5:
                continue

            if slope < 0:
                left_lines.append(line[0])
            else:
                right_lines.append(line[0])

    def average_line(lines):
        if len(lines) == 0:
            return None

        x1 = int(np.mean([l[0] for l in lines]))
        y1 = int(np.mean([l[1] for l in lines]))
        x2 = int(np.mean([l[2] for l in lines]))
        y2 = int(np.mean([l[3] for l in lines]))

        return x1, y1, x2, y2

    left_avg = average_line(left_lines)
    right_avg = average_line(right_lines)

    if left_avg:
        cv2.line(frame, (left_avg[0], left_avg[1]),
                 (left_avg[2], left_avg[3]), (0, 255, 0), 5)

    if right_avg:
        cv2.line(frame, (right_avg[0], right_avg[1]),
                 (right_avg[2], right_avg[3]), (0, 255, 0), 5)

    return frame
# ------------------------------------------------------


uploaded_file = st.file_uploader("Upload Image or Video", type=["jpg", "png", "mp4", "avi"])

if uploaded_file is not None:

    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(uploaded_file.read())

    # ---------------- IMAGE ----------------
    if uploaded_file.type.startswith("image"):
        img = cv2.imread(tfile.name)
        results = model(img)

        for r in results:
            output = r.plot()

        output = detect_lanes(output)

        st.image(output, caption="Detected Image")

    # ---------------- VIDEO ----------------
    else:
        cap = cv2.VideoCapture(tfile.name)
        stframe = st.empty()

        total_frames = 0
        warnings = 0

        while cap.isOpened():
            start = time.time()

            ret, frame = cap.read()
            if not ret:
                break

            results = model(frame)

            for r in results:
                frame = r.plot()

                # -------- COLLISION WARNING --------
                for box in r.boxes:
                    conf = float(box.conf[0])

                    # 🔥 Confidence filtering
                    if conf < 0.5:
                        continue

                    x1, y1, x2, y2 = map(int, box.xyxy[0])

                    w = x2 - x1
                    h = y2 - y1
                    box_area = w * h
                    frame_area = frame.shape[0] * frame.shape[1]

                    ratio = box_area / frame_area

                    frame_center = frame.shape[1] // 2
                    center_x = (x1 + x2) // 2

                    # 🔥 Smart collision logic
                    if ratio > 0.12 and abs(center_x - frame_center) < 120:
                        warnings += 1
                        cv2.putText(frame, "WARNING: OBJECT TOO CLOSE!",
                                    (50, 50),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    1,
                                    (0, 0, 255),
                                    3)

            # -------- LANE DETECTION --------
            frame = detect_lanes(frame)

            # -------- FPS DISPLAY --------
            fps = 1 / (time.time() - start)
            cv2.putText(frame, f"FPS: {int(fps)}",
                        (20, 90),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (255, 0, 0),
                        2)

            total_frames += 1

            stframe.image(frame, channels="BGR")

        cap.release()

        # -------- FINAL ACCURACY --------
        if total_frames > 0:
            accuracy = warnings / total_frames
            st.write(f"⚠️ Warning Rate: {accuracy:.2f}")
            
import streamlit as st
from ultralytics import YOLO
import cv2
import tempfile
import numpy as np
import time
from playsound import playsound
from lane_ai import AILaneDetector
lane_detector = AILaneDetector()

st.title("🚗 Smart Driver Assistance System")

# Load model
model = YOLO("yolov8m.pt")

# ---------------- LANE DETECTION ----------------


uploaded_file = st.file_uploader("Upload Image or Video", type=["jpg","png","mp4","avi"])

conf_threshold = st.sidebar.slider("Confidence Threshold", 0.1, 1.0, 0.5)

if uploaded_file is not None:

    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(uploaded_file.read())

    cap = cv2.VideoCapture(tfile.name)
    stframe = st.empty()

    total_frames = 0
    warnings = 0
    high_conf_warnings = 0

    while cap.isOpened():
        start = time.time()

        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame)

        frame_center = frame.shape[1] // 2
        danger_detected = False

        for r in results:
            frame = r.plot()

            for box in r.boxes:
                conf = float(box.conf[0])

                if conf < conf_threshold:
                    continue

                x1, y1, x2, y2 = map(int, box.xyxy[0])

                w = x2 - x1
                h = y2 - y1
                box_area = w * h
                frame_area = frame.shape[0] * frame.shape[1]

                ratio = box_area / frame_area

                # Distance estimation
                distance = 1 / (ratio + 1e-6)

                center_x = (x1 + x2) // 2

                if distance < 8 and abs(center_x - frame_center) < 120:
                    danger_detected = True
                    warnings += 1

                    if conf > 0.7:
                        high_conf_warnings += 1

                    cv2.putText(frame, "⚠ COLLISION WARNING!",
                                (50, 50),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                1,
                                (0, 0, 255), 3)

        # 🔊 Sound alert
        if danger_detected:
            try:
                playsound("alert.wav", block=False)
            except:
                pass

        # Lane detection
        frame = lane_detector.detect(frame)
        # FPS
        fps = 1 / (time.time() - start)
        cv2.putText(frame, f"FPS: {int(fps)}",
                    (20, 100),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0,255,0), 2)

        total_frames += 1
        stframe.image(frame, channels="BGR")

    cap.release()

    # Metrics
    if total_frames > 0:
        warning_rate = warnings / total_frames
        reliability = high_conf_warnings / warnings if warnings > 0 else 0

        st.write(f"⚠ Warning Rate: {warning_rate:.2f}")
        st.write(f"✅ Reliability: {reliability:.2f}")
        
import streamlit as st
from ultralytics import YOLO
import cv2
import tempfile
import numpy as np
import time
from lane_ai import AILaneDetector

st.title("🚗 AI-Based Driver Assistance System")

# 🔥 Fast model
model = YOLO("yolov8n.pt")

lane_detector = AILaneDetector()

uploaded_file = st.file_uploader("Upload Video", type=["jpg","jpeg","png","mp4","avi"])

conf_threshold = st.sidebar.slider("Confidence Threshold", 0.1, 1.0, 0.5)

if uploaded_file is not None:

    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(uploaded_file.read())
    
    if uploaded_file.type.startswith("image"):
        img = cv2.imread(tfile.name)
        results = model(img)

        for r in results:
            output = r.plot()

        st.image(output, caption="Detected Image")

    
    cap = cv2.VideoCapture(tfile.name)
    stframe = st.empty()

    total_frames = 0
    warnings = 0
    high_conf_warnings = 0

    frame_count = 0

    while cap.isOpened():
        start = time.time()

        ret, frame = cap.read()
        if not ret:
            break

        # 🔥 Resize for speed
        frame = cv2.resize(frame, (640, 360))

        frame_count += 1

        # 🔥 Skip frames
        if frame_count % 2 != 0:
            continue

        results = model(frame)

        frame_center = frame.shape[1] // 2
        danger_detected = False

        for r in results:
            frame = r.plot()

            for box in r.boxes:
                conf = float(box.conf[0])

                if conf < conf_threshold:
                    continue

                x1, y1, x2, y2 = map(int, box.xyxy[0])

                w = x2 - x1
                h = y2 - y1
                box_area = w * h
                frame_area = frame.shape[0] * frame.shape[1]

                ratio = box_area / frame_area
                distance = 1 / (ratio + 1e-6)

                center_x = (x1 + x2) // 2

                if distance < 8 and abs(center_x - frame_center) < 120:
                    danger_detected = True
                    warnings += 1

                    if conf > 0.7:
                        high_conf_warnings += 1

                    cv2.putText(frame, "⚠ COLLISION WARNING!",
                                (50, 50),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                1,
                                (0, 0, 255), 2)

                    cv2.putText(frame, f"Dist: {distance:.2f}",
                                (50, 90),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.8,
                                (255, 255, 0), 2)

        # 🔥 Run lane detection less frequently
        if frame_count % 3 == 0:
            frame = lane_detector.detect(frame)

        # FPS
        fps = 1 / (time.time() - start)
        cv2.putText(frame, f"FPS: {int(fps)}",
                    (20, 140),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0,255,0), 2)

        total_frames += 1
        stframe.image(frame, channels="BGR")

    cap.release()

    # Metrics
    if total_frames > 0:
        warning_rate = warnings / total_frames
        reliability = high_conf_warnings / warnings if warnings > 0 else 0
        accuracy = high_conf_warnings / total_frames

        st.write(f"⚠ Warning Rate: {warning_rate:.2f}")
        st.write(f"✅ Reliability: {reliability:.2f}")
        st.write(f"🎯 Accuracy: {accuracy:.2f}")
        
        
        
import streamlit as st
from ultralytics import YOLO
import cv2
import tempfile
import numpy as np
import time
from lane_ai import AILaneDetector

st.title("🚗 AI-Based Driver Assistance System")
mode = st.sidebar.selectbox(
    "Driving Mode",
    ["City Mode", "Highway Mode"]
)

st.write(f"### Current Mode: {mode}")

# Load model
model = YOLO("yolov8n.pt")
lane_detector = AILaneDetector()

uploaded_file = st.file_uploader("Upload File", type=["jpg","jpeg","png","mp4","avi"])
conf_threshold = st.sidebar.slider("Confidence Threshold", 0.1, 1.0, 0.5)

if uploaded_file is not None:

    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(uploaded_file.read())

    # ================= IMAGE PROCESSING =================
    if uploaded_file.type.startswith("image"):
        img = cv2.imread(tfile.name)
        results = model(img)

        for r in results:
            output = r.plot()

        st.image(output, caption="Detected Image")

    # ================= VIDEO PROCESSING =================
    else:
        cap = cv2.VideoCapture(tfile.name)
        stframe = st.empty()

        total_frames = 0
        warnings = 0
        high_conf_warnings = 0
        frame_count = 0

        while cap.isOpened():
            start = time.time()

            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.resize(frame, (640, 360))
            frame_count += 1

            # Skip frames for speed
            if frame_count % 2 != 0:
                continue

            results = model(frame)
            frame_center = frame.shape[1] // 2

            distance = None  # ✅ FIX: initialize

            for r in results:
                frame = r.plot()

                for box in r.boxes:
                    conf = float(box.conf[0])
                    if conf < conf_threshold:
                        continue

                    x1, y1, x2, y2 = map(int, box.xyxy[0])

                    w = x2 - x1
                    h = y2 - y1
                    ratio = (w * h) / (frame.shape[0] * frame.shape[1])
                    distance = 1 / (ratio + 1e-6)

                    center_x = (x1 + x2) // 2

                    # Collision condition
                    if distance < 8 and abs(center_x - frame_center) < 120:
                        warnings += 1

                        if conf > 0.7:
                            high_conf_warnings += 1

                        cv2.putText(frame, "⚠ COLLISION WARNING!",
                                    (50, 50),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    1, (0, 0, 255), 2)

                        # ✅ SHOW DISTANCE ONLY WHEN VALID
                        cv2.putText(frame, f"Dist: {distance:.2f}",
                                    (50, 90),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    0.8,
                                    (255, 255, 0), 2)

            # Lane detection (reduced frequency)
            if frame_count % 3 == 0:
                #frame = lane_detector.detect(frame)
                frame = lane_detector.detect(frame, mode)

            # FPS display
            fps = 1 / (time.time() - start)
            cv2.putText(frame, f"FPS: {int(fps)}",
                        (20, 140),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1, (0, 255, 0), 2)

            total_frames += 1
            stframe.image(frame, channels="BGR")

        cap.release()

        # ================= METRICS =================
        if total_frames > 0:
            warning_rate = warnings / total_frames
            reliability = high_conf_warnings / warnings if warnings > 0 else 0
            accuracy = high_conf_warnings / total_frames

            st.write(f"⚠ Warning Rate: {warning_rate:.2f}")
            st.write(f"✅ Reliability: {reliability:.2f}")
            st.write(f"🎯 Accuracy: {accuracy:.2f}")
            
    
            
            
import streamlit as st
from ultralytics import YOLO
import cv2
import tempfile
import numpy as np
import time
from lane_ai import AILaneDetector

st.title("🚗 AI-Based Driver Assistance System")

# 🔥 Mode selection
mode = st.sidebar.selectbox(
    "Driving Mode",
    ["City Mode", "Highway Mode"]
)

st.write(f"### Current Mode: {mode}")

model = YOLO("yolov8n.pt")
lane_detector = AILaneDetector()

uploaded_file = st.file_uploader("Upload File", type=["jpg","jpeg","png","mp4","avi"])
conf_threshold = st.sidebar.slider("Confidence Threshold", 0.1, 1.0, 0.5)

if uploaded_file is not None:

    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(uploaded_file.read())

    # IMAGE
    if uploaded_file.type.startswith("image"):
        img = cv2.imread(tfile.name)
        results = model(img)

        for r in results:
            output = r.plot()

        st.image(output, caption="Detected Image")

    # VIDEO
    else:
        cap = cv2.VideoCapture(tfile.name)
        stframe = st.empty()

        total_frames = 0
        warnings = 0
        high_conf_warnings = 0
        frame_count = 0

        while cap.isOpened():
            start = time.time()

            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.resize(frame, (640, 360))
            frame_count += 1

            if frame_count % 2 != 0:
                continue

            results = model(frame)
            frame_center = frame.shape[1] // 2

            for r in results:
                frame = r.plot()

                for box in r.boxes:
                    conf = float(box.conf[0])
                    if conf < conf_threshold:
                        continue

                    x1, y1, x2, y2 = map(int, box.xyxy[0])

                    w = x2 - x1
                    h = y2 - y1
                    ratio = (w * h) / (frame.shape[0] * frame.shape[1])
                    distance = 1 / (ratio + 1e-6)

                    center_x = (x1 + x2) // 2

                    cls = int(box.cls[0])
                    label = model.names[cls]

                    # 🔥 Mode-based thresholds
                    if mode == "City Mode":
                        collision_threshold = 12
                        center_range = 150
                        if label in ["person", "bicycle"]:
                            collision_threshold += 2
                    else:
                        collision_threshold = 6
                        center_range = 100
                        if label in ["car", "truck", "bus"]:
                            collision_threshold -= 1

                    # Collision check
                    if distance < collision_threshold and abs(center_x - frame_center) < center_range:
                        warnings += 1

                        if conf > 0.7:
                            high_conf_warnings += 1

                        cv2.putText(frame, "⚠ COLLISION WARNING!",
                                    (50, 50),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    1, (0, 0, 255), 2)

                        cv2.putText(frame, f"Dist: {distance:.2f}",
                                    (50, 90),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    0.8,
                                    (255, 255, 0), 2)

            # 🔥 Lane detection based on mode
            if mode == "Highway Mode":
                if frame_count % 2 == 0:
                    frame = lane_detector.detect(frame, mode)
            else:
                if frame_count % 4 == 0:
                    frame = lane_detector.detect(frame, mode)

            # 🔥 Show mode
            if mode == "City Mode":
                cv2.putText(frame, "MODE: CITY",
                            (20, 40),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1, (0, 255, 255), 2)
            else:
                cv2.putText(frame, "MODE: HIGHWAY",
                            (20, 40),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1, (255, 0, 0), 2)

            fps = 1 / (time.time() - start)
            cv2.putText(frame, f"FPS: {int(fps)}",
                        (20, 140),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1, (0, 255, 0), 2)

            total_frames += 1
            stframe.image(frame, channels="BGR")

        cap.release()

        if total_frames > 0:
            warning_rate = warnings / total_frames
            reliability = high_conf_warnings / warnings if warnings > 0 else 0
            accuracy = high_conf_warnings / total_frames

            st.write(f"⚠ Warning Rate: {warning_rate:.2f}")
            st.write(f"✅ Reliability: {reliability:.2f}")
            st.write(f"🎯 Accuracy: {accuracy:.2f}")
            
            
            
            
            
import streamlit as st
from ultralytics import YOLO
import cv2
import tempfile
import numpy as np
import time
from lane_ai import AILaneDetector

st.title("🚗 AI-Based Driver Assistance System")

# Mode controls
auto_mode = st.sidebar.checkbox("Enable Auto Mode", value=True)

manual_mode = st.sidebar.selectbox(
    "Manual Mode",
    ["City Mode", "Highway Mode"]
)

mode = manual_mode

model = YOLO("yolov8n.pt")
lane_detector = AILaneDetector()

uploaded_file = st.file_uploader("Upload File", type=["jpg","jpeg","png","mp4","avi"])
conf_threshold = st.sidebar.slider("Confidence Threshold", 0.1, 1.0, 0.5)

if uploaded_file is not None:

    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(uploaded_file.read())

    cap = cv2.VideoCapture(tfile.name)
    stframe = st.empty()

    total_frames = 0
    warnings = 0
    high_conf_warnings = 0
    frame_count = 0

    if "prev_mode" not in st.session_state:
        st.session_state.prev_mode = "City Mode"

    while cap.isOpened():
        start = time.time()

        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.resize(frame, (640, 360))
        frame_count += 1

        if frame_count % 3 != 0:
            continue

        results = model(frame)
        frame_center = frame.shape[1] // 2

        vehicle_count = 0
        person_count = 0

        # First pass: count objects
        for r in results:
            frame = r.plot()

            for box in r.boxes:
                conf = float(box.conf[0])
                if conf < conf_threshold:
                    continue

                cls = int(box.cls[0])
                label = model.names[cls]

                if label in ["car", "truck", "bus"]:
                    vehicle_count += 1
                if label == "person":
                    person_count += 1

        # Auto mode decision
        if auto_mode:
            if vehicle_count > 3:
                mode = "Highway Mode"
            elif person_count > 2:
                mode = "City Mode"
            else:
                mode = st.session_state.prev_mode

            st.session_state.prev_mode = mode

        # Second pass: collision detection
        for r in results:
            for box in r.boxes:
                conf = float(box.conf[0])
                if conf < conf_threshold:
                    continue

                x1, y1, x2, y2 = map(int, box.xyxy[0])

                w = x2 - x1
                h = y2 - y1
                ratio = (w * h) / (frame.shape[0] * frame.shape[1])
                distance = 1 / (ratio + 1e-6)

                center_x = (x1 + x2) // 2

                # Mode thresholds
                if mode == "City Mode":
                    collision_threshold = 12
                    center_range = 150
                else:
                    collision_threshold = 6
                    center_range = 100

                if distance < collision_threshold and abs(center_x - frame_center) < center_range:
                    warnings += 1

                    if conf > 0.7:
                        high_conf_warnings += 1

                    cv2.putText(frame, "⚠ COLLISION WARNING!",
                                (50, 80),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                1.2, (0, 0, 255), 3)

        # Lane detection (AFTER YOLO)
        frame = lane_detector.detect(frame, mode)

        # Display mode
        display_text = f"AUTO: {mode}" if auto_mode else f"MANUAL: {mode}"

        cv2.putText(frame, display_text,
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1, (255, 255, 0), 2)

        fps = 1 / (time.time() - start)
        cv2.putText(frame, f"FPS: {int(fps)}",
                    (20, 140),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0, 255, 0), 2)

        total_frames += 1
        stframe.image(frame, channels="BGR")

    cap.release()

    if total_frames > 0:
        warning_rate = warnings / total_frames
        reliability = high_conf_warnings / warnings if warnings > 0 else 0
        accuracy = high_conf_warnings / total_frames

        st.write(f"⚠ Warning Rate: {warning_rate:.2f}")
        st.write(f"✅ Reliability: {reliability:.2f}")
        st.write(f"🎯 Accuracy: {accuracy:.2f}")
        
        
        
        
        
import streamlit as st
from ultralytics import YOLO
import cv2
import tempfile
import numpy as np
import time
from lane_ai import AILaneDetector

st.title("🚗 AI-Based Driver Assistance System")

# Mode controls
auto_mode = st.sidebar.checkbox("Enable Auto Mode", value=True)

manual_mode = st.sidebar.selectbox(
    "Manual Mode",
    ["City Mode", "Highway Mode"]
)

mode = manual_mode

model = YOLO("yolov8n.pt")
lane_detector = AILaneDetector()

uploaded_file = st.file_uploader("Upload File", type=["jpg","jpeg","png","mp4","avi"])
conf_threshold = st.sidebar.slider("Confidence Threshold", 0.1, 1.0, 0.5)

if uploaded_file is not None:

    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(uploaded_file.read())

    # ================= IMAGE PROCESSING =================
    if uploaded_file.type.startswith("image"):

        img = cv2.imread(tfile.name)
        results = model(img)

        for r in results:
            output = r.plot()

        st.image(output, caption="Detected Image", channels="BGR")
        st.success("Image Mode: Object Detection Only")

    # ================= VIDEO PROCESSING =================
    else:

        cap = cv2.VideoCapture(tfile.name)
        stframe = st.empty()

        total_frames = 0
        warnings = 0
        high_conf_warnings = 0
        frame_count = 0

        if "prev_mode" not in st.session_state:
            st.session_state.prev_mode = "City Mode"

        st.write(f"### Current Mode: {mode}")

        while cap.isOpened():
            start = time.time()

            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.resize(frame, (640, 360))
            frame_count += 1

            if frame_count % 3 != 0:
                continue

            results = model(frame)
            frame_center = frame.shape[1] // 2

            vehicle_count = 0
            person_count = 0

            # ---------- First pass: count objects ----------
            for r in results:
                frame = r.plot()

                for box in r.boxes:
                    conf = float(box.conf[0])
                    if conf < conf_threshold:
                        continue

                    cls = int(box.cls[0])
                    label = model.names[cls]

                    if label in ["car", "truck", "bus"]:
                        vehicle_count += 1
                    if label == "person":
                        person_count += 1

            # ---------- Auto Mode ----------
            if auto_mode:
                if vehicle_count > 3:
                    mode = "Highway Mode"
                elif person_count > 2:
                    mode = "City Mode"
                else:
                    mode = st.session_state.prev_mode

                st.session_state.prev_mode = mode

            # ---------- Collision Detection ----------
            for r in results:
                for box in r.boxes:
                    conf = float(box.conf[0])
                    if conf < conf_threshold:
                        continue

                    x1, y1, x2, y2 = map(int, box.xyxy[0])

                    w = x2 - x1
                    h = y2 - y1
                    ratio = (w * h) / (frame.shape[0] * frame.shape[1])
                    distance = 1 / (ratio + 1e-6)

                    center_x = (x1 + x2) // 2

                    if mode == "City Mode":
                        collision_threshold = 12
                        center_range = 150
                    else:
                        collision_threshold = 6
                        center_range = 100

                    if distance < collision_threshold and abs(center_x - frame_center) < center_range:
                        warnings += 1

                        if conf > 0.7:
                            high_conf_warnings += 1

                        cv2.putText(frame, "⚠ COLLISION WARNING!",
                                    (50, 80),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    1.2, (0, 0, 255), 3)

            # ---------- Lane Detection (ONLY HIGHWAY) ----------
            if mode == "Highway Mode":
                frame = lane_detector.detect(frame, mode)

            # ---------- Display Mode ----------
            display_text = f"AUTO: {mode}" if auto_mode else f"MANUAL: {mode}"

            cv2.putText(frame, display_text,
                        (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1, (255, 255, 0), 2)

            fps = 1 / (time.time() - start)
            cv2.putText(frame, f"FPS: {int(fps)}",
                        (20, 140),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1, (0, 255, 0), 2)

            total_frames += 1
            stframe.image(frame, channels="BGR")

        cap.release()

        if total_frames > 0:
            warning_rate = warnings / total_frames
            reliability = high_conf_warnings / warnings if warnings > 0 else 0
            accuracy = high_conf_warnings / total_frames

            st.write(f"⚠ Warning Rate: {warning_rate:.2f}")
            st.write(f"✅ Reliability: {reliability:.2f}")
            st.write(f"🎯 Accuracy: {accuracy:.2f}")    
            
import streamlit as st
from ultralytics import YOLO
import cv2
import tempfile
import numpy as np
import time
from lane_ai import AILaneDetector

st.title("🚗 AI-Based Driver Assistance System")

# Sidebar controls
auto_mode = st.sidebar.checkbox("Enable Auto Mode", value=True)
manual_mode = st.sidebar.selectbox("Manual Mode", ["City Mode", "Highway Mode"])
conf_threshold = st.sidebar.slider("Confidence Threshold", 0.1, 1.0, 0.5)

mode = manual_mode

model = YOLO("yolov8n.pt")
lane_detector = AILaneDetector()

uploaded_file = st.file_uploader("Upload File", type=["jpg","jpeg","png","mp4","avi"])

if uploaded_file is not None:

    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(uploaded_file.read())

    # ================= IMAGE MODE =================
    if uploaded_file.type.startswith("image"):

        img = cv2.imread(tfile.name)
        results = model(img)

        for r in results:
            output = r.plot()

        st.image(output, channels="BGR")
        st.success("Image Mode: Object Detection Only")

    # ================= VIDEO MODE =================
    else:

        cap = cv2.VideoCapture(tfile.name)
        stframe = st.empty()

        if "prev_mode" not in st.session_state:
            st.session_state.prev_mode = "City Mode"

        if "mode_counter" not in st.session_state:
            st.session_state.mode_counter = 0

        warnings = 0
        high_conf_warnings = 0
        total_frames = 0
        frame_count = 0

        while cap.isOpened():

            start = time.time()

            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.resize(frame, (640, 360))
            frame_count += 1

            if frame_count % 2 != 0:
                continue

            results = model(frame)
            frame_center = frame.shape[1] // 2

            vehicle_count = 0
            person_count = 0

            # ---------- First pass ----------
            for r in results:
                frame = r.plot()

                for box in r.boxes:
                    conf = float(box.conf[0])
                    if conf < conf_threshold:
                        continue

                    cls = int(box.cls[0])
                    label = model.names[cls]

                    if label in ["car", "truck", "bus"]:
                        vehicle_count += 1
                    if label == "person":
                        person_count += 1

            # ---------- Stable Auto Mode ----------
            if auto_mode:
                if person_count > 3:
                    new_mode = "City Mode"
                elif vehicle_count > 5:
                    new_mode = "Highway Mode"
                else:
                    new_mode = st.session_state.prev_mode

                if new_mode == st.session_state.prev_mode:
                    mode = new_mode
                else:
                    st.session_state.mode_counter += 1
                    if st.session_state.mode_counter > 5:
                        mode = new_mode
                        st.session_state.prev_mode = new_mode
                        st.session_state.mode_counter = 0
              # ---------- STRONG AUTO MODE ----------
	if auto_mode:

    # Priority: highway detection first
    if vehicle_count >= 2:
        new_mode = "Highway Mode"

    elif person_count >= 2:
        new_mode = "City Mode"

    else:
        new_mode = st.session_state.prev_mode

    # Stable switching (avoid flicker)
    if new_mode == st.session_state.prev_mode:
        mode = new_mode
        st.session_state.mode_counter = 0
    else:
        st.session_state.mode_counter += 1

        if st.session_state.mode_counter > 3:
            mode = new_mode
            st.session_state.prev_mode = new_mode
            st.session_state.mode_counter = 0

            # ---------- Collision Detection ----------
            for r in results:
                for box in r.boxes:

                    conf = float(box.conf[0])
                    if conf < conf_threshold:
                        continue

                    x1, y1, x2, y2 = map(int, box.xyxy[0])

                    w = x2 - x1
                    h = y2 - y1
                    ratio = (w * h) / (frame.shape[0] * frame.shape[1])
                    distance = 1 / (ratio + 1e-6)

                    center_x = (x1 + x2) // 2

                    if mode == "City Mode":
                        threshold = 12
                        center_range = 150
                    else:
                        threshold = 6
                        center_range = 100

                    if distance < threshold and abs(center_x - frame_center) < center_range:

                        warnings += 1
                        if conf > 0.7:
                            high_conf_warnings += 1

                        cv2.putText(frame, "⚠ COLLISION WARNING",
                                    (50, 80),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    1, (0, 0, 255), 3)

            # ---------- Lane Detection ONLY HIGHWAY ----------
            if mode == "Highway Mode":
                frame = lane_detector.detect(frame, mode)

            # ---------- UI ----------
            text = f"AUTO: {mode}" if auto_mode else f"MANUAL: {mode}"

            cv2.putText(frame, text,
                        (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1, (255, 255, 0), 2)

            fps = 1 / (time.time() - start)

            cv2.putText(frame, f"FPS: {int(fps)}",
                        (20, 120),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1, (0, 255, 0), 2)

            stframe.image(frame, channels="BGR")
            total_frames += 1

        cap.release()

        # ---------- Metrics ----------
        if total_frames > 0:
            st.write(f"⚠ Warning Rate: {warnings/total_frames:.2f}")         
import streamlit as st
from ultralytics import YOLO
import cv2
import tempfile
import time
from lane_ai import AILaneDetector

st.title("🚗 AI-Based Driver Assistance System")

# Sidebar
auto_mode = st.sidebar.checkbox("Enable Auto Mode", value=True)
manual_mode = st.sidebar.selectbox("Manual Mode", ["City Mode", "Highway Mode"])
conf_threshold = st.sidebar.slider("Confidence Threshold", 0.1, 1.0, 0.5)

mode = manual_mode

model = YOLO("yolov8n.pt")
lane_detector = AILaneDetector()

uploaded_file = st.file_uploader("Upload File", type=["jpg","jpeg","png","mp4","avi"])

if uploaded_file is not None:

    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(uploaded_file.read())

    # ================= IMAGE MODE =================
    if uploaded_file.type.startswith("image"):

        img = cv2.imread(tfile.name)
        results = model(img)

        for r in results:
            output = r.plot()

        st.image(output, channels="BGR")
        st.success("Image Mode: Object Detection Only")

    # ================= VIDEO MODE =================
    else:

        cap = cv2.VideoCapture(tfile.name)
        stframe = st.empty()

        # session state
        if "prev_mode" not in st.session_state:
            st.session_state.prev_mode = "City Mode"

        if "mode_counter" not in st.session_state:
            st.session_state.mode_counter = 0

        warnings = 0
        high_conf_warnings = 0
        total_frames = 0
        frame_count = 0

        while cap.isOpened():

            start = time.time()

            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.resize(frame, (640, 360))
            frame_count += 1

            # skip frames for speed
            if frame_count % 2 != 0:
                continue

            results = model(frame)
            frame_center = frame.shape[1] // 2

            vehicle_count = 0
            person_count = 0

            # ---------- OBJECT DETECTION ----------
            for r in results:
                frame = r.plot()

                for box in r.boxes:
                    conf = float(box.conf[0])
                    if conf < conf_threshold:
                        continue

                    cls = int(box.cls[0])
                    label = model.names[cls]

                    if label in ["car", "truck", "bus"]:
                        vehicle_count += 1
                    if label == "person":
                        person_count += 1

            # ---------- AUTO MODE ----------
            if auto_mode:

                if vehicle_count >= 2:
                    new_mode = "Highway Mode"
                elif person_count >= 2:
                    new_mode = "City Mode"
                else:
                    new_mode = st.session_state.prev_mode

                if new_mode == st.session_state.prev_mode:
                    mode = new_mode
                    st.session_state.mode_counter = 0
                else:
                    st.session_state.mode_counter += 1

                    if st.session_state.mode_counter >= 3:
                        mode = new_mode
                        st.session_state.prev_mode = new_mode
                        st.session_state.mode_counter = 0

            # ---------- COLLISION DETECTION ----------
            for r in results:
                for box in r.boxes:

                    conf = float(box.conf[0])
                    if conf < conf_threshold:
                        continue

                    x1, y1, x2, y2 = map(int, box.xyxy[0])

                    w = x2 - x1
                    h = y2 - y1
                    ratio = (w * h) / (frame.shape[0] * frame.shape[1])
                    distance = 1 / (ratio + 1e-6)

                    center_x = (x1 + x2) // 2

                    if mode == "City Mode":
                        threshold = 12
                        center_range = 150
                    else:
                        threshold = 6
                        center_range = 100

                    if distance < threshold and abs(center_x - frame_center) < center_range:

                        warnings += 1
                        if conf > 0.7:
                            high_conf_warnings += 1

                        cv2.putText(frame, "⚠ COLLISION WARNING",
                                    (50, 80),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    1, (0, 0, 255), 3)

            # ---------- LANE DETECTION ----------
            if mode == "Highway Mode":
                frame = lane_detector.detect(frame, mode)

                cv2.putText(frame, "Lane Detection ON",
                            (20, 80),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7, (0, 255, 255), 2)

            # ---------- UI ----------
            text = f"AUTO: {mode}" if auto_mode else f"MANUAL: {mode}"

            cv2.putText(frame, text,
                        (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1, (255, 255, 0), 2)

            fps = 1 / (time.time() - start)

            cv2.putText(frame, f"FPS: {int(fps)}",
                        (20, 120),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1, (0, 255, 0), 2)

            stframe.image(frame, channels="BGR")
            total_frames += 1

        cap.release()

        # ---------- METRICS ----------
        if total_frames > 0:
            st.write(f"⚠ Warning Rate: {warnings/total_frames:.2f}")
            st.write(f"🎯 Accuracy: {high_conf_warnings/total_frames:.2f}")
            st.write(f"🎯 Accuracy: {high_conf_warnings/total_frames:.2f}")
            
import streamlit as st
from ultralytics import YOLO
import cv2
import tempfile
import time
from lane_ai import AILaneDetector

st.title("🚗 AI-Based Driver Assistance System")

model = YOLO("yolov8n.pt")
lane_detector = AILaneDetector()

uploaded_file = st.file_uploader("Upload File", type=["jpg","jpeg","png","mp4","avi"])

conf_threshold = st.sidebar.slider("Confidence Threshold", 0.1, 1.0, 0.5)

if uploaded_file is not None:

    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(uploaded_file.read())

    # IMAGE MODE
    if uploaded_file.type.startswith("image"):

        img = cv2.imread(tfile.name)
        results = model(img)

        for r in results:
            output = r.plot()

        st.image(output, channels="BGR")

    # VIDEO MODE
    else:
        cap = cv2.VideoCapture(tfile.name)
        stframe = st.empty()

        frame_count = 0

        while cap.isOpened():
            start = time.time()

            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.resize(frame, (640, 360))
            frame_count += 1

            # Skip frames
            if frame_count % 2 != 0:
                continue

            results = model(frame)

            frame_center = frame.shape[1] // 2
            distance = None

            for r in results:
                frame = r.plot()

                for box in r.boxes:
                    conf = float(box.conf[0])
                    if conf < conf_threshold:
                        continue

                    x1, y1, x2, y2 = map(int, box.xyxy[0])

                    w = x2 - x1
                    h = y2 - y1
                    ratio = (w * h) / (frame.shape[0] * frame.shape[1])
                    distance = 1 / (ratio + 1e-6)

                    center_x = (x1 + x2) // 2

                    if distance < 8 and abs(center_x - frame_center) < 120:
                        cv2.putText(frame, "⚠ COLLISION WARNING",
                                    (50, 60),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    1, (0, 0, 255), 3)

                        cv2.putText(frame, f"Dist: {distance:.2f}",
                                    (50, 100),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    0.8, (255,255,0), 2)

            # LANE DETECTION
            frame = lane_detector.detect(frame)

            # FPS
            fps = 1 / (time.time() - start)
            cv2.putText(frame, f"FPS: {int(fps)}",
                        (20, 140),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1, (0,255,0), 2)

            stframe.image(frame, channels="BGR")

        cap.release()     
            
            
            
import streamlit as st
from ultralytics import YOLO
import cv2
import tempfile
import time
import pandas as pd
from lane_ai import AILaneDetector

st.title("🚗 AI-Based Driver Assistance System")

# Sidebar mode selection
view_mode = st.sidebar.radio("Select View", ["Video Output", "Dashboard"])

model = YOLO("yolov8n.pt")
lane_detector = AILaneDetector()

uploaded_file = st.file_uploader("Upload File", type=["jpg","jpeg","png","mp4","avi"])
conf_threshold = st.sidebar.slider("Confidence Threshold", 0.1, 1.0, 0.5)

# Data storage
fps_list = []
warning_list = []
frame_index = []

if uploaded_file is not None:

    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(uploaded_file.read())

    # ---------------- IMAGE MODE ----------------
    if uploaded_file.type.startswith("image"):

        img = cv2.imread(tfile.name)
        results = model(img)

        for r in results:
            output = r.plot()

        st.image(output, channels="BGR", caption="Detected Image")

        st.info("📌 Dashboard is only available for video processing.")

    # ---------------- VIDEO MODE ----------------
    else:

        cap = cv2.VideoCapture(tfile.name)
        stframe = st.empty()

        warnings = 0
        frame_count = 0
        last_distance = None

        while cap.isOpened():
            start = time.time()

            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.resize(frame, (640, 360))
            frame_count += 1

            if frame_count % 2 != 0:
                continue

            results = model(frame)
            frame_center = frame.shape[1] // 2

            for r in results:
                frame = r.plot()

                for box in r.boxes:
                    conf = float(box.conf[0])
                    if conf < conf_threshold:
                        continue

                    x1, y1, x2, y2 = map(int, box.xyxy[0])

                    w = x2 - x1
                    h = y2 - y1
                    ratio = (w * h) / (frame.shape[0] * frame.shape[1])
                    distance = 1 / (ratio + 1e-6)
                    last_distance = distance

                    center_x = (x1 + x2) // 2

                    if distance < 8 and abs(center_x - frame_center) < 120:
                        warnings += 1

                        cv2.putText(frame, "⚠ COLLISION WARNING",
                                    (50, 60),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    1, (0, 0, 255), 3)

                        cv2.putText(frame, f"Dist: {distance:.2f}",
                                    (50, 100),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    0.8, (255,255,0), 2)

            # Lane detection (Highway only)
            frame = lane_detector.detect(frame)

            fps = 1 / (time.time() - start)

            fps_list.append(int(fps))
            warning_list.append(warnings)
            frame_index.append(frame_count)

            cv2.putText(frame, f"FPS: {int(fps)}",
                        (20, 140),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1, (0,255,0), 2)

            # Show video only in video mode
            if view_mode == "Video Output":
                stframe.image(frame, channels="BGR")

        cap.release()

        # ---------------- DASHBOARD ----------------
        if view_mode == "Dashboard":

            st.header("📊 Driving Analysis Dashboard")

            # Risk Level
            if warnings > 10:
                st.error("🔴 HIGH RISK DRIVING CONDITION")
            elif warnings > 5:
                st.warning("🟡 MODERATE RISK")
            else:
                st.success("🟢 SAFE DRIVING")

            # Distance Analysis
            if last_distance is not None:
                st.subheader("📏 Distance Analysis")

                if last_distance < 5:
                    st.error("Object very close! Immediate action needed.")
                elif last_distance < 10:
                    st.warning("Maintain safe distance.")
                else:
                    st.success("Safe distance maintained.")

                st.write(f"Estimated Distance: {last_distance:.2f}")

            # FPS Performance
            st.subheader("⚡ System Performance")

            avg_fps = sum(fps_list) / len(fps_list)
            st.write(f"Average FPS: {int(avg_fps)}")

            if avg_fps < 10:
                st.warning("Low FPS - Not fully real-time")
            else:
                st.success("Good real-time performance")

            # Graph
            df = pd.DataFrame({
                "Frame": frame_index,
                "FPS": fps_list,
                "Warnings": warning_list
            })

            st.subheader("📈 Performance Graph")
            st.line_chart(df.set_index("Frame"))
	    st.line_chart({
   		 "FPS": fps_list,
   		 "Warnings": warning_list
		})
            # Safety Tips
            st.subheader("🚦 Driving Safety Suggestions")
            st.markdown("""
            - Maintain safe distance from vehicles  
            - Reduce speed in heavy traffic  
            - Stay within lane boundaries  
            - Be cautious in low-light conditions  
            - Respond quickly to warnings  
            """)'''
            
            
            
import streamlit as st
from ultralytics import YOLO
import cv2
import tempfile
import time
from lane_ai import AILaneDetector

st.title("🚗 AI-Based Driver Assistance System")

model = YOLO("yolov8n.pt")
lane_detector = AILaneDetector()

uploaded_file = st.file_uploader("Upload File", type=["jpg","jpeg","png","mp4","avi"])
conf_threshold = st.sidebar.slider("Confidence Threshold", 0.1, 1.0, 0.5)

# Data storage
fps_list = []
warning_list = []
frame_index = []

if uploaded_file is not None:

    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(uploaded_file.read())

    # ---------------- IMAGE MODE ----------------
    if uploaded_file.type.startswith("image"):

        img = cv2.imread(tfile.name)
        results = model(img)

        for r in results:
            output = r.plot()

        st.image(output, channels="BGR", caption="Detected Image")
        st.info("📌 Dashboard available only for video input")

    # ---------------- VIDEO MODE ----------------
    else:

        cap = cv2.VideoCapture(tfile.name)
        stframe = st.empty()

        warnings = 0
        frame_count = 0
        last_distance = None

        while cap.isOpened():
            start = time.time()

            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.resize(frame, (640, 360))
            frame_count += 1

            # Skip frames for speed
            if frame_count % 2 != 0:
                continue

            results = model(frame)
            frame_center = frame.shape[1] // 2

            for r in results:
                frame = r.plot()

                for box in r.boxes:
                    conf = float(box.conf[0])
                    if conf < conf_threshold:
                        continue

                    x1, y1, x2, y2 = map(int, box.xyxy[0])

                    w = x2 - x1
                    h = y2 - y1
                    ratio = (w * h) / (frame.shape[0] * frame.shape[1])
                    distance = 1 / (ratio + 1e-6)
                    last_distance = distance

                    center_x = (x1 + x2) // 2

                    if distance < 8 and abs(center_x - frame_center) < 120:
                        warnings += 1

                        cv2.putText(frame, "⚠ COLLISION WARNING",
                                    (50, 60),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    1, (0, 0, 255), 3)

                        cv2.putText(frame, f"Dist: {distance:.2f}",
                                    (50, 100),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    0.8, (255,255,0), 2)

            # Lane detection
            frame = lane_detector.detect(frame)

            # FPS
            fps = 1 / (time.time() - start)

            fps_list.append(int(fps))
            warning_list.append(warnings)
            frame_index.append(frame_count)

            cv2.putText(frame, f"FPS: {int(fps)}",
                        (20, 140),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1, (0,255,0), 2)

            stframe.image(frame, channels="BGR")

        cap.release()

        # ---------------- DASHBOARD ----------------
        st.header("📊 Driving Analysis Dashboard")

        # Risk Level
        if warnings > 10:
            st.error("🔴 HIGH RISK DRIVING CONDITION")
        elif warnings > 5:
            st.warning("🟡 MODERATE RISK")
        else:
            st.success("🟢 SAFE DRIVING")

        # Distance
        if last_distance is not None:
            st.subheader("📏 Distance Analysis")

            if last_distance < 5:
                st.error("Object very close! Immediate action needed.")
            elif last_distance < 10:
                st.warning("Maintain safe distance.")
            else:
                st.success("Safe distance maintained.")

            st.write(f"Estimated Distance: {last_distance:.2f}")

        # FPS
        st.subheader("⚡ Performance")

        if len(fps_list) > 0:
            avg_fps = sum(fps_list) / len(fps_list)
            st.write(f"Average FPS: {int(avg_fps)}")

            if avg_fps < 10:
                st.warning("Low FPS - Not real-time")
            else:
                st.success("Good real-time performance")

        # Graph (NO pandas)
        st.subheader("📈 Performance Graph")

        st.line_chart({
            "FPS": fps_list,
            "Warnings": warning_list
        })

        # Safety tips
        st.subheader("🚦 Driving Safety Suggestions")

        st.markdown("""
        - Maintain safe distance from vehicles  
        - Reduce speed in heavy traffic  
        - Stay within lane boundaries  
        - Be cautious in low-light conditions  
        - Respond quickly to warnings  
        """)        


