import cv2
import os
import pickle
import mediapipe as mp
import numpy as np

# Initialize MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, min_detection_confidence=0.5)

def find_encodings(imagesList):
    encodeList = []
    for img in imagesList:
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(imgRGB)

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                encodeList.append(np.array([(lm.x, lm.y, lm.z) for lm in face_landmarks.landmark]))
        else:
            print("No face landmarks detected in an image.")
    return encodeList

# Importing student images
folderPath = 'Images'
pathList = os.listdir(folderPath)
print("Image Paths:", pathList)
imgList = []
studentIds = []

for path in pathList:
    try:
        img = cv2.imread(os.path.join(folderPath, path))
        
        if img is None:
            print(f"Failed to load image: {path}")
            continue

        imgList.append(img)
        studentIds.append(os.path.splitext(path)[0])

    except Exception as e:
        print(f"Error processing {path}: {e}")

print("Student IDs:", studentIds)

print("Encoding Started ...")
encodeListKnown = find_encodings(imgList)
encodeListKnownWithIds = [encodeListKnown, studentIds]
print("Encoding Complete")

# Save the encodings to a file
with open("EncodeFile.p", 'wb') as file:
    pickle.dump(encodeListKnownWithIds, file)

print("File Saved")
