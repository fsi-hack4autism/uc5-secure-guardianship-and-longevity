# Deployment & Configuration Guide

## 1. Getting Started - Project Setup

### 1.1 Local Development Environment

#### Prerequisites
```bash
# Required software
- Docker & Docker Compose (latest)
- Node.js 18+ (for frontend)
- Python 3.11+ (for backend)
- PostgreSQL 15+ client tools
- Git

# Optional but recommended
- VS Code with extensions:
  - Python, Prettier, ESLint
  - Docker, Kubernetes
  - Thunder Client (API testing)
```

#### Clone and Initialize
```bash
# Clone repository
git clone https://github.com/fsi-hack4autism/uc5-secure-guardianship-and-longevity.git
cd uc5-secure-guardianship-and-longevity

# Install development dependencies
make setup

# Create environment configuration
cp .env.example .env
# Edit .env with your local settings
```

#### Start Local Services
```bash
# Start all services with Docker Compose
docker-compose up -d

# Verify all services are running
docker-compose ps

# View logs
docker-compose logs -f api-gateway

# Run database migrations
make db-migrate

# Seed test data
make db-seed

# Access services:
- API Gateway: http://localhost:8000
- Frontend Dev: http://localhost:3000
- PostgreSQL: localhost:5432
- Redis: localhost:6379
- Elasticsearch: http://localhost:9200
```

### 1.2 Environment Configuration

#### .env Template
```env
# Application
APP_ENV=development
APP_DEBUG=true
SECRET_KEY=your-secret-key-here

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=guardianship_db
DB_USER=postgres
DB_PASSWORD=postgres

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Elasticsearch
ES_HOST=localhost
ES_PORT=9200

# Authentication
JWT_SECRET=your-jwt-secret
JWT_EXPIRATION=86400
MFA_ENABLED=true

# Kafka
KAFKA_BROKER=localhost:9092
KAFKA_TOPICS=transactions,alerts,audit

# AWS (if using cloud)
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret

# ML Models
ML_MODEL_PATH=/models
ML_ENABLED=true
FRAUD_DETECTION_THRESHOLD=0.65

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Notifications
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDGRID_API_KEY=your-key

# Feature Flags
ENABLE_FRAUD_DETECTION=true
ENABLE_ML_MODELS=false  # Set to true when models ready
ENABLE_GUARDIAN_APPROVAL=true
ENABLE_LONGEVITY_FEATURES=false
```

---

## 2. Docker Configuration

### 2.1 Base Docker Image

Create `docker/Dockerfile.base`:
```dockerfile
FROM python:3.11-slim-bullseye

# Security updates
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Create app user (non-root)
RUN useradd -m -u 1000 appuser

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Set permissions
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2.2 Docker Compose Stack

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: guardianship-postgres
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: guardianship_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backend/shared/database/init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - guardianship-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: guardianship-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - guardianship-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.7.0
    container_name: guardianship-elasticsearch
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
    networks:
      - guardianship-network
    healthcheck:
      test: ["CMD-SHELL", "curl -s http://localhost:9200 | grep -q cluster_name"]
      interval: 10s
      timeout: 5s
      retries: 5

  kafka:
    image: confluentinc/cp-kafka:7.5.0
    container_name: guardianship-kafka
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:29092,PLAINTEXT_HOST://localhost:9092
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
    networks:
      - guardianship-network

  zookeeper:
    image: confluentinc/cp-zookeeper:7.5.0
    container_name: guardianship-zookeeper
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
    ports:
      - "2181:2181"
    networks:
      - guardianship-network

  api-gateway:
    build:
      context: ./backend/api-gateway
      dockerfile: Dockerfile
    container_name: guardianship-api
    environment:
      - APP_ENV=development
      - DEBUG=true
      - DB_HOST=postgres
      - REDIS_HOST=redis
      - ES_HOST=elasticsearch
      - KAFKA_BROKER=kafka:29092
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - guardianship-network
    volumes:
      - ./backend:/app

  auth-service:
    build:
      context: ./backend/auth-service
      dockerfile: Dockerfile
    container_name: guardianship-auth
    environment:
      - APP_ENV=development
      - DB_HOST=postgres
      - REDIS_HOST=redis
    ports:
      - "8001:8000"
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - guardianship-network

  transaction-service:
    build:
      context: ./backend/transaction-service
      dockerfile: Dockerfile
    container_name: guardianship-transactions
    environment:
      - APP_ENV=development
      - DB_HOST=postgres
      - REDIS_HOST=redis
      - KAFKA_BROKER=kafka:29092
    ports:
      - "8002:8000"
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - guardianship-network

  ai-risk-engine:
    build:
      context: ./backend/ai-risk-engine
      dockerfile: Dockerfile
    container_name: guardianship-ai
    environment:
      - APP_ENV=development
      - ML_ENABLED=false
      - KAFKA_BROKER=kafka:29092
    ports:
      - "8003:8000"
    depends_on:
      - kafka
    networks:
      - guardianship-network
    volumes:
      - ./ml-models:/models

  frontend-dev:
    build:
      context: ./frontend/guardian-dashboard
      dockerfile: Dockerfile.dev
    container_name: guardianship-frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    depends_on:
      - api-gateway
    networks:
      - guardianship-network
    volumes:
      - ./frontend:/app

volumes:
  postgres_data:
  redis_data:
  elasticsearch_data:

networks:
  guardianship-network:
    driver: bridge
```

---

## 3. Database Setup

### 3.1 Database Initialization

Create `backend/shared/database/init.sql`:
```sql
-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS public;
CREATE SCHEMA IF NOT EXISTS audit;

-- Create base tables (see TECHNICAL_SPEC.md for full schema)
CREATE TABLE public.users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    user_type VARCHAR(20) NOT NULL, -- 'beneficiary', 'guardian', 'advisor'
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE public.user_profiles (
    user_id UUID PRIMARY KEY REFERENCES public.users(user_id),
    profile_type VARCHAR(50),
    full_name VARCHAR(255),
    date_of_birth DATE,
    diagnosed_conditions TEXT[],
    accessibility_needs TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE audit.transaction_audit (
    audit_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    transaction_id UUID,
    user_id UUID,
    action VARCHAR(50),
    old_values JSONB,
    new_values JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_ip VARCHAR(45)
);

-- Create indexes
CREATE INDEX idx_users_email ON public.users(email);
CREATE INDEX idx_users_created ON public.users(created_at DESC);
CREATE INDEX idx_audit_timestamp ON audit.transaction_audit(timestamp DESC);

-- Create audit trigger
CREATE OR REPLACE FUNCTION audit_trigger_func()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit.transaction_audit (transaction_id, action, new_values, user_ip)
    VALUES (NEW.transaction_id, TG_OP, row_to_json(NEW), current_setting('app.user_ip'));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

### 3.2 Database Migration Management

Create `backend/shared/database/migrate.py`:
```python
import os
from alembic import command
from alembic.config import Config

def run_migrations(direction='upgrade', revision='head'):
    """
    Run database migrations
    
    Args:
        direction: 'upgrade' or 'downgrade'
        revision: Target revision (default: 'head')
    """
    alembic_cfg = Config('alembic.ini')
    alembic_cfg.set_main_option('sqlalchemy.url', os.getenv('DATABASE_URL'))
    
    if direction == 'upgrade':
        command.upgrade(alembic_cfg, revision)
    elif direction == 'downgrade':
        command.downgrade(alembic_cfg, revision)
    else:
        raise ValueError(f"Invalid direction: {direction}")
    
    print(f"Migration {direction} to {revision} completed successfully")

if __name__ == '__main__':
    import sys
    direction = sys.argv[1] if len(sys.argv) > 1 else 'upgrade'
    revision = sys.argv[2] if len(sys.argv) > 2 else 'head'
    run_migrations(direction, revision)
```

---

## 4. Kubernetes Deployment

### 4.1 Namespace Setup

Create `infrastructure/kubernetes/namespaces/guardianship.yaml`:
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: guardianship
  labels:
    name: guardianship
    environment: production
```

### 4.2 API Gateway Deployment

Create `infrastructure/kubernetes/deployments/api-gateway.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-gateway
  namespace: guardianship
  labels:
    app: api-gateway
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api-gateway
  template:
    metadata:
      labels:
        app: api-gateway
    spec:
      containers:
      - name: api-gateway
        image: guardianship/api-gateway:latest
        imagePullPolicy: Always
        ports:
        - containerPort: 8000
          name: http
        env:
        - name: APP_ENV
          value: "production"
        - name: DB_HOST
          value: "postgres.guardianship.svc.cluster.local"
        - name: REDIS_HOST
          value: "redis.guardianship.svc.cluster.local"
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: api-gateway-service
  namespace: guardianship
spec:
  type: LoadBalancer
  selector:
    app: api-gateway
  ports:
  - port: 80
    targetPort: 8000
    protocol: TCP
```

---

## 5. CI/CD Pipeline

### 5.1 GitHub Actions Workflow

Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy to Production

on:
  push:
    branches:
      - main
  workflow_dispatch:

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: pytest --cov=. tests/
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost/test_db
    
    - name: Run accessibility tests
      run: pytest tests/accessibility/

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Login to Container Registry
      uses: docker/login-action@v2
      with:
        registry: ${{ secrets.REGISTRY_URL }}
        username: ${{ secrets.REGISTRY_USERNAME }}
        password: ${{ secrets.REGISTRY_PASSWORD }}
    
    - name: Build and push Docker images
      run: |
        docker build -t ${{ secrets.REGISTRY_URL }}/api-gateway:${{ github.sha }} ./backend/api-gateway
        docker push ${{ secrets.REGISTRY_URL }}/api-gateway:${{ github.sha }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Configure kubectl
      run: |
        mkdir -p $HOME/.kube
        echo "${{ secrets.KUBE_CONFIG }}" | base64 -d > $HOME/.kube/config
    
    - name: Deploy to Kubernetes
      run: |
        kubectl set image deployment/api-gateway \
          api-gateway=${{ secrets.REGISTRY_URL }}/api-gateway:${{ github.sha }} \
          -n guardianship
        kubectl rollout status deployment/api-gateway -n guardianship

  notify:
    needs: deploy
    runs-on: ubuntu-latest
    if: always()
    steps:
    - name: Send Slack notification
      uses: slackapi/slack-github-action@v1.24.0
      with:
        payload: |
          {
            "text": "Deployment to production ${{ job.status }}",
            "blocks": [
              {
                "type": "section",
                "text": {
                  "type": "mrkdwn",
                  "text": "*Deployment Status*: ${{ job.status }}\n*Commit*: ${{ github.sha }}\n*Branch*: ${{ github.ref }}"
                }
              }
            ]
          }
      env:
        SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

---

## 6. Monitoring & Observability

### 6.1 Prometheus Configuration

Create `infrastructure/monitoring/prometheus.yml`:
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']

rule_files:
  - 'alert_rules.yml'

scrape_configs:
  - job_name: 'api-gateway'
    static_configs:
      - targets: ['api-gateway:8000']
    metrics_path: '/metrics'

  - job_name: 'transaction-service'
    static_configs:
      - targets: ['transaction-service:8000']

  - job_name: 'ai-risk-engine'
    static_configs:
      - targets: ['ai-risk-engine:8000']

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
```

### 6.2 Alert Rules

Create `infrastructure/monitoring/alert_rules.yml`:
```yaml
groups:
  - name: guardianship_alerts
    interval: 30s
    rules:
      - alert: HighFraudDetectionRate
        expr: fraud_detection_rate > 0.95
        for: 5m
        annotations:
          summary: "High fraud detection rate detected"
          description: "Fraud detection rate is {{ $value }}"

      - alert: HighFalsePositiveRate
        expr: false_positive_rate > 0.05
        for: 5m
        annotations:
          summary: "High false positive rate"
          description: "FP rate is {{ $value }}"

      - alert: APILatencySpiking
        expr: http_request_duration_seconds{quantile="0.99"} > 0.5
        for: 5m
        annotations:
          summary: "API latency spike"

      - alert: DatabaseConnectionPoolExhausted
        expr: pg_stat_activity_count > 90
        for: 2m
        annotations:
          summary: "Database connection pool nearly exhausted"

      - alert: MLModelInferenceSlow
        expr: ml_inference_duration_seconds > 0.5
        for: 5m
        annotations:
          summary: "ML inference time exceeding threshold"
```

---

## 7. Security Setup

### 7.1 Secrets Management

Create `infrastructure/secrets/setup-vault.sh`:
```bash
#!/bin/bash

# Initialize HashiCorp Vault
vault server -config=vault-config.hcl &

# Unseal vault (development only - use HSM in production)
vault operator unseal

# Create secret engine
vault secrets enable -path=guardianship kv-v2

# Store secrets
vault kv put guardianship/database \
  username=dbuser \
  password=$DB_PASSWORD

vault kv put guardianship/jwt \
  secret=$JWT_SECRET

vault kv put guardianship/aws \
  access_key=$AWS_ACCESS_KEY \
  secret_key=$AWS_SECRET_KEY

echo "Vault initialized with all secrets"
```

### 7.2 SSL/TLS Configuration

Create `infrastructure/nginx/nginx.conf`:
```nginx
upstream api_gateway {
    server api-gateway:8000;
}

server {
    listen 80;
    server_name _;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name guardianship.example.com;

    ssl_certificate /etc/letsencrypt/live/guardianship.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/guardianship.example.com/privkey.pem;
    ssl_protocols TLSv1.3 TLSv1.2;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req zone=api_limit burst=20 nodelay;

    location / {
        proxy_pass http://api_gateway;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 8. Makefile Commands

Create `Makefile`:
```makefile
.PHONY: help setup build deploy test clean logs

help:
	@echo "Available commands:"
	@echo "  make setup          - Set up development environment"
	@echo "  make build          - Build Docker images"
	@echo "  make deploy         - Deploy to Kubernetes"
	@echo "  make test           - Run tests"
	@echo "  make accessibility  - Run accessibility tests"
	@echo "  make clean          - Clean up Docker resources"
	@echo "  make db-migrate     - Run database migrations"
	@echo "  make logs           - View container logs"

setup:
	@echo "Setting up development environment..."
	pip install -r requirements.txt
	npm --prefix frontend/guardian-dashboard install
	docker-compose up -d
	$(MAKE) db-migrate
	@echo "Setup complete!"

build:
	@echo "Building Docker images..."
	docker-compose build

deploy:
	@echo "Deploying to Kubernetes..."
	kubectl apply -f infrastructure/kubernetes/
	kubectl rollout status deployment/api-gateway -n guardianship

test:
	@echo "Running tests..."
	pytest tests/ --cov=.

accessibility:
	@echo "Running accessibility tests..."
	pytest tests/accessibility/ -v

security:
	@echo "Running security checks..."
	bandit -r backend/
	safety check

clean:
	@echo "Cleaning up..."
	docker-compose down
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

db-migrate:
	@echo "Running database migrations..."
	python backend/shared/database/migrate.py upgrade

logs:
	docker-compose logs -f $(SERVICE)
```

---

## 9. Checklist for Production Deployment

Before deploying to production:

- [ ] All tests passing (unit, integration, e2e)
- [ ] Accessibility audit complete (WCAG 2.1 AA)
- [ ] Security audit completed
- [ ] Penetration testing done
- [ ] Load testing performed (100,000+ concurrent users)
- [ ] Disaster recovery plan tested
- [ ] Backup and restore procedures verified
- [ ] Monitoring and alerting configured
- [ ] Runbooks for common issues prepared
- [ ] On-call rotation established
- [ ] Compliance certifications obtained
- [ ] Insurance and legal reviewed
- [ ] Training completed for support team
- [ ] Documentation finalized
- [ ] Approval from stakeholders

---

## 10. Troubleshooting

### Common Issues

**Issue**: PostgreSQL connection refused
```bash
# Solution
docker-compose restart postgres
docker-compose logs postgres
```

**Issue**: API gateway returning 500 errors
```bash
# Solution
docker-compose logs api-gateway
curl http://localhost:8000/health  # Check health endpoint
```

**Issue**: ML models not loading
```bash
# Solution
ls -la ml-models/  # Check model files exist
python -c "import torch; print(torch.__version__)"  # Verify dependencies
```

**Issue**: Kubernetes deployment stuck
```bash
# Solution
kubectl describe deployment api-gateway -n guardianship
kubectl get events -n guardianship --sort-by='.lastTimestamp'
```

---

For more detailed information, refer to the main [DESIGN.md](DESIGN.md) document.

