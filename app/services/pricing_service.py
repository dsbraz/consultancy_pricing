from app.models.models import Project
from app.services.calendar_service import CalendarService
from sqlalchemy.orm import Session

import logging

logger = logging.getLogger(__name__)


class PricingService:
    def __init__(self, db: Session):
        self.db = db
        self.calendar_service = CalendarService()

    def calculate_project_pricing(self, project: Project):
        """
        Calculate project pricing based on weekly allocations with selling rates.

        Total Cost = sum(hours_allocated * hourly_cost)
        Total Selling = sum(hours_allocated * selling_hourly_rate)
        Margin = Total Selling - Total Cost
        Tax = Total Selling * tax_rate
        Final Price = Total Selling + Tax
        """
        logger.info(
            f"Calculating pricing for project: id={project.id}, name={project.name}"
        )

        if not project.allocations:
            logger.warning(f"Project has no allocations: id={project.id}")

        total_cost = 0.0
        total_selling = 0.0

        for allocation in project.allocations:
            professional = allocation.professional
            if not professional:
                continue

            hourly_cost = allocation.cost_hourly_rate
            selling_rate = allocation.selling_hourly_rate

            for weekly_alloc in allocation.weekly_allocations:
                hours = weekly_alloc.hours_allocated
                total_cost += hours * hourly_cost
                total_selling += hours * selling_rate


        total_margin = total_selling - total_cost

        tax_rate_decimal = project.tax_rate / 100.0
        total_tax = total_selling * tax_rate_decimal
        final_price = total_selling + total_tax

        final_margin_percent = (
            (1 - (total_cost / total_selling)) * 100 if total_selling > 0 else 0
        )

        logger.info(
            f"Pricing calculation completed for project {project.id}: "
            f"cost={total_cost:.2f}, selling={total_selling:.2f}, "
            f"margin={total_margin:.2f}, tax={total_tax:.2f}, "
            f"final_price={final_price:.2f}, final_margin={final_margin_percent:.1f}%"
        )

        return {
            "total_cost": total_cost,
            "total_selling": total_selling,
            "total_margin": total_margin,
            "total_tax": total_tax,
            "final_price": final_price,
            "final_margin_percent": final_margin_percent,
        }
