from app.models.models import Project, Professional
from app.services.calendar_service import CalendarService
from sqlalchemy.orm import Session
from datetime import datetime

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
        Tax = Calculated such that Total Selling / (1 - tax_rate) - Total Selling
        Final Price = Total Selling / (1 - tax_rate)
        """
        total_cost = 0.0
        total_selling = 0.0
        monthly_costs = {}
        monthly_selling = {}
        weekly_costs = {}
        weekly_selling = {}
        
        # Iterate through all allocations
        for allocation in project.allocations:
            professional = allocation.professional
            if not professional:
                continue
            
            hourly_cost = professional.hourly_cost
            selling_rate = allocation.selling_hourly_rate
            
            # Sum up all weekly allocations
            for weekly_alloc in allocation.weekly_allocations:
                hours = weekly_alloc.hours_allocated
                
                week_cost = hours * hourly_cost
                week_selling = hours * selling_rate
                
                total_cost += week_cost
                total_selling += week_selling
                
                # Track by week
                week_key = f"Week {weekly_alloc.week_number}"
                weekly_costs[week_key] = weekly_costs.get(week_key, 0) + week_cost
                weekly_selling[week_key] = weekly_selling.get(week_key, 0) + week_selling
                
                # Aggregate by month
                week_date = weekly_alloc.week_start_date
                month_key = f"{week_date.year}-{week_date.month:02d}"
                monthly_costs[month_key] = monthly_costs.get(month_key, 0) + week_cost
                monthly_selling[month_key] = monthly_selling.get(month_key, 0) + week_selling
        
        # Calculate margin (Selling - Cost)
        total_margin = total_selling - total_cost
        
        # Calculate Tax: Selling * (tax_rate / 100)
        # This implies Tax is added ON TOP of the Selling Price.
        tax_rate_decimal = project.tax_rate / 100.0
        total_tax = total_selling * tax_rate_decimal
        
        # Final Price = Selling + Tax
        final_price = total_selling + total_tax
        
        # Calculate final margin percentage: (1 - (Cost / Selling)) * 100
        final_margin_percent = (1 - (total_cost / total_selling)) * 100 if total_selling > 0 else 0
        
        return {
            "total_cost": total_cost,
            "total_selling": total_selling,
            "total_margin": total_margin,
            "total_tax": total_tax,
            "final_price": final_price,
            "final_margin_percent": final_margin_percent,
            "monthly_breakdown": {
                "costs": monthly_costs,
                "selling": monthly_selling
            },
            "weekly_breakdown": {
                "costs": weekly_costs,
                "selling": weekly_selling
            }
        }
