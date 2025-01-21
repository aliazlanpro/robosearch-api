from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List
import os
from robosearch.robots.rct_robot import RCTRobot

app = FastAPI(
    title="RoboSearch API",
    description="API for RoboSearch",
    version="0.1.0"
)
rct_clf = RCTRobot()
security = HTTPBearer()

# Function to verify token
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = os.environ.get("API_TOKEN")
    if not token or credentials.credentials != token:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials

class PredictItem(BaseModel):
    title: str
    abstract: str
    ptyp: List[str]
    id: str
    use_ptyp: bool

class PredictRequest(BaseModel):
    citations: List[PredictItem]

@app.get("/")
def read_root():
    return app.openapi()

@app.post("/predict")
def predict(request: PredictRequest, token: str = Depends(verify_token)):
    predictions = []
    for item in request.citations:
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