from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from database.repository import OrderRepository
from database.schemas import OrderCreateSchema
from .models import Order


class OrderService:
    def __init__(self, session: AsyncSession):
        self.repo = OrderRepository(session)

    async def create_order(self, data: OrderCreateSchema) -> Order:
        order = await self.repo.create_order(**data.model_dump())
        return order

    async def get_all_orders(self) -> List[Order]:
        orders = await self.repo.get_all_orders()
        return orders

    async def get_order_by_id(self, order_id: int) -> Optional[Order]:
        order = await self.repo.get_order_by_id(order_id)
        if not order:
            raise ValueError(f"Заявка #{order_id} не найдена")
        return order
