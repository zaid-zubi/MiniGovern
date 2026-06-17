# MiniGovern — README

## A. Setup Steps

### 1. Install dependencies

```bash
poerty install | make install
```

---

### 2. Configure `.env`

Copy example file and configure environment variables:

```bash
cp .env.example .env
```

Update required values:
 
```
DATABASE_URL=postgresql://user:password@localhost:5432/minigovern
MYSQL_URL=mysql://user:password@localhost:3306/minigovern
SECRET_KEY=your_secret_key
```

---

### 3. Run Postgres migrations

```bash
alembic upgrade head
```

---

### 4. Load MySQL seed script

```bash
mysql -u root -p minigovern < seeds/mysql_seed.sql
```

---

### 5. Start API

```bash
uvicorn app.main:app --reload
```

---

### 6. Start background worker

```bash
python worker.py
```

---

## B. Tech Versions

* Python: 3.11+
* PostgreSQL: 14+
* MySQL: 8+

---

## C. How to Run Tests

Run all tests with:

```bash
pytest
```

---

## D. Admin User Setup

### Option 1: Seeder (recommended)

```bash
python scripts/seed_admin.py
```

### Option 2: API (if enabled)

Send request to register admin user and assign role manually in DB.

Default admin credentials (if seeded):

```
email: admin@minigovern.com
password: Admin123!
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

## F. Design Notes

### Key Decisions

* Separated API and background worker for scalability
* Used Postgres for metadata and MySQL for source simulation
* Async processing for scan jobs

---

### Trade-offs

* Simplified permissions model for faster delivery
* Basic worker instead of full queue system (e.g., Celery)
* Limited frontend (API-first approach)

---

### What was NOT implemented

* Advanced RBAC system
* Distributed task queue (Redis/Celery)
* Full frontend dashboard

---

### What I would improve

* Replace custom worker with queue-based system
* Add caching layer for scan results
* Improve observability (logs + metrics)
* Add full frontend UI

---
