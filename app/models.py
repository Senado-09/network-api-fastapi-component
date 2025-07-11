from sqlalchemy import (
    Column, String, ForeignKey, Enum, DateTime, Boolean,
    Integer
)
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime, timedelta
import uuid


def generate_uuid():
    return str(uuid.uuid4())


class Users(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    username = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=True)
    email = Column(String(255), unique=True, nullable=True)
    password = Column(String(255), nullable=False)
    country = Column(String(255), nullable=True)
    phone_number = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True)
    sexe = Column(Enum("M", "F", "O", name="user_sexe"), nullable=True, default="O")
    verify_code = Column(String(8), nullable=True)
    expired_date = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(days=1))
    role_id = Column(String(36), ForeignKey("roles.id"), nullable=True)
    parranage_code = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # One-to-one: each user may be a commercial
    commercial = relationship(
        "Commercials",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    # Network participation (as user)
    network_members = relationship(
        "NetworkMembers",
        foreign_keys="NetworkMembers.user_id",
        back_populates="user"
    )

    # Sponsored others in the network
    sponsored_members = relationship(
        "NetworkMembers",
        foreign_keys="NetworkMembers.sponsor_id",
        back_populates="sponsor"
    )


class Commercials(Base):
    __tablename__ = "commercials"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    reference = Column(String(255), nullable=False, unique=True)
    status = Column(String(255), default="Active")
    country_operation = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("Users", back_populates="commercial")

    # One commercial → many networks
    networks = relationship(
        "Networks",
        back_populates="commercial",
        cascade="all, delete-orphan"
    )


class Networks(Base):
    __tablename__ = "networks"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    commercial_id = Column(String(36), ForeignKey("commercials.id"), nullable=True)
    plan_type = Column(String(255), nullable=False)  # e.g., '5:4'
    status = Column(String(255), default="Active")
    total_members = Column(Integer, default=0)
    max_members = Column(Integer, default=780)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    commercial = relationship("Commercials", back_populates="networks")

    members = relationship(
        "NetworkMembers",
        back_populates="network",
        cascade="all, delete-orphan"
    )


class NetworkMembers(Base):
    __tablename__ = "network_members"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    network_id = Column(String(36), ForeignKey("networks.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    sponsor_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    generation = Column(Integer, nullable=False)
    position_in_generation = Column(Integer, nullable=False)

    network = relationship("Networks", back_populates="members")

    user = relationship(
        "Users",
        foreign_keys=[user_id],
        back_populates="network_members"
    )

    sponsor = relationship(
        "Users",
        foreign_keys=[sponsor_id],
        back_populates="sponsored_members"
    )
