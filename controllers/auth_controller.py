
import hashlib
import os
import binascii
from database.queries import UserQueries, DoctorQueries, PatientQueries
from models.user import User
from models.doctor import Doctor
from models.patient import Patient

class AuthController:
    @staticmethod
    def hash_password(password):
        """
        Şifreyi güvenli bir şekilde hash'ler.
        """
        # Salt oluşturma
        salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
        # PBKDF2 ile hash'leme
        hash_bytes = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 100000)
        hash_hex = binascii.hexlify(hash_bytes)
        # Salt ve hash'i birleştirme
        return (salt + hash_hex).decode('ascii')
    
    @staticmethod
    def verify_password(stored_password, provided_password):

        
        salt = stored_password[:64]
        stored_hash = stored_password[64:]
        
        # Aynı salt ile hash'leme
        hash_bytes = hashlib.pbkdf2_hmac('sha512', provided_password.encode('utf-8'), 
                                        salt.encode('ascii'), 100000)
        hash_hex = binascii.hexlify(hash_bytes).decode('ascii')
        
        
        return hash_hex == stored_hash
        

    @staticmethod
    def login(tc_id, password):
        """
        Kullanıcı girişi yapar.
        """
        user_data = UserQueries.get_user_by_tc_id(tc_id)
        
        if not user_data:
            return None
        
        stored_password = user_data['password']
        
        if not AuthController.verify_password(stored_password, password):
            return None
        
        # Kullanıcı tipine göre doktor veya hasta nesnesi dön
        if user_data['user_type'] == 'doctor':
            doctor_data = DoctorQueries.get_doctor_by_user_id(user_data['id'])
            if doctor_data:
                doctor = Doctor()
                doctor.id = doctor_data['id']
                doctor.tc_id = user_data['tc_id']
                doctor.name = user_data['name']
                doctor.surname = user_data['surname']
                doctor.birthdate = user_data['birthdate']
                doctor.gender = user_data['gender']
                doctor.email = user_data['email']
                doctor.profile_image = user_data['profile_image']
                doctor.user_type = user_data['user_type']
                doctor.specialty = doctor_data['specialty']
                doctor.hospital = doctor_data['hospital']
                return doctor
        elif user_data['user_type'] == 'patient':
            patient_data = PatientQueries.get_patient_by_user_id(user_data['id'])
            if patient_data:
                patient = Patient()
                patient.id = patient_data['id']
                patient.tc_id = user_data['tc_id']
                patient.name = user_data['name']
                patient.surname = user_data['surname']
                patient.birthdate = user_data['birthdate']
                patient.gender = user_data['gender']
                patient.email = user_data['email']
                patient.profile_image = user_data['profile_image']
                patient.user_type = user_data['user_type']
                patient.doctor_id = patient_data['doctor_id']
                patient.diagnosis = patient_data['diagnosis']
                patient.diabetes_type = patient_data['diabetes_type']
                patient.diagnosis_date = patient_data['diagnosis_date']
                return patient
        
        return None
    
    @staticmethod
    def change_password(user_id, old_password, new_password):
        # user_id patients tablosundan geliyor, users tablosundan almalıyız
        patient_data = PatientQueries.get_patient_by_id(user_id)
        
        if not patient_data:
            return False
        
        # Patient verisinden user_id'yi al
        real_user_id = patient_data['user_id']

        
        user_data = UserQueries.get_user_by_id(real_user_id)
        
        if not user_data:
            print(f"User not found with ID: {real_user_id}")
            return False
        
        stored_password = user_data['password']
        
        if not AuthController.verify_password(stored_password, old_password):
            print("Password verification failed")
            return False
        
        # Yeni şifreyi hash'le
        hashed_password = AuthController.hash_password(new_password)
        
        # Şifreyi güncelle
        result = UserQueries.update_password(real_user_id, hashed_password)
        print(f"Password update result: {result}")
        
        return result is not None