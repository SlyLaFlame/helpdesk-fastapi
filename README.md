# ICT Helpdesk — IT Support Ticket Tracker

> Modeled after the ticket workflow I manage daily at KIHBT's ICT department (password resets, printer, desktop, and WiFi issues for students and staff).

**Stack:** FastAPI · SQLAlchemy 2 · SQLite (swap to PostgreSQL via `DATABASE_URL`) · JWT auth · React 18 + Vite · Recharts

## Features
1. **CRUD**: create, list and view tickets, plus comments.
2. **Filtering & search**: `GET /tickets?status=open&category=printer&priority=high&assigned_to=2&unassigned=true&date_from=2026-01-01&date_to=2026-01-31&q=lab`. Each parameter becomes a SQLAlchemy `.where()` clause (see `crud.filter_tickets`).
3. **Status workflow**: `open → in_progress → resolved → closed`, plus "send back" and "reopen" paths. Invalid jumps return `400`. Every status, priority and assignment change is logged automatically as a system comment, giving an audit trail.
4. **Role-based permissions**: students and staff submit tickets and see only their own. IT agents see all tickets, assign them and change status. Admins can also manage user roles. The first registered user becomes admin.
5. **Analytics**: `GET /tickets/analytics` returns counts by category and status, open vs closed, and average resolution time.

## Run it

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # set SECRET_KEY
python seed.py                  # optional demo data (admin@example.com / password123)
uvicorn app.main:app --reload   # API docs at http://localhost:8000/docs

# Frontend (new terminal)
cd frontend
npm install
cp .env.example .env
npm run dev                     # http://localhost:5173
```

## Why `models.py` vs `schemas.py`
`models.py` holds the database tables (SQLAlchemy). `schemas.py` holds the API request and response shapes (Pydantic). Keeping them separate gives you validated input and clean auto-generated docs at `/docs`, and it keeps fields like `hashed_password` out of API responses.

## Next steps
- Email notifications (smtplib / SendGrid) when a ticket is assigned or resolved
- Alembic migrations, a pytest suite, and Docker Compose with PostgreSQL
