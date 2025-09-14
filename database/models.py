from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class OrderCreate(BaseModel):
    user_id: int
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    name: str
    phone: str
    email: str
    car_model: str
    budget: str

class Order(OrderCreate):
    id: int
    status: str = "new"
    created_at: datetime
    updated_at: datetime