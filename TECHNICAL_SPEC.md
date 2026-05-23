# Technical Specification: AI Risk Engine

## 1. Real-Time Fraud Detection Service

### 1.1 API Specification

#### Score Transaction Endpoint
```
POST /api/v1/risk/score-transaction
Content-Type: application/json
Authorization: Bearer <token>

Request Body:
{
  "transaction_id": "txn_8a9f2b3c",
  "user_id": "user_123abc",
  "amount": 2500.00,
  "currency": "USD",
  "merchant": {
    "id": "merchant_456def",
    "name": "Amazon.com",
    "category": "E-Commerce",
    "country": "US",
    "mcc": "5961"
  },
  "beneficiary": {
    "account_number": "***1234",
    "routing_number": "***5678"
  },
  "device": {
    "id": "device_789ghi",
    "ip_address": "192.168.1.1",
    "user_agent": "Mozilla/5.0...",
    "platform": "iOS",
    "is_trusted": false
  },
  "context": {
    "timestamp": "2024-05-20T14:30:00Z",
    "location": {
      "latitude": 40.7128,
      "longitude": -74.0060,
      "country": "US",
      "city": "New York"
    },
    "is_recurring": false,
    "user_confirmed": true
  }
}

Response (Success - 200):
{
  "transaction_id": "txn_8a9f2b3c",
  "risk_score": 23,
  "risk_level": "LOW",
  "risk_factors": [
    {
      "factor": "amount_exceeds_merchant_average",
      "weight": 0.15,
      "explanation": "Amount is 2.3x higher than typical purchases at this merchant"
    },
    {
      "factor": "new_device",
      "weight": 0.08,
      "explanation": "Transaction from untrusted device"
    }
  ],
  "confidence": 0.94,
  "recommendation": "APPROVE",
  "requires_guardian_approval": false,
  "decision_explanation": "Low fraud risk detected. Transaction approved for processing.",
  "model_version": "fraud_detection_v2.3.1",
  "processing_time_ms": 187
}

Response (Requires Review - 202):
{
  "transaction_id": "txn_8a9f2b3c",
  "risk_score": 68,
  "risk_level": "MEDIUM",
  "requires_guardian_approval": true,
  "decision_explanation": "Unusual transaction pattern detected. Guardian approval required.",
  "action_required_by": "guardian",
  "approval_deadline": "2024-05-21T14:30:00Z"
}

Response (Blocked - 403):
{
  "transaction_id": "txn_8a9f2b3c",
  "risk_score": 92,
  "risk_level": "CRITICAL",
  "blocked": true,
  "reason": "High-risk transaction pattern detected",
  "alert_sent_to": ["guardian_1", "guardian_2", "advisor"],
  "requires_manual_review": true
}
```

### 1.2 Risk Scoring Algorithm

#### Input Feature Engineering
```
User Behavioral Features:
  - avg_transaction_amount (by category)
  - std_dev_amount (by category)
  - daily_transaction_count
  - monthly_spending_total
  - days_since_last_transaction
  - preferred_merchants (top 10)
  - typical_transaction_time_hour
  - typical_transaction_day_of_week

Transaction Features:
  - amount_ratio_to_average (current / historical average)
  - amount_ratio_to_category_max (current / max in category)
  - merchant_deviation_score (distance from usual merchants)
  - merchant_fraud_rate (historical fraud % for merchant)
  - merchant_reputation_score (third-party data)
  - transaction_recency (how recent is this type?)

Device Features:
  - is_trusted_device (historical)
  - device_age (days since first seen)
  - failed_auth_attempts_recent
  - location_deviation_km
  - location_consistency_score
  - vpn_detected
  - tor_network_detected

Temporal Features:
  - hour_of_day (0-23)
  - day_of_week (0-6)
  - days_since_payday
  - is_holiday
  - is_unusual_time (for user)
  - transaction_velocity_5min
  - transaction_velocity_1hour

External Features:
  - merchant_fraud_alert (from threat intel)
  - location_fraud_alert
  - payment_method_compromised
  - suspicious_activity_network
```

#### Scoring Components
```
Risk Score = Weighted Ensemble of Multiple Models

Model 1: Gradient Boosting (Weight: 0.40)
  Input: All engineered features
  Output: Fraud probability 0-1
  Training: Labeled fraud/legitimate transactions
  
Model 2: Isolation Forest (Weight: 0.30)
  Input: Anomaly-detection features
  Output: Anomaly score -1 to 1
  Detects novel fraud patterns

Model 3: Neural Network (Weight: 0.20)
  Input: Transaction embedding + user embedding
  Output: Deep fraud probability 0-1
  Learns complex interactions

Model 4: Rule Engine (Weight: 0.10)
  Input: Policy checks + hard constraints
  Output: 0 (pass) or 1 (fail)
  Catches known fraud patterns

Final Score = (Model1 * 0.40) + (Model2 * 0.30) + 
              (Model3 * 0.20) + (Model4 * 0.10)
Final Score: 0-100
```

#### Risk Level Classification
```
Risk Score Range | Risk Level | Action
0-20            | LOW        | Auto-approve
21-40           | MEDIUM     | Single guardian approval
41-70           | HIGH       | Multiple guardian approval
71-85           | CRITICAL   | Block & alert all
86-100          | BLOCKED    | Automatic block + escalation
```

---

## 2. Behavioral Baseline Learning

### 2.1 Profile Construction Algorithm

#### Initial Learning Phase (First 30 days)
```
Phase 1A: Data Collection (Days 1-7)
  - Collect all transactions without flagging
  - Identify transaction categories automatically
  - Note typical amounts and frequencies
  - Record location patterns
  - Note device usage patterns

Phase 1B: Pattern Extraction (Days 7-14)
  - Build category baselines (average, std dev, min, max)
  - Calculate daily/weekly/monthly spending averages
  - Identify merchant preferences
  - Establish temporal patterns (time of day, day of week)
  - Detect recurring transactions

Phase 1C: Anomaly Threshold Setting (Days 14-30)
  - Analyze distribution of each feature
  - Set upper/lower bounds for normal behavior
  - Configure alert thresholds
  - Begin flagging extreme outliers (not blocking)
  - Refine thresholds based on feedback

Transition to Normal Operation (Day 30+)
  - Enable risk scoring with learned baseline
  - Begin blocking high-risk transactions
  - Require guardian approvals for medium-risk
  - Continue learning and adapting
```

#### Continuous Learning
```
Daily Update Process:
  1. Collect completed transactions from past 24 hours
  2. Update statistical baselines (rolling window)
  3. Recalculate feature importance
  4. Retrain anomaly detection models
  5. Evaluate model performance
  6. Deploy improved models at 2 AM UTC

Monthly Evaluation:
  1. Calculate false positive/negative rates
  2. Analyze guardian override patterns
  3. Adjust thresholds if needed
  4. Review for concept drift
  5. Document changes for audit

Quarterly Review:
  1. Full model retraining with 3 months data
  2. Feature importance analysis
  3. A/B testing of new features
  4. Bias and fairness assessment
  5. Guardian and user feedback incorporation
```

### 2.2 Data Model

#### User Profile Schema
```sql
CREATE TABLE user_profiles (
  user_id UUID PRIMARY KEY,
  onboarding_date TIMESTAMP NOT NULL,
  profile_status VARCHAR(20), -- 'learning', 'active', 'paused'
  
  -- Demographic (if consented)
  age_range VARCHAR(10),
  diagnosed_conditions TEXT[], -- ['autism', 'adhd', 'dyscalculia']
  communication_needs TEXT[],
  
  -- Spending Baselines (by category)
  category_baselines JSONB, -- {
                            --   'groceries': { 'mean': 150, 'std': 30, 'max': 250 },
                            --   'utilities': { 'mean': 120, 'std': 20, 'max': 200 },
                            --   ...
                            -- }
  
  -- Temporal Patterns
  typical_transaction_hour INT,
  typical_transaction_dow INT,
  
  -- Trust & Safety
  trusted_merchants UUID[],
  trusted_devices UUID[],
  blocked_merchants UUID[],
  
  -- Feature Flags
  requires_notification_for_all BOOLEAN,
  requires_guardian_approval_threshold DECIMAL,
  
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

CREATE TABLE transaction_history (
  transaction_id UUID PRIMARY KEY,
  user_id UUID REFERENCES user_profiles(user_id),
  merchant_id UUID,
  amount DECIMAL(10, 2),
  category VARCHAR(50),
  device_id UUID,
  location_id UUID,
  risk_score INT,
  guardian_approval_required BOOLEAN,
  guardian_approved_by UUID,
  guardian_approval_timestamp TIMESTAMP,
  fraud_flag BOOLEAN,
  user_confirmed BOOLEAN,
  
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  
  INDEX idx_user_created (user_id, created_at DESC),
  INDEX idx_risk_score (risk_score DESC)
);

CREATE TABLE merchants (
  merchant_id UUID PRIMARY KEY,
  name VARCHAR(255),
  category VARCHAR(50),
  mcc INT,
  fraud_rate DECIMAL(5, 2), -- percentage
  reputation_score DECIMAL(3, 2), -- 0-1.0
  is_trusted BOOLEAN,
  user_interaction_count INT,
  last_transaction TIMESTAMP,
  
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  
  INDEX idx_fraud_rate (fraud_rate DESC)
);

CREATE TABLE devices (
  device_id UUID PRIMARY KEY,
  user_id UUID REFERENCES user_profiles(user_id),
  device_type VARCHAR(20), -- 'mobile', 'tablet', 'desktop'
  platform VARCHAR(20), -- 'iOS', 'Android', 'Windows'
  is_trusted BOOLEAN DEFAULT FALSE,
  trust_score DECIMAL(3, 2),
  first_seen TIMESTAMP,
  last_seen TIMESTAMP,
  
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

CREATE TABLE user_alerts (
  alert_id UUID PRIMARY KEY,
  user_id UUID REFERENCES user_profiles(user_id),
  alert_type VARCHAR(50), -- 'fraud_detected', 'unusual_activity', 'exploitation_risk'
  severity VARCHAR(10), -- 'low', 'medium', 'high', 'critical'
  description TEXT,
  transaction_id UUID,
  action_taken VARCHAR(50), -- 'auto_blocked', 'guardian_notified', 'escalated'
  resolved BOOLEAN,
  resolved_by UUID,
  resolved_at TIMESTAMP,
  
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  
  INDEX idx_user_created (user_id, created_at DESC),
  INDEX idx_severity (severity)
);
```

---

## 3. Guardian Approval Workflow

### 3.1 State Machine

```
Transaction States:
  PENDING_INITIAL_RISK_SCORE
    ↓ (AI scoring complete)
  APPROVED_AUTO (if risk_score < 20)
    ↓
  PROCESSING
    ↓
  COMPLETED
  
  OR

  PENDING_GUARDIAN_REVIEW (if 20 <= risk_score < 80)
    ↓ (Guardian notified)
  PENDING_GUARDIAN_DECISION
    ↓ (Guardian approves/denies/modifies)
  APPROVED_BY_GUARDIAN or DENIED or MODIFIED
    ↓
  PROCESSING or REJECTED
    ↓
  COMPLETED or FAILED
  
  OR

  FLAGGED_FOR_ESCALATION (if risk_score >= 80)
    ↓ (All guardians + advisor notified)
  PENDING_ESCALATION_REVIEW
    ↓ (Decision required within 4 hours)
  APPROVED_ESCALATION or DENIED_ESCALATION
    ↓
  PROCESSING or REJECTED
    ↓
  COMPLETED or FAILED
```

### 3.2 Guardian Notification Protocol

```
Notification Triggers:

TIER 1 (Medium Risk - Single Guardian):
  - Email within 5 minutes
  - In-app notification
  - SMS if configured
  - Decision deadline: 24 hours
  
TIER 2 (High Risk - Multiple Guardians):
  - Email + SMS to all guardians immediately
  - Phone call to primary guardian (optional automated)
  - In-app push notification
  - Decision deadline: 4 hours
  
TIER 3 (Critical Risk - Escalation):
  - Emergency SMS to all guardians
  - Phone call to primary guardian (must answer)
  - Email to financial advisor
  - Dashboard alert (highest priority)
  - Decision deadline: 1 hour
  - Auto-escalate to authorities if not addressed in 1 hour

Notification Content:
{
  "title": "Transaction Review Required",
  "priority": "HIGH",
  "transaction": {
    "id": "txn_123",
    "amount": 2500,
    "merchant": "Best Buy",
    "time": "2024-05-20 14:30 UTC",
    "user": "John Doe"
  },
  "risk_summary": {
    "score": 68,
    "level": "HIGH",
    "reasons": [
      "Amount 3.2x higher than typical electronics purchases",
      "Transaction at new merchant location",
      "Rapid sequence of transactions detected"
    ]
  },
  "quick_action_links": {
    "approve": "https://...",
    "deny": "https://...",
    "review_details": "https://..."
  },
  "context": {
    "user_baseline": "Typically spends $100-200 on electronics",
    "recent_transactions": "2 transactions in past hour",
    "device": "Trusted device"
  }
}
```

---

## 4. Model Training Pipeline

### 4.1 Training Architecture

```yaml
Training Pipeline:
  name: fraud_detection_retraining
  schedule: "0 2 * * *"  # Daily at 2 AM UTC
  
  stages:
    - name: data_collection
      duration: 30min
      tasks:
        - collect_transaction_data(past_30_days)
        - collect_fraud_labels(verified_cases)
        - collect_guardian_feedback(feedback_log)
    
    - name: feature_engineering
      duration: 45min
      tasks:
        - extract_user_features()
        - extract_transaction_features()
        - extract_merchant_features()
        - extract_temporal_features()
        - normalize_features()
    
    - name: model_training
      duration: 60min
      tasks:
        - train_gradient_boosting_model()
        - train_isolation_forest()
        - train_neural_network()
        - hyperparameter_tuning()
    
    - name: model_evaluation
      duration: 30min
      tasks:
        - evaluate_precision_recall()
        - evaluate_fairness_across_demographics()
        - evaluate_adversarial_robustness()
        - compare_against_baseline()
    
    - name: model_deployment
      duration: 15min
      tasks:
        - if metrics_improved():
            - deploy_to_production()
            - monitor_performance()
          else:
            - rollback()
            - alert_team()

monitoring:
  metrics:
    - name: fraud_detection_rate
      warning_threshold: 85%
      error_threshold: 75%
    
    - name: false_positive_rate
      warning_threshold: 6%
      error_threshold: 10%
    
    - name: model_latency_p99
      warning_threshold: 700ms
      error_threshold: 1000ms
```

### 4.2 Training Data Requirements

```
Minimum Dataset Size:
  - 100,000 labeled transactions (fraud vs legitimate)
  - 70/30 train/test split
  - Stratified by user_risk_profile
  - Balanced by fraud/non-fraud (1:99 ratio typical)

Data Quality Requirements:
  - No PII (personally identifiable information)
  - No direct account numbers or SSNs
  - Tokenized identifiers for users and merchants
  - Complete transaction records (no nulls in critical fields)
  - Verified fraud labels with high confidence

Class Imbalance Handling:
  - Use SMOTE (Synthetic Minority Over-sampling)
  - Class weights in gradient boosting
  - Threshold optimization for precision/recall trade-off
  - Stratified cross-validation

Feature Importance Analysis:
  - Use SHAP for model interpretation
  - Remove low-importance features (<0.01 weight)
  - Validate feature correlation (remove multicollinearity)
  - Document feature rationale for compliance
```

---

## 5. Fairness & Bias Mitigation

### 5.1 Fairness Metrics

```python
# Calculate Fairness Metrics by Demographic

fairness_metrics = {
    "false_positive_disparity": {
        "definition": "Ratio of false positive rates between groups",
        "target": "< 1.25 (25% difference tolerance)",
        "by_demographic": {
            "age": check_fairness_by_age_group(),
            "neurodivergent_type": check_fairness_by_condition(),
            "gender": check_fairness_by_gender(),
            "geography": check_fairness_by_region()
        }
    },
    
    "equal_opportunity": {
        "definition": "True positive rates should be equal across groups",
        "target": "> 0.90",
        "calculation": "min_tpr / max_tpr across groups"
    },
    
    "demographic_parity": {
        "definition": "Approval rates should be similar across groups",
        "target": "> 0.80",
        "calculation": "min_approval_rate / max_approval_rate"
    },
    
    "calibration": {
        "definition": "Predicted scores should match actual fraud rates",
        "target": "< 0.05 error",
        "calculation": "Brier score by demographic groups"
    }
}

# Monitoring Process
for demographic in ['age', 'condition', 'gender', 'region']:
    for group in demographic.unique_values():
        group_transactions = filter_by_demographic(transactions, demographic, group)
        metrics = calculate_fairness_metrics(group_transactions)
        
        if metrics['fpr_disparity'] > 1.25:
            alert("Fairness violation for", demographic, group)
            adjust_model_thresholds(demographic, group)
```

### 5.2 Bias Mitigation Strategies

```
1. Balanced Training Data
   - Ensure representation of all demographic groups
   - Oversample underrepresented groups if needed
   - Monitor class distribution in training set

2. Adversarial Debiasing
   - Add adversarial branch to network
   - Penalize model for learning demographic features
   - Trade off accuracy for fairness

3. Threshold Optimization
   - Use different decision thresholds for different groups
   - Optimize for equalized odds or demographic parity
   - Document threshold differences for compliance

4. Feature Engineering
   - Remove or mask proxy variables for protected attributes
   - Create synthetic features that are demographic-agnostic
   - Validate features don't encode demographic information

5. Audit & Retrain
   - Monthly fairness audits across all dimensions
   - Retrain if disparities detected
   - Document all fairness interventions
```

---

## 6. Model Explainability (SHAP)

### 6.1 Per-Transaction Explanation

```json
{
  "transaction_id": "txn_8a9f2b3c",
  "risk_score": 68,
  "base_value": 0.32,
  "prediction": 0.68,
  "feature_contributions": [
    {
      "feature": "amount_to_average_ratio",
      "value": 3.2,
      "shap_value": 0.18,
      "direction": "increases_risk",
      "explanation": "Amount is 3.2x the user's typical spending in this category"
    },
    {
      "feature": "merchant_fraud_rate",
      "value": 0.05,
      "shap_value": 0.12,
      "direction": "increases_risk",
      "explanation": "This merchant has a 5% fraud rate, which is above average"
    },
    {
      "feature": "device_trust_score",
      "value": 0.9,
      "shap_value": -0.08,
      "direction": "decreases_risk",
      "explanation": "Transaction from trusted device reduces fraud likelihood"
    },
    {
      "feature": "transaction_velocity_1hour",
      "value": 2,
      "shap_value": 0.15,
      "direction": "increases_risk",
      "explanation": "2 transactions in past hour is unusual for this user"
    }
  ],
  "user_facing_explanation": "This transaction has a medium fraud risk because the amount ($2,500) is significantly higher than your typical purchases at this store, and there have been multiple transactions in the past hour. The transaction is from a trusted device, which is a positive factor. A guardian's approval is recommended before processing."
}
```

---

## Conclusion

This technical specification provides the implementation blueprint for the AI Risk Engine component. Key implementation priorities:

1. **Real-time Performance**: <500ms scoring latency required
2. **Accuracy**: >95% fraud detection with <5% false positives
3. **Fairness**: <25% disparity in error rates across demographics
4. **Explainability**: Every decision must have clear explanation
5. **Scalability**: Support 100,000+ concurrent users
6. **Compliance**: Full audit trail and regulatory alignment

