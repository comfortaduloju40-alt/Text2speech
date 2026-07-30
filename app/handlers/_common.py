"""
Shared helpers used across multiple handlers.
"""

from sqlalchemy.orm import Session

from app.models import User, UserSettings


def get_or_create_user(db: Session, tg_user) -> User:
    """
    Fetches the User for this Telegram user, creating them (and a
    default UserSettings row) if this is their first interaction.
    """
    user = db.query(User).filter(User.telegram_id == tg_user.id).first()
    if user is None:
        user = User(
            telegram_id=tg_user.id,
            username=tg_user.username,
            first_name=tg_user.first_name,
        )
        db.add(user)
        db.flush()

    if user.settings is None:
        db.add(UserSettings(user_id=user.id))
        db.flush()

    return user
