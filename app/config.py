import os
from app.database import SessionLocal
from dotenv import load_dotenv

load_dotenv()

# Environment variables
SECRET_KEY = os.getenv("SECRET_KEY", "your-default-secret-key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

# Dependency for getting DB session in FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
