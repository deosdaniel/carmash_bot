import sqlalchemy as sa
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from typing import Optional
from datetime import datetime


# Базовый класс для моделей SQLAlchemy 2.0
class Base(DeclarativeBase):
    pass


# Модель заказа с синтаксисом SQLAlchemy 2.0
class OrderModel(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(sa.BigInteger, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(sa.String(100))
    first_name: Mapped[Optional[str]] = mapped_column(sa.String(100))
    last_name: Mapped[Optional[str]] = mapped_column(sa.String(100))
    name: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    phone: Mapped[str] = mapped_column(sa.String(20), nullable=False)
    email: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    car_model: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    budget: Mapped[str] = mapped_column(sa.String(50), nullable=False)
    status: Mapped[str] = mapped_column(sa.String(20), default="new")
    created_at: Mapped[datetime] = mapped_column(default=sa.func.now())
    updated_at: Mapped[datetime] = mapped_column(
        default=sa.func.now(),
        onupdate=sa.func.now()
    )


class Database:
    def __init__(self, database_url: str):
        # Создаем асинхронный движок
        self.engine = create_async_engine(
            database_url,
            echo=True,  # Показывать SQL запросы в логах
            future=True  # Включаем режим будущего (обязательно для 2.0)
        )

        # Создаем асинхронную сессию
        self.async_session = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    async def create_tables(self):
        """Создание таблиц в базе данных"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def save_order(self, order_data: dict) -> OrderModel:
        """Сохранение заявки в базу данных"""
        async with self.async_session() as session:
            # Создаем объект модели
            order = OrderModel(**order_data)

            # Добавляем в сессию и сохраняем
            session.add(order)
            await session.commit()

            # Обновляем объект чтобы получить ID
            await session.refresh(order)
            return order

    async def get_order(self, order_id: int) -> Optional[OrderModel]:
        """Получение заявки по ID"""
        async with self.async_session() as session:
            # SQLAlchemy 2.0 стиль запросов
            stmt = sa.select(OrderModel).where(OrderModel.id == order_id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def get_user_orders(self, user_id: int) -> list[OrderModel]:
        """Получение всех заявок пользователя"""
        async with self.async_session() as session:
            stmt = sa.select(OrderModel).where(OrderModel.user_id == user_id)
            result = await session.execute(stmt)
            return result.scalars().all()