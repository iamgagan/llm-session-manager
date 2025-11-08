"""Analytics router."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import Optional
from datetime import datetime, timedelta

from ..database import get_db
from ..models import SessionModel, Team, User, TeamMetric, SessionHistory

router = APIRouter()


@router.get("/team")
async def team_analytics(
    team_id: Optional[str] = Query(None, description="Team ID to filter by"),
    db: Session = Depends(get_db)
):
    """Get comprehensive team analytics."""
    query = db.query(SessionModel)

    if team_id:
        # Team-specific analytics
        team = db.query(Team).filter(Team.id == team_id).first()
        if not team:
            return {"error": "Team not found"}

        query = query.filter(SessionModel.team_id == team_id)
        team_name = team.name
    else:
        # Global analytics across all teams
        team_name = "All Teams"

    sessions = query.all()

    if not sessions:
        return {
            "team_name": team_name,
            "total_sessions": 0,
            "message": "No sessions found"
        }

    # Calculate metrics
    total_sessions = len(sessions)
    active_sessions = sum(1 for s in sessions if s.status == "active")
    completed_sessions = sum(1 for s in sessions if s.status == "completed")
    failed_sessions = sum(1 for s in sessions if s.status == "failed")

    total_tokens = sum(s.token_count for s in sessions)
    avg_tokens = total_tokens / total_sessions if total_sessions > 0 else 0

    total_health = sum(s.health_score for s in sessions)
    avg_health = total_health / total_sessions if total_sessions > 0 else 0

    # Health distribution
    healthy = sum(1 for s in sessions if s.health_score >= 80)
    warning = sum(1 for s in sessions if 50 <= s.health_score < 80)
    critical = sum(1 for s in sessions if s.health_score < 50)

    # Session types
    session_types = {}
    for session in sessions:
        session_types[session.type] = session_types.get(session.type, 0) + 1

    # Top projects
    projects = {}
    for session in sessions:
        if session.project_name:
            if session.project_name not in projects:
                projects[session.project_name] = {
                    "session_count": 0,
                    "total_tokens": 0,
                    "avg_health": 0,
                    "health_sum": 0
                }
            projects[session.project_name]["session_count"] += 1
            projects[session.project_name]["total_tokens"] += session.token_count
            projects[session.project_name]["health_sum"] += session.health_score

    # Calculate average health for each project
    for project in projects.values():
        project["avg_health"] = round(
            project["health_sum"] / project["session_count"], 2
        )
        del project["health_sum"]

    # Sort projects by session count
    top_projects = sorted(
        [{"name": k, **v} for k, v in projects.items()],
        key=lambda x: x["session_count"],
        reverse=True
    )[:10]

    return {
        "team_name": team_name,
        "summary": {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "completed_sessions": completed_sessions,
            "failed_sessions": failed_sessions,
            "total_tokens": total_tokens,
            "average_tokens_per_session": round(avg_tokens, 2),
            "average_health_score": round(avg_health, 2)
        },
        "health_distribution": {
            "healthy": healthy,
            "warning": warning,
            "critical": critical,
            "percentages": {
                "healthy": round(healthy / total_sessions * 100, 1) if total_sessions > 0 else 0,
                "warning": round(warning / total_sessions * 100, 1) if total_sessions > 0 else 0,
                "critical": round(critical / total_sessions * 100, 1) if total_sessions > 0 else 0
            }
        },
        "session_types": session_types,
        "top_projects": top_projects
    }


@router.get("/trends")
async def analytics_trends(
    team_id: Optional[str] = Query(None),
    days: int = Query(7, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """Get usage trends over time."""
    cutoff_date = datetime.utcnow() - timedelta(days=days)

    query = db.query(SessionModel).filter(SessionModel.start_time >= cutoff_date)

    if team_id:
        query = query.filter(SessionModel.team_id == team_id)

    sessions = query.all()

    if not sessions:
        return {
            "period_days": days,
            "total_sessions": 0,
            "daily_breakdown": []
        }

    # Group by day
    daily_stats = {}
    for session in sessions:
        day = session.start_time.date().isoformat()

        if day not in daily_stats:
            daily_stats[day] = {
                "date": day,
                "session_count": 0,
                "total_tokens": 0,
                "avg_health": 0,
                "health_sum": 0,
                "active_count": 0,
                "completed_count": 0,
                "failed_count": 0
            }

        daily_stats[day]["session_count"] += 1
        daily_stats[day]["total_tokens"] += session.token_count
        daily_stats[day]["health_sum"] += session.health_score

        if session.status == "active":
            daily_stats[day]["active_count"] += 1
        elif session.status == "completed":
            daily_stats[day]["completed_count"] += 1
        elif session.status == "failed":
            daily_stats[day]["failed_count"] += 1

    # Calculate averages
    for stats in daily_stats.values():
        if stats["session_count"] > 0:
            stats["avg_health"] = round(stats["health_sum"] / stats["session_count"], 2)
        del stats["health_sum"]

    # Sort by date
    daily_breakdown = sorted(daily_stats.values(), key=lambda x: x["date"])

    # Calculate overall trend
    if len(daily_breakdown) >= 2:
        first_half = daily_breakdown[:len(daily_breakdown)//2]
        second_half = daily_breakdown[len(daily_breakdown)//2:]

        first_avg = sum(d["session_count"] for d in first_half) / len(first_half)
        second_avg = sum(d["session_count"] for d in second_half) / len(second_half)

        trend = "increasing" if second_avg > first_avg else "decreasing" if second_avg < first_avg else "stable"
        trend_percentage = round(((second_avg - first_avg) / first_avg * 100), 1) if first_avg > 0 else 0
    else:
        trend = "insufficient_data"
        trend_percentage = 0

    return {
        "period_days": days,
        "total_sessions": len(sessions),
        "trend": trend,
        "trend_percentage": trend_percentage,
        "daily_breakdown": daily_breakdown
    }


@router.get("/health-distribution")
async def health_distribution(
    team_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get detailed health score distribution."""
    query = db.query(SessionModel)

    if team_id:
        query = query.filter(SessionModel.team_id == team_id)

    sessions = query.all()

    if not sessions:
        return {"total_sessions": 0, "distribution": {}}

    # Define health buckets
    buckets = {
        "90-100": 0,
        "80-89": 0,
        "70-79": 0,
        "60-69": 0,
        "50-59": 0,
        "40-49": 0,
        "30-39": 0,
        "20-29": 0,
        "10-19": 0,
        "0-9": 0
    }

    for session in sessions:
        score = int(session.health_score)
        if score >= 90:
            buckets["90-100"] += 1
        elif score >= 80:
            buckets["80-89"] += 1
        elif score >= 70:
            buckets["70-79"] += 1
        elif score >= 60:
            buckets["60-69"] += 1
        elif score >= 50:
            buckets["50-59"] += 1
        elif score >= 40:
            buckets["40-49"] += 1
        elif score >= 30:
            buckets["30-39"] += 1
        elif score >= 20:
            buckets["20-29"] += 1
        elif score >= 10:
            buckets["10-19"] += 1
        else:
            buckets["0-9"] += 1

    total = len(sessions)

    # Add percentages
    distribution = {
        k: {
            "count": v,
            "percentage": round(v / total * 100, 1) if total > 0 else 0
        }
        for k, v in buckets.items()
    }

    return {
        "total_sessions": total,
        "distribution": distribution,
        "average_health": round(sum(s.health_score for s in sessions) / total, 2) if total > 0 else 0
    }


@router.get("/top-sessions")
async def top_sessions(
    team_id: Optional[str] = Query(None),
    metric: str = Query("health_score", description="Metric to rank by: health_score, token_count, duration"),
    limit: int = Query(10, description="Number of results"),
    db: Session = Depends(get_db)
):
    """Get top sessions ranked by various metrics."""
    query = db.query(SessionModel)

    if team_id:
        query = query.filter(SessionModel.team_id == team_id)

    # Order by requested metric
    if metric == "health_score":
        query = query.order_by(SessionModel.health_score.desc())
    elif metric == "token_count":
        query = query.order_by(SessionModel.token_count.desc())
    else:
        # Default to health score
        query = query.order_by(SessionModel.health_score.desc())

    sessions = query.limit(limit).all()

    return {
        "metric": metric,
        "sessions": [
            {
                "id": s.id,
                "type": s.type,
                "status": s.status,
                "health_score": s.health_score,
                "token_count": s.token_count,
                "project_name": s.project_name,
                "start_time": s.start_time.isoformat(),
                "duration_minutes": round(
                    (s.last_activity - s.start_time).total_seconds() / 60, 1
                ) if s.last_activity and s.start_time else 0
            }
            for s in sessions
        ],
        "count": len(sessions)
    }


@router.get("/token-usage")
async def token_usage_analytics(
    team_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get detailed token usage patterns."""
    query = db.query(SessionModel)

    if team_id:
        query = query.filter(SessionModel.team_id == team_id)

    sessions = query.all()

    if not sessions:
        return {"total_sessions": 0, "token_stats": {}}

    total_tokens = sum(s.token_count for s in sessions)
    avg_tokens = total_tokens / len(sessions)

    # Token usage distribution
    token_buckets = {
        "0-10k": 0,
        "10k-50k": 0,
        "50k-100k": 0,
        "100k-150k": 0,
        "150k-200k": 0,
        "200k+": 0
    }

    for session in sessions:
        tokens = session.token_count
        if tokens < 10000:
            token_buckets["0-10k"] += 1
        elif tokens < 50000:
            token_buckets["10k-50k"] += 1
        elif tokens < 100000:
            token_buckets["100k-150k"] += 1
        elif tokens < 150000:
            token_buckets["150k-200k"] += 1
        elif tokens < 200000:
            token_buckets["150k-200k"] += 1
        else:
            token_buckets["200k+"] += 1

    # Find sessions approaching limits
    approaching_limit = [
        {
            "id": s.id,
            "token_count": s.token_count,
            "token_limit": s.token_limit,
            "usage_percentage": round(s.token_count / s.token_limit * 100, 1) if s.token_limit > 0 else 0,
            "project_name": s.project_name
        }
        for s in sessions
        if s.token_limit > 0 and (s.token_count / s.token_limit) > 0.8
    ]

    approaching_limit.sort(key=lambda x: x["usage_percentage"], reverse=True)

    return {
        "total_sessions": len(sessions),
        "token_stats": {
            "total_tokens": total_tokens,
            "average_tokens": round(avg_tokens, 2),
            "max_tokens": max(s.token_count for s in sessions),
            "min_tokens": min(s.token_count for s in sessions)
        },
        "distribution": token_buckets,
        "sessions_approaching_limit": approaching_limit[:10]
    }


@router.get("/session-duration")
async def session_duration_analytics(
    team_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Analyze session duration patterns."""
    query = db.query(SessionModel)

    if team_id:
        query = query.filter(SessionModel.team_id == team_id)

    sessions = query.filter(
        and_(
            SessionModel.start_time.isnot(None),
            SessionModel.last_activity.isnot(None)
        )
    ).all()

    if not sessions:
        return {"total_sessions": 0, "duration_stats": {}}

    durations = []
    for session in sessions:
        duration_minutes = (session.last_activity - session.start_time).total_seconds() / 60
        durations.append({
            "session_id": session.id,
            "duration_minutes": round(duration_minutes, 1),
            "project_name": session.project_name,
            "status": session.status
        })

    duration_values = [d["duration_minutes"] for d in durations]

    return {
        "total_sessions": len(sessions),
        "duration_stats": {
            "average_minutes": round(sum(duration_values) / len(duration_values), 1),
            "max_minutes": round(max(duration_values), 1),
            "min_minutes": round(min(duration_values), 1),
            "median_minutes": round(sorted(duration_values)[len(duration_values)//2], 1)
        },
        "longest_sessions": sorted(durations, key=lambda x: x["duration_minutes"], reverse=True)[:10]
    }
