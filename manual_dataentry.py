###############################################################
'''
"Students": {
  "student_id": {
    "name": "John Doe",
    "phone_number": "1234567890",
    "department": "Computer Science",
    "starting_year": "2023",
    "total_attendance": 5,
    "daily_attendance": {
      "2024-08-01": 1,
      "2024-08-02": 2
    },
    "last_attendance_time": "2024-08-02 14:30:00"
  }
}
'''
###############################################################
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime

# Initialize Firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://console.firebase.google.com/u/1/project/face-attendance-project-af54f/database/face-attendance-project-af54f-default-rtdb/data/~2F"
})

# Function to submit data to Firebase
def submit_data():
    student_id = entry_id.get().strip()
    name = entry_name.get().strip()
    phone_number = entry_phone.get().strip()
    department = department_var.get().strip()
    starting_year = entry_starting_year.get().strip()

    # Check if all fields are filled
    if not (student_id and name and phone_number and department and starting_year):
        messagebox.showwarning("Input Error", "Please fill all fields")
        return

    try:
        ref = db.reference(f'Students/{student_id}')
        student_info = ref.get()
        
        if student_info:
            # If student exists, show an error message
            messagebox.showwarning("Data Exists", "Student data already exists in the database")
        else:
            # If student does not exist, add new student data
            student_data = {
                'name': name,
                'phone_number': phone_number,
                'department': department,
                'starting_year': starting_year,
                'total_attendance': 0,
                'daily_attendance': {},
                'last_attendance_time': ''
            }
            ref.set(student_data)
            messagebox.showinfo("Success", "Student data added successfully")
            clear_entries()
        
    except Exception as e:
        messagebox.showerror("Submission Error", f"Failed to submit data: {e}")

# Function to clear the entry fields
def clear_entries():
    entry_id.delete(0, tk.END)
    entry_name.delete(0, tk.END)
    entry_phone.delete(0, tk.END)
    department_var.set("")
    entry_starting_year.delete(0, tk.END)

# Create the main window
root = tk.Tk()
root.title("Student Data Entry")

# Create and place labels and entry widgets
labels = ["Student ID", "Name", "Phone Number", "Department", "Starting Year"]
entries = {}

for i, label_text in enumerate(labels):
    tk.Label(root, text=label_text).grid(row=i, column=0, padx=10, pady=5, sticky="e")

# Entry widgets
entry_id = ttk.Entry(root, width=30)
entry_name = ttk.Entry(root, width=30)
entry_phone = ttk.Entry(root, width=30)
entry_starting_year = ttk.Entry(root, width=30)

entry_id.grid(row=0, column=1, padx=10, pady=5)
entry_name.grid(row=1, column=1, padx=10, pady=5)
entry_phone.grid(row=2, column=1, padx=10, pady=5)
entry_starting_year.grid(row=4, column=1, padx=10, pady=5)

# Dropdown menu for Department
department_var = tk.StringVar()
departments = ["Computer Science", "Electrical Engineering", "Mechanical Engineering", "Civil Engineering"]
ttk.OptionMenu(root, department_var, "", *departments).grid(row=3, column=1, padx=10, pady=5)

# Create and place the submit button
submit_button = ttk.Button(root, text='Submit', command=submit_data)
submit_button.grid(row=len(labels), column=1, pady=10)

# Run the application
root.mainloop()
