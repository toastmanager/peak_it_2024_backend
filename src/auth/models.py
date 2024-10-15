import uuid
from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from src.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4
    )
    phone_number: Mapped[str] = mapped_column(unique=True, index=True)


class AuthCode(Base):
    __tablename__ = "auth_codes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4
    )
    phone_number: Mapped[str] = mapped_column(index=True)
    code: Mapped[str] = mapped_column()
    expiry: Mapped[datetime] = mapped_column(DateTime(timezone=True))
