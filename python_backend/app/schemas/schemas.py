from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    country: Optional[str] = None
    phone: Optional[str] = None


class UserCreate(UserBase):
    password: str
    role_id: Optional[int] = None


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    country: Optional[str] = None
    phone: Optional[str] = None
    role_id: Optional[int] = None
    is_active: Optional[bool] = None


class UserInDB(UserBase):
    id: int
    role_id: Optional[int]
    email_verified_at: Optional[datetime]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class User(UserInDB):
    pass


# Order Schemas
class OrderBase(BaseModel):
    currency_code: str


class OrderCreate(OrderBase):
    user_id: int


class OrderUpdate(BaseModel):
    currency_code: Optional[str] = None


class Order(OrderBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Service Schemas
class ServiceBase(BaseModel):
    name: str
    product_id: int
    plan_id: Optional[int] = None
    price: float = 0.00
    quantity: int = 1
    status: str = "pending"


class ServiceCreate(ServiceBase):
    user_id: int
    order_id: int


class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[int] = None


class Service(ServiceBase):
    id: int
    user_id: int
    order_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Invoice Schemas
class InvoiceItemBase(BaseModel):
    description: str
    quantity: int = 1
    price: float
    total: float


class InvoiceItemCreate(InvoiceItemBase):
    invoice_id: int


class InvoiceItem(InvoiceItemBase):
    id: int
    invoice_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InvoiceBase(BaseModel):
    status: str = "pending"
    currency_code: str
    subtotal: float = 0.00
    tax: float = 0.00
    total: float = 0.00
    due_date: Optional[datetime] = None


class InvoiceCreate(InvoiceBase):
    user_id: int


class InvoiceUpdate(BaseModel):
    status: Optional[str] = None
    total: Optional[float] = None
    tax: Optional[float] = None
    subtotal: Optional[float] = None
    due_date: Optional[datetime] = None
    paid_at: Optional[datetime] = None


class Invoice(InvoiceBase):
    id: int
    user_id: int
    paid_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    items: List[InvoiceItem] = []

    model_config = ConfigDict(from_attributes=True)


# Ticket Schemas
class TicketMessageBase(BaseModel):
    message: str
    is_staff: bool = False


class TicketMessageCreate(TicketMessageBase):
    ticket_id: int
    user_id: Optional[int] = None


class TicketMessage(TicketMessageBase):
    id: int
    ticket_id: int
    user_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TicketBase(BaseModel):
    subject: str
    status: str = "open"
    priority: str = "normal"


class TicketCreate(TicketBase):
    user_id: int


class TicketUpdate(BaseModel):
    subject: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None


class Ticket(TicketBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    messages: List[TicketMessage] = []

    model_config = ConfigDict(from_attributes=True)


# Authentication Schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None
    email: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
