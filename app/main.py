import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.controllers import userController
from app.controllers import hotelController
from app.controllers import roomController
from app.controllers import userRoleController

app = FastAPI()

origins = [""]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=[""],
    allow_headers=["*"],
)

app.include_router(userController.router)
app.include_router(hotelController.router)
app.include_router(roomController.router)
app.include_router(userRoleController.router)

@app.get("/")
def root():
    return {"message": "Bienvenue dans l'API FastAPI"}

def start():
    """Launched with `poetry run start` at root level"""
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)