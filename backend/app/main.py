from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas
from .database import engine, get_db, check_database_connection
from fastapi.middleware.cors import CORSMiddleware
import os

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the API"}

@app.get("/health/db")
def check_db_connection():
    result = check_database_connection()
    if result["status"] == "unhealthy":
        raise HTTPException(
            status_code=500,
            detail=f"Database connection failed: {result.get('error', 'Unknown error')}"
        )
    return result

@app.post("/messages/", response_model=schemas.Message)
def create_message(message: schemas.MessageCreate, db: Session = Depends(get_db)):
    db_message = models.Message(content=message.content)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

@app.get("/messages/", response_model=list[schemas.Message])
def read_messages(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    messages = db.query(models.Message).offset(skip).limit(limit).all()
    return messages

