from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import models
from .database import engine
from .routers import messages_route

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="CoachAI")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(messages_route.router)


@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}
