# models/insulin.py
from datetime import datetime

class Insulin:
    def __init__(self, patient_id=None, recommended_dose=None, administered_dose=None, 
                 average_glucose=None, date=None, notes=None, id=None):
        self.id = id
        self.patient_id = patient_id
        self.recommended_dose = recommended_dose  # ml cinsinden
        self.administered_dose = administered_dose  # Uygulanan doz (ml)
        self.average_glucose = average_glucose  # Ortalama kan şekeri (mg/dL)
        self.date = date or datetime.now()
        self.notes = notes
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    @staticmethod
    def calculate_recommended_dose(average_glucose):
        if average_glucose is None:
            return None
        if average_glucose < 70:
            return 0  # Hipoglisemi - insülin yok
        elif 70 <= average_glucose <= 110:
            return 0  # Normal - insülin yok
        elif 111 <= average_glucose <= 150:
            return 1  # Orta yüksek - 1 ml
        elif 151 <= average_glucose <= 200:
            return 2  # Yüksek - 2 ml
        else:
            return 3  # Çok yüksek - 3 ml
    
    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'recommended_dose': self.recommended_dose,
            'administered_dose': self.administered_dose,
            'average_glucose': self.average_glucose,
            'date': self.date,
            'notes': self.notes,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @staticmethod
    def from_dict(data):
        insulin = Insulin()
        insulin.id = data.get('id')
        insulin.patient_id = data.get('patient_id')
        insulin.recommended_dose = data.get('recommended_dose')
        insulin.administered_dose = data.get('administered_dose')
        insulin.average_glucose = data.get('average_glucose')
        insulin.date = data.get('date')
        insulin.notes = data.get('notes')
        insulin.created_at = data.get('created_at', datetime.now())
        insulin.updated_at = data.get('updated_at', datetime.now())
        return insulin