"""Teams router."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from ..database import get_db
from ..models import Team, User, SessionModel

router = APIRouter()


# Pydantic models for request/response
class TeamCreate(BaseModel):
    name: str
    description: Optional[str] = None
    settings: Optional[dict] = None


class TeamUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    settings: Optional[dict] = None


class MemberAdd(BaseModel):
    email: str
    username: str
    role: str = "member"  # admin, member, viewer


@router.get("/")
async def list_teams(db: Session = Depends(get_db)):
    """List all teams with member counts and session stats."""
    teams = db.query(Team).all()

    result = []
    for team in teams:
        # Get member count
        member_count = db.query(func.count(User.id)).filter(User.team_id == team.id).scalar()

        # Get session count
        session_count = db.query(func.count(SessionModel.id)).filter(
            SessionModel.team_id == team.id
        ).scalar()

        # Get active sessions
        active_count = db.query(func.count(SessionModel.id)).filter(
            SessionModel.team_id == team.id,
            SessionModel.status == "active"
        ).scalar()

        result.append({
            "id": team.id,
            "name": team.name,
            "description": team.description,
            "member_count": member_count,
            "session_count": session_count,
            "active_sessions": active_count,
            "created_at": team.created_at.isoformat()
        })

    return {"teams": result, "count": len(result)}


@router.post("/")
async def create_team(team_data: TeamCreate, db: Session = Depends(get_db)):
    """Create a new team."""
    # Check if team name already exists
    existing = db.query(Team).filter(Team.name == team_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Team name already exists")

    team = Team(
        name=team_data.name,
        description=team_data.description,
        settings=team_data.settings or {}
    )

    db.add(team)
    db.commit()
    db.refresh(team)

    return {
        "id": team.id,
        "name": team.name,
        "description": team.description,
        "created_at": team.created_at.isoformat(),
        "message": "Team created successfully"
    }


@router.get("/{team_id}")
async def get_team(team_id: str, db: Session = Depends(get_db)):
    """Get detailed information about a specific team."""
    team = db.query(Team).filter(Team.id == team_id).first()

    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    # Get members
    members = db.query(User).filter(User.team_id == team_id).all()

    # Get sessions
    sessions = db.query(SessionModel).filter(SessionModel.team_id == team_id).all()

    # Calculate stats
    total_tokens = sum(s.token_count for s in sessions)
    avg_health = sum(s.health_score for s in sessions) / len(sessions) if sessions else 0

    return {
        "id": team.id,
        "name": team.name,
        "description": team.description,
        "settings": team.settings,
        "created_at": team.created_at.isoformat(),
        "members": [
            {
                "id": m.id,
                "email": m.email,
                "username": m.username,
                "role": m.role,
                "is_active": m.is_active,
                "created_at": m.created_at.isoformat()
            }
            for m in members
        ],
        "stats": {
            "member_count": len(members),
            "total_sessions": len(sessions),
            "active_sessions": sum(1 for s in sessions if s.status == "active"),
            "total_tokens": total_tokens,
            "average_health": round(avg_health, 2)
        }
    }


@router.patch("/{team_id}")
async def update_team(team_id: str, team_data: TeamUpdate, db: Session = Depends(get_db)):
    """Update team information."""
    team = db.query(Team).filter(Team.id == team_id).first()

    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    if team_data.name is not None:
        # Check if new name conflicts
        existing = db.query(Team).filter(
            Team.name == team_data.name,
            Team.id != team_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Team name already exists")
        team.name = team_data.name

    if team_data.description is not None:
        team.description = team_data.description

    if team_data.settings is not None:
        team.settings = team_data.settings

    team.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(team)

    return {
        "id": team.id,
        "name": team.name,
        "description": team.description,
        "updated_at": team.updated_at.isoformat(),
        "message": "Team updated successfully"
    }


@router.delete("/{team_id}")
async def delete_team(team_id: str, db: Session = Depends(get_db)):
    """Delete a team."""
    team = db.query(Team).filter(Team.id == team_id).first()

    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    # Check if team has members
    member_count = db.query(func.count(User.id)).filter(User.team_id == team_id).scalar()
    if member_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete team with {member_count} members. Remove members first."
        )

    db.delete(team)
    db.commit()

    return {"message": "Team deleted successfully"}


@router.get("/{team_id}/members")
async def list_team_members(team_id: str, db: Session = Depends(get_db)):
    """List all members of a team."""
    team = db.query(Team).filter(Team.id == team_id).first()

    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    members = db.query(User).filter(User.team_id == team_id).all()

    return {
        "team_id": team_id,
        "team_name": team.name,
        "members": [
            {
                "id": m.id,
                "email": m.email,
                "username": m.username,
                "full_name": m.full_name,
                "role": m.role,
                "is_active": m.is_active,
                "last_login": m.last_login.isoformat() if m.last_login else None,
                "created_at": m.created_at.isoformat()
            }
            for m in members
        ],
        "count": len(members)
    }


@router.post("/{team_id}/members")
async def add_team_member(team_id: str, member_data: MemberAdd, db: Session = Depends(get_db)):
    """Add a member to a team."""
    team = db.query(Team).filter(Team.id == team_id).first()

    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    # Check if user already exists
    existing_user = db.query(User).filter(User.email == member_data.email).first()
    if existing_user:
        # Update their team
        if existing_user.team_id and existing_user.team_id != team_id:
            raise HTTPException(
                status_code=400,
                detail=f"User already belongs to team: {existing_user.team_id}"
            )
        existing_user.team_id = team_id
        existing_user.role = member_data.role
        db.commit()
        db.refresh(existing_user)
        return {
            "id": existing_user.id,
            "message": "User added to team",
            "email": existing_user.email
        }

    # Create new user (simplified - in production, would send invite)
    from ..auth import get_password_hash

    new_user = User(
        email=member_data.email,
        username=member_data.username,
        password_hash=get_password_hash("changeme123"),  # Temporary password
        team_id=team_id,
        role=member_data.role,
        is_active=True,
        is_verified=False
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "id": new_user.id,
        "email": new_user.email,
        "username": new_user.username,
        "role": new_user.role,
        "message": "Member added successfully. Temporary password: changeme123"
    }


@router.delete("/{team_id}/members/{user_id}")
async def remove_team_member(team_id: str, user_id: str, db: Session = Depends(get_db)):
    """Remove a member from a team."""
    team = db.query(Team).filter(Team.id == team_id).first()

    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    user = db.query(User).filter(User.id == user_id, User.team_id == team_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found in this team")

    # Remove user from team (don't delete user, just unassign)
    user.team_id = None
    user.role = "member"

    db.commit()

    return {"message": f"User {user.email} removed from team"}


@router.get("/{team_id}/sessions")
async def list_team_sessions(
    team_id: str,
    status: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """List all sessions for a team."""
    team = db.query(Team).filter(Team.id == team_id).first()

    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    query = db.query(SessionModel).filter(SessionModel.team_id == team_id)

    if status:
        query = query.filter(SessionModel.status == status)

    sessions = query.order_by(SessionModel.last_activity.desc()).limit(limit).all()

    return {
        "team_id": team_id,
        "team_name": team.name,
        "sessions": [
            {
                "id": s.id,
                "type": s.type,
                "status": s.status,
                "token_count": s.token_count,
                "health_score": s.health_score,
                "project_name": s.project_name,
                "start_time": s.start_time.isoformat(),
                "last_activity": s.last_activity.isoformat(),
                "visibility": s.visibility
            }
            for s in sessions
        ],
        "count": len(sessions)
    }
