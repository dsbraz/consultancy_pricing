from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, Date
from sqlalchemy.orm import relationship
from app.database import Base


class Professional(Base):
    __tablename__ = "professionals"

    id = Column(Integer, primary_key=True, index=True)
    pid = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, index=True, nullable=False)
    role = Column(String, nullable=False)
    level = Column(String, nullable=False)
    is_template = Column(Boolean, default=False, nullable=False)
    hourly_cost = Column(Float, default=0.0, nullable=False)

    project_allocations = relationship(
        "ProjectAllocation", back_populates="professional"
    )


class Offer(Base):
    __tablename__ = "offers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)

    items = relationship("OfferItem", back_populates="offer")


class OfferItem(Base):
    __tablename__ = "offer_items"

    id = Column(Integer, primary_key=True, index=True)
    offer_id = Column(Integer, ForeignKey("offers.id"), nullable=False)
    professional_id = Column(Integer, ForeignKey("professionals.id"), nullable=False)

    allocation_percentage = Column(Float, default=100.0, nullable=False)

    offer = relationship("Offer", back_populates="items")
    professional = relationship("Professional")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    start_date = Column(Date, nullable=False)
    duration_months = Column(Integer, nullable=False)
    tax_rate = Column(Float, default=0.0, nullable=False)
    margin_rate = Column(Float, default=0.0, nullable=False)

    allocations = relationship("ProjectAllocation", back_populates="project")


class ProjectAllocation(Base):
    __tablename__ = "project_allocations"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    professional_id = Column(Integer, ForeignKey("professionals.id"), nullable=False)
    selling_hourly_rate = Column(
        Float, default=0.0, nullable=False
    )  # Fixed selling rate for this professional in this project

    project = relationship("Project", back_populates="allocations")
    professional = relationship("Professional", back_populates="project_allocations")
    weekly_allocations = relationship(
        "WeeklyAllocation", back_populates="allocation", cascade="all, delete-orphan"
    )


class WeeklyAllocation(Base):
    __tablename__ = "weekly_allocations"

    id = Column(Integer, primary_key=True, index=True)
    allocation_id = Column(
        Integer, ForeignKey("project_allocations.id"), nullable=False
    )
    week_number = Column(Integer, nullable=False)  # Sequential: 1, 2, 3...
    hours_allocated = Column(Float, default=0.0, nullable=False)
    available_hours = Column(
        Float, nullable=False
    )  # Business hours available in this week

    allocation = relationship("ProjectAllocation", back_populates="weekly_allocations")
