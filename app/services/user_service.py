from sqlalchemy import or_
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models.user import User


def get_my_profile(current_user: User) -> User:
    return current_user


def get_users(db: Session, query: str | None = None) -> list[User]:
    users_query = db.query(User)
    if query:
        users_query = users_query.filter(
            or_(User.email.contains(query), User.full_name.contains(query))
        )
    return users_query.order_by(User.id.desc()).all()
