"""
SQLAlchemy models for the database
"""
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Float, JSON, UUID, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from database import Base


class User(Base):
    """User model - represents beneficiary, guardian, or advisor"""
    __tablename__ = "users"
    
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    user_type = Column(String(20), nullable=False)  # 'beneficiary', 'guardian', 'advisor'
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    transactions = relationship("Transaction", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")


class UserProfile(Base):
    """User profile - additional user information"""
    __tablename__ = "user_profiles"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), primary_key=True)
    full_name = Column(String(255), nullable=True)
    date_of_birth = Column(DateTime, nullable=True)
    profile_type = Column(String(50), nullable=True)
    diagnosed_conditions = Column(JSON, nullable=True)  # ['autism', 'adhd', etc.]
    accessibility_needs = Column(JSON, nullable=True)  # ['text_to_speech', 'high_contrast', etc.]
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="profile")


class Transaction(Base):
    """Transaction model - financial transactions"""
    __tablename__ = "transactions"
    
    transaction_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    merchant_id = Column(String(255), nullable=True)
    merchant_name = Column(String(255), nullable=True)
    merchant_category = Column(String(50), nullable=True)
    status = Column(String(20), nullable=False)  # 'pending', 'approved', 'rejected', 'processed'
    risk_score = Column(Float, nullable=True)  # 0-100
    risk_level = Column(String(20), nullable=True)  # 'low', 'medium', 'high', 'critical'
    requires_guardian_approval = Column(Boolean, default=False)
    guardian_approved_by = Column(UUID(as_uuid=True), nullable=True)
    guardian_approved_at = Column(DateTime, nullable=True)
    fraud_flag = Column(Boolean, default=False)
    user_confirmed = Column(Boolean, default=False)
    device_id = Column(String(255), nullable=True)
    location_lat = Column(Float, nullable=True)
    location_lon = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="transactions")


class AuditLog(Base):
    """Audit log - immutable record of all actions"""
    __tablename__ = "audit_logs"
    
    audit_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=True)
    action = Column(String(50), nullable=False)
    entity_type = Column(String(50), nullable=False)  # 'transaction', 'user', 'guardian', etc.
    entity_id = Column(String(255), nullable=False)
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    user_ip = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")


class GuardianRelationship(Base):
    """Guardian relationships - links guardians to beneficiaries"""
    __tablename__ = "guardian_relationships"
    
    relationship_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    beneficiary_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False, index=True)
    guardian_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False, index=True)
    relationship_type = Column(String(50), nullable=False)  # 'primary', 'secondary', 'institutional'
    approval_authority = Column(Boolean, default=False)  # Can approve transactions
    is_active = Column(Boolean, default=True)
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class FraudAlert(Base):
    """Fraud alerts - tracks detected fraud and alerts"""
    __tablename__ = "fraud_alerts"
    
    alert_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False, index=True)
    alert_type = Column(String(50), nullable=False)  # 'fraud', 'anomaly', 'exploitation'
    severity = Column(String(20), nullable=False)  # 'low', 'medium', 'high', 'critical'
    description = Column(String(500), nullable=False)
    transaction_id = Column(UUID(as_uuid=True), nullable=True)
    action_taken = Column(String(50), nullable=True)  # 'blocked', 'alerted', 'escalated'
    resolved = Column(Boolean, default=False)
    resolved_by = Column(UUID(as_uuid=True), nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
