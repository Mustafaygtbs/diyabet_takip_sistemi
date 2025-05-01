# controllers/measurement_controller.py
from datetime import datetime, time
from models.measurement import Measurement
from models.insulin import Insulin
from database.queries import MeasurementQueries, InsulinQueries
from controllers.alert_controller import AlertController

class MeasurementController:
    @staticmethod
    def calculate_daily_average_and_recommend_insulin(patient_id, date=None):
        """
        Günlük ölçüm ortalamasını hesaplar ve insülin önerir.
        
        :param patient_id: Hasta ID
        :param date: Tarih (varsayılan: bugün)
        :return: Önerilen insülin dozu
        """
        if not date:
            date = datetime.now().date()
        
        # Günün ölçümlerini al
        measurements = MeasurementQueries.get_measurements_by_date(patient_id, date)
        
        if not measurements:
            # Ölçüm yoksa uyarı oluştur
            AlertController.create_missing_measurement_alert(patient_id, date)
            return None
        
        if len(measurements) < 3:
            # Yetersiz ölçüm uyarısı
            AlertController.create_insufficient_measurement_alert(patient_id, date)
        
        # Periyotlara göre ölçümleri sınıflandır
        periods = {'morning': None, 'noon': None, 'afternoon': None, 'evening': None, 'night': None}
        
        for m in measurements:
            period = m['period']
            if period and period in periods:
                periods[period] = m['glucose_level']
        
        # Gece ölçümü için ortalama hesapla
        night_avg = MeasurementController._calculate_average_glucose(periods)
        
        # İnsülin öneri dozu hesapla
        recommended_dose = Insulin.calculate_recommended_dose(night_avg)
        
        # İnsülin kaydı oluştur
        insulin = Insulin()
        insulin.patient_id = patient_id
        insulin.recommended_dose = recommended_dose
        insulin.average_glucose = night_avg
        insulin.date = datetime.combine(date, time(23, 0))
        
        # Veritabanına ekle
        insulin_id = InsulinQueries.insert_insulin(insulin)
        
        return recommended_dose
    
    @staticmethod
    def _calculate_average_glucose(periods):
        """
        Periyotlara göre ortalama kan şekeri hesaplar.
        
        :param periods: Periyot bazlı ölçüm değerleri
        :return: Ortalama kan şekeri
        """
        total = 0
        count = 0
        
        # Sabah
        if periods['morning'] is not None:
            total += periods['morning']
            count += 1
        
        # Öğlen - Sabah ve öğlen ortalaması
        if periods['noon'] is not None:
            if periods['morning'] is not None:
                noon_avg = (periods['morning'] + periods['noon']) / 2
            else:
                noon_avg = periods['noon']
            total += noon_avg
            count += 1
        
        # İkindi - Sabah, öğlen ve ikindi ortalaması
        if periods['afternoon'] is not None:
            afternoon_values = []
            if periods['morning'] is not None:
                afternoon_values.append(periods['morning'])
            if periods['noon'] is not None:
                afternoon_values.append(periods['noon'])
            afternoon_values.append(periods['afternoon'])
            
            afternoon_avg = sum(afternoon_values) / len(afternoon_values)
            total += afternoon_avg
            count += 1
        
        # Akşam - Sabah, öğlen, ikindi ve akşam ortalaması
        if periods['evening'] is not None:
            evening_values = []
            if periods['morning'] is not None:
                evening_values.append(periods['morning'])
            if periods['noon'] is not None:
                evening_values.append(periods['noon'])
            if periods['afternoon'] is not None:
                evening_values.append(periods['afternoon'])
            evening_values.append(periods['evening'])
            
            evening_avg = sum(evening_values) / len(evening_values)
            total += evening_avg
            count += 1
        
        # Gece - Tüm ölçümlerin ortalaması
        if periods['night'] is not None:
            night_values = []
            if periods['morning'] is not None:
                night_values.append(periods['morning'])
            if periods['noon'] is not None:
                night_values.append(periods['noon'])
            if periods['afternoon'] is not None:
                night_values.append(periods['afternoon'])
            if periods['evening'] is not None:
                night_values.append(periods['evening'])
            night_values.append(periods['night'])
            
            night_avg = sum(night_values) / len(night_values)
            total += night_avg
            count += 1
        
        # Hiç ölçüm yoksa None döndür
        if count == 0:
            return None
        
        # Ortalama hesapla
        return total / count