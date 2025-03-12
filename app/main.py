import uvicorn
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.http import HTTPBearer
from fastapi.openapi.utils import get_openapi

# Import controllers
from app.controllers import (
    userController,
    hotelController,
    roomController,
    userRoleController,
    bookingController,
)

app = FastAPI()

# Define allowed origins (CORS policy)
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add JWT Bearer security
security = HTTPBearer()

# Include application routers
app.include_router(userController.router)
app.include_router(hotelController.router)
app.include_router(roomController.router)
app.include_router(userRoleController.router)
app.include_router(bookingController.router)

@app.get("/")
def root():
    return {"message": "Bienvenue dans l'API FastAPI"}

# Custom OpenAPI with JWT security
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="FastAPI Hotel Booking",
        version="1.0.0",
        description="API for hotel booking with JWT authentication",
        routes=app.routes,
    )

    # Define JWT Bearer authentication scheme
    openapi_schema["components"]["securitySchemes"] = {
        "BearerToken": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    
    # Apply security globally to all endpoints
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            openapi_schema["paths"][path][method]["security"] = [{"BearerToken": []}]

    app.openapi_schema = openapi_schema
    return openapi_schema

# Override default OpenAPI schema
app.openapi = custom_openapi

def start():
    """Launched with `poetry run start` at root level"""
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)