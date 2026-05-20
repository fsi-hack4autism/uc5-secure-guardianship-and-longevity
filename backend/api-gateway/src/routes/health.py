"""
Health check endpoints
"""
from fastapi import APIRouter, Depends
from datetime import datetime
from sqlalchemy.orm import Session

from database import get_db

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "api-gateway",
    }


@router.get("/ready")
async def readiness_check(db: Session = Depends(get_db)):
    """Readiness check - tests database connection"""
    try:
        # Simple query to test database connection
        result = db.execute("SELECT 1")
        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat(),
            "database": "connected",
        }
    except Exception as e:
        return {
            "status": "not_ready",
            "timestamp": datetime.utcnow().isoformat(),
            "database": "disconnected",
            "error": str(e),
        }, 503
