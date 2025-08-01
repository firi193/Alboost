# db/init_db.py
from connect import engine
from models import metadata

def create_tables():
    metadata.create_all(bind=engine)

if __name__ == "__main__":
    create_tables()
