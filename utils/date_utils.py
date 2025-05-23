
from datetime import datetime, date, time, timedelta

class DateUtils:
    @staticmethod
    def format_date(date_obj):
        """
        datetime.date nesnesini Türkiye formatında string'e dönüştürür (DD.MM.YYYY).

        """
        if not date_obj:
            return ""
        
        return date_obj.strftime('%d.%m.%Y')
    
    @staticmethod
    def format_time(time_obj):
        """
        datetime.time nesnesini Türkiye formatında string'e dönüştürür (HH:MM:SS).

        """
        if not time_obj:
            return ""
        
        return time_obj.strftime('%H:%M:%S')
    
    @staticmethod
    def format_datetime(datetime_obj):
        """
        datetime.datetime nesnesini Türkiye formatında string'e dönüştürür (DD.MM.YYYY HH:MM:SS).

        """
        if not datetime_obj:
            return ""
        
        return datetime_obj.strftime('%d.%m.%Y %H:%M:%S')
    
    @staticmethod
    def parse_date(date_str):
        """
        Türkiye formatındaki tarih string'ini datetime.date nesnesine dönüştürür.
        
 
        """
        if not date_str:
            return None
        
        try:
            return datetime.strptime(date_str, '%d.%m.%Y').date()
        except ValueError:
            return None
    
    @staticmethod
    def parse_time(time_str):
        """
        Türkiye formatındaki saat string'ini datetime.time nesnesine dönüştürür.

        """
        if not time_str:
            return None
        
        try:
            return datetime.strptime(time_str, '%H:%M:%S').time()
        except ValueError:
            try:
                # HH:MM formatı da destekle
                return datetime.strptime(time_str, '%H:%M').time()
            except ValueError:
                return None
    
    @staticmethod
    def parse_datetime(datetime_str):
        """
        Türkiye formatındaki tarih ve saat string'ini datetime.datetime nesnesine dönüştürür.
        
        """
        if not datetime_str:
            return None
        
        try:
            return datetime.strptime(datetime_str, '%d.%m.%Y %H:%M:%S')
        except ValueError:
            try:
                # HH:MM formatı da destekle
                return datetime.strptime(datetime_str, '%d.%m.%Y %H:%M')
            except ValueError:
                return None
    
    @staticmethod
    def get_week_range(date_obj=None):
        """
        Verilen tarihin bulunduğu haftanın başlangıç ve bitiş tarihlerini döndürür.
        
        """
        if not date_obj:
            date_obj = date.today()
        
        # Haftanın başlangıcı (Pazartesi)
        start_of_week = date_obj - timedelta(days=date_obj.weekday())
        # Haftanın sonu (Pazar)
        end_of_week = start_of_week + timedelta(days=6)
        
        return start_of_week, end_of_week
    
    @staticmethod
    def get_month_range(date_obj=None):
        """
        Verilen tarihin bulunduğu ayın başlangıç ve bitiş tarihlerini döndürür.
        
        """
        if not date_obj:
            date_obj = date.today()
        
        # Ayın başlangıcı
        start_of_month = date(date_obj.year, date_obj.month, 1)
        
        # Ayın sonu
        if date_obj.month == 12:
            end_of_month = date(date_obj.year + 1, 1, 1) - timedelta(days=1)
        else:
            end_of_month = date(date_obj.year, date_obj.month + 1, 1) - timedelta(days=1)
        
        return start_of_month, end_of_month