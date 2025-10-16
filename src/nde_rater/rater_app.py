"""NDE Rater Web Application - Rater IDE."""

import logging
from pathlib import Path
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.storage.database import get_db_session
from .models import (
    RatingTask, Judgment, RaterProfile, GoldenSetItem,
    RatingTaskType, TaskStatus, JudgmentChoice
)
from .rubrics import get_rubric
from .auto_checks import run_auto_checks_for_task

logger = logging.getLogger(__name__)


def create_rater_app() -> FastAPI:
    """
    Create NDE Rater IDE application.
    
    Returns:
        FastAPI application
    """
    app = FastAPI(
        title="RMN NDE Rater IDE",
        description="Non-Domain Expert Rating Interface for RLHF",
        version="1.0.0"
    )
    
    # Set up templates
    templates_dir = Path(__file__).parent / "templates"
    templates_dir.mkdir(exist_ok=True)
    templates = Jinja2Templates(directory=str(templates_dir))
    
    @app.get("/", response_class=HTMLResponse)
    async def home(request: Request, db: Session = Depends(get_db_session)):
        """Rater home page."""
        # Get stats
        total_tasks = db.query(RatingTask).count()
        pending_tasks = db.query(RatingTask).filter(
            RatingTask.status == TaskStatus.PENDING
        ).count()
        completed_tasks = db.query(RatingTask).filter(
            RatingTask.status == TaskStatus.COMPLETED
        ).count()
        
        return templates.TemplateResponse(
            "rater_home.html",
            {
                "request": request,
                "total_tasks": total_tasks,
                "pending_tasks": pending_tasks,
                "completed_tasks": completed_tasks
            }
        )
    
    @app.get("/calibration/{rater_id}", response_class=HTMLResponse)
    async def calibration(
        request: Request,
        rater_id: str,
        db: Session = Depends(get_db_session)
    ):
        """Calibration tasks for new raters."""
        # Get or create rater profile
        rater = db.query(RaterProfile).filter(
            RaterProfile.rater_id == rater_id
        ).first()
        
        if not rater:
            rater = RaterProfile(
                rater_id=rater_id,
                name=rater_id,
                is_calibrated=False
            )
            db.add(rater)
            db.commit()
        
        # Get golden set tasks for calibration
        golden_tasks = db.query(RatingTask).join(GoldenSetItem).filter(
            RatingTask.is_golden == True,
            RatingTask.status.in_([TaskStatus.PENDING, TaskStatus.IN_PROGRESS])
        ).limit(10).all()
        
        if not golden_tasks:
            return HTMLResponse(content="No calibration tasks available", status_code=404)
        
        # Get first uncompleted golden task
        for task in golden_tasks:
            existing_judgment = db.query(Judgment).filter(
                Judgment.task_id == task.id,
                Judgment.rater_id == rater.id
            ).first()
            
            if not existing_judgment:
                # Mark task as in progress
                task.status = TaskStatus.IN_PROGRESS
                task.assigned_at = datetime.utcnow()
                db.commit()
                
                return RedirectResponse(url=f"/rate/{task.task_id}?rater_id={rater_id}")
        
        # All calibration tasks completed
        return HTMLResponse(content="Calibration complete! Calculating accuracy...")
    
    @app.get("/rate/{task_id}", response_class=HTMLResponse)
    async def rate_task(
        request: Request,
        task_id: str,
        rater_id: str,
        db: Session = Depends(get_db_session)
    ):
        """Rate a specific task - Rater IDE."""
        # Get task
        task = db.query(RatingTask).filter(
            RatingTask.task_id == task_id
        ).first()
        
        if not task:
            return HTMLResponse(content="Task not found", status_code=404)
        
        # Get rater
        rater = db.query(RaterProfile).filter(
            RaterProfile.rater_id == rater_id
        ).first()
        
        if not rater:
            return RedirectResponse(url=f"/calibration/{rater_id}")
        
        # Check if already rated
        existing_judgment = db.query(Judgment).filter(
            Judgment.task_id == task.id,
            Judgment.rater_id == rater.id
        ).first()
        
        if existing_judgment:
            return HTMLResponse(content="Task already rated", status_code=400)
        
        # Get rubric
        rubric = get_rubric(task.task_type.value)
        
        # Run auto-checks
        auto_checks = run_auto_checks_for_task(
            task.task_type.value,
            task.candidate_a,
            task.candidate_b,
            task.context_snippets
        )
        
        return templates.TemplateResponse(
            "rater_ide.html",
            {
                "request": request,
                "task": task,
                "rater": rater,
                "rubric": rubric,
                "auto_checks": auto_checks,
                "task_type_label": task.task_type.value.replace("_", " ").title()
            }
        )
    
    @app.post("/submit-judgment")
    async def submit_judgment(
        task_id: str = Form(...),
        rater_id: str = Form(...),
        choice: str = Form(...),
        reasons: str = Form("[]"),
        free_text: str = Form(""),
        confidence: float = Form(...),
        time_spent: float = Form(...),
        escalate: bool = Form(False),
        escalation_reason: str = Form(""),
        rubric_scores: str = Form("{}"),
        db: Session = Depends(get_db_session)
    ):
        """Submit a judgment."""
        import json
        
        # Get task and rater
        task = db.query(RatingTask).filter(RatingTask.task_id == task_id).first()
        rater = db.query(RaterProfile).filter(RaterProfile.rater_id == rater_id).first()
        
        if not task or not rater:
            raise HTTPException(status_code=404, detail="Task or rater not found")
        
        # Parse JSON fields
        reasons_list = json.loads(reasons)
        rubric_scores_dict = json.loads(rubric_scores)
        
        # Create judgment
        judgment = Judgment(
            judgment_id=f"jdg_{task_id}_{rater_id}_{int(datetime.utcnow().timestamp())}",
            task_id=task.id,
            rater_id=rater.id,
            choice=JudgmentChoice(choice),
            reasons=reasons_list,
            free_text_feedback=free_text,
            confidence=confidence,
            time_spent_seconds=time_spent,
            is_escalated=escalate,
            escalation_reason=escalation_reason if escalate else None,
            rubric_scores=rubric_scores_dict
        )
        
        # Check against golden set
        if task.is_golden:
            judgment.matches_golden = (judgment.choice == task.golden_choice)
        
        db.add(judgment)
        
        # Update task status
        if escalate:
            task.status = TaskStatus.ESCALATED
        else:
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
        
        # Update rater stats
        rater.total_judgments += 1
        rater.avg_confidence = (
            (rater.avg_confidence * (rater.total_judgments - 1) + confidence) /
            rater.total_judgments
        )
        rater.avg_time_per_task_seconds = (
            (rater.avg_time_per_task_seconds * (rater.total_judgments - 1) + time_spent) /
            rater.total_judgments
        )
        
        # Update golden set accuracy
        if task.is_golden:
            golden_judgments = db.query(Judgment).join(RatingTask).filter(
                Judgment.rater_id == rater.id,
                RatingTask.is_golden == True,
                Judgment.matches_golden.isnot(None)
            ).all()
            
            if golden_judgments:
                correct = sum(1 for j in golden_judgments if j.matches_golden)
                rater.golden_set_accuracy = correct / len(golden_judgments)
        
        db.commit()
        
        logger.info(f"Judgment submitted: {judgment.judgment_id}")
        
        # Get next task
        next_task = db.query(RatingTask).filter(
            RatingTask.status == TaskStatus.PENDING
        ).order_by(RatingTask.priority.desc()).first()
        
        if next_task:
            return RedirectResponse(
                url=f"/rate/{next_task.task_id}?rater_id={rater_id}&success=true",
                status_code=303
            )
        else:
            return RedirectResponse(
                url=f"/complete?rater_id={rater_id}",
                status_code=303
            )
    
    @app.get("/next-task", response_class=JSONResponse)
    async def get_next_task(
        rater_id: str,
        db: Session = Depends(get_db_session)
    ):
        """Get next task for rater (API endpoint)."""
        # Get rater
        rater = db.query(RaterProfile).filter(
            RaterProfile.rater_id == rater_id
        ).first()
        
        if not rater:
            raise HTTPException(status_code=404, detail="Rater not found")
        
        # Get next task (prioritize by uncertainty score and priority)
        next_task = db.query(RatingTask).filter(
            RatingTask.status == TaskStatus.PENDING
        ).order_by(
            RatingTask.priority.desc(),
            RatingTask.uncertainty_score.desc().nullslast()
        ).first()
        
        if not next_task:
            return {"task_id": None, "message": "No tasks available"}
        
        return {
            "task_id": next_task.task_id,
            "task_type": next_task.task_type.value,
            "retailer_id": next_task.retailer_id
        }
    
    @app.get("/stats/{rater_id}", response_class=HTMLResponse)
    async def rater_stats(
        request: Request,
        rater_id: str,
        db: Session = Depends(get_db_session)
    ):
        """Rater statistics page."""
        rater = db.query(RaterProfile).filter(
            RaterProfile.rater_id == rater_id
        ).first()
        
        if not rater:
            return HTMLResponse(content="Rater not found", status_code=404)
        
        # Get judgment stats
        judgments = db.query(Judgment).filter(
            Judgment.rater_id == rater.id
        ).all()
        
        # Calculate stats
        by_choice = {}
        by_task_type = {}
        escalation_rate = 0
        
        for judgment in judgments:
            # By choice
            choice = judgment.choice.value
            by_choice[choice] = by_choice.get(choice, 0) + 1
            
            # By task type
            task_type = judgment.task.task_type.value
            by_task_type[task_type] = by_task_type.get(task_type, 0) + 1
            
            # Escalation rate
            if judgment.is_escalated:
                escalation_rate += 1
        
        escalation_rate = (escalation_rate / len(judgments) * 100) if judgments else 0
        
        return templates.TemplateResponse(
            "rater_stats.html",
            {
                "request": request,
                "rater": rater,
                "by_choice": by_choice,
                "by_task_type": by_task_type,
                "escalation_rate": escalation_rate
            }
        )
    
    @app.get("/complete", response_class=HTMLResponse)
    async def complete(
        request: Request,
        rater_id: str,
        db: Session = Depends(get_db_session)
    ):
        """Completion page."""
        rater = db.query(RaterProfile).filter(
            RaterProfile.rater_id == rater_id
        ).first()
        
        return templates.TemplateResponse(
            "complete.html",
            {
                "request": request,
                "rater": rater
            }
        )
    
    return app


if __name__ == "__main__":
    import uvicorn
    
    # Initialize database
    from src.storage.database import init_db
    init_db("sqlite:///nde_rater.db")
    
    # Create and run app
    app = create_rater_app()
    uvicorn.run(app, host="0.0.0.0", port=8002)
