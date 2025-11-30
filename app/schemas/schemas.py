from typing import List, Optional, Annotated
from pydantic import BaseModel, ConfigDict, Field, AfterValidator
from datetime import date


def _strip_non_empty_string(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    if not value.strip():
        raise ValueError("Campo não pode ser vazio ou conter apenas espaços")
    return value.strip()


NonEmptyStr = Annotated[
    str, Field(min_length=1), AfterValidator(_strip_non_empty_string)
]
OptionalNonEmptyStr = Annotated[
    Optional[str], Field(None, min_length=1), AfterValidator(_strip_non_empty_string)
]


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ProfessionalBase(BaseModel):
    pid: NonEmptyStr
    name: NonEmptyStr
    role: NonEmptyStr
    level: NonEmptyStr
    is_template: bool = False
    hourly_cost: float = Field(default=0.0, ge=0.0)


class ProfessionalCreate(ProfessionalBase):
    pass


class ProfessionalUpdate(BaseModel):
    pid: OptionalNonEmptyStr = None
    name: OptionalNonEmptyStr = None
    role: OptionalNonEmptyStr = None
    level: OptionalNonEmptyStr = None
    is_template: Optional[bool] = None
    hourly_cost: Optional[float] = Field(None, ge=0.0)


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
    name: NonEmptyStr


class OfferCreate(OfferBase):
    items: List[OfferItemCreate] = Field(default_factory=list)


class OfferUpdate(BaseModel):
    name: OptionalNonEmptyStr = None


class Offer(OfferBase, ORMModel):
    id: int


class ApplyOfferRequest(BaseModel):
    offer_id: int


class ProjectBase(BaseModel):
    name: NonEmptyStr
    start_date: date
    duration_months: int = Field(..., ge=1)
    tax_rate: float = Field(..., ge=0.0, le=100.0)
    margin_rate: float = Field(..., ge=0.0, le=100.0)


class ProjectUpdate(BaseModel):
    name: OptionalNonEmptyStr = None
    start_date: Optional[date] = None
    duration_months: Optional[int] = Field(None, ge=1)
    tax_rate: Optional[float] = Field(None, ge=0.0, le=100.0)
    margin_rate: Optional[float] = Field(None, ge=0.0, le=100.0)


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
