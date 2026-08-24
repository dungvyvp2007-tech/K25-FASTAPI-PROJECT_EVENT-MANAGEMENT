from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from models.user import User


def get_my_profile(current_user: User) -> User:
    return current_user


def get_users(db: Session, query: str | None = None) -> list[User]:
    statement = select(User)
    if query:
        statement = statement.where(
            or_(User.email.contains(query), User.full_name.contains(query))
        )
    return list(db.scalars(statement.order_by(User.id.desc())).all())
