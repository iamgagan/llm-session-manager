"""Projects router."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..models import SessionModel

router = APIRouter()


@router.get("/")
async def list_projects(db: Session = Depends(get_db)):
    """List all projects with session counts."""
    projects = (
        db.query(
            SessionModel.project_name,
            func.count(SessionModel.id).label("session_count")
        )
        .filter(SessionModel.project_name.isnot(None))
        .filter(SessionModel.project_name != "")
        .group_by(SessionModel.project_name)
        .order_by(func.count(SessionModel.id).desc())
        .all()
    )
    
    return {
        "projects": [
            {
                "project_name": p.project_name,
                "session_count": p.session_count
            }
            for p in projects
        ]
    }

