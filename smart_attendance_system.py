# Smart Face Recognition Attendance System
# Fixed version with duplicate prevention and clean interface

import os
import sqlite3
import cv2
import numpy as np
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import pandas as pd
import pickle
import time


class SmartAttendanceSystem:
    def __init__(self):
        print("🚀 Initializing Smart Attendance System...")
        
        # Initialize all attributes first
        self.root = tk.Tk()
        self.root.title("Smart Face Recognition Attendance System")
        self.root.geometry("1000x700")
        self.root.configure(bg="#2c3e50")
        
        self.is_capturing = False
        self.face_data = {}
        self.students = {}
        self.last_recognition = {}  # Track last recognition time for each student
        self.recognition_cooldown = 10  # 10 seconds cooldown between recognitions
        
        # Initialize face cascade
        try:
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
            print("✅ Face detector loaded successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Could not load face detector: {e}")
            return
        
        # Initialize database
        self.init_database()
        
        # Create directories
        self.create_directories()
        
        # Load existing data
        self.load_face_data()
        
        # Setup GUI
        self.setup_gui()
        
        print("✅ Smart system initialized successfully!")
    
    def init_database(self):
        """Initialize SQLite database"""
        try:
            self.conn = sqlite3.connect('smart_attendance.db', check_same_thread=False)
            self.cursor = self.conn.cursor()
            
            # Students table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS students (
                    student_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    registration_date TEXT
                )
            ''')
            
            # Attendance table with UNIQUE constraint to prevent duplicates
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id TEXT,
                    name TEXT,
                    date TEXT,
                    time TEXT,
                    status TEXT DEFAULT 'Present',
                    UNIQUE(student_id, date)
                )
            ''')
            
            self.conn.commit()
            print("✅ Database initialized with duplicate prevention")
        except Exception as e:
            print(f"❌ Database error: {e}")
    
    def create_directories(self):
        """Create necessary directories"""
        for directory in ['faces', 'attendance_records']:
            if not os.path.exists(directory):
                os.makedirs(directory)
    
    def setup_gui(self):
        """Setup clean GUI interface"""
        # Title
        title_label = tk.Label(
            self.root,
            text="🎯 Smart Attendance System",
            font=("Arial", 20, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        title_label.pack(pady=15)
        
        # Main frame
        main_frame = tk.Frame(self.root, bg="#2c3e50")
        main_frame.pack(expand=True, fill="both", padx=15, pady=10)
        
        # Left panel (controls)
        left_panel = tk.Frame(main_frame, bg="#34495e", relief="raised", bd=2)
        left_panel.pack(side="left", fill="y", padx=(0, 10))
        
        # Right panel (smart display)
        right_panel = tk.Frame(main_frame, bg="white", relief="raised", bd=2)
        right_panel.pack(side="right", expand=True, fill="both")
        
        # Control buttons
        tk.Label(left_panel, text="📋 Controls", font=("Arial", 14, "bold"),
                bg="#34495e", fg="white").pack(pady=15)
        
        buttons = [
            ("👤 Register Student", self.register_student, "#27ae60"),
            ("📸 Take Attendance", self.take_attendance, "#3498db"),
            ("📊 Today's Records", self.view_today, "#e74c3c"),
            ("📈 All Records", self.view_all, "#f39c12"),
            ("👥 Students", self.view_students, "#9b59b6"),
            ("❌ Exit", self.exit_app, "#e74c3c")
        ]
        
        self.buttons = {}
        for text, command, color in buttons:
            btn = tk.Button(
                left_panel,
                text=text,
                command=command,
                width=18,
                height=2,
                font=("Arial", 11, "bold"),
                bg=color,
                fg="white",
                relief="raised",
                bd=2,
                cursor="hand2"
            )
            btn.pack(pady=8, padx=15)
            self.buttons[text] = btn
        
        # Status panel
        status_frame = tk.Frame(left_panel, bg="#34495e")
        status_frame.pack(pady=20, padx=15, fill="x")
        
        tk.Label(status_frame, text="📊 Today's Summary", font=("Arial", 12, "bold"),
                bg="#34495e", fg="white").pack()
        
        self.status_label = tk.Label(
            status_frame,
            text="Loading...",
            font=("Arial", 10),
            bg="#34495e",
            fg="#2ecc71",
            justify="center"
        )
        self.status_label.pack(pady=8)
        
        # Smart display area
        self.setup_smart_display(right_panel)
        
        # Update status
        self.update_status()
    
    def setup_smart_display(self, parent):
        """Setup smart display interface"""
        # Header
        header_frame = tk.Frame(parent, bg="white")
        header_frame.pack(fill="x", padx=20, pady=20)
        
        tk.Label(header_frame, text="🎯 Smart Attendance System", 
                font=("Arial", 18, "bold"), bg="white", fg="#2c3e50").pack()
        
        # Stats cards frame
        stats_frame = tk.Frame(parent, bg="white")
        stats_frame.pack(fill="x", padx=20, pady=10)
        
        # Create stats cards
        self.create_stats_card(stats_frame, "👥 Registered", "students_count", "#3498db")
        self.create_stats_card(stats_frame, "✅ Present Today", "present_count", "#27ae60") 
        self.create_stats_card(stats_frame, "📈 Attendance Rate", "attendance_rate", "#e74c3c")
        
        # Live status frame
        live_frame = tk.Frame(parent, bg="white")
        live_frame.pack(fill="x", padx=20, pady=20)
        
        tk.Label(live_frame, text="🔴 Live Status", 
                font=("Arial", 14, "bold"), bg="white", fg="#e74c3c").pack()
        
        self.live_status = tk.Label(
            live_frame,
            text="System Ready - Click 'Take Attendance' to start",
            font=("Arial", 12),
            bg="white",
            fg="#7f8c8d",
            pady=10
        )
        self.live_status.pack()
        
        # Recent activity frame
        activity_frame = tk.Frame(parent, bg="white")
        activity_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        tk.Label(activity_frame, text="📋 Recent Activity", 
                font=("Arial", 14, "bold"), bg="white", fg="#2c3e50").pack(anchor="w")
        
        # Activity list
        self.activity_listbox = tk.Listbox(
            activity_frame,
            font=("Arial", 10),
            height=8,
            bg="#ecf0f1",
            fg="#2c3e50",
            selectbackground="#3498db",
            relief="flat",
            bd=0
        )
        self.activity_listbox.pack(fill="both", expand=True, pady=10)
        
        # Load recent activity
        self.load_recent_activity()
    
    def create_stats_card(self, parent, title, stat_type, color):
        """Create a stats card"""
        card_frame = tk.Frame(parent, bg=color, relief="raised", bd=2)
        card_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        tk.Label(card_frame, text=title, font=("Arial", 10, "bold"), 
                bg=color, fg="white").pack(pady=(10, 5))
        
        # Create label for the stat value
        stat_label = tk.Label(card_frame, text="0", font=("Arial", 16, "bold"), 
                             bg=color, fg="white")
        stat_label.pack(pady=(0, 10))
        
        # Store reference for updates
        setattr(self, f"{stat_type}_label", stat_label)
    
    def register_student(self):
        """Register a new student"""
        name = tk.simpledialog.askstring("Registration", "Enter student's full name:")
        if not name or len(name.strip()) < 2:
            return
        
        student_id = tk.simpledialog.askstring("Registration", "Enter student ID:")
        if not student_id or len(student_id.strip()) < 1:
            return
        
        name = name.strip()
        student_id = student_id.strip()
        
        if student_id in self.students:
            messagebox.showerror("Error", "Student ID already exists!")
            return
        
        self.capture_student_face(name, student_id)
    
    def capture_student_face(self, name, student_id):
        """Capture student's face with improved interface"""
        try:
            if messagebox.askquestion("Face Capture", 
                                    f"Ready to capture face for {name}?\n\n"
                                    "📷 Instructions:\n"
                                    "• Look directly at camera\n"
                                    "• Press SPACE to capture\n"
                                    "• Capture multiple angles\n\n"
                                    "Ready?") != 'yes':
                return
            
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                messagebox.showerror("Error", "Cannot access camera!")
                return
            
            face_templates = []
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame = cv2.flip(frame, 1)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
                
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    cv2.putText(frame, "Press SPACE to capture", 
                               (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    captured_face = gray[y:y+h, x:x+w]
                
                # Display info
                cv2.putText(frame, f"{name} ({student_id})", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                cv2.putText(frame, f"Templates: {len(face_templates)}/6", (10, 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(frame, "SPACE=Capture, Q=Finish", (10, 90),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                
                cv2.imshow('Face Registration', frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord(' ') and len(faces) > 0:
                    # Capture templates at different sizes
                    for size in [50, 75, 100]:
                        try:
                            resized = cv2.resize(captured_face, (size, size))
                            face_templates.append(resized)
                        except:
                            continue
                    
                    if len(face_templates) >= 6:
                        break
                
                elif key == ord('q'):
                    break
            
            cap.release()
            cv2.destroyAllWindows()
            
            if face_templates:
                # Save student
                self.face_data[student_id] = face_templates
                self.students[student_id] = {'name': name, 'id': student_id}
                
                try:
                    self.cursor.execute('''
                        INSERT INTO students (student_id, name, registration_date)
                        VALUES (?, ?, ?)
                    ''', (student_id, name, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                    self.conn.commit()
                    
                    self.save_face_data()
                    messagebox.showinfo("Success", f"✅ {name} registered successfully!")
                    self.update_status()
                    self.load_recent_activity()
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Database error: {e}")
            else:
                messagebox.showerror("Error", "No face captured!")
        
        except Exception as e:
            messagebox.showerror("Error", f"Capture failed: {e}")
            cv2.destroyAllWindows()
    
    def take_attendance(self):
        """Take attendance with smart duplicate prevention"""
        if not self.face_data:
            messagebox.showerror("Error", "No students registered!")
            return
        
        if self.is_capturing:
            self.stop_attendance()
            return
        
        self.is_capturing = True
        self.buttons["📸 Take Attendance"]["text"] = "🛑 Stop Attendance"
        self.live_status.config(text="🔴 LIVE: Taking attendance...", fg="#e74c3c")
        
        # Reset recognition tracking
        self.last_recognition = {}
        
        self.attendance_process()
    
    def attendance_process(self):
        """Smart attendance process with duplicate prevention"""
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                self.stop_attendance()
                return
            
            today = datetime.now().strftime('%Y-%m-%d')
            already_marked = self.get_today_marked()
            current_session_marked = set()
            
            while self.is_capturing:
                ret, frame = cap.read()
                if not ret:
                    continue
                
                frame = cv2.flip(frame, 1)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray, 1.3, 5, minSize=(50, 50))
                
                current_time = time.time()
                
                for (x, y, w, h) in faces:
                    face_roi = gray[y:y+h, x:x+w]
                    best_match = self.match_face(face_roi)
                    
                    name = "Unknown"
                    student_id = "Unknown"
                    color = (0, 0, 255)
                    status = ""
                    
                    if best_match:
                        student_id = best_match
                        name = self.students[student_id]['name']
                        
                        # Check if already marked today
                        if student_id in already_marked:
                            color = (255, 165, 0)  # Orange
                            status = "Already marked today"
                        
                        # Check cooldown period for this session
                        elif student_id in self.last_recognition:
                            time_since_last = current_time - self.last_recognition[student_id]
                            if time_since_last < self.recognition_cooldown:
                                color = (255, 255, 0)  # Yellow
                                status = f"Wait {int(self.recognition_cooldown - time_since_last)}s"
                            else:
                                # Ready to mark
                                if self.mark_attendance_smart(name, student_id):
                                    already_marked.add(student_id)
                                    current_session_marked.add(student_id)
                                    self.last_recognition[student_id] = current_time
                                    color = (0, 255, 0)  # Green
                                    status = "✓ MARKED"
                                    self.live_status.config(text=f"🎉 Marked: {name}", fg="#27ae60")
                                    self.update_status()
                                    self.load_recent_activity()
                        else:
                            # First recognition in this session
                            if self.mark_attendance_smart(name, student_id):
                                already_marked.add(student_id)
                                current_session_marked.add(student_id)
                                self.last_recognition[student_id] = current_time
                                color = (0, 255, 0)  # Green
                                status = "✓ MARKED"
                                self.live_status.config(text=f"🎉 Marked: {name}", fg="#27ae60")
                                self.update_status()
                                self.load_recent_activity()
                    
                    # Draw face detection
                    cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                    
                    # Create label
                    label = f"{name}"
                    if status:
                        label += f" - {status}"
                    
                    cv2.putText(frame, label, (x, y-10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                
                # Display session info
                cv2.putText(frame, f"Session: {len(current_session_marked)} marked", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(frame, f"Today Total: {len(already_marked)}", (10, 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(frame, "Press 'q' to stop", (10, 90),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                
                cv2.imshow('Smart Attendance', frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                
                # Update GUI
                self.root.update()
            
            cap.release()
            cv2.destroyAllWindows()
            
            # Show completion message
            messagebox.showinfo("Session Complete", 
                              f"Attendance session completed!\n\n"
                              f"📅 Date: {today}\n"
                              f"✅ New marks this session: {len(current_session_marked)}\n"
                              f"📊 Total present today: {len(already_marked)}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Attendance failed: {e}")
        finally:
            self.stop_attendance()
    
    def mark_attendance_smart(self, name, student_id):
        """Smart attendance marking with duplicate prevention"""
        try:
            now = datetime.now()
            date = now.strftime('%Y-%m-%d')
            time_str = now.strftime('%H:%M:%S')
            
            # Use INSERT OR IGNORE to prevent duplicates
            self.cursor.execute('''
                INSERT OR IGNORE INTO attendance (student_id, name, date, time, status)
                VALUES (?, ?, ?, ?, 'Present')
            ''', (student_id, name, date, time_str))
            
            # Check if row was actually inserted
            if self.cursor.rowcount > 0:
                self.conn.commit()
                print(f"✅ Marked: {name} ({student_id}) at {time_str}")
                return True
            else:
                print(f"⚠️ {name} already marked today")
                return False
        
        except Exception as e:
            print(f"❌ Mark error: {e}")
            return False
    
    def get_today_marked(self):
        """Get set of students marked today"""
        today = datetime.now().strftime('%Y-%m-%d')
        self.cursor.execute('SELECT student_id FROM attendance WHERE date = ?', (today,))
        return set(row[0] for row in self.cursor.fetchall())
    
    def match_face(self, face_roi):
        """Face matching with improved threshold"""
        try:
            best_match = None
            best_score = 0
            threshold = 0.65  # Slightly higher threshold for better accuracy
            
            for student_id, templates in self.face_data.items():
                for template in templates:
                    try:
                        resized_face = cv2.resize(face_roi, (template.shape[1], template.shape[0]))
                        result = cv2.matchTemplate(resized_face, template, cv2.TM_CCOEFF_NORMED)
                        _, max_val, _, _ = cv2.minMaxLoc(result)
                        
                        if max_val > best_score and max_val > threshold:
                            best_score = max_val
                            best_match = student_id
                    except:
                        continue
            
            return best_match
        except:
            return None
    
    def stop_attendance(self):
        """Stop attendance capture"""
        self.is_capturing = False
        self.buttons["📸 Take Attendance"]["text"] = "📸 Take Attendance"
        self.live_status.config(text="System Ready - Click 'Take Attendance' to start", fg="#7f8c8d")
        cv2.destroyAllWindows()
    
    def update_status(self):
        """Update all status displays"""
        try:
            # Get counts
            total_students = len(self.students)
            today = datetime.now().strftime('%Y-%m-%d')
            
            self.cursor.execute('SELECT COUNT(*) FROM attendance WHERE date = ?', (today,))
            present_today = self.cursor.fetchone()[0]
            
            # Calculate rate
            rate = (present_today / max(total_students, 1)) * 100
            
            # Update stats cards
            self.students_count_label.config(text=str(total_students))
            self.present_count_label.config(text=str(present_today))
            self.attendance_rate_label.config(text=f"{rate:.1f}%")
            
            # Update left panel status
            self.status_label.config(
                text=f"Students: {total_students}\nPresent: {present_today}\nRate: {rate:.1f}%"
            )
        
        except Exception as e:
            print(f"Status update error: {e}")
    
    def load_recent_activity(self):
        """Load recent activity"""
        try:
            self.activity_listbox.delete(0, tk.END)
            
            self.cursor.execute('''
                SELECT name, date, time FROM attendance 
                ORDER BY date DESC, time DESC LIMIT 10
            ''')
            
            records = self.cursor.fetchall()
            
            if not records:
                self.activity_listbox.insert(0, "No activity yet")
            else:
                for name, date, time in records:
                    activity = f"✅ {name} - {date} {time}"
                    self.activity_listbox.insert(tk.END, activity)
        
        except Exception as e:
            self.activity_listbox.insert(0, "Error loading activity")
    
    def view_today(self):
        """View today's attendance"""
        self.show_records_window("Today's Attendance", True)
    
    def view_all(self):
        """View all records"""
        self.show_records_window("All Attendance Records", False)
    
    def show_records_window(self, title, today_only):
        """Show records window"""
        try:
            window = tk.Toplevel(self.root)
            window.title(title)
            window.geometry("800x500")
            
            tk.Label(window, text=title, font=("Arial", 14, "bold")).pack(pady=10)
            
            columns = ("Student ID", "Name", "Date", "Time", "Status")
            tree = ttk.Treeview(window, columns=columns, show="headings")
            
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=120, anchor="center")
            
            scrollbar = ttk.Scrollbar(window, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            
            tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
            scrollbar.pack(side="right", fill="y", pady=10)
            
            if today_only:
                today = datetime.now().strftime('%Y-%m-%d')
                self.cursor.execute('''
                    SELECT student_id, name, date, time, status 
                    FROM attendance WHERE date = ? ORDER BY time
                ''', (today,))
            else:
                self.cursor.execute('''
                    SELECT student_id, name, date, time, status 
                    FROM attendance ORDER BY date DESC, time DESC LIMIT 100
                ''')
            
            records = self.cursor.fetchall()
            for record in records:
                tree.insert("", "end", values=record)
            
            tk.Label(window, text=f"Total Records: {len(records)}", 
                    font=("Arial", 10, "bold")).pack(pady=5)
        
        except Exception as e:
            messagebox.showerror("Error", f"Could not display records: {e}")
    
    def view_students(self):
        """View students"""
        try:
            window = tk.Toplevel(self.root)
            window.title("Registered Students")
            window.geometry("700x400")
            
            tk.Label(window, text="Registered Students", 
                    font=("Arial", 14, "bold")).pack(pady=10)
            
            columns = ("Student ID", "Name", "Registration Date", "Face Templates")
            tree = ttk.Treeview(window, columns=columns, show="headings")
            
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=150, anchor="center")
            
            scrollbar = ttk.Scrollbar(window, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            
            tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
            scrollbar.pack(side="right", fill="y", pady=10)
            
            self.cursor.execute('SELECT * FROM students ORDER BY registration_date DESC')
            students = self.cursor.fetchall()
            
            for student in students:
                student_id, name, reg_date = student
                template_count = len(self.face_data.get(student_id, []))
                tree.insert("", "end", values=(student_id, name, reg_date, template_count))
            
            tk.Label(window, text=f"Total Students: {len(students)}", 
                    font=("Arial", 10, "bold")).pack(pady=5)
        
        except Exception as e:
            messagebox.showerror("Error", f"Could not display students: {e}")
    
    def save_face_data(self):
        """Save face data"""
        try:
            with open('faces/smart_face_data.pkl', 'wb') as f:
                pickle.dump({
                    'face_data': self.face_data,
                    'students': self.students
                }, f)
        except Exception as e:
            print(f"Save error: {e}")
    
    def load_face_data(self):
        """Load face data"""
        try:
            if os.path.exists('faces/smart_face_data.pkl'):
                with open('faces/smart_face_data.pkl', 'rb') as f:
                    data = pickle.load(f)
                    self.face_data = data.get('face_data', {})
                    self.students = data.get('students', {})
            
            # Try to load from old files too
            elif os.path.exists('faces/face_data.pkl'):
                with open('faces/face_data.pkl', 'rb') as f:
                    data = pickle.load(f)
                    self.face_data = data.get('face_data', {})
                    self.students = data.get('students', {})
                
                # Save in new format
                self.save_face_data()
            
            print(f"✅ Loaded {len(self.students)} students")
        except Exception as e:
            print(f"Load error: {e}")
    
    def exit_app(self):
        """Exit application"""
        if messagebox.askquestion("Exit", "Are you sure?") == 'yes':
            try:
                if self.is_capturing:
                    self.stop_attendance()
                self.save_face_data()
                self.conn.close()
                cv2.destroyAllWindows()
                self.root.destroy()
            except:
                self.root.destroy()
    
    def run(self):
        """Run the application"""
        self.root.protocol("WM_DELETE_WINDOW", self.exit_app)
        self.root.mainloop()


# Import required modules
import tkinter.simpledialog

if __name__ == "__main__":
    print("🎯 Smart Face Recognition Attendance System")
    print("=" * 50)
    print("✅ Duplicate prevention implemented")
    print("✅ Clean smart interface")
    print("✅ Real-time stats and activity")
    print("✅ 10-second recognition cooldown")
    print("=" * 50)
    
    try:
        app = SmartAttendanceSystem()
        app.run()
    except Exception as e:
        print(f"❌ Error: {e}")
        input("Press Enter to exit...") 
