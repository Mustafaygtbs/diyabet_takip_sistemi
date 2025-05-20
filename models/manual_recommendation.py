from datetime import datetime

class ManualRecommendation:
    TYPE_DIET = 'diet'
    TYPE_EXERCISE = 'exercise'
    TYPE_INSULIN = 'insulin'
    TYPE_OTHER = 'other'
    TYPES = [TYPE_DIET, TYPE_EXERCISE, TYPE_INSULIN, TYPE_OTHER]

    def __init__(self, doctor_id=None, patient_id=None, recommendation_type=None, content=None, id=None, created_at=None, updated_at=None):
        self.id = id
        self.doctor_id = doctor_id
        self.patient_id = patient_id
        self.recommendation_type = recommendation_type
        self.content = content
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    def to_dict(self):
        return {
            'id': self.id,
            'doctor_id': self.doctor_id,
            'patient_id': self.patient_id,
            'recommendation_type': self.recommendation_type,
            'content': self.content,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @staticmethod
    def from_dict(data):
        return ManualRecommendation(
            id=data.get('id'),
            doctor_id=data.get('doctor_id'),
            patient_id=data.get('patient_id'),
            recommendation_type=data.get('recommendation_type'),
            content=data.get('content'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        ) 