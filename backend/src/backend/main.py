from backend import models
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from .config import Config
from .api.routes import messages_route

models.Base.metadata.create_all(bind=engine)

app = FastAPI(debug=Config.stage == "dev")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(messages_route.router)
