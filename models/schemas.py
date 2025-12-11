"""
SQLAlchemy ORM models for the shop bot database.
"""
import json
from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    Column, Integer, String, Float, Text, 
    DateTime, ForeignKey, Boolean
)
from sqlalchemy.orm import relationship

from models.db import Base


class User(Base):
    """User model - represents Telegram users."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tg_id = Column(Integer, unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    language = Column(String(5), default="uk")
    
    # User state for multi-step conversations
    state = Column(String(100), nullable=True)
    state_data = Column(Text, nullable=True)  # JSON string
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    carts = relationship("Cart", back_populates="user")
    orders = relationship("Order", back_populates="user")
    feedbacks = relationship("Feedback", back_populates="user")
    
    def set_state_data(self, data: dict):
        """Set state data as JSON."""
        self.state_data = json.dumps(data) if data else None
    
    def get_state_data(self) -> Optional[dict]:
        """Get state data from JSON."""
        return json.loads(self.state_data) if self.state_data else None
    
    def __repr__(self):
        return f"<User(tg_id={self.tg_id}, name={self.first_name})>"


class Item(Base):
    """Item model - represents shop products."""
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sku = Column(String(50), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    
    # JSON arrays stored as text
    sizes = Column(Text, nullable=False)  # ["38", "39", "40"]
    images = Column(Text, nullable=True)  # ["file_id_1", "file_id_2"]
    
    category = Column(String(50), nullable=True)  # men/women/kids
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    cart_items = relationship("CartItem", back_populates="item")
    order_items = relationship("OrderItem", back_populates="item")
    
    def get_sizes(self) -> List[str]:
        """Get sizes as list."""
        return json.loads(self.sizes) if self.sizes else []
    
    def set_sizes(self, sizes: List[str]):
        """Set sizes from list."""
        self.sizes = json.dumps(sizes)
    
    def get_images(self) -> List[str]:
        """Get image file IDs as list."""
        return json.loads(self.images) if self.images else []
    
    def set_images(self, images: List[str]):
        """Set image file IDs from list."""
        self.images = json.dumps(images)
    
    def get_first_image(self) -> Optional[str]:
        """Get first image file ID."""
        imgs = self.get_images()
        return imgs[0] if imgs else None
    
    def __repr__(self):
        return f"<Item(sku={self.sku}, name={self.name})>"


class Cart(Base):
    """Cart model - shopping cart for users."""
    __tablename__ = "carts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="carts")
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Cart(id={self.id}, user_id={self.user_id})>"


class CartItem(Base):
    """CartItem model - items in shopping cart."""
    __tablename__ = "cart_items"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    cart_id = Column(Integer, ForeignKey("carts.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    size = Column(String(10), nullable=False)
    quantity = Column(Integer, default=1)
    
    # Relationships
    cart = relationship("Cart", back_populates="items")
    item = relationship("Item", back_populates="cart_items")
    
    def __repr__(self):
        return f"<CartItem(item_id={self.item_id}, size={self.size}, qty={self.quantity})>"


class Order(Base):
    """Order model - customer orders."""
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_number = Column(String(50), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    total = Column(Float, nullable=False)
    
    # Status: pending, confirmed, paid, shipped, cancelled
    status = Column(String(20), default="pending")
    
    delivery_method = Column(String(50), nullable=True)  # pickup/delivery
    address = Column(Text, nullable=True)
    phone = Column(String(20), nullable=True)
    
    # Promo code
    promo_code = Column(String(50), nullable=True)
    discount = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Order(number={self.order_number}, status={self.status})>"


class OrderItem(Base):
    """OrderItem model - items in order."""
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    size = Column(String(10), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)  # Price at time of order
    
    # Relationships
    order = relationship("Order", back_populates="items")
    item = relationship("Item", back_populates="order_items")
    
    def subtotal(self) -> float:
        """Calculate subtotal for this item."""
        return self.price * self.quantity
    
    def __repr__(self):
        return f"<OrderItem(order_id={self.order_id}, item_id={self.item_id})>"


class Feedback(Base):
    """Feedback model - user feedback."""
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="feedbacks")
    
    def __repr__(self):
        return f"<Feedback(user_id={self.user_id})>"


class PromoCode(Base):
    """PromoCode model - discount codes."""
    __tablename__ = "promo_codes"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False)
    discount_percent = Column(Float, nullable=False)  # 10.0 for 10%
    
    valid_until = Column(DateTime, nullable=True)
    usage_limit = Column(Integer, nullable=True)
    usage_count = Column(Integer, default=0)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def is_valid(self) -> bool:
        """Check if promo code is valid."""
        if not self.is_active:
            return False
        
        if self.valid_until and datetime.utcnow() > self.valid_until:
            return False
        
        if self.usage_limit and self.usage_count >= self.usage_limit:
            return False
        
        return True
    
    def __repr__(self):
        return f"<PromoCode(code={self.code}, discount={self.discount_percent}%)>"