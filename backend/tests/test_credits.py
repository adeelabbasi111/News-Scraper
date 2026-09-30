import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.models.models import User, ResearchJob, CreditTransaction
from app.services.credit_service import CreditService

# In-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture()
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

def test_credit_reservation(db):
    user = User(username="test", balance=100)
    db.add(user)
    db.commit()
    
    job = ResearchJob(user_id=user.id, topic="Test", content_type="SHORT_FORM", status="pending")
    db.add(job)
    db.commit()
    
    # SHORT_FORM should cost 10 credits
    success = CreditService.reserve_credits(db, user.id, job.id, "SHORT_FORM")
    
    assert success is True
    assert user.balance == 90
    assert job.credits_used == 10
    
    txs = db.query(CreditTransaction).all()
    assert len(txs) == 1
    assert txs[0].amount == -10
    assert txs[0].type.value == "research_usage"

def test_credit_refund(db):
    user = User(username="test", balance=90)
    db.add(user)
    db.commit()
    
    job = ResearchJob(user_id=user.id, topic="Test", content_type="SHORT_FORM", status="failed", credits_used=10)
    db.add(job)
    db.commit()
    
    CreditService.refund_credits(db, job.id, "Failed search")
    
    assert user.balance == 100
    assert job.credits_used == 0
    
    tx = db.query(CreditTransaction).filter(CreditTransaction.amount > 0).first()
    assert tx.amount == 10
    assert tx.type.value == "refund"

def test_insufficient_credits(db):
    user = User(username="test", balance=5)
    db.add(user)
    db.commit()
    
    job = ResearchJob(user_id=user.id, topic="Test", content_type="LONG_FORM", status="pending")
    db.add(job)
    db.commit()
    
    success = CreditService.reserve_credits(db, user.id, job.id, "LONG_FORM")
    assert success is False
    assert user.balance == 5
    assert job.credits_used == 0
