```python
import cv2
import dlib
import numpy as np
import os
from datetime import datetime

# Load face detector and shape predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("data/data_dlib/shape_predictor_68_face_landmarks.dat")

# Attendance file
attendance_file = "attendance.csv"

# Function to adjust brightness/contrast automatically
def adjust_brightness(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    mean_val = np.mean(gray)

    if mean_val < 80:  # too dark → brighten
        alpha = 1.5
        beta = 30
    elif mean_val > 180:  # too bright → darken
        alpha = 0.7
        beta = -30
    else:  # normal lighting
        alpha = 1.0
        beta = 0

    adjusted = cv2.convertScaleAbs(frame, alpha=alpha, beta=beta)
    return adjusted

# Function to mark attendance
def mark_attendance(name):
    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
    with open(attendance_file, "a") as f:
        f.write(f"{name},{dt_string}\n")

# Example recognition function (placeholder)
def recognize_face(frame):
    faces = detector(frame)
    for face in faces:
        landmarks = predictor(frame, face)
        # For now, we’ll just return a dummy name
        return "Student_1"
    return None

def main():
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Adjust brightness for poor lighting
        frame = adjust_brightness(frame)

        # Convert to grayscale for detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Face recognition
        name = recognize_face(gray)
        if name:
            mark_attendance(name)
            cv2.putText(frame, f"Recognized: {name}", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow("Attendance System", frame)

        # Quit on 'q'
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # Create attendance file if not exists
    if not os.path.exists("attendance.csv"):
        with open("attendance.csv", "w") as f:
            f.write("Name,DateTime\n")

    main()
```
