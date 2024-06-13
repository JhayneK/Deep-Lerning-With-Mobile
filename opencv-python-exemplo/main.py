from fastapi import FastAPI, WebSocket
import json
import base64
import cv2
import numpy as np
from opencv import OpenCVProcessor, ConvNet

app = FastAPI()

# Inicializando a classe pra processar a imagem
# O modelo eu treinei usando um modelo genérico que está no arquivo opencv.py, eu não usei todos os dados pra treinar pra ser mais rápido
# Talvez seja melhor usar dlib porque com esse modelo não tava prevendo meus olhos fechados, mas seria bom treinar um modelo melhor primeiro pra testar
processor = OpenCVProcessor(
    model_path='model.pkl',
    face_cascade_path='haar-cascade-files/haarcascade_frontalface_alt2.xml',
    eyes_cascade_path='haar-cascade-files/haarcascade_eye_tree_eyeglasses.xml'
)

# Websocket
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        # Nome do campo: image
        image_data = json.loads(data)['image']
        image = base64.b64decode(image_data.split(',')[1])
        # Converte pra matriz numpy e carrega num frame do opencv
        np_img = np.frombuffer(image, dtype=np.uint8)
        frame = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

        # Processando o frame
        _, eye = processor.process_frame(frame)

        # Enviando mensagem caso tenha abaixado a cabeça ou ambos os olhos estejam fechados (provavelmente vai ser alterado)
        if processor.predicted_classes is not None:
            if processor.predicted_classes[0] == 1 and processor.predicted_classes[1] == 1:
                await websocket.send_json({"status": "dormindo"})
            if (processor.y_array[-1] - (processor.face_height * 0.5)) > processor.y_array[0]:
                await websocket.send_json({"status": "pescando"})
        else:
            await websocket.send_json({"status": "erro"})

        _, buffer = cv2.imencode('.jpg', eye)
        encoded_eye = base64.b64encode(buffer).decode('utf-8')
        await websocket.send_json({'processed_image': encoded_eye})
        
        _, frame_buffer = cv2.imencode('.jpg', frame)
        encoded_frame = base64.b64encode(frame_buffer).decode('utf-8')
        await websocket.send_json({'frame': encoded_frame})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
