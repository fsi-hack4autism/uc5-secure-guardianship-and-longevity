# Contributing to AI Financial Guardrails

Thank you for your interest in contributing! This document provides guidelines for participating in this project.

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please treat all contributors with respect.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Create a feature branch** for your work
4. **Make your changes** following our guidelines
5. **Submit a pull request** for review

## Development Setup

```bash
# Clone and setup
git clone https://github.com/fsi-hack4autism/uc5-secure-guardianship-and-longevity.git
cd uc5-secure-guardianship-and-longevity

# Using Makefile
make setup
make up

# Or manually
cp .env.example .env
docker-compose up -d
```

## Code Style

### Backend (Python)

We use the following tools for code quality:

- **Black** for formatting
- **Flake8** for linting
- **MyPy** for type checking
- **isort** for import sorting

```bash
# Format code
black backend/api-gateway/src/

# Check linting
flake8 backend/api-gateway/src/ --max-line-length=100

# Type check
mypy backend/api-gateway/src/ --ignore-missing-imports
```

### Frontend (TypeScript/React)

- **ESLint** for linting
- **Prettier** for formatting
- **TypeScript** for type safety

```bash
# Format code
cd frontend/guardian-dashboard
npm run format

# Lint
npm run lint
```

## Commit Message Convention

Follow the conventional commits format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style changes (no logic change)
- `refactor`: Code refactoring
- `perf`: Performance improvement
- `test`: Test additions/changes
- `chore`: Build, dependencies, etc.

Examples:
```
feat(auth): add JWT token refresh endpoint
fix(fraud): handle edge case in risk calculation
docs(api): update authentication documentation
```

## Testing

### Backend Tests
```bash
# Run all tests
docker-compose exec api-gateway pytest tests/ -v

# Run specific test
docker-compose exec api-gateway pytest tests/test_auth.py -v

# With coverage
docker-compose exec api-gateway pytest tests/ --cov=src --cov-report=html
```

### Frontend Tests
```bash
cd frontend/guardian-dashboard
npm test
```

All new features should include tests. Aim for >80% code coverage.

## Pull Request Process

1. **Create descriptive PR title** following conventional commits
2. **Link related issues** using GitHub syntax (e.g., "Fixes #123")
3. **Provide detailed description** of changes
4. **Ensure all tests pass** (CI/CD will verify)
5. **Request review** from maintainers
6. **Address feedback** promptly

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Breaking change

## Testing
Describe testing done:
- [ ] Unit tests added
- [ ] Integration tests added
- [ ] Manual testing

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation is updated
- [ ] Tests pass locally
- [ ] No new warnings generated
```

## Documentation

- Update [DESIGN.md](DESIGN.md) for architecture changes
- Update [TECHNICAL_SPEC.md](TECHNICAL_SPEC.md) for technical changes
- Update [ACCESSIBILITY_SPEC.md](ACCESSIBILITY_SPEC.md) for UX/accessibility changes
- Add inline code comments for complex logic
- Update API documentation in docstrings

## Security

- **Never** commit secrets, tokens, or credentials
- Use `.env.example` for template variables
- Report security issues privately (don't post in issues)
- Follow OWASP best practices
- Keep dependencies updated

## Accessibility

All code must meet WCAG 2.1 Level AA standards:

- **Frontend**: Semantic HTML, ARIA labels, keyboard navigation
- **Backend**: Clear error messages, proper HTTP status codes
- **Documentation**: Use plain language, clear structure

See [ACCESSIBILITY_SPEC.md](ACCESSIBILITY_SPEC.md) for detailed requirements.

## Performance

- Keep API response times <500ms
- Optimize database queries (use indexes)
- Minimize frontend bundle size
- Use caching appropriately
- Monitor with APM tools

## Architecture Decisions

For significant changes:

1. **Discuss first** - Open an issue for design discussion
2. **Document decision** - Update ADRs (Architecture Decision Records)
3. **Get approval** - Require maintainer review
4. **Implement carefully** - Consider backward compatibility

## Issues

### Reporting Bugs

Provide:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment (OS, Python version, etc.)
- Error messages/logs

### Requesting Features

Provide:
- Clear use case or problem statement
- Proposed solution or examples
- Why this is important
- Any relevant references or research

## Labels

Issues are labeled to help with organization:

- `good first issue` - Good for new contributors
- `help wanted` - Extra attention needed
- `accessibility` - A11y related
- `security` - Security related
- `urgent` - High priority
- `documentation` - Doc improvements needed

## Questions?

- **Discord**: [Join our community](link-here)
- **Email**: contact@example.com
- **Discussion**: Use GitHub Discussions

## Recognition

Contributors will be:
- Added to CONTRIBUTORS.md
- Mentioned in release notes
- Thanked in documentation

---

## Development Workflow

### 1. Create Feature Branch
```bash
git checkout -b feat/my-feature
```

### 2. Make Changes
```bash
# Edit files...
# Test locally
make test
```

### 3. Commit Changes
```bash
git add .
git commit -m "feat(scope): description"
```

### 4. Push and Create PR
```bash
git push origin feat/my-feature
# Create PR on GitHub
```

### 5. Address Feedback
```bash
# Make requested changes
git add .
git commit -m "refactor: address review feedback"
git push origin feat/my-feature
```

### 6. Merge
Maintainer will merge once approved.

---

Thank you for contributing to making financial guardianship more secure and accessible! 🙏

