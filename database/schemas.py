from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class OrderCreateSchema(BaseModel):
    user_id: int
    username: Optional[str]
    name: str
    phone: str
    email: str
    city: str
    car_model: str
    budget: str

class OrderSchema(OrderCreateSchema):
    id: int
    status: str = "new"
    created_at: datetime
    updated_at: datetime