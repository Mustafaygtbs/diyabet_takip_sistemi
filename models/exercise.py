# models/exercise.py
from datetime import datetime

class Exercise:
    TYPE_WALKING = 'walking'
    TYPE_CYCLING = 'cycling'
    TYPE_CLINICAL = 'clinical'
    
    TYPES = [TYPE_WALKING, TYPE_CYCLING, TYPE_CLINICAL]
    
    def __init__(self, patient_id=None, exercise_type=None, date=None, 
                 is_completed=False, notes=None, id=None):
        self.id = id
        self.patient_id = patient_id
        self.exercise_type = exercise_type
        self.date = date or datetime.now()
        self.is_completed = is_completed
        self.notes = notes
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    @property
    def type_name(self):
        if self.exercise_type == self.TYPE_WALKING:
            return "Yürüyüş"
        elif self.exercise_type == self.TYPE_CYCLING:
            return "Bisiklet"
        elif self.exercise_type == self.TYPE_CLINICAL:
            return "Klinik Egzersiz"
        return self.exercise_type
    
    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'exercise_type': self.exercise_type,
            'date': self.date,
            'is_completed': self.is_completed,
            'notes': self.notes,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @staticmethod
    def from_dict(data):
        exercise = Exercise()
        exercise.id = data.get('id')
        exercise.patient_id = data.get('patient_id')
        exercise.exercise_type = data.get('exercise_type')
        exercise.date = data.get('date')
        exercise.is_completed = data.get('is_completed', False)
        exercise.notes = data.get('notes')
        exercise.created_at = data.get('created_at', datetime.now())
        exercise.updated_at = data.get('updated_at', datetime.now())
        return exercise