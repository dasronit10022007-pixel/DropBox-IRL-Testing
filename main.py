import os
from fastapi import FastAPI
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load environment variables (for local testing)
load_dotenv()

# Initialize FastAPI
app = FastAPI(title="DropBox IRL API")

# Setup Database Connection
# We will inject the Aiven Service URI via Render's environment variables
# Setup Database Connection
DATABASE_URL = os.getenv("DATABASE_URL")

# Fix SQLAlchemy dialect prefix if necessary
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
from models import Base

# (Keep your existing engine creation code here)

# This command tells SQLAlchemy to create the tables in PostgreSQL if they don't exist
Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"status": "online", "message": "DropBox IRL Backend is running."}

# We will add the /secrets/nearby PostGIS endpoint here next!