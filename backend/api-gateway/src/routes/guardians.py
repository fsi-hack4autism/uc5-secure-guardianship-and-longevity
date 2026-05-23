"""
Guardian management routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

from database import get_db
from models import GuardianRelationship, User
from routes.auth import get_current_user

router = APIRouter()


class GuardianRelationshipResponse(BaseModel):
    """Guardian relationship response"""
    relationship_id: str
    beneficiary_id: str
    guardian_id: str
    relationship_type: str
    approval_authority: bool
    is_active: bool
    
    class Config:
        from_attributes = True


class CreateGuardianRequest(BaseModel):
    """Create guardian relationship request"""
    beneficiary_id: str
    guardian_id: str
    relationship_type: str  # 'primary', 'secondary', 'institutional'
    approval_authority: bool = False


@router.post("/", response_model=GuardianRelationshipResponse)
async def create_guardian_relationship(
    request: CreateGuardianRequest,
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create guardian relationship (admin/advisor only)"""
    
    # Verify both users exist
    beneficiary = db.query(User).filter(
        User.user_id == uuid.UUID(request.beneficiary_id)
    ).first()
    if not beneficiary:
        raise HTTPException(status_code=404, detail="Beneficiary not found")
    
    guardian = db.query(User).filter(
        User.user_id == uuid.UUID(request.guardian_id)
    ).first()
    if not guardian:
        raise HTTPException(status_code=404, detail="Guardian not found")
    
    # Verify guardian is actually a guardian
    if guardian.user_type != "guardian":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not a guardian"
        )
    
    # Create relationship
    relationship = GuardianRelationship(
        beneficiary_id=uuid.UUID(request.beneficiary_id),
        guardian_id=uuid.UUID(request.guardian_id),
        relationship_type=request.relationship_type,
        approval_authority=request.approval_authority,
        is_active=True,
    )
    
    db.add(relationship)
    db.commit()
    db.refresh(relationship)
    
    return GuardianRelationshipResponse(
        relationship_id=str(relationship.relationship_id),
        beneficiary_id=str(relationship.beneficiary_id),
        guardian_id=str(relationship.guardian_id),
        relationship_type=relationship.relationship_type,
        approval_authority=relationship.approval_authority,
        is_active=relationship.is_active,
    )


@router.get("/beneficiary/{beneficiary_id}", response_model=List[GuardianRelationshipResponse])
async def get_beneficiary_guardians(
    beneficiary_id: str,
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get guardians for a beneficiary"""
    
    relationships = db.query(GuardianRelationship).filter(
        GuardianRelationship.beneficiary_id == uuid.UUID(beneficiary_id),
        GuardianRelationship.is_active == True,
    ).all()
    
    return [
        GuardianRelationshipResponse(
            relationship_id=str(r.relationship_id),
            beneficiary_id=str(r.beneficiary_id),
            guardian_id=str(r.guardian_id),
            relationship_type=r.relationship_type,
            approval_authority=r.approval_authority,
            is_active=r.is_active,
        )
        for r in relationships
    ]


@router.get("/guardian/{guardian_id}", response_model=List[GuardianRelationshipResponse])
async def get_guardian_beneficiaries(
    guardian_id: str,
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get beneficiaries for a guardian"""
    
    relationships = db.query(GuardianRelationship).filter(
        GuardianRelationship.guardian_id == uuid.UUID(guardian_id),
        GuardianRelationship.is_active == True,
    ).all()
    
    return [
        GuardianRelationshipResponse(
            relationship_id=str(r.relationship_id),
            beneficiary_id=str(r.beneficiary_id),
            guardian_id=str(r.guardian_id),
            relationship_type=r.relationship_type,
            approval_authority=r.approval_authority,
            is_active=r.is_active,
        )
        for r in relationships
    ]
