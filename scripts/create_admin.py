import os
from getpass import getpass

from dotenv import load_dotenv

load_dotenv()

from backend_service.services.auth_service import get_user_by_email, create_user
from backend_service.models import RoleEnum


def main():
    email = os.getenv("ADMIN_EMAIL") or input("Admin email: ")
    password = os.getenv("ADMIN_PASSWORD") or getpass("Admin password: ")
    if not email or not password:
        print("ADMIN_EMAIL and ADMIN_PASSWORD must be provided")
        return

    existing = get_user_by_email(email)
    if existing:
        print("Admin already exists")
        return

    user = create_user(email=email, password=password, role=RoleEnum.admin)
    print(f"Created admin: {user.email}")


if __name__ == '__main__':
    main()
