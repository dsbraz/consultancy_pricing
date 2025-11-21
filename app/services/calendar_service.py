import holidays
from datetime import date, timedelta
import calendar

class CalendarService:
    def __init__(self, country_code='BR', state_code=None):
        self.holidays = holidays.country_holidays(country_code, subdiv=state_code)

    def is_business_day(self, check_date: date) -> bool:
        # 0-4 are Monday-Friday, 5-6 are Saturday-Sunday
        if check_date.weekday() >= 5:
            return False
        if check_date in self.holidays:
            return False
        return True

    def get_business_hours_in_month(self, year: int, month: int, hours_per_day: int = 8) -> int:
        _, num_days = calendar.monthrange(year, month)
        business_days = 0
        for day in range(1, num_days + 1):
            current_date = date(year, month, day)
            if self.is_business_day(current_date):
                business_days += 1
        return business_days * hours_per_day

    def get_business_hours_for_period(self, start_date: date, duration_months: int, hours_per_day: int = 8) -> dict:
        """
        Returns a dictionary mapping (year, month) tuples to business hours.
        """
        result = {}
        current_date = start_date
        
        for _ in range(duration_months):
            year = current_date.year
            month = current_date.month
            
            _, num_days_in_month = calendar.monthrange(year, month)
            
            
            days_in_month = 0
            for day in range(current_date.day, num_days_in_month + 1):
                 if self.is_business_day(date(year, month, day)):
                     days_in_month += 1
            
            result[(year, month)] = days_in_month * hours_per_day
            
            if month == 12:
                current_date = date(year + 1, 1, 1)
            else:
                current_date = date(year, month + 1, 1)
                
        return result

    def get_monday_of_week(self, check_date: date) -> date:
        """Returns the Monday of the week for the given date."""
        days_since_monday = check_date.weekday()  # 0 = Monday, 6 = Sunday
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
        
        for day_offset in range(7):  # Monday to Sunday
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
        weeks = []
        
        # Calculate end date (approximate)
        end_date = start_date
        for _ in range(duration_months):
            month = end_date.month
            year = end_date.year
            if month == 12:
                end_date = date(year + 1, 1, 1)
            else:
                end_date = date(year, month + 1, 1)
        
        # Get the Monday of the start week
        current_monday = self.get_monday_of_week(start_date)
        week_number = 1
        
        while current_monday < end_date:
            week_end = current_monday + timedelta(days=6)  # Sunday
            
            available_hours, holidays_in_week = self.get_business_hours_in_week(current_monday, hours_per_day)
            
            # Count only business days
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
            
            # Move to next Monday
            current_monday += timedelta(days=7)
            week_number += 1
        
        return weeks
