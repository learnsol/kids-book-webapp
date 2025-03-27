from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
import logging
import urllib.parse

logger = logging.getLogger('kidsbook')

Base = declarative_base()

class Story(Base):
    __tablename__ = 'stories'
    
    id = Column(Integer, primary_key=True)
    input_text = Column(Text, nullable=False)
    edited_text = Column(Text, nullable=False)
    cover_image_url = Column(String(500))
    editor_prompt = Column(Text)
    illustrator_prompt = Column(Text)
    editor_response = Column(JSON)
    illustrator_response = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
class Database:
    def __init__(self):
        try:
            conn_str = os.getenv('AZURE_SQL_CONNECTION_STRING')
            if not conn_str:
                raise ValueError("Azure SQL connection string not found in environment variables")
            
            # Create SQLAlchemy engine with proper connection pooling
            self.engine = create_engine(
                conn_str,
                pool_size=5,
                max_overflow=2,
                pool_timeout=30,
                pool_recycle=1800
            )
            self.SessionLocal = sessionmaker(bind=self.engine)
            logger.info("Database connection established successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise

    def create_tables(self):
        try:
            Base.metadata.create_all(self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create tables: {str(e)}")
            raise
        
    def get_session(self):
        return self.SessionLocal()