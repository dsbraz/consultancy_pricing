import logging
from typing import List, Sequence

from sqlalchemy.orm import Session, joinedload

from app.models import models
from app.services.calendar_service import CalendarService

logger = logging.getLogger(__name__)


class ProjectAllocationService:
    """Encapsulates recurring allocation logic used across project endpoints."""

    def __init__(self, db: Session):
        self.db = db
        self.calendar_service = CalendarService(country_code="BR")

    def get_project_weeks(self, project: models.Project) -> List[dict]:
        return self.calendar_service.get_weekly_breakdown(
            project.start_date, project.duration_months
        )

    def calculate_selling_rate(
        self,
        project: models.Project,
        professional: models.Professional,
        explicit_rate: float | None = None,
    ) -> float:
        if explicit_rate is not None and explicit_rate > 0:
            return explicit_rate

        margin_rate = (
            project.margin_rate / 100.0
            if project.margin_rate > 1
            else project.margin_rate
        )
        divisor = 1 - margin_rate
        if divisor <= 0:
            return professional.hourly_cost
        return professional.hourly_cost / divisor

    def create_allocation(
        self,
        *,
        project: models.Project,
        professional: models.Professional,
        selling_hourly_rate: float | None = None,
        allocation_percentage: float = 0.0,
        weeks: Sequence[dict] | None = None,
    ) -> models.ProjectAllocation:
        selling_rate = selling_hourly_rate
        if selling_rate is None:
            selling_rate = self.calculate_selling_rate(project, professional)

        allocation = models.ProjectAllocation(
            project_id=project.id,
            professional_id=professional.id,
            cost_hourly_rate=professional.hourly_cost,
            selling_hourly_rate=selling_rate,
        )
        self.db.add(allocation)
        self.db.flush()

        self.create_weekly_allocations(
            allocation_id=allocation.id,
            weeks=weeks or self.get_project_weeks(project),
            allocation_percentage=allocation_percentage,
        )
        return allocation

    def clone_allocation(
        self, *, original: models.ProjectAllocation, target_project: models.Project
    ) -> models.ProjectAllocation:
        new_alloc = models.ProjectAllocation(
            project_id=target_project.id,
            professional_id=original.professional_id,
            cost_hourly_rate=original.cost_hourly_rate,
            selling_hourly_rate=original.selling_hourly_rate,
        )
        self.db.add(new_alloc)
        self.db.flush()

        for orig_weekly in original.weekly_allocations:
            weekly = models.WeeklyAllocation(
                allocation_id=new_alloc.id,
                week_number=orig_weekly.week_number,
                hours_allocated=orig_weekly.hours_allocated,
                available_hours=orig_weekly.available_hours,
            )
            self.db.add(weekly)
        return new_alloc

    def sync_project_weeks(self, project: models.Project) -> int:
        """Align allocation calendars after a change in dates/duration."""
        new_weeks = self.get_project_weeks(project)
        new_weeks_map = {w["week_number"]: w for w in new_weeks}
        new_week_numbers = set(new_weeks_map.keys())

        allocations = (
            self.db.query(models.ProjectAllocation)
            .options(joinedload(models.ProjectAllocation.weekly_allocations))
            .filter(models.ProjectAllocation.project_id == project.id)
            .all()
        )

        for allocation in allocations:
            existing_weeks = {w.week_number: w for w in allocation.weekly_allocations}
            existing_week_numbers = set(existing_weeks.keys())

            weeks_to_update = existing_week_numbers & new_week_numbers
            for week_num in weeks_to_update:
                existing_week = existing_weeks[week_num]
                new_week_data = new_weeks_map[week_num]
                existing_week.available_hours = new_week_data["available_hours"]

            weeks_to_remove = existing_week_numbers - new_week_numbers
            for week_num in weeks_to_remove:
                self.db.delete(existing_weeks[week_num])

            weeks_to_add = sorted(new_week_numbers - existing_week_numbers)
            if weeks_to_add:
                weeks_data_to_add = [new_weeks_map[wn] for wn in weeks_to_add]
                self.create_weekly_allocations(
                    allocation.id, weeks_data_to_add, allocation_percentage=0.0
                )

        return len(new_weeks)

    def create_weekly_allocations(
        self,
        allocation_id: int,
        weeks: Sequence[dict],
        allocation_percentage: float = 100.0,
    ) -> None:
        for week in weeks:
            hours = 0.0
            if allocation_percentage > 0:
                hours = week["available_hours"] * (allocation_percentage / 100.0)

            weekly_alloc = models.WeeklyAllocation(
                allocation_id=allocation_id,
                week_number=week["week_number"],
                hours_allocated=hours,
                available_hours=week["available_hours"],
            )
            self.db.add(weekly_alloc)
