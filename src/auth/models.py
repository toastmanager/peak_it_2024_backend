from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, validates

from src.database import Base

class User(SQLAlchemyBaseUserTableUUID, Base):
    phone: Mapped[str] = mapped_column(unique=True, index=True)
    email: Mapped[str] = mapped_column(String(length=0), unique=True, nullable=True)

    @validates('phone_number')
    def validate_phone_number(self, phone_number: str) -> str:
        if not self.is_valid_phone(phone_number):
            raise ValueError("Invalid phone number format")
        return phone_number
    
    def is_valid_phone(self, phone_number) -> bool:
        # TODO: Add phone validator
        return True