import os
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

from models import Base, Secret
from schemas import SecretCreate

# Load environment variables (for local testing)
load_dotenv()

# Initialize FastAPI
app = FastAPI(title="DropBox IRL API")

# Setup Database Connection
DATABASE_URL = os.getenv("DATABASE_URL")

# Fix SQLAlchemy dialect prefix if necessary for PostgreSQL
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Initialize the SQLAlchemy Engine
engine = create_engine(DATABASE_URL)

# Initialize SessionLocal to handle database connections
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- TEMPORARY SCHEMA RESET ---
# This drops all existing tables before recreating them to ensure the schema is synced.
# IMPORTANT: Comment out or remove the drop_all line after your first successful test!
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

# Dependency injection to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"status": "online", "message": "DropBox IRL Backend is running."}

@app.post("/drop")
def drop_secret(secret_data: SecretCreate, db: Session = Depends(get_db)):
    try:
        # Convert the lat/lng into a PostGIS POINT geometry
        point_location = f"POINT({secret_data.lng} {secret_data.lat})"
        
        # Create the database row
        new_secret = Secret(
            creator_id=secret_data.creator_id,
            message=secret_data.message,
            location=point_location,
            expires_at=secret_data.expires_at
        )
        
        db.add(new_secret)
        db.commit()
        db.refresh(new_secret)
        
        return {"status": "success", "message": "Secret dropped successfully!", "secret_id": new_secret.id}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))