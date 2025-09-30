### SMART ATTENDANCE SYSTEM
  Uses HOG & CNN (via `face_recognition`), multiple OpenCV Haar/LBP cascades (frontal, alt, profile), and fallback edge/gradient methods.  
- **Extreme Preprocessing Pipelines**  
  Gamma correction, CLAHE, color space conversion, morphological operations, multi-scale search, etc.  
- **RGB Conversion Guarantee**  
  Ensures a consistent input format for all detection pipelines.  
- **Detailed Diagnostic Reporting**  
  For each frame, the console logs exactly which methods were attempted and which succeeded or failed.  
- **Manual Fallback Option**  
  If automated detection fails, you can manually select the face bounding box.  
- **Registration & Attendance Modules**  
  Easily enroll new faces and perform live recognition for attendance.

---

## 📸 Screenshot / Demo (optional)

_Insert here one or more screenshots of the UI or outputs, e.g.:_  

![Detection Demo](docs/demo_screenshot.png)  

(You can put your images in a `docs/` folder or root, and reference them here.)

---

## 🛠️ Installation

### 1. Clone & Enter Repo
```bash
git clone https://github.com/Harini1824/Smart-Attendance-System.git
cd Smart-Attendance-System
```

### 2. Setup Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate    # On macOS / Linux
.env\Scriptsctivate     # On Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

**Core dependencies:**
- opencv-python  
- dlib  
- face_recognition  
- numpy  
- pandas  

(Also uses `tkinter` for GUI elements—typically included with Python.)

---

## ▶️ Usage

Run the main app:
```bash
python smart_attendance_system.py
```

The main GUI offers modes:

- **🎯 Camera Test**  
  Test detection on live feed and see diagnostics.  
- **👤 Register**  
  Capture and enroll a new face.  
- **📸 Attendance / Recognition**  
  Recognize enrolled faces in real time and mark attendance.

While running, the console displays which detection method succeeded (or failed) for each frame.

---

## ⚠️ Troubleshooting & Tips

- If detection fails:
  - Improve lighting (avoid backlighting; use front/side lights).
  - Remove glasses, hats, or scarves that obstruct face.
  - Adjust your distance from the camera.
  - Use better-quality webcams (an external USB camera often helps).
- CNN-based detection is slower on CPU; using GPU acceleration (if available) helps.
- Ensure correct library versions to avoid incompatibilities.

---

## 🧪 Developer Notes & Roadmap

- Modularize detection pipelines (e.g. separate classifier modules).  
- Add GPU support for dlib / CNN backends.  
- Expand the fallback methods (e.g. integrate new detection models).  
- Improve GUI (add status overlays, error prompts).  
- Introduce logging to file (in addition to console) for post-run analysis.


---

## 🔗 References & Further Reading

- [face_recognition documentation](https://github.com/ageitgey/face_recognition)  
- [OpenCV Haar & LBP cascade documentation](https://docs.opencv.org/master/d7/d8b/tutorial_py_face_detection.html)  
- [Real Python Face Recognition Guide](https://realpython.com/face-recognition-with-python/)  



