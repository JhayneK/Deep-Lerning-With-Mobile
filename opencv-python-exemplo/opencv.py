import cv2
import numpy as np
import pickle
import torch
import torch.nn as nn


# Modelo genérico de rede neural convolucional
class ConvNet(nn.Module):
    def __init__(self):
        super(ConvNet, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2, padding=0)
        self.fc1 = nn.Linear(64 * 8 * 8, 128)
        self.fc2 = nn.Linear(128, 2)
        self.dropout = nn.Dropout(0.25)

    def forward(self, x):
        x = self.pool(torch.relu(self.conv1(x)))
        x = self.pool(torch.relu(self.conv2(x)))
        x = x.view(-1, 64 * 8 * 8)
        x = torch.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        return x

# Carregando o modelo e processando o frame
class OpenCVProcessor:
    def __init__(self, model_path, face_cascade_path, eyes_cascade_path):
        with open(model_path, 'rb') as model:
            self.cnn_model = pickle.load(model)
        
        self.face_cascade = cv2.CascadeClassifier(face_cascade_path)
        self.eyes_cascade = cv2.CascadeClassifier(eyes_cascade_path)
        self.y_array = np.zeros(42)
        self.count = 0
        self.predicted_classes = None
        self.face_height = 0
        self.eyes_position = np.zeros((2,4), int)

    def process_frame(self, frame):
        # Converte pra escala de cinza
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Detectando o rosto pra usar como referência pro tamanho dos olhos e pra detectar se a pessoa abaixou a cabeça
        minsize_face = (30, 30)
        face_edges = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=6, minSize=minsize_face)
        self.face_height = 0
        for (x, y, w, h) in face_edges:
            # O retângulo é só pra se quiser puxar a imagem da api depois
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            self.face_height = h

        # Tamanho dos olhos com base no tamanho do rosto
        minsize_eyes = (int(self.face_height/4.5), int(self.face_height/4.5))
        maxsize_eyes = (int(self.face_height/3), int(self.face_height/3))

        eyes_edges = self.eyes_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=6, minSize=minsize_eyes, maxSize=maxsize_eyes)

        # Array pra armazenar os olhos pra depois detectar se estão fechados
        eyes_array = np.zeros((2, 32, 32, 1))
        index = 0
        eye_ = 0
        for (x, y, w, h) in eyes_edges:
            if index > 1:
                break
            # O retângulo é só pra se quiser puxar a imagem da api depois
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            if self.count == len(self.y_array):
                self.y_array = np.roll(self.y_array, -1)
                self.y_array[-1] = int(y)
            else: 
                self.y_array[self.count] = int(y)
                self.count += 1
            eye_ = gray[y:y+h, x:x+w]
            self.eyes_position[index] = [int(y),int(y+h), int(x), int(x+w)]
            # Redimensionando a imagem pra 32x32 (pode ser alterado)
            eye = cv2.resize(eye_, (32, 32))
            eye = eye / 255
            eyes_array[index] = eye.reshape(32, 32, -1)
            index += 1

        # Condição olhos não encontrados
        if len(eyes_edges) == 0 and 0 not in self.eyes_position and gray.size != 0:
            eye_1 = gray[self.eyes_position[0,0]:self.eyes_position[0,1], 
                         self.eyes_position[0,2]:self.eyes_position[0,3]]
            eye_2 = gray[self.eyes_position[1,0]:self.eyes_position[1,1], 
                         self.eyes_position[1,2]:self.eyes_position[1,3]]
            if eye_1.size != 0: 
                eye_1 = cv2.resize(eye_1, (32, 32))
                eye_ = eye_1
                eye_1 = eye_1 / 255
                eyes_array[0] = eye_1.reshape(32, 32, -1)
            if eye_2.size != 0:
                eye_2 = cv2.resize(eye_2, (32, 32))
                eye_ = eye_2
                eye_2 = eye_2 / 255
                eyes_array[1] = eye_2.reshape(32, 32, -1)
            

        self.cnn_model.eval()
        # Dando reshape e convertendo em tensor do pytorch pra poder prever
        eyes_array = eyes_array.reshape(-1, 1, 32, 32)
        tensor = torch.tensor(eyes_array, dtype=torch.float32)

        with torch.no_grad():
            predictions = self.cnn_model(tensor)
            _, self.predicted_classes = torch.max(predictions, 1)

        # Retorna o frame com os retângulos nos olhos caso quiser usar
        return frame, eye_
