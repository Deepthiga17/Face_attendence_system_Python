import os
import pickle
import numpy as np
import cv2
import cvzone
import mediapipe as mp
import firebase_admin
from firebase_admin import credentials, db, storage
from datetime import datetime

# Initialize Firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://face-attendance-project-af54f-default-rtdb.asia-southeast1.firebasedatabase.app/",
    'storageBucket': "gs://face-attendance-project-af54f.appspot.com"
})

bucket = storage.bucket()

# Initialize MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, min_detection_confidence=0.5)

# Initialize video capture
cap = cv2.VideoCapture(0)  # Change to 1 if necessary
cap.set(3, 640)
cap.set(4, 480)

# Load background and mode images
imgBackground = cv2.imread('Resources/background.png')
folderModePath = 'Resources/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = [cv2.imread(os.path.join(folderModePath, path)) for path in modePathList]

# Load encoded faces
print("Loading Encode File ...")
with open('EncodeFile.p', 'rb') as file:
    encodeListKnownWithIds = pickle.load(file)
encodeListKnown, studentIds = encodeListKnownWithIds
print("Encode File Loaded")

modeType = 0
counter = 0
id = -1
imgStudent = []

# Function to calculate face landmark similarity
def find_landmark_similarity(landmarks1, landmarks2):
    return np.linalg.norm(landmarks1 - landmarks2)

while True:
    success, img = cap.read()
    if not success:
        break

    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(imgRGB)

    imgBackground[162:162 + 480, 55:55 + 640] = img
    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            landmarks = np.array([(lm.x, lm.y, lm.z) for lm in face_landmarks.landmark])

            min_distance = float('inf')
            matchIndex = -1

            for idx, known_landmarks in enumerate(encodeListKnown):
                distance = find_landmark_similarity(landmarks, known_landmarks)
                if distance < min_distance:
                    min_distance = distance
                    matchIndex = idx

            if min_distance < 0.6:  # You can adjust this threshold
                id = studentIds[matchIndex]

                if counter == 0:
                    cvzone.putTextRect(imgBackground, "Loading", (275, 400))
                    cv2.imshow("Face Attendance", imgBackground)
                    cv2.waitKey(1)
                    counter = 1
                    modeType = 1

        if counter != 0:
            if counter == 1:
                studentInfo = db.reference(f'Students/{id}').get()
                print(studentInfo)

                blob = bucket.get_blob(f'Images/{id}.png')
                array = np.frombuffer(blob.download_as_string(), np.uint8)
                imgStudent = cv2.imdecode(array, cv2.IMREAD_COLOR)

                today_str = datetime.now().strftime("%Y-%m-%d")
                if today_str not in studentInfo['daily_attendance']:
                    studentInfo['daily_attendance'][today_str] = 0

                # Increment the daily attendance count
                studentInfo['daily_attendance'][today_str] += 1
                studentInfo['total_attendance'] += 1

                ref = db.reference(f'Students/{id}')
                ref.update({
                    'total_attendance': studentInfo['total_attendance'],
                    'daily_attendance': studentInfo['daily_attendance']
                })

                last_attendance_str = studentInfo['last_attendance_time']
                datetimeObject = datetime.strptime(last_attendance_str, "%Y-%m-%d %H:%M:%S")
                secondsElapsed = (datetime.now() - datetimeObject).total_seconds()
                print(secondsElapsed)

                if secondsElapsed > 30:
                    ref.update({
                        'last_attendance_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })

            if modeType != 3:
                if 10 < counter < 20:
                    modeType = 2

                imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

                if counter <= 10:
                    # Display only relevant information
                    cv2.putText(imgBackground, f'ID: {id}', (861, 125),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
                    cv2.putText(imgBackground, f'Department: {studentInfo["department"]}', (861, 175),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
                    cv2.putText(imgBackground, f'Starting Year: {studentInfo["starting_year"]}', (861, 225),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
                    cv2.putText(imgBackground, f'Total Attendance: {studentInfo["total_attendance"]}', (861, 275),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)

                    (w, h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                    offset = (414 - w) // 2
                    cv2.putText(imgBackground, studentInfo['name'], (808 + offset, 445),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)

                    imgBackground[175:175 + 216, 909:909 + 216] = imgStudent

                counter += 1

                if counter >= 20:
                    counter = 0
                    modeType = 0
                    studentInfo = []
                    imgStudent = []
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
    else:
        modeType = 0
        counter = 0

    cv2.imshow("Face Attendance", imgBackground)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
