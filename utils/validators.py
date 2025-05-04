# utils/validators.py
import re
from datetime import datetime, date, time

class Validators:
    @staticmethod
    def validate_tc_id(tc_id):

        if not tc_id or not isinstance(tc_id, str):
            return False
        

        if not re.match(r'^\d{11}$', tc_id):
            return False
        

        if tc_id[0] == '0':
            return False

        # son iki hanenin kontrolü
        digits = [int(d) for d in tc_id]
        
        odd_sum = sum(digits[0:9:2])
        even_sum = sum(digits[1:9:2])
        if (odd_sum * 7 - even_sum) % 10 != digits[9]:
            return False
        
        if sum(digits[:10]) % 10 != digits[10]:
            return False
        
        return True
    
    @staticmethod
    def validate_email(email):
        if not email or not isinstance(email, str):
            return False
        
        email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return bool(re.match(email_pattern, email))
    
    @staticmethod
    def validate_date(date_str):
        if not date_str or not isinstance(date_str, str):
            return None
        
        # Tarih formatını kontrol et
        date_pattern = r'^(\d{2})\.(\d{2})\.(\d{4})$'
        match = re.match(date_pattern, date_str)
        
        if not match:
            return None
        
        try:
            day, month, year = map(int, match.groups())
            return date(year, month, day)
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def validate_time(time_str):
        if not time_str or not isinstance(time_str, str):
            return None
        time_pattern = r'^(\d{2}):(\d{2})(?::(\d{2}))?$'
        match = re.match(time_pattern, time_str)
        
        if not match:
            return None
        
        try:
            groups = match.groups()
            hour, minute = int(groups[0]), int(groups[1])
            second = int(groups[2]) if groups[2] else 0
            
            return time(hour, minute, second)
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def validate_glucose_level(glucose_level):

        try:
            glucose = float(glucose_level)
            # internette bu aralıktan bahsediyordu
            return 20 <= glucose <= 600
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_period(period):
        valid_periods = ['morning', 'noon', 'afternoon', 'evening', 'night']
        return period in valid_periods
    
    @staticmethod
    def validate_period_time(period, time_obj):

        if not period or not time_obj:
            return False
        period_ranges = {
            'morning': (time(7, 0), time(8, 0)),
            'noon': (time(12, 0), time(13, 0)),
            'afternoon': (time(15, 0), time(16, 0)),
            'evening': (time(18, 0), time(19, 0)),
            'night': (time(22, 0), time(23, 0))
        }
        
        if period not in period_ranges:
            return False
        
        start, end = period_ranges[period]
        return start <= time_obj <= end