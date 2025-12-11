"""
Database connection and session management.
"""
import os
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

from config import Config

# Create base class for models
Base = declarative_base()

# Create engine
engine = create_engine(
    Config.DB_URL,
    echo=False,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False} if "sqlite" in Config.DB_URL else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create scoped session for thread safety
Session = scoped_session(SessionLocal)


def init_db():
    """Initialize database - create all tables."""
    # Ensure data directory exists
    if "sqlite" in Config.DB_URL:
        db_path = Config.DB_URL.replace("sqlite:///", "")
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

    # Import all models to register them
    from models.schemas import (
        User, Item, Cart, CartItem, Order, OrderItem,
        Feedback, PromoCode
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✓ Database initialized successfully")


@contextmanager
def get_db():
    """Get database session as context manager."""
    db = Session()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def get_db_session():
    """Get database session for direct use."""
    return Session()


def close_db():
    """Close database session."""
    Session.remove()