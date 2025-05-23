# models/alert.py
from datetime import datetime

class Alert:
    TYPE_HYPOGLYCEMIA = 'hypoglycemia'  
    TYPE_NORMAL = 'normal'  
    TYPE_MEDIUM_HIGH = 'medium_high' 
    TYPE_HIGH = 'high'  
    TYPE_HYPERGLYCEMIA = 'hyperglycemia'  
    TYPE_MISSING_MEASUREMENT = 'missing_measurement'  
    TYPE_INSUFFICIENT_MEASUREMENT = 'insufficient_measurement'  
    
    TYPES = [
        TYPE_HYPOGLYCEMIA,
        TYPE_NORMAL,
        TYPE_MEDIUM_HIGH,
        TYPE_HIGH,
        TYPE_HYPERGLYCEMIA,
        TYPE_MISSING_MEASUREMENT,
        TYPE_INSUFFICIENT_MEASUREMENT
    ]
    
    def __init__(self, patient_id=None, alert_type=None, message=None, 
                 glucose_level=None, date=None, is_read=False, id=None):
        self.id = id
        self.patient_id = patient_id
        self.alert_type = alert_type
        self.message = message
        self.glucose_level = glucose_level  
        self.date = date or datetime.now()
        self.is_read = is_read
        self.created_at = datetime.now()
    
    @property
    def type_name(self):
        if self.alert_type == self.TYPE_HYPOGLYCEMIA:
            return "Hipoglisemi Riski"
        elif self.alert_type == self.TYPE_NORMAL:
            return "Normal Seviye"
        elif self.alert_type == self.TYPE_MEDIUM_HIGH:
            return "Takip Uyarısı"
        elif self.alert_type == self.TYPE_HIGH:
            return "İzleme Uyarısı"
        elif self.alert_type == self.TYPE_HYPERGLYCEMIA:
            return "Acil Müdahale Uyarısı"
        elif self.alert_type == self.TYPE_MISSING_MEASUREMENT:
            return "Ölçüm Eksik Uyarısı"
        elif self.alert_type == self.TYPE_INSUFFICIENT_MEASUREMENT:
            return "Ölçüm Yetersiz Uyarısı"
        return self.alert_type
    
    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'alert_type': self.alert_type,
            'message': self.message,
            'glucose_level': self.glucose_level,
            'date': self.date,
            'is_read': self.is_read,
            'created_at': self.created_at
        }
    
    @staticmethod
    def from_dict(data):
        alert = Alert()
        alert.id = data.get('id')
        alert.patient_id = data.get('patient_id')
        alert.alert_type = data.get('alert_type')
        alert.message = data.get('message')
        alert.glucose_level = data.get('glucose_level')
        alert.date = data.get('date')
        alert.is_read = data.get('is_read', False)
        alert.created_at = data.get('created_at', datetime.now())
        return alert