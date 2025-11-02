"""Insights router."""

from fastapi import APIRouter
import sys
from pathlib import Path

# Add parent directory to import recommendation engine
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

router = APIRouter()


@router.get("/")
async def list_insights():
    """List all insights."""
    return {"message": "Insights list - to be implemented"}


@router.get("/recommendations")
async def get_recommendations():
    """Get smart recommendations for all sessions."""
    try:
        from llm_session_manager.services.recommendation_engine import RecommendationEngine
        from llm_session_manager.storage.database import Database
        from llm_session_manager.core.health_monitor import HealthMonitor
        
        db = Database()
        health_monitor = HealthMonitor(db)
        engine = RecommendationEngine(db, health_monitor)
        
        # Get all sessions
        sessions = db.get_all_sessions()
        
        # Get recommendations for each session
        all_recommendations = []
        for session in sessions:
            recommendations = engine.analyze_session(session)
            for rec in recommendations:
                all_recommendations.append({
                    "session_id": session.id,
                    "type": rec.type.value,
                    "priority": rec.priority.value,
                    "title": rec.title,
                    "description": rec.description,
                    "action": rec.action
                })
        
        return {
            "recommendations": all_recommendations,
            "count": len(all_recommendations)
        }
    except Exception as e:
        return {
            "recommendations": [],
            "count": 0,
            "error": str(e)
        }
