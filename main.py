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
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

@app.get("/")
def read_root():
    return {"status": "online", "message": "DropBox IRL Backend is running."}

# We will add the /secrets/nearby PostGIS endpoint here next!