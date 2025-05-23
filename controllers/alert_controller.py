
from datetime import datetime
from models.alert import Alert
from database.queries import AlertQueries

class AlertController:
    @staticmethod
    def create_glucose_alert(patient_id, glucose_level, period=None):
        """
        Kan şekeri seviyesine göre uyarı oluşturur.
        """
        alert = Alert()
        alert.patient_id = patient_id
        alert.glucose_level = glucose_level
        alert.date = datetime.now()
        
        # Ölçüm seviyesine göre uyarı türü ve mesajı belirle
        if glucose_level < 70:
            alert.alert_type = Alert.TYPE_HYPOGLYCEMIA
            alert.message = f"Hastanın kan şekeri seviyesi 70 mg/dL'nin altına düştü. Hipoglisemi riski! Hızlı müdahale gerekebilir. Ölçüm: {glucose_level} mg/dL"
        elif 70 <= glucose_level <= 110:
            alert.alert_type = Alert.TYPE_NORMAL
            alert.message = f"Kan şekeri seviyesi normal aralıkta. Hiçbir işlem gerekmez. Ölçüm: {glucose_level} mg/dL"
        elif 111 <= glucose_level <= 150:
            alert.alert_type = Alert.TYPE_MEDIUM_HIGH
            alert.message = f"Hastanın kan şekeri 111-150 mg/dL arasında. Durum izlenmeli. Ölçüm: {glucose_level} mg/dL"
        elif 151 <= glucose_level <= 200:
            alert.alert_type = Alert.TYPE_HIGH
            alert.message = f"Hastanın kan şekeri 151-200 mg/dL arasında. Diyabet kontrolü gereklidir. Ölçüm: {glucose_level} mg/dL"
        else:  # > 200
            alert.alert_type = Alert.TYPE_HYPERGLYCEMIA
            alert.message = f"Hastanın kan şekeri 200 mg/dL'nin üzerinde. Hiperglisemi durumu. Acil müdahale gerekebilir. Ölçüm: {glucose_level} mg/dL"
        
        # Periyot bilgisini ekle
        if period:
            period_names = {
                'morning': 'Sabah',
                'noon': 'Öğle',
                'afternoon': 'İkindi',
                'evening': 'Akşam',
                'night': 'Gece'
            }
            period_name = period_names.get(period, period)
            alert.message += f" ({period_name} ölçümü)"
        
        # Acil durumlar için özel işaretleme (is_read = False)
        if alert.alert_type in [Alert.TYPE_HYPOGLYCEMIA, Alert.TYPE_HYPERGLYCEMIA]:
            alert.is_read = False
        else:
            # Normal değerler için otomatik okundu olarak işaretle
            alert.is_read = alert.alert_type == Alert.TYPE_NORMAL
        
        # Veritabanına ekle
        alert_id = AlertQueries.insert_alert(alert)
        
        return alert_id
    
    @staticmethod
    def create_missing_measurement_alert(patient_id, date):
        """
        Eksik ölçüm uyarısı oluşturur.
        """
        alert = Alert()
        alert.patient_id = patient_id
        alert.alert_type = Alert.TYPE_MISSING_MEASUREMENT
        alert.message = f"Hasta {date.strftime('%d.%m.%Y')} tarihinde hiç kan şekeri ölçümü yapmamıştır. Acil takip önerilir."
        alert.date = datetime.now()
        alert.is_read = False
        
        # Veritabanına ekle
        alert_id = AlertQueries.insert_alert(alert)
        
        return alert_id
    
    @staticmethod
    def create_insufficient_measurement_alert(patient_id, date):
        """
        Yetersiz ölçüm uyarısı oluşturur.
        """
        alert = Alert()
        alert.patient_id = patient_id
        alert.alert_type = Alert.TYPE_INSUFFICIENT_MEASUREMENT
        alert.message = f"Hastanın {date.strftime('%d.%m.%Y')} tarihindeki kan şekeri ölçüm sayısı yetersiz (<3). Durum izlenmelidir."
        alert.date = datetime.now()
        alert.is_read = False
        
        # Veritabanına ekle
        alert_id = AlertQueries.insert_alert(alert)
        
        return alert_id
    
    @staticmethod
    def mark_alert_as_read(alert_id):
        """
        Uyarıyı okundu olarak işaretler.
        """
        result = AlertQueries.mark_alert_as_read(alert_id)
        return result is not None