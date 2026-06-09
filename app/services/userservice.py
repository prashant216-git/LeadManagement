from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.User import User


class UserService:

    @staticmethod
    def get_user(
        db: Session,
        phone_number: str | None = None,
        email: str | None = None
    ) -> User | None:

        if not phone_number and not email:
            raise ValueError(
                "phone_number or email is required"
            )

        query = db.query(User)

        conditions = []

        if phone_number:
            conditions.append(
                User.phone_number == phone_number
            )

        if email:
            conditions.append(
                User.email == email
            )

        return query.filter(
            or_(*conditions)
        ).first()

    @staticmethod
    def create_user(
        db: Session,
        phone_number: str | None = None,
        email: str | None = None,
        name: str | None = None
    ) -> User:

        if not phone_number and not email:
            raise ValueError(
                "phone_number or email is required"
            )

        user = User(
            name=name,
            email=email,
            phone_number=phone_number
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def get_or_create_user(
        db: Session,
        phone_number: str | None = None,
        email: str | None = None,
        name: str | None = None
    ) -> User:

        user = UserService.get_user(
            db=db,
            phone_number=phone_number,
            email=email
        )

        if user:
            return user

        return UserService.create_user(
            db=db,
            phone_number=phone_number,
            email=email,
            name=name
        )

    @staticmethod
    def get_user_by_id(
            db: Session,
            user_id: int
    ):
        return (
            db.query(User)
            .filter(
                User.id == user_id
            )
            .first()
        )