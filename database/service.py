from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from database.repository import OrderRepository
from database.schemas import OrderCreateSchema
from utils.decorators import commit_session, read_only_session
from .models import Order


class OrderService:
    def __init__(self, session_factory):
        self._session_factory = session_factory

    @commit_session
    async def create_order(
        self, session: AsyncSession, data: OrderCreateSchema
    ) -> Order:
        repo = OrderRepository(session)
        order = await repo.create_order(**data.model_dump())
        return order

    @read_only_session
    async def get_all_orders(self, session: AsyncSession) -> List[Order]:
        repo = OrderRepository(session)
        orders = await repo.get_all_orders()
        return orders

    @read_only_session
    async def get_order_by_id(
        self, session: AsyncSession, order_id: int
    ) -> Optional[Order]:
        repo = OrderRepository(session)
        order = await repo.get_order_by_id(order_id)
        return order
