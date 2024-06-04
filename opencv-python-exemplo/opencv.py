import cv2
import sys
import numpy as np
import pickle
import torch

with open('model.pkl', 'rb') as model:
    cnn_model = pickle.load(model)


face = cv2.CascadeClassifier('haar-cascade-files/haarcascade_frontalface_alt2.xml')
eyes = cv2.CascadeClassifier('haar-cascade-files/haarcascade_eye_tree_eyeglasses.xml')

s = 0
if len(sys.argv) > 1:
    s = sys.argv[1]
    print(s)

source = cv2.VideoCapture(s)

win_name = 'Camera Preview'
cv2.namedWindow(win_name, cv2.WINDOW_NORMAL)


y_array = np.zeros(42)
count = 0

while cv2.waitKey(1) != 27: # Escape
    has_frame, frame = source.read()
    if not has_frame:
        break

    height,width = frame.shape[:2]

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    minsize_face = (30, 30)
    face_edges = face.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=6, minSize=minsize_face)
    face_height = 0
    for (x, y, w, h) in face_edges:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        face_height = h

    
    minsize_eyes = (face_height/5, face_height/5)
    maxsize_eyes = (face_height/3.5, face_height/3.5)
    eyes_edges = eyes.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=6, minSize=minsize_eyes, maxSize=maxsize_eyes)

    eyes_array = np.ndarray(2, 24, 24, 1)
    index = 0
    for (x, y, w, h) in eyes_edges:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
        if count == len(y_array):
            y_array = np.roll(y_array, -1)
            y_array[-1] = int(y)
        else: 
            y_array[count] = int(y)
            count += 1
        eye=frame[y:y+h,x:x+w] # Frame do olho
        eye = cv2.cvtColor(eye,cv2.COLOR_BGR2GRAY) # Escala de cinza
        eye = cv2.resize(eye,(32,32)) # Redimensionando
        eye= eye/255 # Normalizando
        eyes_array[index]= eye.reshape(32,32,-1)
        index += 1
        
    model.eval()
    eyes_array = eyes_array.reshape(-1, 1, 32, 32)
    tensor = torch.tensor(eyes_array, dtype=torch.float32)

    with torch.no_grad():
        predictions = model(tensor)
        _, predicted_classes = torch.max(predictions, 1)

    if predicted_classes.mean() == 1:
        cv2.putText(frame, "ta dormindo", (w-20, h+70), cv2.FONT_HERSHEY_PLAIN, 2.3, (0, 255, 0), 2, cv2.LINE_AA)


    if (y_array[-1] -(face_height*0.5)) > y_array[0]:
        cv2.putText(frame, "ta pescando", (w-20, h+70), cv2.FONT_HERSHEY_PLAIN, 2.3, (0, 255, 0), 2, cv2.LINE_AA)

    cv2.imshow(win_name, frame)

source.release()
cv2.destroyWindow(win_name)