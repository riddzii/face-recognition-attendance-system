import cv2
import numpy as np
import face_recognition
import os
import tkinter as tk
import csv
from tkinter import ttk
from tkinter import filedialog
from datetime import datetime
from PIL import Image, ImageTk
from ttkthemes import ThemedStyle 

# Initialize tkinter GUI
root = tk.Tk()
root.title("Face Recognition Attendance System")
root.geometry("1360x700")

# Load images and classnames
path = 'photos'
images = []
classnames = []
mylist = os.listdir(path)
for i in mylist:
    current_image = face_recognition.load_image_file(f'{path}/{i}')
    images.append(current_image)
    classnames.append(os.path.splitext(i)[0])

# Load known face encodings
encodeListKnown = []
for img in images:
    encode = face_recognition.face_encodings(img)[0]
    encodeListKnown.append(encode)

# Initialize camera
capture = cv2.VideoCapture(0)

# Initialize attendance database
def markAttendance(name, lecture_name):
    with open('attendance.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        now = datetime.now()
        lecture_date = now.strftime('%d-%m-%Y')
        lecture_time = now.strftime('%H:%M:%S')
        writer.writerow([lecture_name, lecture_date, lecture_time, name])
    show_attendance_marked_label()  # Show "Attendance Marked" message

def show_attendance_marked_label():
    attendance_marked_label.config(text="Attendance Marked", foreground="green")
    root.after(3000, hide_attendance_marked_label)

def hide_attendance_marked_label():
    attendance_marked_label.config(text="")

def open_photos_folder():
    os.system("explorer photos")

def open_attendance_file():
    os.system("attendance.csv")

def clear_attendance_data():
    with open('attendance.csv', 'w') as f:
        f.truncate(0)
    clear_attendance_label.config(text="Attendance data cleared", foreground="green")
    root.after(3000, hide_clear_attendance_label)

def hide_clear_attendance_label():
    clear_attendance_label.config(text="", foreground="black")

def start_recognition():
    lecture_name = lecture_entry.get()
    if not lecture_name.strip():  # Check if the lecture name is empty or contains only spaces
        error_label.config(text="Error: Please enter lecture name", fg="red")
        return
    else:
        error_label.config(text="")
        lecture_entry.focus_set()  # Move cursor away from the entry field

    marked_students = set()  # Set to keep track of marked students

    def update_frame():
        ret, img = capture.read()
        if not ret:
            return

        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        face_current_frame = face_recognition.face_locations(imgS)
        encode_current_frame = face_recognition.face_encodings(imgS, face_current_frame)

        for encodeface, facelocation in zip(encode_current_frame, face_current_frame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeface)
            facedistance = face_recognition.face_distance(encodeListKnown, encodeface)
            matchIndex = np.argmin(facedistance)

            if matches[matchIndex]:
                name = classnames[matchIndex].upper()
                if name not in marked_students:
                    y1, x2, y2, x1 = facelocation
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 3)  # Green bounding box
                    cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                    cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                    markAttendance(name, lecture_name)
                    marked_students.add(name)

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        img_tk = ImageTk.PhotoImage(image=img_pil)
        label.config(image=img_tk)
        label.image = img_tk

        if not stop_recognition:
            root.after(10, update_frame)

    stop_recognition = False
    update_frame()

def stop_recognition():
    global stop_recognition
    stop_recognition = True

def quit_app(event):
    root.destroy()

# Set a themed style for the application
style = ThemedStyle(root)
style.set_theme("radiance")  # Choose a theme from available themes
root.configure(bg=style.lookup("TFrame", "background"))

header_label = ttk.Label(root, text="Face Recognition Attendance System", font=("Helvetica", 20, "bold"), background=style.lookup("TFrame", "background"))
header_label.pack(pady=20)

entry_frame = ttk.Frame(root, padding=10)
entry_frame["style"] = "TFrame"  # Set the style directly
entry_frame.pack()

lecture_label = ttk.Label(entry_frame, text="Enter Lecture Name:", font=("Helvetica", 12), background=style.lookup("TFrame", "background"))
lecture_label.grid(row=0, column=0, padx=5, pady=5)

lecture_entry = ttk.Entry(entry_frame, font=("Helvetica", 12))
lecture_entry.grid(row=0, column=1, padx=5, pady=5)

error_label = ttk.Label(entry_frame, text="", font=("Helvetica", 12), foreground="red", background=style.lookup("TFrame", "background"))
error_label.grid(row=1, columnspan=2, padx=5, pady=5)

label = ttk.Label(root, background=style.lookup("TFrame", "background"))
label.pack()

attendance_marked_label = ttk.Label(root, text="", font=("Helvetica", 12), foreground="green", background=style.lookup("TFrame", "background"))
attendance_marked_label.pack()

button_frame = ttk.Frame(root, padding=10)
button_frame["style"] = "TFrame"  # Set the style directly
button_frame.pack()

button_style = ttk.Style()
button_style.configure("Custom.TButton", background="#DAF7A6", foreground="#000000", bordercolor="#FF5733")

start_button = ttk.Button(button_frame, text="Start Recognition", command=start_recognition, style="Custom.TButton")
start_button.grid(row=0, column=0, padx=10, pady=10)

stop_button = ttk.Button(button_frame, text="Stop Recognition", command=stop_recognition, style="Custom.TButton")
stop_button.grid(row=0, column=1, padx=10, pady=10)

open_photos_button = ttk.Button(button_frame, text="Open Photos Folder", command=open_photos_folder, style="Custom.TButton")
open_photos_button.grid(row=0, column=2, padx=10, pady=10)

open_attendance_button = ttk.Button(button_frame, text="Open Attendance File", command=open_attendance_file, style="Custom.TButton")
open_attendance_button.grid(row=0, column=3, padx=10, pady=10)

clear_attendance_button = ttk.Button(button_frame, text="Clear Attendance Data", command=clear_attendance_data, style="Custom.TButton")
clear_attendance_button.grid(row=1, columnspan=4, padx=10, pady=10)

clear_attendance_label = ttk.Label(button_frame, text="Attendance Data Cleared", font=("Helvetica", 12), background=style.lookup("TFrame", "background"))
clear_attendance_label.grid(row=2, columnspan=4, padx=5, pady=5)

quit_label = ttk.Label(root, text="Press 'q' to quit", font=("Helvetica", 12), background=style.lookup("TFrame", "background"))
quit_label.pack(pady=5)

root.bind('q', quit_app)

root.mainloop()

# Release the camera
capture.release()
cv2.destroyAllWindows()