from typing import Union
from fastapi import APIRouter, FastAPI
from pydantic import BaseModel
from contextlib import asynccontextmanager
import base64
import requests

class Itens(BaseModel):
    name: str
    description: str | None = None

def fake_answer_to_everything_ml_model(x: float):
    return x * 42

ml_models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    ml_models["answer_to_everything"] = fake_answer_to_everything_ml_model
    yield
    # Clean up the ML models and release the resources
    ml_models.clear()

app = FastAPI(lifespan=lifespan)
router = APIRouter()

class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}

@router.post("/items/")
def create_item(item: Item):
    return {"message": "Item created"}

@router.delete("/items/{item_id}")
def delete_item(item_id: str):
    return {"message": "Item deleted"}

@router.patch("/items/")
def update_item(item: Item):
    return {"message": "Item updated in place"}

@app.get("/predict")
async def predict(x: float):
    result = ml_models["answer_to_everything"](x)
    return {"result": result}






app.include_router(router)