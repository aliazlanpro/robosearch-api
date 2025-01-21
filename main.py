from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from robosearch.robots.rct_robot import RCTRobot

app = FastAPI()
rct_clf = RCTRobot()

class PredictItem(BaseModel):
    title: str
    abstract: str
    ptyp: List[str]
    id: str
    use_ptyp: bool

class PredictRequest(BaseModel):
    items: List[PredictItem]

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None):
    return {"item_id": item_id, "q": q}

@app.post("/predict")
def predict(request: PredictRequest):
    predictions = []
    for item in request.items:
        pred = rct_clf.predict({
            "title": item.title,
            "abstract": item.abstract,
            "ptyp": item.ptyp,
            "use_ptyp": item.use_ptyp
        })[0]  # Get first item since predict returns list
        
        predictions.append({
            "id": item.id,
            "is_rct": pred["is_rct"],
            "threshold_value": pred["threshold_value"],
            "ptyp_rct": pred["ptyp_rct"]
        })
    
    return predictions