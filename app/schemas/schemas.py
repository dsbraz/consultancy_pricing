from typing import List, Optional
from pydantic import BaseModel
from datetime import date

# Professional Schemas
class ProfessionalBase(BaseModel):
    name: str
    role: str
    level: str
    is_vacancy: bool = False
    hourly_cost: float = 0.0

class ProfessionalCreate(ProfessionalBase):
    pass

class ProfessionalUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    level: Optional[str] = None
    is_vacancy: Optional[bool] = None
    hourly_cost: Optional[float] = None

class Professional(ProfessionalBase):
    id: int
    class Config:
        from_attributes = True

# Template Schemas
class TemplateItemBase(BaseModel):
    role: Optional[str] = None
    level: Optional[str] = None
    quantity: int = 1
    allocation_percentage: float = 100.0
    professional_id: Optional[int] = None

class TemplateItemCreate(TemplateItemBase):
    pass

class TemplateItem(TemplateItemBase):
    id: int
    template_id: int
    class Config:
        orm_mode = True

class TemplateBase(BaseModel):
    name: str

class TemplateCreate(TemplateBase):
    items: List[TemplateItemCreate] = []

class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    items: Optional[List[TemplateItemCreate]] = None

class Template(TemplateBase):
    id: int
    items: List[TemplateItem] = []
    class Config:
        from_attributes = True

# Project Schemas
class WeeklyAllocationBase(BaseModel):
    week_number: int
    week_start_date: date
    hours_allocated: float = 0.0
    available_hours: float

class WeeklyAllocationCreate(WeeklyAllocationBase):
    pass

class WeeklyAllocation(WeeklyAllocationBase):
    id: int
    class Config:
        from_attributes = True

class ProjectAllocationBase(BaseModel):
    professional_id: int
    selling_hourly_rate: float = 0.0

class ProjectAllocationCreate(ProjectAllocationBase):
    weekly_allocations: List[WeeklyAllocationCreate] = []

class ProjectAllocation(ProjectAllocationBase):
    id: int
    professional: Professional
    weekly_allocations: List[WeeklyAllocation] = []
    class Config:
        from_attributes = True

class ProjectBase(BaseModel):
    name: str
    start_date: date
    duration_months: int
    tax_rate: float
    margin_rate: float

class ProjectCreate(ProjectBase):
    allocations: List[ProjectAllocationCreate] = []

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    start_date: Optional[date] = None
    duration_months: Optional[int] = None
    tax_rate: Optional[float] = None
    margin_rate: Optional[float] = None

class Project(ProjectBase):
    id: int
    allocations: List[ProjectAllocation] = []
    class Config:
        from_attributes = True

# Pricing Calculation Schemas
class ProjectPricing(BaseModel):
    total_cost: float
    total_selling: float
    total_margin: float
    total_tax: float
    final_price: float
    final_margin_percent: float  # (Final - Cost) / Cost * 100
    monthly_breakdown: dict = {}
    weekly_breakdown: dict = {}
    class Config:
        from_attributes = True # Updated from orm_mode
