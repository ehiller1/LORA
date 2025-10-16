"""Web UI for RLHF feedback collection."""

import logging
from pathlib import Path
from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from src.storage.database import get_db_session
from src.storage.models import Brand, Feedback, FeedbackType
from .feedback_api import FeedbackAPI

logger = logging.getLogger(__name__)


def create_rlhf_app() -> FastAPI:
    """
    Create RLHF feedback collection web app.
    
    Returns:
        FastAPI application
    """
    app = FastAPI(
        title="RMN RLHF Feedback",
        description="Reinforcement Learning from Human Feedback interface",
        version="1.0.0"
    )
    
    # Set up templates
    templates_dir = Path(__file__).parent / "templates"
    templates_dir.mkdir(exist_ok=True)
    templates = Jinja2Templates(directory=str(templates_dir))
    
    # Include feedback API
    feedback_api = FeedbackAPI()
    app.include_router(feedback_api.get_router())
    
    # Home page
    @app.get("/", response_class=HTMLResponse)
    async def home(request: Request, db: Session = Depends(get_db_session)):
        """Home page with brand selection."""
        brands = db.query(Brand).filter(Brand.is_active == True).all()
        return templates.TemplateResponse(
            "home.html",
            {"request": request, "brands": brands}
        )
    
    # Feedback interface
    @app.get("/feedback/{brand_id}", response_class=HTMLResponse)
    async def feedback_interface(
        request: Request,
        brand_id: str,
        task_type: str = "budgeting",
        db: Session = Depends(get_db_session)
    ):
        """Feedback collection interface."""
        brand = db.query(Brand).filter(Brand.brand_id == brand_id).first()
        if not brand:
            return HTMLResponse(content="Brand not found", status_code=404)
        
        # Get sample prompts for the task type
        sample_prompts = get_sample_prompts(task_type)
        
        return templates.TemplateResponse(
            "feedback.html",
            {
                "request": request,
                "brand": brand,
                "task_type": task_type,
                "sample_prompts": sample_prompts
            }
        )
    
    # Submit thumbs up/down feedback
    @app.post("/submit-simple-feedback")
    async def submit_simple_feedback(
        brand_id: str = Form(...),
        user_id: str = Form(...),
        task_type: str = Form(...),
        prompt: str = Form(...),
        model_output: str = Form(...),
        feedback_type: str = Form(...),
        db: Session = Depends(get_db_session)
    ):
        """Submit simple thumbs up/down feedback."""
        brand = db.query(Brand).filter(Brand.brand_id == brand_id).first()
        if not brand:
            return HTMLResponse(content="Brand not found", status_code=404)
        
        # Create feedback
        feedback = Feedback(
            brand_id=brand.id,
            user_id=user_id,
            task_type=task_type,
            prompt=prompt,
            model_output=model_output,
            feedback_type=FeedbackType(feedback_type)
        )
        
        db.add(feedback)
        db.commit()
        
        logger.info(f"Simple feedback submitted: {feedback_type} for {task_type}")
        
        return RedirectResponse(
            url=f"/feedback/{brand_id}?task_type={task_type}&success=true",
            status_code=303
        )
    
    # Submit preference pair
    @app.post("/submit-preference")
    async def submit_preference(
        brand_id: str = Form(...),
        user_id: str = Form(...),
        task_type: str = Form(...),
        prompt: str = Form(...),
        output_a: str = Form(...),
        output_b: str = Form(...),
        preferred: str = Form(...),
        db: Session = Depends(get_db_session)
    ):
        """Submit preference between two outputs."""
        brand = db.query(Brand).filter(Brand.brand_id == brand_id).first()
        if not brand:
            return HTMLResponse(content="Brand not found", status_code=404)
        
        # Determine chosen and rejected
        chosen = output_a if preferred == "a" else output_b
        rejected = output_b if preferred == "a" else output_a
        
        # Create feedback
        feedback = Feedback(
            brand_id=brand.id,
            user_id=user_id,
            task_type=task_type,
            prompt=prompt,
            model_output=chosen,
            feedback_type=FeedbackType.PREFERENCE,
            preferred_output=chosen,
            rejected_output=rejected
        )
        
        db.add(feedback)
        db.commit()
        
        logger.info(f"Preference submitted for {task_type}")
        
        return RedirectResponse(
            url=f"/feedback/{brand_id}?task_type={task_type}&success=true",
            status_code=303
        )
    
    # Submit rating
    @app.post("/submit-rating")
    async def submit_rating(
        brand_id: str = Form(...),
        user_id: str = Form(...),
        task_type: str = Form(...),
        prompt: str = Form(...),
        model_output: str = Form(...),
        rating: int = Form(...),
        db: Session = Depends(get_db_session)
    ):
        """Submit rating feedback."""
        brand = db.query(Brand).filter(Brand.brand_id == brand_id).first()
        if not brand:
            return HTMLResponse(content="Brand not found", status_code=404)
        
        # Create feedback
        feedback = Feedback(
            brand_id=brand.id,
            user_id=user_id,
            task_type=task_type,
            prompt=prompt,
            model_output=model_output,
            feedback_type=FeedbackType.RATING,
            rating=rating
        )
        
        db.add(feedback)
        db.commit()
        
        logger.info(f"Rating submitted: {rating}/5 for {task_type}")
        
        return RedirectResponse(
            url=f"/feedback/{brand_id}?task_type={task_type}&success=true",
            status_code=303
        )
    
    # Statistics dashboard
    @app.get("/dashboard", response_class=HTMLResponse)
    async def dashboard(
        request: Request,
        brand_id: str = None,
        db: Session = Depends(get_db_session)
    ):
        """Feedback statistics dashboard."""
        query = db.query(Feedback)
        
        if brand_id:
            brand = db.query(Brand).filter(Brand.brand_id == brand_id).first()
            if brand:
                query = query.filter(Feedback.brand_id == brand.id)
        
        feedbacks = query.all()
        
        # Calculate stats
        total = len(feedbacks)
        by_type = {}
        by_task = {}
        
        for fb in feedbacks:
            by_type[fb.feedback_type.value] = by_type.get(fb.feedback_type.value, 0) + 1
            by_task[fb.task_type] = by_task.get(fb.task_type, 0) + 1
        
        brands = db.query(Brand).filter(Brand.is_active == True).all()
        
        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "total_feedback": total,
                "by_type": by_type,
                "by_task": by_task,
                "brands": brands,
                "selected_brand": brand_id
            }
        )
    
    return app


def get_sample_prompts(task_type: str) -> list:
    """
    Get sample prompts for a task type.
    
    Args:
        task_type: Type of task
    
    Returns:
        List of sample prompts
    """
    prompts = {
        "budgeting": [
            "Allocate $100,000 across Amazon, Walmart, and Target for Q4 holiday campaign",
            "Optimize budget for new product launch with $50k budget and 3.0x ROAS target",
            "Reallocate budget from underperforming placements to high-ROAS segments"
        ],
        "creative": [
            "Generate 5 headline variants for organic snack promotion on Walmart",
            "Create compliant copy for Amazon Sponsored Product ad (80 char limit)",
            "Write product description emphasizing sustainability for Target audience"
        ],
        "measurement": [
            "Design geo experiment to measure lift for new beverage launch",
            "Calculate required sample size for switchback test with 10% MDE",
            "Analyze experiment results and estimate incremental ROAS"
        ],
        "planning": [
            "Create media plan for Q1 with $200k budget across 3 RMNs",
            "Recommend placement mix for awareness campaign targeting millennials",
            "Optimize campaign structure for maximum incrementality"
        ]
    }
    
    return prompts.get(task_type, [])


if __name__ == "__main__":
    import uvicorn
    
    # Initialize database
    from src.storage.database import init_db
    init_db("sqlite:///rlhf_feedback.db")
    
    # Create and run app
    app = create_rlhf_app()
    uvicorn.run(app, host="0.0.0.0", port=8001)
