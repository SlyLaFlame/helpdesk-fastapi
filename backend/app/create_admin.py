"""Create an admin account. Run from the backend folder:  python create_admin.py"""
import getpass
import sys

from fastapi import HTTPException

from app import crud, models, schemas
from app.database import SessionLocal


def main() -> None:
    name = input("Name: ").strip()
    email = input("Email: ").strip()
    department = input("Department [ICT]: ").strip() or "ICT"
    password = getpass.getpass("Password (min 12 chars): ")
    if len(password) < 12:
        sys.exit("Password too short.")
    if password != getpass.getpass("Confirm password: "):
        sys.exit("Passwords don't match.")

    data = schemas.UserCreate(name=name, email=email, password=password, department=department)
    with SessionLocal() as db:
        try:
            user = crud.create_user(db, data, force_role=models.Role.admin)
        except HTTPException as e:
            sys.exit(e.detail)
    print(f"Admin created: {user.email}")


if __name__ == "__main__":
    main()