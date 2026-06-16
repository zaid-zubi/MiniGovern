
# MiniGovern — Setup & Run Guide

MiniGovern is a lightweight data governance service.

It scans databases, profiles data, detects PII, and supports dataset approval workflows.

---

# 🚀 1. Setup Project

```bash
git clone <repo>
cd minigovern
cp .env.example .env
````

---

# ⚙️ 2. Configure Environment

Generate encryption key:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Add to `.env`:

```env
ENCRYPTION_KEY=your_key
```

---

# 📦 3. Install & DB Setup

```bash
make install
make db-up
make migrate
make defaultAdmin
```

---

# ▶️ 4. Run Application

Start API:

```bash
make run
```

Open Swagger:

```
http://localhost:8000/docs
```

---

# 📧 5. Email System (IMPORTANT)

Run SMTP server in a **second terminal**:

```bash
make smtp
```

OR:

```bash
python -m aiosmtpd -n -l localhost:1025
```

Emails will appear in this terminal.

---

# 🔄 6. Full Workflow Test

1. Create data source
2. Trigger scan
3. Poll job status
4. View catalog
5. Submit dataset
6. Approve / reject dataset
7. Check email output

---

# 🧪 7. Dev Commands

```bash
make test
make lint
make format
make db-down
```

---