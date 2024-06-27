from fastapi import APIRouter, FastAPI
from fastapi import FastAPI, WebSocket
from contextlib import asynccontextmanager
import base64
import cv2
import numpy as np
import json
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from eye_detection import EyeDetection


ml_models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Loading eye detection object
    ml_models["eye_detection"] = EyeDetection()
    
    yield
    # Clean up the ML models and release the resources
    ml_models.clear()

app = FastAPI(lifespan=lifespan)
router = APIRouter()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    count = 0
    while True:
        data = await websocket.receive_text()
        # Field name to send the image: image
        image_data = json.loads(data)['image']
        image = base64.b64decode(image_data.split(',')[1])
        # Converting to numpy array and loading into an opencv frame
        np_img = np.frombuffer(image, dtype=np.uint8)
        frame = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
        # Predicting if the eyes are open or closed
        prediction = ml_models["eye_detection"].predict(frame)
        
        if prediction is not None:
           count += 1
           if count > 4:
            await websocket.send_json({"status": prediction})
            count = 0
        else:
            await websocket.send_json({"status": "indisponivel"})

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
