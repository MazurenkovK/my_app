from sqlalchemy import create_engine, Column, Integer, DateTime, String, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Image(Base):
    __tablename__ = 'images'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False)
    description = Column(String, nullable=False)
    image_data = Column(LargeBinary, nullable=False)

# Настройка базы данных 
DATABASE_URL = 'sqlite:///images.db'
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
   
