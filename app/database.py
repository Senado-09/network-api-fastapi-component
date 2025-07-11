import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Load environment variables from .env file
load_dotenv()

# Choose between Postgres and MySQL based on environment variable
db_type = os.getenv("TYPE_DB", "mysql")  # Default to MySQL
print(f"[INFO] Database type selected: {db_type}")

if db_type == "postgres":
    DATABASE_URL = os.getenv("DATABASE_URL_POSTGRES")
else:
    DATABASE_URL = os.getenv("DATABASE_URL_MYSQL")

# Compatibility fix for old-style postgres URLs
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
