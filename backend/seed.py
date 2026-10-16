"""Populate the SQLite DB with demo users and tickets: `python seed.py`"""
import random
from datetime import datetime, timedelta, timezone

from app import crud, schemas
from app.database import Base, SessionLocal, engine
from app.models import Category, Priority, Role, Status, Ticket

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
db = SessionLocal()


def mk(name, email, role, dept):
    data = schemas.UserCreate(name=name, email=email, password="password123", department=dept)
    return crud.create_user(db, data, force_role=role)


mk("Admin User", "admin@example.com", Role.admin, "ICT")
agents = [mk("Grace Agent", "grace@example.com", Role.it_agent, "ICT"),
          mk("Peter Agent", "peter@example.com", Role.it_agent, "ICT")]
users = [mk("Jane Student", "jane@example.com", Role.student, "Civil Engineering"),
         mk("Tom Staff", "tom@example.com", Role.staff, "Finance")]

samples = [
    ("Forgot my portal password", Category.password_reset),
    ("Printer in Library jams", Category.printer),
    ("Lab 3 PC won't boot", Category.desktop),
    ("WiFi drops in Hostel B", Category.wifi),
    ("Projector cable missing", Category.other),
]
now = datetime.now(timezone.utc)
for _ in range(30):
    title, cat = random.choice(samples)
    created = now - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))
    status = random.choice(list(Status))
    t = Ticket(title=title, description="Seeded demo ticket.", category=cat, priority=random.choice(list(Priority)),
               status=status, created_by=random.choice(users).id, created_at=created,
               assigned_to=None if status == Status.open else random.choice(agents).id)
    if status in (Status.resolved, Status.closed):
        t.resolved_at = created + timedelta(hours=random.randint(1, 72))
    db.add(t)
db.commit()
print("Seeded. Log in as admin@example.com / password123")
