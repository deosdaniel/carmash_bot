from typing import List, Optional

from database.repository import OrderRepository
from database.schemas import OrderCreateSchema
from .models import Order


class OrderService:
    def __init__(self, session_factory):
        self._session_factory = session_factory

    async def create_order(self, data: OrderCreateSchema) -> Order:
        async with self._session_factory() as session:
            repo = OrderRepository(session)
            try:
                order = await repo.create_order(**data.model_dump())
                await session.commit()
            except Exception:
                await session.rollback()
                raise
        return order

    async def get_all_orders(self) -> List[Order]:
        async with self._session_factory() as session:
            repo = OrderRepository(session)
            try:
                orders = await repo.get_all_orders()
            except Exception:
                await session.rollback()
                raise
        return orders

    async def get_order_by_id(self, order_id: int) -> Optional[Order]:
        async with self._session_factory() as session:
            repo = OrderRepository(session)
            try:
                order = await repo.get_order_by_id(order_id)
            except Exception:
                await session.rollback()
                raise
        if not order:
            raise ValueError(f"Заявка #{order_id} не найдена")
        return order
