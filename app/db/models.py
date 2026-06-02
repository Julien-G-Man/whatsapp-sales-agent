from datetime import datetime
from sqlalchemy import (
    Integer, String, Boolean, DateTime, Text, Enum, ForeignKey, func, JSON
)
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship
from typing import Optional, List


class Base(DeclarativeBase):
    pass


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    name_aliases: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)
    price_xaf: Mapped[int] = mapped_column(Integer, nullable=False)
    stock_qty: Mapped[int] = mapped_column(Integer, default=0)
    low_stock_threshold: Mapped[int] = mapped_column(Integer, default=5)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer_phone: Mapped[str] = mapped_column(String, nullable=False)
    items: Mapped[Optional[dict]] = mapped_column(JSON)
    total_xaf: Mapped[Optional[int]] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(
        Enum("pending", "paid", "fulfilled", "cancelled", "payment_failed", name="order_status"),
        default="pending",
    )
    momo_ref: Mapped[Optional[str]] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    transactions: Mapped[List["Transaction"]] = relationship("Transaction", back_populates="order")


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("orders.id"))
    momo_ref: Mapped[str] = mapped_column(String, unique=True)
    amount_xaf: Mapped[int] = mapped_column(Integer)
    customer_phone: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(
        Enum("initiated", "confirmed", "failed", name="transaction_status"),
        default="initiated",
    )
    confirmed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    order: Mapped[Optional["Order"]] = relationship("Order", back_populates="transactions")


class ConversationMessage(Base):
    __tablename__ = "conversation_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    phone: Mapped[str] = mapped_column(String, nullable=False, index=True)
    role: Mapped[str] = mapped_column(Enum("user", "assistant", name="message_role"))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
