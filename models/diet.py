# models/diet.py
from datetime import datetime

class Diet:
    TYPE_LOW_SUGAR = 'low_sugar'
    TYPE_NO_SUGAR = 'no_sugar'
    TYPE_BALANCED = 'balanced'
    
    TYPES = [TYPE_LOW_SUGAR, TYPE_NO_SUGAR, TYPE_BALANCED]
    
    def __init__(self, patient_id=None, diet_type=None, date=None, 
                 is_followed=False, notes=None, id=None):
        self.id = id
        self.patient_id = patient_id
        self.diet_type = diet_type
        self.date = date or datetime.now()
        self.is_followed = is_followed
        self.notes = notes
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    @property
    def type_name(self):
        if self.diet_type == self.TYPE_LOW_SUGAR:
            return "Az Şekerli Diyet"
        elif self.diet_type == self.TYPE_NO_SUGAR:
            return "Şekersiz Diyet"
        elif self.diet_type == self.TYPE_BALANCED:
            return "Dengeli Beslenme"
        return self.diet_type
    
    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'diet_type': self.diet_type,
            'date': self.date,
            'is_followed': self.is_followed,
            'notes': self.notes,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @staticmethod
    def from_dict(data):
        diet = Diet()
        diet.id = data.get('id')
        diet.patient_id = data.get('patient_id')
        diet.diet_type = data.get('diet_type')
        diet.date = data.get('date')
        diet.is_followed = data.get('is_followed', False)
        diet.notes = data.get('notes')
        diet.created_at = data.get('created_at', datetime.now())
        diet.updated_at = data.get('updated_at', datetime.now())
        return diet