from typing import List, Optional
from pydantic import BaseModel, field_validator, Field
from datetime import date


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
        if not v or not v.strip():
            raise ValueError("Campo não pode ser vazio ou conter apenas espaços")
        return v.strip()


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
        if v is not None and (not v or not v.strip()):
            raise ValueError("Campo não pode ser vazio ou conter apenas espaços")
        return v.strip() if v else None


class Professional(ProfessionalBase):
    id: int

    class Config:
        from_attributes = True


class OfferItemBase(BaseModel):
    allocation_percentage: float = Field(default=100.0, ge=0.0, le=100.0)
    professional_id: int


class OfferItemCreate(OfferItemBase):
    professional_id: int


class OfferItemUpdate(BaseModel):
    professional_id: Optional[int] = None
    allocation_percentage: Optional[float] = Field(None, ge=0.0, le=100.0)


class OfferItem(OfferItemBase):
    id: int
    offer_id: int

    class Config:
        orm_mode = True


class OfferBase(BaseModel):
    name: str = Field(..., min_length=1)

    @field_validator("name")
    @classmethod
    def validate_non_empty_string(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Campo não pode ser vazio ou conter apenas espaços")
        return v.strip()


class OfferCreate(OfferBase):
    items: List[OfferItemCreate] = []


class OfferUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1)
    items: Optional[List[OfferItemCreate]] = None

    @field_validator("name")
    @classmethod
    def validate_non_empty_string(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and (not v or not v.strip()):
            raise ValueError("Campo não pode ser vazio ou conter apenas espaços")
        return v.strip() if v else None


class Offer(OfferBase):
    id: int

    class Config:
        from_attributes = True


class OfferWithItems(OfferBase):
    id: int
    items: List[OfferItem] = []

    class Config:
        from_attributes = True


class ApplyOfferRequest(BaseModel):
    offer_id: int


class WeeklyAllocationBase(BaseModel):
    week_number: int
    hours_allocated: float = Field(default=0.0, ge=0.0)
    available_hours: float = Field(..., ge=0.0)


class WeeklyAllocationCreate(WeeklyAllocationBase):
    pass


class WeeklyAllocation(WeeklyAllocationBase):
    id: int

    class Config:
        from_attributes = True


class ProjectAllocationBase(BaseModel):
    professional_id: int
    selling_hourly_rate: float = Field(default=0.0, ge=0.0)
    cost_hourly_rate: float = Field(default=0.0, ge=0.0)



class ProjectAllocationCreate(ProjectAllocationBase):
    weekly_allocations: List[WeeklyAllocationCreate] = []


class ProjectAllocation(ProjectAllocationBase):
    id: int
    professional: Professional
    weekly_allocations: List[WeeklyAllocation] = []

    class Config:
        from_attributes = True


class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1)
    start_date: date
    duration_months: int = Field(..., ge=1)
    tax_rate: float = Field(..., ge=0.0, le=100.0)
    margin_rate: float = Field(..., ge=0.0, le=100.0)

    @field_validator("name")
    @classmethod
    def validate_non_empty_string(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Campo não pode ser vazio ou conter apenas espaços")
        return v.strip()


class ProjectCreate(ProjectBase):
    allocations: List[ProjectAllocationCreate] = []
    from_project_id: Optional[int] = None  # For cloning from existing project


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1)
    start_date: Optional[date] = None
    duration_months: Optional[int] = Field(None, ge=1)
    tax_rate: Optional[float] = Field(None, ge=0.0, le=100.0)
    margin_rate: Optional[float] = Field(None, ge=0.0, le=100.0)

    @field_validator("name")
    @classmethod
    def validate_non_empty_string(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and (not v or not v.strip()):
            raise ValueError("Campo não pode ser vazio ou conter apenas espaços")
        return v.strip() if v else None


class Project(ProjectBase):
    id: int

    class Config:
        from_attributes = True


class ProjectPricing(BaseModel):
    total_cost: float
    total_selling: float
    total_margin: float
    total_tax: float
    final_price: float
    final_margin_percent: float

    class Config:
        from_attributes = True
