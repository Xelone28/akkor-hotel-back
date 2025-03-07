from fastapi import FastAPI
from app.controllers import userController

app = FastAPI()

app.include_router(userController.router)

@app.get("/")
def root():
    return {"message": "Bienvenue dans l'API FastAPI"}