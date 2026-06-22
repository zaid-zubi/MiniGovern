# MiniGovern

MiniGovern is a lightweight data governance platform that scans databases, discovers datasets, detects sensitive information (PII), and manages dataset approval workflows.

The system allows organizations to:

* Connect external data sources
* Scan and profile datasets
* Detect sensitive fields (PII)
* Manage dataset metadata and tags
* Add category for datasources
* Submit datasets for approval
* Approve or reject datasets through a governance workflow
* Send notifications for governance actions

---

#### FastAPI Application

Responsible for:

* Authentication & Authorization
* RBAC
* Datasets Management
* User Management
* Categories Management
* Tags Management
* Approval Workflows
* Scan Requests
* Enrichment & PII validation
* Send Notification
* Catalog APIs

#### PostgreSQL

##Database Schema
The application database contains the following tables:

- users
- datasources
- categories
- category_datasource
- scan_jobs
- table_catalogs
- column_catalogs
- datasets
- tags
- dataset_tags
- audit_logs

#### MySQL Source Database

Acts as a sample external data source that can be scanned and profiled.

#### Background Workers

Responsible for:

* Executing scan jobs
* Profiling datasets
* Detecting PII
* Processing asynchronous tasks

---

# Features

## Authentication & Authorization

* JWT-based authentication
* Role-based access control
* Admin and standard user roles

## Data Source Management

* Register data sources
* Manage external database connections

## Dataset Discovery

* Scan external databases
* Discover tables and columns
* Build catalog entries

## PII Detection

Automatic detection of:

* Email addresses
* Phone numbers
* Countries
* Other supported patterns

## Governance Workflow

* Submit datasets
* Review datasets
* Approve or reject datasets
* Track approval status

## Notifications

* Trigger notifications after governance actions

---

# Technology Stack

| Component             | Technology    |
| --------------------- | ------------- |
| API                   | FastAPI       |
| ORM                   | SQLAlchemy    |
| Validation            | Pydantic      |
| Database              | PostgreSQL    |
| Source Database       | MySQL         |
| Migrations            | Alembic       |
| Authentication        | JWT           |
| Testing               | Pytest        |
| HTTP Client           | HTTPX         |
| Background Processing | Async Workers |
---

# Prerequisites

* Python 3.12+
* PostgreSQL 15+
* MySQL 8+

---

# Local Setup

## 1. Clone Repository

```bash
git clone <repository-url>
cd MiniGovern
```

## 2. Install Dependencies

```bash
poetry install
```

## 3. Configure Environment Variables

Create a local environment file:

```bash
cp .env.example .env
```

Update required values:

```env
APP_ENV=development
DEBUG=false
LOG_LEVEL=INFO

DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/MiniGovern
SOURCE_DATABASE_URL=mysql+asyncmy://reader:reader_pass@localhost:3306/source_db

HOST=127.0.0.1
PORT=8000

JWT_SECRET_KEY=your-jwt-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

ENCRYPTION_KEY=your-fernet-encryption-key

SMTP_HOST=localhost
SMTP_PORT=1025
SMTP_USER=
SMTP_PASSWORD=
EMAIL_FROM=noreply@minigovern.local

COUNTRY_API=
```

---

## 4. Run Database Migrations
- You have to create MiniGovern in your local machine

```bash
alembic upgrade head
```

---

## 5. Create Default Admin User

```bash
python scripts/seed_admin.py 
```
OR
```bash
make defaultAdmin
```

---

## 6. Start Application

```bash
uvicorn app.main:app --reload
```

Application:

```text
http://localhost:8000
```

Swagger Documentation:

```text
http://localhost:8000/docs
```

---

# Running Tests

Run all tests:

```bash
PYTHONPATH=. pytest
```

Run with coverage:

```bash
PYTHONPATH=. pytest --cov
```

---
## E. Example Flow (Full System)

### 1. Register user

```bash
curl -X POST http://localhost:8000/auth/register \
-H "Content-Type: application/json" \
-d '{"email":"user@test.com","password":"Test123!"}'
```

---

### 2. Create data source

```bash
curl -X POST http://localhost:8000/datasources \
-H "Authorization: Bearer <token>" \
-d '{"name":"My DB","type":"mysql"}'
```

---

### 3. Run scan

```bash
curl -X POST http://localhost:8000/scans \
-H "Authorization: Bearer <token>" \
-d '{"datasource_id":1}'
```

---

### 4. Poll scan status

```bash
curl http://localhost:8000/scans/1/status \
-H "Authorization: Bearer <token>"
```

---

### 5. View catalog with PII tags

```bash
curl http://localhost:8000/catalog/1 \
-H "Authorization: Bearer <token>"
```

---

### 6. Submit dataset

```bash
curl -X POST http://localhost:8000/datasets/1/submit \
-H "Authorization: Bearer <token>"
```

---

### 7. Approve dataset

```bash
curl -X POST http://localhost:8000/datasets/1/approve \
-H "Authorization: Bearer <token>"
```

---

### 8. Email notification

Triggered automatically after approval (via worker).

---

# Design Decisions

## Why Async Processing?

Scanning databases and profiling datasets can be expensive operations.

Using asynchronous processing:

* Prevents API blocking
* Improves responsiveness
* Supports larger scans
* Allows future horizontal scaling

## Why Separate Source and Application Databases?

The application database stores governance metadata while source databases contain business data.

This separation:

* Reflects real-world governance platforms
* Improves security
* Keeps scanning logic isolated

## Why Modular Services?

The system was designed to make future extensions easier.

Examples:

* Add new PII detectors
* Support new database engines
* Introduce new approval workflows
* Integrate external notification providers

---

# Limitations

The following items were intentionally left out due to assignment scope:

* Frontend dashboard
* Advanced analytics
* Real-time notifications

---

# Future Improvements

Given additional time, I would implement:

* Frontend dashboard
* Redis caching
* Distributed task queue
* More advanced PII detection
* Audit logging
* Scan scheduling
* Dataset versioning
* Monitoring and observability
* CI/CD deployment pipeline

---

# Assignment Notes

Development Time: **6 Days**

The focus of this implementation was:

* Clean architecture
* Maintainability
* Extensibility
* Testability
* Real-world governance workflow design
