from datetime import datetime, timedelta

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from .models import Order  # Импортируем модель


class OrderRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_order(
            self,
            user_id: int,
            name: str,
            phone: str,
            email: str,
            city: str,
            car_model: str,
            budget: str,
            username: Optional[str] = None,
    ) -> Order:
        """Создание новой заявки"""
        order = Order(
            user_id=user_id,
            username=username,
            name=name,
            phone=phone,
            email=email,
            city=city,
            car_model=car_model,
            budget=budget
        )

        self.session.add(order)
        await self.session.commit()
        return order

    async def get_order_by_id(self, order_id: int) -> Optional[Order]:
        """Получение заявки по ID"""
        result = await self.session.execute(
            sa.select(Order).where(Order.id == order_id)
        )
        return result.scalar_one_or_none()

    async def get_all_orders(self) -> List[Order]:
        result = await self.session.execute(
            sa.select(Order).order_by(sa.desc(Order.created_at))
        )
        return result.scalars().all()

    async def get_user_orders(self, user_id: int) -> List[Order]:
        """Получение всех заявок пользователя"""
        result = await self.session.execute(
            sa.select(Order)
            .where(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
        )
        return result.scalars().all()

    async def get_recent_orders(self, hours: int = 24) -> List[Order]:
        """Получение свежих заявок"""
        from sqlalchemy import func
        recent_time = datetime.now() - timedelta(hours=hours)

        result = await self.session.execute(
            sa.select(Order)
            .where(Order.created_at >= recent_time)
            .order_by(Order.created_at.desc())
        )
        return result.scalars().all()

    async def update_order_status(self, order_id: int, status: str) -> Optional[Order]:
        """Обновление статуса заявки"""
        order = await self.get_order_by_id(order_id)
        if order:
            order.status = status
            await self.session.commit()
        return order