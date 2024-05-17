import cv2
import sys
import numpy as np

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

    face_edges = face.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=6, minSize=(100, 100))
    face_height = 0
    for (x, y, w, h) in face_edges:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        face_height = h
    eyes_edges = eyes.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=6, minSize=(30, 30))

    for (x, y, w, h) in eyes_edges:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
        if count == len(y_array):
            y_array = np.roll(y_array, -1)
            y_array[-1] = int(y)
        else: 
            y_array[count] = int(y)
            count += 1

    #cv2.putText(frame, f"y[0]:{y_array[0]}", (w-10, h-10), cv2.FONT_HERSHEY_PLAIN, 2.3, (0, 255, 0), 2, cv2.LINE_AA)
    #cv2.putText(frame, f"y[-1]:{y_array[-1]}", (400, h-10), cv2.FONT_HERSHEY_PLAIN, 2.3, (0, 255, 0), 2, cv2.LINE_AA)

    if (y_array[-1] -(face_height*0.5)) > y_array[0]:
        cv2.putText(frame, "ta pescando", (w-20, h+70), cv2.FONT_HERSHEY_PLAIN, 2.3, (0, 255, 0), 2, cv2.LINE_AA)

    cv2.imshow(win_name, frame)

source.release()
cv2.destroyWindow(win_name)