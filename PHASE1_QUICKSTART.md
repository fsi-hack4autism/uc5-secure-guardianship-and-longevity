# Phase 1: Foundation - Quick Start Guide

## 🚀 Getting Started with Local Development

### Prerequisites

Before you begin, ensure you have installed:
- **Docker** and **Docker Compose** (latest version)
- **Make** (optional, for running Makefile commands)
- **Git** (for version control)

### Quick Start (5 minutes)

1. **Clone and navigate to repository**
   ```bash
   cd uc5-secure-guardianship-and-longevity
   ```

2. **Copy environment configuration**
   ```bash
   cp .env.example .env
   ```

3. **Start all services**
   ```bash
   docker-compose up -d
   ```

4. **Wait for services to be ready** (about 10 seconds)

5. **Access the application**
   - **API Gateway**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/docs
   - **Guardian Dashboard**: http://localhost:3000

### Using Makefile (Easier)

If you have `make` installed, you can use simplified commands:

```bash
# Initial setup
make setup
make up

# View logs
make logs

# Stop services
make down

# Check health
make health-check
```

---

## 🔐 Test Credentials

Use these credentials to sign in to the guardian dashboard:

```
Email: guardian@example.com
Password: password123
User Type: Guardian
```

Or create a new account at http://localhost:3000/login

---

## 📚 API Documentation

Once the API is running, visit: **http://localhost:8000/docs**

### Key Endpoints (Phase 1)

#### Authentication
- `POST /api/v1/auth/signup` - Register new user
- `POST /api/v1/auth/signin` - Login user
- `POST /api/v1/auth/refresh` - Refresh token

#### Users
- `GET /api/v1/users/me` - Get current user profile
- `PUT /api/v1/users/me` - Update user profile
- `GET /api/v1/users/{user_id}` - Get user by ID

#### Transactions
- `POST /api/v1/transactions/` - Create transaction
- `GET /api/v1/transactions/` - List user's transactions
- `GET /api/v1/transactions/{transaction_id}` - Get transaction details
- `POST /api/v1/transactions/{transaction_id}/approve` - Guardian approves
- `POST /api/v1/transactions/{transaction_id}/reject` - Guardian rejects

#### Guardians
- `POST /api/v1/guardians/` - Create guardian relationship
- `GET /api/v1/guardians/beneficiary/{beneficiary_id}` - Get guardians
- `GET /api/v1/guardians/guardian/{guardian_id}` - Get beneficiaries

---

## 🗂️ Project Structure

```
uc5-secure-guardianship-and-longevity/
├── backend/
│   ├── api-gateway/                 # Main API Gateway (FastAPI)
│   │   ├── src/
│   │   │   ├── main.py             # FastAPI app
│   │   │   ├── config.py           # Configuration
│   │   │   ├── database.py         # Database setup
│   │   │   ├── models.py           # SQLAlchemy models
│   │   │   └── routes/             # API endpoints
│   │   ├── requirements.txt        # Python dependencies
│   │   └── Dockerfile             # Container definition
│   └── shared/                      # Shared code
│       └── database/
│
├── frontend/
│   └── guardian-dashboard/          # React dashboard
│       ├── src/
│       │   ├── pages/              # Page components
│       │   ├── components/         # Reusable components
│       │   ├── store/              # State management (Zustand)
│       │   ├── services/           # API services
│       │   └── App.tsx
│       ├── package.json
│       └── Dockerfile
│
├── docker-compose.yml               # Docker orchestration
├── Makefile                        # Development commands
├── .env.example                    # Environment template
└── DOCUMENTATION_INDEX.md          # Full documentation

```

---

## 🔧 Common Commands

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api-gateway
docker-compose logs -f frontend
docker-compose logs -f postgres
```

### Database Access
```bash
# Connect to PostgreSQL
psql postgresql://postgres:postgres@localhost:5432/guardianship_db

# or use Docker
docker-compose exec postgres psql -U postgres -d guardianship_db
```

### Backend Development
```bash
# Access backend container
docker-compose exec api-gateway bash

# Install additional Python packages
docker-compose exec api-gateway pip install <package>

# Run tests
docker-compose exec api-gateway pytest tests/
```

### Frontend Development
```bash
# Access frontend container
docker-compose exec frontend sh

# Install additional npm packages
docker-compose exec frontend npm install <package>
```

---

## 🧪 Testing the System

### 1. Test API Signup
```bash
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!",
    "user_type": "guardian",
    "full_name": "Test Guardian"
  }'
```

### 2. Test API Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/signin \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!"
  }'
```

### 3. Test Protected Endpoint
```bash
# Replace TOKEN with actual token from login
curl -X GET http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer TOKEN"
```

### 4. Create a Transaction
```bash
curl -X POST http://localhost:8000/api/v1/transactions/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 50.00,
    "merchant_name": "Target",
    "merchant_category": "Retail"
  }'
```

---

## 🐛 Troubleshooting

### Services Won't Start
```bash
# Check Docker is running
docker ps

# View detailed error logs
docker-compose logs

# Rebuild containers
docker-compose build --no-cache
docker-compose up
```

### API Not Responding
```bash
# Check if API container is healthy
docker-compose ps

# View API logs
docker-compose logs api-gateway

# Try restarting
docker-compose restart api-gateway
```

### Database Connection Issues
```bash
# Test database connection
docker-compose exec postgres pg_isready

# Check database logs
docker-compose logs postgres
```

### Port Already in Use
If ports are already in use, edit `docker-compose.yml`:
```yaml
ports:
  - "9000:8000"  # Change 9000 to available port
```

---

## 📋 Phase 1 Features Implemented

✅ **Backend (FastAPI)**
- API Gateway with FastAPI
- User authentication (signup/signin)
- Role-based users (beneficiary, guardian, advisor)
- Database models (PostgreSQL)
- Transaction management
- Guardian relationships
- Health check endpoints
- Audit logging infrastructure
- CORS support

✅ **Frontend (React)**
- Login page with signup option
- Guardian dashboard
- Navigation structure
- Transaction list view
- Beneficiary management
- Responsive design
- Accessibility basics (WCAG A)

✅ **Infrastructure**
- Docker containerization
- Docker Compose orchestration
- PostgreSQL database
- Redis caching (ready)
- Environment configuration
- Makefile for common tasks

---

## 🚀 Next Steps

### Phase 1.5 (Next Iteration)
1. Add database migrations (Alembic)
2. Implement more transaction validation
3. Add fraud detection rule engine (basic)
4. Create better error handling
5. Add logging system

### Phase 2 (Months 4-6)
1. Machine learning models for fraud detection
2. Advanced transaction analysis
3. More comprehensive dashboards
4. Guardian approval workflows
5. Notification system

See [IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP.md) for full timeline.

---

## 📖 Documentation

- **Full System Design**: [DESIGN.md](DESIGN.md)
- **Technical Specifications**: [TECHNICAL_SPEC.md](TECHNICAL_SPEC.md)
- **Accessibility Guide**: [ACCESSIBILITY_SPEC.md](ACCESSIBILITY_SPEC.md)
- **Implementation Roadmap**: [IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP.md)
- **Deployment Guide**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **Quick Reference**: [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

---

## 💡 Development Tips

### Hot Reload
Both backend and frontend have hot reload enabled:
- **Backend**: Changes to `src/` auto-reload
- **Frontend**: Changes to `src/` trigger rebuild

### Database Queries
```bash
# Connect to PostgreSQL CLI
docker-compose exec postgres psql -U postgres -d guardianship_db

# Useful queries
\dt                    # List tables
\d users              # Describe table
SELECT * FROM users;  # Query data
```

### API Debugging
- Use the interactive API docs: http://localhost:8000/docs
- Use curl or Postman for API testing
- Check logs with `docker-compose logs api-gateway`

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:
- Code style (Black, Flake8)
- Commit conventions
- Pull request process
- Testing requirements

---

## 📞 Support

For issues or questions:
1. Check [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) troubleshooting section
2. Review API logs: `docker-compose logs api-gateway`
3. Check database: `docker-compose logs postgres`
4. Open an issue on GitHub

---

**Status**: ✅ Phase 1 Foundation Complete  
**Last Updated**: May 20, 2024  
**Ready to Run**: Yes, follow quick start above

