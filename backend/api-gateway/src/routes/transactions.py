"""
Transaction routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid
import logging

from database import get_db
from models import Transaction, User, AuditLog
from routes.auth import get_current_user
from config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


class TransactionRequest(BaseModel):
    """Transaction request"""
    amount: float
    merchant_name: str
    merchant_category: str
    device_id: Optional[str] = None
    location_lat: Optional[float] = None
    location_lon: Optional[float] = None


class TransactionResponse(BaseModel):
    """Transaction response"""
    transaction_id: str
    user_id: str
    amount: float
    merchant_name: str
    merchant_category: str
    status: str
    risk_score: Optional[float]
    risk_level: Optional[str]
    requires_guardian_approval: bool
    fraud_flag: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.post("/", response_model=TransactionResponse)
async def create_transaction(
    request: TransactionRequest,
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new transaction"""
    
    user = db.query(User).filter(User.user_id == uuid.UUID(current_user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Validate amount
    if request.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Amount must be positive"
        )
    
    # Create transaction
    transaction = Transaction(
        user_id=user.user_id,
        amount=request.amount,
        merchant_name=request.merchant_name,
        merchant_category=request.merchant_category,
        device_id=request.device_id,
        location_lat=request.location_lat,
        location_lon=request.location_lon,
        status="pending",
        risk_score=None,
        requires_guardian_approval=False,
        fraud_flag=False,
    )
    
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    
    # TODO: Call fraud detection service
    # TODO: Update risk_score, risk_level, requires_guardian_approval
    
    logger.info(f"Transaction created: {transaction.transaction_id}")
    
    # Log audit trail
    audit_log = AuditLog(
        user_id=user.user_id,
        action="CREATE",
        entity_type="transaction",
        entity_id=str(transaction.transaction_id),
        new_values={
            "amount": transaction.amount,
            "merchant": transaction.merchant_name,
            "status": transaction.status,
        }
    )
    db.add(audit_log)
    db.commit()
    
    return TransactionResponse(
        transaction_id=str(transaction.transaction_id),
        user_id=str(transaction.user_id),
        amount=transaction.amount,
        merchant_name=transaction.merchant_name,
        merchant_category=transaction.merchant_category,
        status=transaction.status,
        risk_score=transaction.risk_score,
        risk_level=transaction.risk_level,
        requires_guardian_approval=transaction.requires_guardian_approval,
        fraud_flag=transaction.fraud_flag,
        created_at=transaction.created_at,
    )


@router.get("/", response_model=List[TransactionResponse])
async def list_transactions(
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 50,
):
    """List user's transactions"""
    
    transactions = db.query(Transaction).filter(
        Transaction.user_id == uuid.UUID(current_user_id)
    ).order_by(
        Transaction.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return [
        TransactionResponse(
            transaction_id=str(t.transaction_id),
            user_id=str(t.user_id),
            amount=t.amount,
            merchant_name=t.merchant_name,
            merchant_category=t.merchant_category,
            status=t.status,
            risk_score=t.risk_score,
            risk_level=t.risk_level,
            requires_guardian_approval=t.requires_guardian_approval,
            fraud_flag=t.fraud_flag,
            created_at=t.created_at,
        )
        for t in transactions
    ]


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: str,
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get transaction details"""
    
    transaction = db.query(Transaction).filter(
        Transaction.transaction_id == uuid.UUID(transaction_id)
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Check authorization
    if str(transaction.user_id) != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this transaction")
    
    return TransactionResponse(
        transaction_id=str(transaction.transaction_id),
        user_id=str(transaction.user_id),
        amount=transaction.amount,
        merchant_name=transaction.merchant_name,
        merchant_category=transaction.merchant_category,
        status=transaction.status,
        risk_score=transaction.risk_score,
        risk_level=transaction.risk_level,
        requires_guardian_approval=transaction.requires_guardian_approval,
        fraud_flag=transaction.fraud_flag,
        created_at=transaction.created_at,
    )


@router.post("/{transaction_id}/approve")
async def approve_transaction(
    transaction_id: str,
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Guardian approves transaction"""
    
    transaction = db.query(Transaction).filter(
        Transaction.transaction_id == uuid.UUID(transaction_id)
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # TODO: Check if user is authorized guardian
    
    transaction.status = "approved"
    transaction.guardian_approved_by = uuid.UUID(current_user_id)
    transaction.guardian_approved_at = datetime.utcnow()
    
    db.commit()
    db.refresh(transaction)
    
    logger.info(f"Transaction approved: {transaction.transaction_id}")
    
    return {"status": "approved", "transaction_id": str(transaction.transaction_id)}


@router.post("/{transaction_id}/reject")
async def reject_transaction(
    transaction_id: str,
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Guardian rejects transaction"""
    
    transaction = db.query(Transaction).filter(
        Transaction.transaction_id == uuid.UUID(transaction_id)
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # TODO: Check if user is authorized guardian
    
    transaction.status = "rejected"
    transaction.guardian_approved_by = uuid.UUID(current_user_id)
    transaction.guardian_approved_at = datetime.utcnow()
    
    db.commit()
    db.refresh(transaction)
    
    logger.info(f"Transaction rejected: {transaction.transaction_id}")
    
    return {"status": "rejected", "transaction_id": str(transaction.transaction_id)}
