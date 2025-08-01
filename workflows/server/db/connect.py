# db/connect.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load .env from the project root directory
load_dotenv()
DATABASE_URL = os.getenv("DB_CONNECTION_STRING")

# Provide a default SQLite database if no connection string is provided
if not DATABASE_URL:
    print("⚠️  No DB_CONNECTION_STRING found in environment. Using SQLite for development.")
    DATABASE_URL = "sqlite:///./marketing_ai_agent.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
