from typing import Optional, List

from pydantic import BaseModel


class ItemBase(BaseModel):
    name: str
    quantity: int
    price: float


class ItemUpdate(BaseModel):
    name: str
    quantity: int
    price: float


class ItemSell(BaseModel):
    name: str
    quantity: int


class ItemCreate(ItemBase):
    pass


class WholesaleSale(BaseModel):
    buyer: str
    extra_info: Optional[str]
    items: List[ItemSell]


class RetailSale(BaseModel):
    extra_info: Optional[str]
    items: List[ItemSell]


class ItemOut(ItemBase):
    id: int

    class Config:
        orm_mode = True
