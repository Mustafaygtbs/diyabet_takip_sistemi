 
from datetime import datetime

class Symptom:
    TYPE_POLYURIA = 'polyuria'  
    TYPE_POLYPHAGIA = 'polyphagia'  
    TYPE_POLYDIPSIA = 'polydipsia'  
    TYPE_NEUROPATHY = 'neuropathy'  
    TYPE_WEIGHT_LOSS = 'weight_loss'  
    TYPE_FATIGUE = 'fatigue'  
    TYPE_SLOW_HEALING = 'slow_healing'  
    TYPE_BLURRED_VISION = 'blurred_vision'  
    
    TYPES = [
        TYPE_POLYURIA,
        TYPE_POLYPHAGIA,
        TYPE_POLYDIPSIA,
        TYPE_NEUROPATHY,
        TYPE_WEIGHT_LOSS,
        TYPE_FATIGUE,
        TYPE_SLOW_HEALING,
        TYPE_BLURRED_VISION
    ]
    
    def __init__(self, patient_id=None, symptom_type=None, severity=None, date=None, 
                 notes=None, id=None):
        self.id = id
        self.patient_id = patient_id
        self.symptom_type = symptom_type
        self.severity = severity  
        self.date = date or datetime.now()
        self.notes = notes
        self.created_at = datetime.now()
    
    @property
    def type_name(self):
        if self.symptom_type == self.TYPE_POLYURIA:
            return "Poliüri (Sık idrara çıkma)"
        elif self.symptom_type == self.TYPE_POLYPHAGIA:
            return "Polifaji (Aşırı açlık hissi)"
        elif self.symptom_type == self.TYPE_POLYDIPSIA:
            return "Polidipsi (Aşırı susama hissi)"
        elif self.symptom_type == self.TYPE_NEUROPATHY:
            return "Nöropati (El ve ayaklarda karıncalanma)"
        elif self.symptom_type == self.TYPE_WEIGHT_LOSS:
            return "Kilo kaybı"
        elif self.symptom_type == self.TYPE_FATIGUE:
            return "Yorgunluk"
        elif self.symptom_type == self.TYPE_SLOW_HEALING:
            return "Yaraların yavaş iyileşmesi"
        elif self.symptom_type == self.TYPE_BLURRED_VISION:
            return "Bulanık görme"
        return self.symptom_type
    
    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'symptom_type': self.symptom_type,
            'severity': self.severity,
            'date': self.date,
            'notes': self.notes,
            'created_at': self.created_at
        }
    
    @staticmethod
    def from_dict(data):
        symptom = Symptom()
        symptom.id = data.get('id')
        symptom.patient_id = data.get('patient_id')
        symptom.symptom_type = data.get('symptom_type')
        symptom.severity = data.get('severity')
        symptom.date = data.get('date')
        symptom.notes = data.get('notes')
        symptom.created_at = data.get('created_at', datetime.now())
        return symptom