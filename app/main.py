import uvicorn
from fastapi import FastAPI
from app.controllers import userController

app = FastAPI()

app.include_router(userController.router)

@app.get("/")
def root():
    return {"message": "Bienvenue dans l'API FastAPI"}

def start():
    """Launched with `poetry run start` at root level"""
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)