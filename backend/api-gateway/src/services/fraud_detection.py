"""
Fraud Detection Service - Rule-based and ML-based fraud detection
Phase 1: Rule-based detection
Phase 2: ML models
"""
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class RiskLevel(str, Enum):
    """Risk level classification"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class FraudDetectionResult:
    """Fraud detection result"""
    risk_score: float  # 0-100
    risk_level: RiskLevel
    requires_guardian_approval: bool
    fraud_indicators: List[str]
    recommendation: str


class RuleBasedFraudDetector:
    """Rule-based fraud detection (Phase 1)"""
    
    def __init__(self):
        self.high_amount_threshold = 1000.0
        self.suspicious_categories = [
            "cash_advance",
            "gambling",
            "jewelry",
            "cryptocurrency",
            "money_transfer",
        ]
        self.time_window_hours = 24
        self.max_daily_transactions = 50
        
    def detect_fraud(
        self,
        amount: float,
        merchant_category: str,
        user_id: str,
        recent_transactions: List[Dict] = None,
        user_profile: Dict = None,
    ) -> FraudDetectionResult:
        """
        Detect fraud using rule-based approach
        
        Args:
            amount: Transaction amount
            merchant_category: Merchant category
            user_id: User ID
            recent_transactions: List of recent transactions
            user_profile: User profile data
            
        Returns:
            FraudDetectionResult with risk assessment
        """
        
        indicators: List[str] = []
        risk_score = 0.0
        
        # Rule 1: High amount transaction
        if amount > self.high_amount_threshold:
            indicators.append(f"High transaction amount (${amount})")
            risk_score += 15
        
        # Rule 2: Suspicious merchant category
        if merchant_category.lower() in self.suspicious_categories:
            indicators.append(f"Suspicious merchant category: {merchant_category}")
            risk_score += 20
        
        # Rule 3: Unusual spending pattern
        if recent_transactions:
            recent_count = len(recent_transactions)
            if recent_count > self.max_daily_transactions:
                indicators.append(f"Unusual spending pattern ({recent_count} transactions)")
                risk_score += 25
            
            # Check for rapid transactions
            if recent_count >= 3:
                recent_amounts = [t.get("amount", 0) for t in recent_transactions[-3:]]
                total_recent = sum(recent_amounts)
                if total_recent > 500:
                    indicators.append("Rapid consecutive transactions")
                    risk_score += 15
        
        # Rule 4: New geographic location
        # TODO: Implement location-based detection
        
        # Rule 5: User profile considerations
        if user_profile:
            diagnosed_conditions = user_profile.get("diagnosed_conditions", [])
            if "autism" in diagnosed_conditions or "adhd" in diagnosed_conditions:
                # More lenient for diagnosed conditions (Phase 2: personalized)
                risk_score *= 0.85
        
        # Cap risk score
        risk_score = min(100, max(0, risk_score))
        
        # Determine risk level
        if risk_score >= 75:
            risk_level = RiskLevel.CRITICAL
        elif risk_score >= 55:
            risk_level = RiskLevel.HIGH
        elif risk_score >= 30:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW
        
        # Determine if guardian approval required
        requires_approval = risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        
        # Generate recommendation
        recommendation = self._generate_recommendation(
            risk_level,
            indicators,
            amount,
            user_profile
        )
        
        return FraudDetectionResult(
            risk_score=risk_score,
            risk_level=risk_level,
            requires_guardian_approval=requires_approval,
            fraud_indicators=indicators,
            recommendation=recommendation,
        )
    
    def _generate_recommendation(
        self,
        risk_level: RiskLevel,
        indicators: List[str],
        amount: float,
        user_profile: Optional[Dict],
    ) -> str:
        """Generate recommendation based on risk assessment"""
        
        if risk_level == RiskLevel.CRITICAL:
            return "BLOCK: Transaction flagged as critical fraud risk. Immediate guardian review required."
        elif risk_level == RiskLevel.HIGH:
            return "PENDING: Transaction flagged for guardian approval due to high fraud risk."
        elif risk_level == RiskLevel.MEDIUM:
            return "MONITOR: Transaction flagged for monitoring but may proceed with caution."
        else:
            return "APPROVED: Transaction appears safe and can proceed."


class FraudDetectionService:
    """Main fraud detection service (Phase 1: Rule-based, Phase 2: ML-based)"""
    
    def __init__(self):
        self.rule_detector = RuleBasedFraudDetector()
        self.ml_model = None  # Will be implemented in Phase 2
        
    def analyze_transaction(
        self,
        amount: float,
        merchant_name: str,
        merchant_category: str,
        user_id: str,
        device_id: Optional[str] = None,
        location_lat: Optional[float] = None,
        location_lon: Optional[float] = None,
        recent_transactions: Optional[List[Dict]] = None,
        user_profile: Optional[Dict] = None,
    ) -> FraudDetectionResult:
        """
        Analyze transaction for fraud
        
        Phase 1: Uses rule-based detection
        Phase 2+: Will use ensemble of models
        """
        
        # Phase 1: Rule-based detection
        rule_result = self.rule_detector.detect_fraud(
            amount=amount,
            merchant_category=merchant_category,
            user_id=user_id,
            recent_transactions=recent_transactions,
            user_profile=user_profile,
        )
        
        # Phase 2: ML model ensemble (TBD)
        # ml_result = self.ml_model.predict(...)
        # weighted_result = ensemble([rule_result, ml_result])
        
        logger.info(
            f"Transaction analysis: user={user_id}, amount={amount}, "
            f"risk_level={rule_result.risk_level}, score={rule_result.risk_score:.1f}"
        )
        
        return rule_result
    
    def explain_decision(self, result: FraudDetectionResult) -> Dict:
        """Explain the fraud detection decision (for transparency & fairness)"""
        
        return {
            "risk_score": result.risk_score,
            "risk_level": result.risk_level.value,
            "requires_guardian_approval": result.requires_guardian_approval,
            "indicators": result.fraud_indicators,
            "recommendation": result.recommendation,
            "explainability": {
                "method": "Rule-based system (Phase 1)",
                "factors": {
                    "high_amount": "Transaction exceeds threshold",
                    "merchant_category": "Category flagged as suspicious",
                    "spending_pattern": "Unusual activity detected",
                    "location_velocity": "Calculated from device/IP",
                },
            }
        }


# Singleton instance
_fraud_detector = None


def get_fraud_detector() -> FraudDetectionService:
    """Get or create fraud detection service"""
    global _fraud_detector
    if _fraud_detector is None:
        _fraud_detector = FraudDetectionService()
    return _fraud_detector
