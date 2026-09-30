from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ResearchRequest(BaseModel):
    topic: str
    category: str
    content_type: str
    time_range: str

class ResearchResponse(BaseModel):
    id: int
    topic: str
    content_type: str
    status: str
    credits_used: int
    
    class Config:
        from_attributes = True

class SourceSchema(BaseModel):
    url: str
    title: Optional[str] = None
    extraction_status: str
    relevance_status: str
    
    class Config:
        from_attributes = True

class JobStatusResponse(BaseModel):
    id: int
    status: str
    error_message: Optional[str] = None
    final_report: Optional[str] = None
    final_script: Optional[str] = None
    pdf_url: Optional[str] = None
    sources: List[SourceSchema] = []
    
    class Config:
        from_attributes = True

class CreditEstimateResponse(BaseModel):
    content_type: str
    estimated_credits: int
