from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, Date
from sqlalchemy.orm import relationship
from app.database import Base

class Professional(Base):
    __tablename__ = "professionals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    role = Column(String)
    level = Column(String)
    is_vacancy = Column(Boolean, default=False)
    hourly_cost = Column(Float, default=0.0)

    project_allocations = relationship("ProjectAllocation", back_populates="professional")

class Template(Base):
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    items = relationship("TemplateItem", back_populates="template")

class TemplateItem(Base):
    __tablename__ = "template_items"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("templates.id"))
    professional_id = Column(Integer, ForeignKey("professionals.id"), nullable=True)
    role = Column(String)
    level = Column(String)
    quantity = Column(Integer, default=1)
    allocation_percentage = Column(Float, default=100.0)

    template = relationship("Template", back_populates="items")
    professional = relationship("Professional")

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    start_date = Column(Date)
    duration_months = Column(Integer)
    tax_rate = Column(Float, default=0.0)
    margin_rate = Column(Float, default=0.0)
    
    allocations = relationship("ProjectAllocation", back_populates="project")

class ProjectAllocation(Base):
    __tablename__ = "project_allocations"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    professional_id = Column(Integer, ForeignKey("professionals.id"))
    selling_hourly_rate = Column(Float, default=0.0)  # Fixed selling rate for this professional in this project

    project = relationship("Project", back_populates="allocations")
    professional = relationship("Professional", back_populates="project_allocations")
    weekly_allocations = relationship("WeeklyAllocation", back_populates="allocation", cascade="all, delete-orphan")

class WeeklyAllocation(Base):
    __tablename__ = "weekly_allocations"

    id = Column(Integer, primary_key=True, index=True)
    allocation_id = Column(Integer, ForeignKey("project_allocations.id"))
    week_number = Column(Integer)  # Sequential: 1, 2, 3...
    week_start_date = Column(Date)  # Monday of the week
    hours_allocated = Column(Float, default=0.0)
    available_hours = Column(Float)  # Business hours available in this week
    
    allocation = relationship("ProjectAllocation", back_populates="weekly_allocations")
