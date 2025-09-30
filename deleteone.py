import sqlite3
import pickle
import os

student_id = "106"  # Change to the ID you want to delete

# 1. Delete from database
conn = sqlite3.connect("smart_attendance.db")
cur = conn.cursor()
cur.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
cur.execute("DELETE FROM attendance WHERE student_id = ?", (student_id,))
conn.commit()
conn.close()

# 2. Remove from face_data.pkl for this ID
face_data_path = "faces/smart_face_data.pkl"
if os.path.exists(face_data_path):
    with open(face_data_path, "rb") as f:
        data = pickle.load(f)
    if "face_data" in data:
        data["face_data"].pop(student_id, None)
    if "students" in data:
        data["students"].pop(student_id, None)
    with open(face_data_path, "wb") as f:
        pickle.dump(data, f)
    print(f"Deleted {student_id} info in DB and face_data.pkl")
else:
    print("face_data.pkl not found, only DB records deleted.")

print(f"Student {student_id} deleted from smart_attendance.db and related face data (if any).")
