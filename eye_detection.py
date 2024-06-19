import cv2 as cv
import dlib
from PIL import Image
from torchvision import transforms
import threading
import torch
from cnn_model import DrowsinessCNN
import torch.nn as nn
import numpy as np

class EyeDetection:
    def __init__(self):
        
        # Global Variables
        self.right_eye = None
        self.left_eye = None

        # Model output variables.
        self.output_right = None
        self.output_left = None


        self.detector = dlib.get_frontal_face_detector()
        # IMPORTANT
        # Inside of the shape_predictor function , we must define the predictor
        self.predictor = dlib.shape_predictor("./saved_model/shape_predictor_68_face_landmarks.dat")

                
        # Input format of the model.
        self.input_transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0, 0, 0), (1, 1, 1))
        ])

        # To load the parameters of the trained model, first we need to initialize same model that we have created into the running application.
        self.model = DrowsinessCNN()

        # Checking if the GPU is available. (if is not, we need to map the model to load on the CPU instead)
        if torch.cuda.is_available():
            self.device = torch.device('cuda:0')
            self.device_string = 'cuda:0'
            
            # Loading the parameters of the model - WEIGHTS, BIASES and more.
            self.model.load_state_dict(torch.load('./saved_model/drowsiness.pth'))
        else:
            self.device = torch.device('cpu')
            self.device_string = 'cpu'

            # Loading the parameters of the model - WEIGHTS, BIASES and more.
            self.model.load_state_dict(torch.load('./saved_model/drowsiness.pth', map_location=torch.device('cpu')))

        self.model.eval()

    # Input data for the prediction
    def __define_input(self, right_eye_input, left_eye_input):

        right_eye_image = Image.fromarray(right_eye_input)
        self.right_eye = right_eye_image.resize((145, 145))

        left_eye_image = Image.fromarray(left_eye_input)
        self.left_eye = left_eye_image.resize((145, 145))

        self.right_eye = self.input_transform(self.right_eye)
        self.left_eye = self.input_transform(self.left_eye)
        


    # Output data of the prediction
    def __model_output(self, right_eye, left_eye):

        with torch.no_grad():
            try:
                self.output_right = self.model(right_eye)
                self.output_left = self.model(left_eye)
                m = nn.Sigmoid()

                self.output_right = m(self.output_right)
                self.output_left = m(self.output_left)

                self.output_right = self.output_right.numpy()
                self.output_left = self.output_left.numpy()
            except TypeError:
                pass

    def predict(self, frame):
        predict = None
        # Get data from VideoCapture(0) - must be in gray format.
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

        # Detect the face inside of the frame
        faces = self.detector(gray)

        # Iterate faces.
        for face in faces:

            # Apply the landmark to the detected face
            face_lndmrks = self.predictor(gray, face)

            righteye_x_strt = face_lndmrks.part(37).x-25
            righteye_x_end = face_lndmrks.part(40).x+25
            righteye_y_strt = face_lndmrks.part(20).y-10
            righteye_y_end = face_lndmrks.part(42).y+20

            lefteye_x_strt = face_lndmrks.part(43).x-25
            lefteye_x_end = face_lndmrks.part(46).x+25
            lefteye_y_strt = face_lndmrks.part(25).y-10
            lefteye_y_end = face_lndmrks.part(47).y+20

            right_eye_input = frame[righteye_y_strt:righteye_y_end,
                                    righteye_x_strt:righteye_x_end]
            left_eye_input = frame[lefteye_y_strt:lefteye_y_end,
                                lefteye_x_strt:lefteye_x_end]
            
            a = threading.Thread(target = self.__define_input, args=(
                right_eye_input, left_eye_input))
            b = threading.Thread(target = self.__model_output, args = (self.right_eye, self.left_eye))
        
            a.start()
            b.start()
        
            a.join()
            b.join()
                
            # Prediction of the eyes whether closed or opened
            drowsiness = []
            if self.output_left != None:
                drowsiness.append(self.output_left)
            if self.output_right != None:
                drowsiness.append(self.output_right)

            drowsiness = np.asarray(drowsiness)
                
            try:
                mean_drows = sum(drowsiness) / len(drowsiness)
                
                if mean_drows < 0.5:
                    predict = "Awake"
                else:
                    predict = "Sleepy"
                cv.putText(frame, predict, (20, 40), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 3)

            except ZeroDivisionError:
                pass
        return predict