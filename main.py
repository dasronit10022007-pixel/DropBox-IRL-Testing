import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

from geoalchemy2.functions import ST_DWithin
from geoalchemy2.elements import WKTElement
from geoalchemy2.shape import to_shape

from models import Base, Secret, User
from schemas import SecretCreate, UserCreate
import security

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

# --- SCHEMA MANAGEMENT ---
# Base.metadata.drop_all(bind=engine)  # Safe: Commented out to prevent accidental data wipes!
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

@app.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    try:
        # Check if username or email already exists
        existing_user = db.query(User).filter(
            (User.username == user_data.username) | (User.email == user_data.email)
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already registered"
            )

        # Hash password and store user
        hashed_pw = security.hash_password(user_data.password)
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_pw
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"status": "success", "message": "User registered!", "user_id": new_user.id}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Authenticate user
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate JWT token
    access_token = security.create_access_token(data={"sub": user.id, "username": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/drop")
def drop_secret(secret_data: SecretCreate, db: Session = Depends(get_db)):
    try:
        # Convert the lat/lng into a PostGIS POINT geometry (Longitude FIRST)
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

@app.get("/secrets/nearby")
def get_nearby_secrets(
    lat: float, 
    lng: float, 
    radius_meters: float = 1000.0, 
    db: Session = Depends(get_db)
):
    """
    Fetch secrets within a given radius (in meters) from latitude and longitude.
    """
    try:
        # Construct PostGIS WKT Point (Longitude ALWAYS comes first in PostGIS WKT)
        user_point = WKTElement(f"POINT({lng} {lat})", srid=4326)

        # Spatial query using ST_DWithin
        raw_secrets = db.query(Secret).filter(
            ST_DWithin(Secret.location, user_point, radius_meters)
        ).all()

        # Format spatial output cleanly for JSON response
        formatted_secrets = []
        for secret in raw_secrets:
            point = to_shape(secret.location)
            formatted_secrets.append({
                "id": secret.id,
                "creator_id": secret.creator_id,
                "message": secret.message,
                "lat": point.y,
                "lng": point.x,
                "created_at": secret.created_at,
                "expires_at": secret.expires_at
            })

        return formatted_secrets

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))