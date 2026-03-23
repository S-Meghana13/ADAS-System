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

        cap.release()'''
        
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

    # Focus only on road area
    mask = np.zeros_like(edges)

    polygon = np.array([[
        (0, height),
        (width, height),
        (width, int(height*0.6)),
        (0, int(height*0.6))
    ]], np.int32)

    cv2.fillPoly(mask, polygon, 255)
    cropped_edges = cv2.bitwise_and(edges, mask)

    lines = cv2.HoughLinesP(cropped_edges, 1, np.pi/180, 100,
                            minLineLength=100, maxLineGap=50)

    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]

            # remove vertical noise
            if abs(x1 - x2) < 50:
                continue

            cv2.line(frame, (x1,y1), (x2,y2), (255,0,0), 3)

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

            # -------- LANE DETECTION --------
            #frame = detect_lanes(frame)

            # Show frame
            stframe.image(frame, channels="BGR")

        cap.release()
