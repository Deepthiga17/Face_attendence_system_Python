import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import firebase_admin
from firebase_admin import credentials, storage, db
import os

# Initialize Firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://face-attendance-project-af54f-default-rtdb.asia-southeast1.firebasedatabase.app/",
    'storageBucket': "face-attendance-project-af54f.appspot.com"
})

bucket = storage.bucket()

# Function to clear the entry fields
def clear_entries():
    entry_id.delete(0, tk.END)
    entry_name.delete(0, tk.END)
    entry_phone.delete(0, tk.END)
    department_var.set("")
    entry_starting_year.delete(0, tk.END)

# Function to submit student data to Firebase Realtime Database
def submit_data(image_blob):
    student_id = entry_id.get().strip()
    name = entry_name.get().strip()
    phone_number = entry_phone.get().strip()
    department = department_var.get().strip()
    starting_year = entry_starting_year.get().strip()

    if not (student_id and name and phone_number and department and starting_year):
        messagebox.showwarning("Input Error", "Please fill all fields")
        return

    try:
        ref = db.reference(f'Students/{student_id}')
        student_info = ref.get()

        if student_info:
            messagebox.showwarning("Data Exists", "Student data already exists in the database")
        else:
            image_url = image_blob.public_url

            student_data = {
                'name': name,
                'phone_number': phone_number,
                'department': department,
                'starting_year': starting_year,
                'total_attendance': 0,
                'daily_attendance': {},
                'last_attendance_time': '',
                'image_url': image_url
            }

            ref.set(student_data)
            messagebox.showinfo("Success", "Student data added successfully")
            clear_entries()

    except Exception as e:
        messagebox.showerror("Submission Error", f"Failed to submit data: {e}")

# Function to upload images to Firebase Storage
def upload_images():
    files = filedialog.askopenfilenames(
        title="Select Images",
        filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")]
    )
    
    if not files:
        return
    
    for file_path in files:
        try:
            student_id = os.path.splitext(os.path.basename(file_path))[0]

            ref = db.reference(f'Students/{student_id}')
            student_info = ref.get()

            if student_info:
                messagebox.showwarning("Data Exists", f"Data for student ID '{student_id}' already exists.")
                continue

            blob = bucket.blob(f'Images/{os.path.basename(file_path)}')
            if blob.exists():
                messagebox.showwarning("File Exists", f"Image with ID '{student_id}' already exists.")
                continue

            blob.upload_from_filename(file_path)
            messagebox.showinfo("Upload Success", f"Image with ID '{student_id}' uploaded successfully.")

            # Now show the form to enter student details
            display_data_entry_form(student_id, blob)

        except Exception as e:
            messagebox.showerror("Upload Error", f"Failed to upload {file_path}: {e}")

# Function to display the data entry form
def display_data_entry_form(student_id, image_blob):
    # Populate the Student ID field
    entry_id.insert(0, student_id)

    # Show the data entry form
    data_entry_frame.pack(padx=10, pady=10)

    # Configure the submit button to save data for the specific image_blob
    submit_button.config(command=lambda: submit_data(image_blob))

# Create the main window
root = tk.Tk()
root.title("Firebase Image and Data Uploader")

# Create the Upload Button
upload_button = ttk.Button(root, text="Upload Images", command=upload_images)
upload_button.pack(pady=20)

# Create Data Entry Frame (Initially hidden)
data_entry_frame = tk.Frame(root)

labels = ["Student ID", "Name", "Phone Number", "Department", "Starting Year"]
entries = {}

for i, label_text in enumerate(labels):
    tk.Label(data_entry_frame, text=label_text).grid(row=i, column=0, padx=10, pady=5, sticky="e")

entry_id = ttk.Entry(data_entry_frame, width=30)
entry_name = ttk.Entry(data_entry_frame, width=30)
entry_phone = ttk.Entry(data_entry_frame, width=30)
entry_starting_year = ttk.Entry(data_entry_frame, width=30)

entry_id.grid(row=0, column=1, padx=10, pady=5)
entry_name.grid(row=1, column=1, padx=10, pady=5)
entry_phone.grid(row=2, column=1, padx=10, pady=5)
entry_starting_year.grid(row=4, column=1, padx=10, pady=5)

# Dropdown menu for Department
department_var = tk.StringVar()
departments = ["CSE", "IT", "MECH", "CSBS", "AIDS", "AIML", "ECE", "EEE"]
ttk.OptionMenu(data_entry_frame, department_var, "", *departments).grid(row=3, column=1, padx=10, pady=5)

# Submit Button for Data Entry Form
submit_button = ttk.Button(data_entry_frame, text='Submit')
submit_button.grid(row=len(labels), column=1, pady=10)

# Hide the data entry form initially
data_entry_frame.pack_forget()

# Run the application
root.mainloop()
