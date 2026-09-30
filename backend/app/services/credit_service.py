from sqlalchemy.orm import Session
from ..models.models import User, CreditTransaction, TransactionType, ResearchJob
from ..core.config import get_content_config

class CreditService:
    @staticmethod
    def get_estimate(content_type: str) -> int:
        config = get_content_config(content_type)
        return config["credits"]

    @staticmethod
    def reserve_credits(db: Session, user_id: int, research_job_id: int, content_type: str) -> bool:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
            
        estimated_credits = CreditService.get_estimate(content_type)
        
        if user.balance < estimated_credits:
            return False
            
        # Deduct credits
        user.balance -= estimated_credits
        
        # Record transaction
        tx = CreditTransaction(
            user_id=user_id,
            amount=-estimated_credits,
            type=TransactionType.research_usage,
            reason=f"Started {content_type} research",
            research_id=research_job_id
        )
        db.add(tx)
        
        # Update job
        job = db.query(ResearchJob).filter(ResearchJob.id == research_job_id).first()
        if job:
            job.credits_used = estimated_credits
            
        db.commit()
        return True

    @staticmethod
    def refund_credits(db: Session, research_job_id: int, reason: str):
        job = db.query(ResearchJob).filter(ResearchJob.id == research_job_id).first()
        if not job or job.credits_used <= 0:
            return
            
        user = db.query(User).filter(User.id == job.user_id).first()
        if not user:
            return
            
        amount_to_refund = job.credits_used
        user.balance += amount_to_refund
        
        tx = CreditTransaction(
            user_id=user.id,
            amount=amount_to_refund,
            type=TransactionType.refund,
            reason=f"Refund: {reason}",
            research_id=research_job_id
        )
        db.add(tx)
        
        job.credits_used = 0
        db.commit()
