# models/doctor.py
from models.user import User

class Doctor(User):
    def __init__(self, tc_id=None, password=None, name=None, surname=None, 
                 birthdate=None, gender=None, email=None, profile_image=None, 
                 specialty=None, hospital=None, id=None):
        super().__init__(tc_id, password, name, surname, birthdate, gender, 
                         email, profile_image, 'doctor', id)
        self.specialty = specialty
        self.hospital = hospital
        self.patients = []
    
    def add_patient(self, patient):
        if patient not in self.patients:
            self.patients.append(patient)
    
    def remove_patient(self, patient):
        if patient in self.patients:
            self.patients.remove(patient)
    
    def to_dict(self):
        doctor_dict = super().to_dict()
        doctor_dict.update({
            'specialty': self.specialty,
            'hospital': self.hospital
        })
        return doctor_dict
    
    @staticmethod
    def from_dict(data):
        doctor = Doctor()
        doctor.id = data.get('id')
        doctor.tc_id = data.get('tc_id')
        doctor.password = data.get('password')
        doctor.name = data.get('name')
        doctor.surname = data.get('surname')
        doctor.birthdate = data.get('birthdate')
        doctor.gender = data.get('gender')
        doctor.email = data.get('email')
        doctor.profile_image = data.get('profile_image')
        doctor.user_type = 'doctor'
        doctor.specialty = data.get('specialty')
        doctor.hospital = data.get('hospital')
        doctor.created_at = data.get('created_at')
        doctor.updated_at = data.get('updated_at')
        return doctor