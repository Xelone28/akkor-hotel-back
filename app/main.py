import uvicorn
from fastapi import FastAPI
from app.controllers import userController
from app.controllers import hotelController
from app.controllers import roomController

app = FastAPI()

app.include_router(userController.router)
app.include_router(hotelController.router)
app.include_router(roomController.router)

@app.get("/")
def root():
    return {"message": "Bienvenue dans l'API FastAPI"}

def start():
    """Launched with `poetry run start` at root level"""
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)