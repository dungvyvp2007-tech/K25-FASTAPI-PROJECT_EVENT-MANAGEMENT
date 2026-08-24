from db.database import SessionLocal
from models.user import User
from core.security import hash_password


def seed_admin():
    db = SessionLocal()
    admin_email = "admin@gmail.com"

    user = db.query(User).filter(User.email == admin_email).first()
    if not user:
        admin_user = User(
            email=admin_email,
            password_hash=hash_password("admin123"),
            full_name="System Admin",
            role="ADMIN",
            is_active=True,
        )
        db.add(admin_user)
        db.commit()
        print("Đã tạo tài khoản Admin thành công!")
    else:
        print("Tài khoản Admin đã tồn tại.")
    db.close()


if __name__ == "__main__":
    seed_admin()
