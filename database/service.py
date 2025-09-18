from sqlalchemy.ext.asyncio import AsyncSession

from database.repository import OrderRepository
from database.schemas import OrderCreateSchema


class OrderService:
    def __init__(self, session: AsyncSession):
        self.repo = OrderRepository(session)

    async def create_order(self, data: OrderCreateSchema):
        order = await self.repo.create_order(**data.model_dump())
        return order