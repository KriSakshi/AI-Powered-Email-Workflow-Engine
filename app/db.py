# app/db.py
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import DATABASE_URL
from app.logger import logger
import datetime

Base = declarative_base()
engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class EmailLog(Base):
    __tablename__ = "email_logs"
    id = Column(Integer, primary_key=True)
    sender = Column(String, index=True)
    subject = Column(String)
    body = Column(Text)
    classification = Column(String)
    action = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

def init_db():
    Base.metadata.create_all(engine)
    logger.info("DB ready")

def log_email(sender, subject, body, classification, action):
    s = SessionLocal()
    try:
        s.add(EmailLog(sender=sender, subject=subject, body=body,
                       classification=classification, action=action))
        s.commit()
    finally:
        s.close()
