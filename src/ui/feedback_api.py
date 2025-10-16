"""API endpoints for RLHF feedback collection."""

import logging
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.storage.database import get_db_session
from src.storage.models import Feedback, FeedbackType, Brand

logger = logging.getLogger(__name__)


# Request/Response models
class FeedbackCreate(BaseModel):
    """Create feedback request."""
    brand_id: str
    user_id: str
    task_type: str
    prompt: str
    model_output: str
    feedback_type: str
    rating: Optional[int] = Field(None, ge=1, le=5)
    preferred_output: Optional[str] = None
    rejected_output: Optional[str] = None
    metadata: Optional[dict] = None
    session_id: Optional[str] = None


class FeedbackResponse(BaseModel):
    """Feedback response."""
    id: int
    brand_id: str
    user_id: str
    task_type: str
    feedback_type: str
    rating: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True


class PreferencePairCreate(BaseModel):
    """Create preference pair for DPO."""
    brand_id: str
    user_id: str
    task_type: str
    prompt: str
    chosen_output: str
    rejected_output: str
    metadata: Optional[dict] = None
    session_id: Optional[str] = None


class FeedbackStats(BaseModel):
    """Feedback statistics."""
    total_feedback: int
    by_type: dict
    by_task: dict
    avg_rating: Optional[float]
    recent_feedback_count: int


class FeedbackAPI:
    """API for feedback collection."""
    
    def __init__(self):
        """Initialize feedback API."""
        self.router = APIRouter(prefix="/feedback", tags=["feedback"])
        self._setup_routes()
    
    def _setup_routes(self):
        """Set up API routes."""
        
        @self.router.post("/", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
        async def create_feedback(
            feedback: FeedbackCreate,
            db: Session = Depends(get_db_session)
        ):
            """
            Create new feedback entry.
            
            Args:
                feedback: Feedback data
                db: Database session
            
            Returns:
                Created feedback
            """
            # Validate brand exists
            brand = db.query(Brand).filter(Brand.brand_id == feedback.brand_id).first()
            if not brand:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Brand not found: {feedback.brand_id}"
                )
            
            # Validate feedback type
            try:
                feedback_type_enum = FeedbackType(feedback.feedback_type)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid feedback type: {feedback.feedback_type}"
                )
            
            # Create feedback
            db_feedback = Feedback(
                brand_id=brand.id,
                user_id=feedback.user_id,
                task_type=feedback.task_type,
                prompt=feedback.prompt,
                model_output=feedback.model_output,
                feedback_type=feedback_type_enum,
                rating=feedback.rating,
                preferred_output=feedback.preferred_output,
                rejected_output=feedback.rejected_output,
                metadata=feedback.metadata,
                session_id=feedback.session_id
            )
            
            db.add(db_feedback)
            db.commit()
            db.refresh(db_feedback)
            
            logger.info(f"Feedback created: {db_feedback.id} for brand {feedback.brand_id}")
            
            return FeedbackResponse(
                id=db_feedback.id,
                brand_id=feedback.brand_id,
                user_id=db_feedback.user_id,
                task_type=db_feedback.task_type,
                feedback_type=db_feedback.feedback_type.value,
                rating=db_feedback.rating,
                created_at=db_feedback.created_at
            )
        
        @self.router.post("/preference-pair", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
        async def create_preference_pair(
            pair: PreferencePairCreate,
            db: Session = Depends(get_db_session)
        ):
            """
            Create preference pair for DPO training.
            
            Args:
                pair: Preference pair data
                db: Database session
            
            Returns:
                Created feedback
            """
            # Validate brand
            brand = db.query(Brand).filter(Brand.brand_id == pair.brand_id).first()
            if not brand:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Brand not found: {pair.brand_id}"
                )
            
            # Create feedback with preference type
            db_feedback = Feedback(
                brand_id=brand.id,
                user_id=pair.user_id,
                task_type=pair.task_type,
                prompt=pair.prompt,
                model_output=pair.chosen_output,  # Store chosen as model_output
                feedback_type=FeedbackType.PREFERENCE,
                preferred_output=pair.chosen_output,
                rejected_output=pair.rejected_output,
                metadata=pair.metadata,
                session_id=pair.session_id
            )
            
            db.add(db_feedback)
            db.commit()
            db.refresh(db_feedback)
            
            logger.info(f"Preference pair created: {db_feedback.id} for brand {pair.brand_id}")
            
            return FeedbackResponse(
                id=db_feedback.id,
                brand_id=pair.brand_id,
                user_id=db_feedback.user_id,
                task_type=db_feedback.task_type,
                feedback_type=db_feedback.feedback_type.value,
                rating=None,
                created_at=db_feedback.created_at
            )
        
        @self.router.get("/stats", response_model=FeedbackStats)
        async def get_feedback_stats(
            brand_id: Optional[str] = None,
            task_type: Optional[str] = None,
            db: Session = Depends(get_db_session)
        ):
            """
            Get feedback statistics.
            
            Args:
                brand_id: Optional brand filter
                task_type: Optional task type filter
                db: Database session
            
            Returns:
                Feedback statistics
            """
            query = db.query(Feedback)
            
            # Apply filters
            if brand_id:
                brand = db.query(Brand).filter(Brand.brand_id == brand_id).first()
                if brand:
                    query = query.filter(Feedback.brand_id == brand.id)
            
            if task_type:
                query = query.filter(Feedback.task_type == task_type)
            
            feedbacks = query.all()
            
            # Calculate statistics
            total = len(feedbacks)
            
            by_type = {}
            by_task = {}
            ratings = []
            
            for fb in feedbacks:
                # Count by type
                fb_type = fb.feedback_type.value
                by_type[fb_type] = by_type.get(fb_type, 0) + 1
                
                # Count by task
                by_task[fb.task_type] = by_task.get(fb.task_type, 0) + 1
                
                # Collect ratings
                if fb.rating:
                    ratings.append(fb.rating)
            
            avg_rating = sum(ratings) / len(ratings) if ratings else None
            
            # Recent feedback (last 7 days)
            from datetime import timedelta
            recent_cutoff = datetime.utcnow() - timedelta(days=7)
            recent_count = len([fb for fb in feedbacks if fb.created_at >= recent_cutoff])
            
            return FeedbackStats(
                total_feedback=total,
                by_type=by_type,
                by_task=by_task,
                avg_rating=avg_rating,
                recent_feedback_count=recent_count
            )
        
        @self.router.get("/export-dpo")
        async def export_dpo_dataset(
            brand_id: Optional[str] = None,
            task_type: Optional[str] = None,
            min_examples: int = 100,
            db: Session = Depends(get_db_session)
        ):
            """
            Export DPO dataset from preference pairs.
            
            Args:
                brand_id: Optional brand filter
                task_type: Optional task type filter
                min_examples: Minimum examples required
                db: Database session
            
            Returns:
                DPO dataset
            """
            query = db.query(Feedback).filter(
                Feedback.feedback_type == FeedbackType.PREFERENCE
            )
            
            # Apply filters
            if brand_id:
                brand = db.query(Brand).filter(Brand.brand_id == brand_id).first()
                if brand:
                    query = query.filter(Feedback.brand_id == brand.id)
            
            if task_type:
                query = query.filter(Feedback.task_type == task_type)
            
            feedbacks = query.all()
            
            if len(feedbacks) < min_examples:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient examples: {len(feedbacks)} < {min_examples}"
                )
            
            # Format as DPO dataset
            dataset = []
            for fb in feedbacks:
                dataset.append({
                    "prompt": fb.prompt,
                    "chosen": fb.preferred_output,
                    "rejected": fb.rejected_output,
                    "task_type": fb.task_type,
                    "metadata": fb.metadata
                })
            
            logger.info(f"Exported DPO dataset: {len(dataset)} examples")
            
            return {
                "count": len(dataset),
                "examples": dataset
            }
    
    def get_router(self) -> APIRouter:
        """Get FastAPI router."""
        return self.router
