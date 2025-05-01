# utils/validators.py
import re
from datetime import datetime, date, time

class Validators:
    @staticmethod
    def validate_tc_id(tc_id):
        """
        TC Kimlik numarasını doğrular.
        
        :param tc_id: TC Kimlik numarası
        :return: Geçerliyse True, değilse False
        """
        if not tc_id or not isinstance(tc_id, str):
            return False
        
        # 11 haneli sayı olmalı
        if not re.match(r'^\d{11}$', tc_id):
            return False
        
        # İlk hane 0 olamaz
        if tc_id[0] == '0':
            return False
        
        # Algoritma kontrolü (son 2 hane için)
        digits = [int(d) for d in tc_id]
        
        # 10. hane kontrolü: 1,3,5,7,9 hanelerinin toplamı * 7 - 2,4,6,8 hanelerinin toplamı mod 10
        odd_sum = sum(digits[0:9:2])
        even_sum = sum(digits[1:9:2])
        if (odd_sum * 7 - even_sum) % 10 != digits[9]:
            return False
        
        # 11. hane kontrolü: İlk 10 hanenin toplamı mod 10
        if sum(digits[:10]) % 10 != digits[10]:
            return False
        
        return True
    
    @staticmethod
    def validate_email(email):
        """
        E-posta adresini doğrular.
        
        :param email: E-posta adresi
        :return: Geçerliyse True, değilse False
        """
        if not email or not isinstance(email, str):
            return False
        
        # Basit e-posta doğrulama
        email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return bool(re.match(email_pattern, email))
    
    @staticmethod
    def validate_date(date_str):
        """
        Tarih formatını doğrular (DD.MM.YYYY).
        
        :param date_str: Tarih string'i
        :return: Geçerliyse datetime.date nesnesi, değilse None
        """
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
        """
        Saat formatını doğrular (HH:MM:SS veya HH:MM).
        
        :param time_str: Saat string'i
        :return: Geçerliyse datetime.time nesnesi, değilse None
        """
        if not time_str or not isinstance(time_str, str):
            return None
        
        # Saat formatını kontrol et
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
        """
        Kan şekeri seviyesini doğrular.
        
        :param glucose_level: Kan şekeri seviyesi
        :return: Geçerliyse True, değilse False
        """
        try:
            glucose = float(glucose_level)
            # Fizyolojik olarak anlamlı aralıkta olmalı
            return 20 <= glucose <= 600
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_period(period):
        """
        Ölçüm periyodunu doğrular.
        
        :param period: Periyot
        :return: Geçerliyse True, değilse False
        """
        valid_periods = ['morning', 'noon', 'afternoon', 'evening', 'night']
        return period in valid_periods
    
    @staticmethod
    def validate_period_time(period, time_obj):
        """
        Periyot ve saat uyumunu doğrular.
        
        :param period: Periyot
        :param time_obj: datetime.time nesnesi
        :return: Geçerliyse True, değilse False
        """
        if not period or not time_obj:
            return False
        
        # Periyotlara göre saat aralıkları
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