from datetime import datetime
from typing import Optional

import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(sa.BigInteger, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(sa.String(100))
    name: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    phone: Mapped[str] = mapped_column(sa.String(20), nullable=False)
    email: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    city: Mapped[str] = mapped_column(sa.String(50), nullable=False)
    car_model: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    budget: Mapped[str] = mapped_column(sa.String(50), nullable=False)
    status: Mapped[str] = mapped_column(sa.String(20), default="new")
    created_at: Mapped[datetime] = mapped_column(default=sa.func.now())
    updated_at: Mapped[datetime] = mapped_column(
        default=sa.func.now(),
        onupdate=sa.func.now()
    )
