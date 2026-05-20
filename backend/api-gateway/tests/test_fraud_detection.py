"""
Tests for fraud detection service
"""
import pytest
from src.services.fraud_detection import (
    FraudDetectionService,
    RuleBasedFraudDetector,
    RiskLevel,
)


class TestRuleBasedDetector:
    """Rule-based fraud detector tests"""
    
    def setup_method(self):
        """Set up detector for each test"""
        self.detector = RuleBasedFraudDetector()
    
    def test_low_risk_small_amount(self):
        """Test low risk for small amount"""
        result = self.detector.detect_fraud(
            amount=50.0,
            merchant_category="grocery",
            user_id="user123",
        )
        
        assert result.risk_level == RiskLevel.LOW
        assert result.requires_guardian_approval is False
        assert result.risk_score < 30
    
    def test_high_risk_large_amount(self):
        """Test high risk for large amount"""
        result = self.detector.detect_fraud(
            amount=2000.0,
            merchant_category="jewelry",
            user_id="user123",
        )
        
        assert result.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        assert result.requires_guardian_approval is True
        assert len(result.fraud_indicators) > 0
    
    def test_suspicious_category(self):
        """Test suspicious merchant category"""
        result = self.detector.detect_fraud(
            amount=100.0,
            merchant_category="gambling",
            user_id="user123",
        )
        
        assert result.risk_level == RiskLevel.MEDIUM or result.risk_level == RiskLevel.HIGH
        assert "gambling" in result.fraud_indicators[0].lower()
    
    def test_rapid_transactions(self):
        """Test detection of rapid consecutive transactions"""
        recent = [
            {"amount": 100},
            {"amount": 150},
            {"amount": 200},
        ]
        
        result = self.detector.detect_fraud(
            amount=50.0,
            merchant_category="retail",
            user_id="user123",
            recent_transactions=recent,
        )
        
        assert result.risk_score > 0
        # Should detect rapid transactions
        indicators_text = " ".join(result.fraud_indicators)
        assert "rapid" in indicators_text.lower() or "unusual" in indicators_text.lower()
    
    def test_neurodivergent_adjustment(self):
        """Test that neurodivergent users get adjusted scores"""
        user_profile_normal = {"diagnosed_conditions": []}
        user_profile_neurodiv = {"diagnosed_conditions": ["autism"]}
        
        result_normal = self.detector.detect_fraud(
            amount=150.0,
            merchant_category="retail",
            user_id="user1",
            user_profile=user_profile_normal,
        )
        
        result_neurodiv = self.detector.detect_fraud(
            amount=150.0,
            merchant_category="retail",
            user_id="user2",
            user_profile=user_profile_neurodiv,
        )
        
        # Neurodivergent users should have slightly lower risk scores
        assert result_neurodiv.risk_score < result_normal.risk_score


class TestFraudDetectionService:
    """Fraud detection service tests"""
    
    def setup_method(self):
        """Set up service for each test"""
        self.service = FraudDetectionService()
    
    def test_analyze_transaction(self):
        """Test transaction analysis"""
        result = self.service.analyze_transaction(
            amount=100.0,
            merchant_name="Target",
            merchant_category="retail",
            user_id="user123",
        )
        
        assert result.risk_score >= 0
        assert result.risk_score <= 100
        assert result.risk_level in [
            RiskLevel.LOW,
            RiskLevel.MEDIUM,
            RiskLevel.HIGH,
            RiskLevel.CRITICAL,
        ]
    
    def test_explain_decision(self):
        """Test decision explanation"""
        result = self.service.analyze_transaction(
            amount=1500.0,
            merchant_name="Jewelry Store",
            merchant_category="jewelry",
            user_id="user123",
        )
        
        explanation = self.service.explain_decision(result)
        
        assert "risk_score" in explanation
        assert "risk_level" in explanation
        assert "indicators" in explanation
        assert "recommendation" in explanation
        assert "explainability" in explanation


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
