from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import date


def _strip_non_empty_string(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    if not value.strip():
        raise ValueError("Campo não pode ser vazio ou conter apenas espaços")
    return value.strip()


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ProfessionalBase(BaseModel):
    pid: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    role: str = Field(..., min_length=1)
    level: str = Field(..., min_length=1)
    is_template: bool = False
    hourly_cost: float = Field(default=0.0, ge=0.0)

    @field_validator("pid", "name", "role", "level")
    @classmethod
    def validate_non_empty_string(cls, v: str) -> str:
        return _strip_non_empty_string(v)


class ProfessionalCreate(ProfessionalBase):
    pass


class ProfessionalUpdate(BaseModel):
    pid: Optional[str] = Field(None, min_length=1)
    name: Optional[str] = Field(None, min_length=1)
    role: Optional[str] = Field(None, min_length=1)
    level: Optional[str] = Field(None, min_length=1)
    is_template: Optional[bool] = None
    hourly_cost: Optional[float] = Field(None, ge=0.0)

    @field_validator("pid", "name", "role", "level")
    @classmethod
    def validate_non_empty_string(cls, v: Optional[str]) -> Optional[str]:
        return _strip_non_empty_string(v)


class Professional(ProfessionalBase, ORMModel):
    id: int


class OfferItemBase(BaseModel):
    allocation_percentage: float = Field(default=100.0, ge=0.0, le=100.0)
    professional_id: int


class OfferItemCreate(OfferItemBase):
    pass


class OfferItemUpdate(BaseModel):
    professional_id: Optional[int] = None
    allocation_percentage: Optional[float] = Field(None, ge=0.0, le=100.0)


class OfferItem(OfferItemBase, ORMModel):
    id: int
    offer_id: int


class OfferBase(BaseModel):
    name: str = Field(..., min_length=1)

    @field_validator("name")
    @classmethod
    def validate_non_empty_string(cls, v: str) -> str:
        return _strip_non_empty_string(v)


class OfferCreate(OfferBase):
    items: List[OfferItemCreate] = Field(default_factory=list)


class OfferUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1)
    items: Optional[List[OfferItemCreate]] = None

    @field_validator("name")
    @classmethod
    def validate_non_empty_string(cls, v: Optional[str]) -> Optional[str]:
        return _strip_non_empty_string(v)


class Offer(OfferBase, ORMModel):
    id: int


class ApplyOfferRequest(BaseModel):
    offer_id: int


class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1)
    start_date: date
    duration_months: int = Field(..., ge=1)
    tax_rate: float = Field(..., ge=0.0, le=100.0)
    margin_rate: float = Field(..., ge=0.0, le=100.0)

    @field_validator("name")
    @classmethod
    def validate_non_empty_string(cls, v: str) -> str:
        return _strip_non_empty_string(v)


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1)
    start_date: Optional[date] = None
    duration_months: Optional[int] = Field(None, ge=1)
    tax_rate: Optional[float] = Field(None, ge=0.0, le=100.0)
    margin_rate: Optional[float] = Field(None, ge=0.0, le=100.0)

    @field_validator("name")
    @classmethod
    def validate_non_empty_string(cls, v: Optional[str]) -> Optional[str]:
        return _strip_non_empty_string(v)


class WeeklyAllocationBase(BaseModel):
    week_number: int
    hours_allocated: float = Field(default=0.0, ge=0.0)
    available_hours: float = Field(..., ge=0.0)


class WeeklyAllocationCreate(WeeklyAllocationBase):
    pass


class WeeklyAllocation(WeeklyAllocationBase, ORMModel):
    id: int


class ProjectAllocationBase(BaseModel):
    professional_id: int
    cost_hourly_rate: float = Field(default=0.0, ge=0.0)
    selling_hourly_rate: float = Field(default=0.0, ge=0.0)


class ProjectAllocationCreate(ProjectAllocationBase):
    weekly_allocations: List[WeeklyAllocationCreate] = Field(default_factory=list)


class ProjectAllocation(ProjectAllocationBase, ORMModel):
    id: int
    professional: Professional
    weekly_allocations: List[WeeklyAllocation] = Field(default_factory=list)


class ProjectCreate(ProjectBase):
    allocations: List[ProjectAllocationCreate] = Field(default_factory=list)
    from_project_id: Optional[int] = None  # For cloning from existing project


class Project(ProjectBase, ORMModel):
    id: int


class ProjectPricing(ORMModel):
    total_cost: float
    total_selling: float
    total_margin: float
    total_tax: float
    final_price: float
    final_margin_percent: float
