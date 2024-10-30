from datetime import datetime
import uuid

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import UUID

from src.core.database import Base


class User(Base):
    id: Mapped[uuid.UUID] = mapped_column(
        UUID, primary_key=True, index=True, default=uuid.uuid4
    )
    phone: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    superuser: Mapped[bool] = mapped_column(default=False, nullable=False)
    active: Mapped[bool] = mapped_column(default=True, nullable=False)


class BlacklistToken(Base):
    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))

    user: Mapped["User"] = relationship()


class AuthCode(Base):
    id: Mapped[uuid.UUID] = mapped_column(
        UUID, primary_key=True, index=True, default=uuid.uuid4
    )
    code: Mapped[str] = mapped_column()
    phone: Mapped[str] = mapped_column()
    expiry: Mapped[datetime] = mapped_column(DateTime(timezone=True))