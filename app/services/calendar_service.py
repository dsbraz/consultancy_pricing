import holidays
from datetime import date, timedelta
import calendar
import logging

logger = logging.getLogger(__name__)

class CalendarService:
    def __init__(self, country_code='BR', state_code=None):
        self.holidays = holidays.country_holidays(country_code, subdiv=state_code)

    def is_business_day(self, check_date: date) -> bool:
        if check_date.weekday() >= 5:
            return False
        if check_date in self.holidays:
            return False
        return True


    def get_monday_of_week(self, check_date: date) -> date:
        """Returns the Monday of the week for the given date."""
        days_since_monday = check_date.weekday()
        monday = check_date - timedelta(days=days_since_monday)
        return monday

    def get_business_hours_in_week(self, week_start: date, hours_per_day: int = 8) -> tuple[int, list[date]]:
        """
        Returns business hours available in a week and list of holidays.
        Week starts on Monday.
        Returns: (available_hours, holidays_in_week)
        """
        business_days = 0
        holidays_in_week = []
        
        for day_offset in range(7):
            current_date = week_start + timedelta(days=day_offset)
            if current_date in self.holidays:
                holidays_in_week.append(current_date)
            if self.is_business_day(current_date):
                business_days += 1
        
        return business_days * hours_per_day, holidays_in_week

    def get_weekly_breakdown(self, start_date: date, duration_months: int, hours_per_day: int = 8) -> list[dict]:
        """
        Returns a list of weeks with their details for the project duration.
        Each week includes: week_number, week_start, week_end, business_days, available_hours, holidays
        """
        logger.debug(f"Generating weekly breakdown: start_date={start_date}, duration_months={duration_months}")
        weeks = []
        
        end_date = start_date
        for _ in range(duration_months):
            month = end_date.month
            year = end_date.year
            if month == 12:
                end_date = date(year + 1, 1, 1)
            else:
                end_date = date(year, month + 1, 1)
        
        current_monday = self.get_monday_of_week(start_date)
        week_number = 1
        
        while current_monday < end_date:
            week_end = current_monday + timedelta(days=6)
            
            available_hours, holidays_in_week = self.get_business_hours_in_week(current_monday, hours_per_day)
            
            business_days = available_hours // hours_per_day if hours_per_day > 0 else 0
            
            week_info = {
                "week_number": week_number,
                "week_start": current_monday.isoformat(),
                "week_end": week_end.isoformat(),
                "business_days": business_days,
                "available_hours": available_hours,
                "holidays": [h.isoformat() for h in holidays_in_week] if holidays_in_week else []
            }
            
            weeks.append(week_info)
            
            current_monday += timedelta(days=7)
            week_number += 1
        
        total_holidays = sum(1 for w in weeks if w['holidays'])
        logger.info(f"Weekly breakdown generated: {len(weeks)} weeks, {total_holidays} weeks with holidays")
        
        return weeks
