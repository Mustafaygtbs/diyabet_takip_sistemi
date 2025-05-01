# models/patient.py
from datetime import datetime
from models.user import User

class Patient(User):
    def __init__(self, tc_id=None, password=None, name=None, surname=None, 
                 birthdate=None, gender=None, email=None, profile_image=None, 
                 doctor_id=None, diagnosis=None, diabetes_type=None, 
                 diagnosis_date=None, id=None):
        super().__init__(tc_id, password, name, surname, birthdate, gender, 
                         email, profile_image, 'patient', id)
        self.doctor_id = doctor_id
        self.diagnosis = diagnosis
        self.diabetes_type = diabetes_type  # 'Tip 1', 'Tip 2', 'Gestasyonel', vb.
        self.diagnosis_date = diagnosis_date
        self.measurements = []
        self.exercises = []
        self.diets = []
        self.symptoms = []
        self.alerts = []
        self.insulins = []
    
    def to_dict(self):
        patient_dict = super().to_dict()
        patient_dict.update({
            'doctor_id': self.doctor_id,
            'diagnosis': self.diagnosis,
            'diabetes_type': self.diabetes_type,
            'diagnosis_date': self.diagnosis_date
        })
        return patient_dict
    
    @staticmethod
    def from_dict(data):
        patient = Patient()
        patient.id = data.get('id')
        patient.tc_id = data.get('tc_id')
        patient.password = data.get('password')
        patient.name = data.get('name')
        patient.surname = data.get('surname')
        patient.birthdate = data.get('birthdate')
        patient.gender = data.get('gender')
        patient.email = data.get('email')
        patient.profile_image = data.get('profile_image')
        patient.user_type = 'patient'
        patient.doctor_id = data.get('doctor_id')
        patient.diagnosis = data.get('diagnosis')
        patient.diabetes_type = data.get('diabetes_type')
        patient.diagnosis_date = data.get('diagnosis_date')
        patient.created_at = data.get('created_at')
        patient.updated_at = data.get('updated_at')
        return patient
    
    def add_measurement(self, measurement):
        self.measurements.append(measurement)
    
    def add_exercise(self, exercise):
        self.exercises.append(exercise)
    
    def add_diet(self, diet):
        self.diets.append(diet)
    
    def add_symptom(self, symptom):
        self.symptoms.append(symptom)
    
    def add_alert(self, alert):
        self.alerts.append(alert)
    
    def add_insulin(self, insulin):
        self.insulins.append(insulin)
    
    def get_measurements_by_date(self, date):
        return [m for m in self.measurements if m.measurement_date.date() == date]
    
    def get_measurements_by_date_range(self, start_date, end_date):
        return [m for m in self.measurements 
                if start_date <= m.measurement_date.date() <= end_date]
    
    def get_exercise_compliance_percentage(self, start_date, end_date):
        exercises = [e for e in self.exercises 
                     if start_date <= e.date.date() <= end_date]
        if not exercises:
            return 0
        completed = sum(1 for e in exercises if e.is_completed)
        return (completed / len(exercises)) * 100
    
    def get_diet_compliance_percentage(self, start_date, end_date):
        diets = [d for d in self.diets 
                if start_date <= d.date.date() <= end_date]
        if not diets:
            return 0
        followed = sum(1 for d in diets if d.is_followed)
        return (followed / len(diets)) * 100