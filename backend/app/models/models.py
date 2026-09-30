from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base
import enum

class TransactionType(str, enum.Enum):
    credit_purchase = "credit_purchase"
    research_usage = "research_usage"
    refund = "refund"
    bonus = "bonus"
    admin_adjustment = "admin_adjustment"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    balance = Column(Integer, default=100)  # Starting balance
    
    transactions = relationship("CreditTransaction", back_populates="user")
    research_jobs = relationship("ResearchJob", back_populates="user")

class CreditTransaction(Base):
    __tablename__ = "credit_transactions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Integer)  # Positive for adding credits, negative for usage
    type = Column(Enum(TransactionType))
    reason = Column(String)
    research_id = Column(Integer, ForeignKey("research_jobs.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="transactions")
    research_job = relationship("ResearchJob", back_populates="credit_transactions")

class ResearchJob(Base):
    __tablename__ = "research_jobs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    topic = Column(String, index=True)
    category = Column(String)
    content_type = Column(String) # "short_form" or "long_form"
    time_range = Column(String)
    status = Column(String, default="pending") # pending, searching, extracting, analyzing, completed, failed
    credits_used = Column(Integer, default=0)
    final_report = Column(Text, nullable=True)
    final_script = Column(Text, nullable=True)
    pdf_path = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    user = relationship("User", back_populates="research_jobs")
    sources = relationship("Source", back_populates="research_job", cascade="all, delete-orphan")
    credit_transactions = relationship("CreditTransaction", back_populates="research_job")

class Source(Base):
    __tablename__ = "sources"
    id = Column(Integer, primary_key=True, index=True)
    research_job_id = Column(Integer, ForeignKey("research_jobs.id"))
    url = Column(String)
    title = Column(String, nullable=True)
    content = Column(Text, nullable=True)  # Cleaned content
    relevance_status = Column(String, default="pending") # pending, relevant, irrelevant
    extraction_status = Column(String, default="pending") # pending, success, failed
    
    research_job = relationship("ResearchJob", back_populates="sources")
