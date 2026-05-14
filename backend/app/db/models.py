import uuid
from sqlalchemy import Column, String, BigInteger, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from .database import Base

class Family(Base):
    __tablename__ = "families"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invite_code = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    users = relationship("User", back_populates="family")
    categories = relationship("Category", back_populates="family")
    products = relationship("Product", back_populates="family")

class User(Base):
    __tablename__ = "users"

    telegram_id = Column(BigInteger, primary_key=True, index=True)
    family_id = Column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=True)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    language = Column(String, default="en", nullable=False, server_default="en")

    family = relationship("Family", back_populates="users")
    subscriptions = relationship("ProductSubscription", back_populates="user")

class Category(Base):
    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id = Column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False)
    name = Column(String, nullable=False)

    family = relationship("Family", back_populates="categories")
    products = relationship("Product", back_populates="category")

class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id = Column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)
    
    name = Column(String, nullable=False)
    lemma = Column(String, nullable=True)
    emoji = Column(String, nullable=True)
    description = Column(String, nullable=True)
    quantity = Column(Float, default=0.0)
    unit = Column(String, nullable=True)

    family = relationship("Family", back_populates="products")
    category = relationship("Category", back_populates="products")
    subscriptions = relationship("ProductSubscription", back_populates="product")

class ProductSubscription(Base):
    __tablename__ = "product_subscriptions"

    user_id = Column(BigInteger, ForeignKey("users.telegram_id"), primary_key=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), primary_key=True)

    user = relationship("User", back_populates="subscriptions")
    product = relationship("Product", back_populates="subscriptions")
