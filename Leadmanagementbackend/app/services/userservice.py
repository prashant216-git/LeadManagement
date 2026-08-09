from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.Leads import Lead


class UserService:

    @staticmethod
    def get_user(
        db: Session,
        phone_number: str | None = None,
        email: str | None = None
    ) -> Lead | None:

        if not phone_number and not email:
            raise ValueError(
                "phone_number or email is required"
            )

        query = db.query(Lead)

        conditions = []

        if phone_number:
            conditions.append(
                Lead.phone_number == phone_number
            )

        if email:
            conditions.append(
                Lead.email == email
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
    ) -> Lead:

        if not phone_number and not email:
            raise ValueError(
                "phone_number or email is required"
            )

        user = Lead(
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
    ) -> Lead:

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
            db.query(Lead)
            .filter(
                Lead.id == user_id
            )
            .first()
        )