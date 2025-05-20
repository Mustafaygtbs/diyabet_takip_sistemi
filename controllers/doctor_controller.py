# controllers/doctor_controller.py
import random
import string
from datetime import datetime, timedelta
from models.doctor import Doctor
from models.patient import Patient
from models.user import User
from database.queries import (
    UserQueries, DoctorQueries, PatientQueries, 
    MeasurementQueries, ExerciseQueries, DietQueries, SymptomQueries, AlertQueries, ManualRecommendationQueries
)
from controllers.auth_controller import AuthController
from utils.email_sender import EmailSender
from database.connection import DatabaseConnection 
class DoctorController:
    @staticmethod
    def register_doctor(tc_id, password, name, surname, birthdate, gender, email, 
                        profile_image, specialty, hospital):
        """
        Doktor kaydeder.
        
        :return: Başarılıysa doktor nesnesi, değilse None
        """
        # Kullanıcı nesnesi oluştur
        doctor = Doctor()
        doctor.tc_id = tc_id
        doctor.password = AuthController.hash_password(password)
        doctor.name = name
        doctor.surname = surname
        doctor.birthdate = birthdate
        doctor.gender = gender
        doctor.email = email
        doctor.profile_image = profile_image
        doctor.specialty = specialty
        doctor.hospital = hospital
        
        # Kullanıcı tablosuna ekle
        user_id = UserQueries.insert_user(doctor)
        
        if not user_id:
            return None
        
        # Doktor tablosuna ekle
        doctor_id = DoctorQueries.insert_doctor(doctor, user_id)
        
        if not doctor_id:
            return None
        
        doctor.id = doctor_id
        return doctor
    
    @staticmethod
    def update_doctor_profile(doctor_id, name, surname, birthdate, gender, email, 
                             profile_image, specialty, hospital):
        """
        Doktor profilini günceller.
        
        :return: Başarılıysa doktor nesnesi, değilse None
        """
        # Doktor verisini al
        doctor_data = DoctorQueries.get_doctor_by_id(doctor_id)
        
        if not doctor_data:
            return None
        
        # User nesnesi oluştur
        doctor = Doctor()
        doctor.id = doctor_id
        doctor.tc_id = doctor_data['tc_id']
        doctor.name = name
        doctor.surname = surname
        doctor.birthdate = birthdate
        doctor.gender = gender
        doctor.email = email
        doctor.profile_image = profile_image if profile_image else doctor_data['profile_image']
        doctor.specialty = specialty
        doctor.hospital = hospital
        
        # User tablosunu güncelle
        updated_user_id = UserQueries.update_user(doctor)
        
        if not updated_user_id:
            return None
        
        # Doktor tablosunu güncelle
        updated_doctor_id = DoctorQueries.update_doctor(doctor)
        
        if not updated_doctor_id:
            return None
        
        return doctor
    
    @staticmethod
    def get_doctor_by_id(doctor_id):
        """
        ID'ye göre doktor getirir.
        
        :param doctor_id: Doktor ID
        :return: Doktor nesnesi veya None
        """
        doctor_data = DoctorQueries.get_doctor_by_id(doctor_id)
        
        if not doctor_data:
            return None
        
        doctor = Doctor()
        doctor.id = doctor_data['id']
        doctor.tc_id = doctor_data['tc_id']
        doctor.name = doctor_data['name']
        doctor.surname = doctor_data['surname']
        doctor.birthdate = doctor_data['birthdate']
        doctor.gender = doctor_data['gender']
        doctor.email = doctor_data['email']
        doctor.profile_image = doctor_data['profile_image']
        doctor.user_type = doctor_data['user_type']
        doctor.specialty = doctor_data['specialty']
        doctor.hospital = doctor_data['hospital']
        
        return doctor
    
    @staticmethod
    def get_doctor_patients(doctor_id):
        """
        Doktorun hastalarını getirir.
        
        :param doctor_id: Doktor ID
        :return: Hasta nesnelerinin listesi
        """
        patients_data = DoctorQueries.get_doctor_patients(doctor_id)
        
        if not patients_data:
            return []
        
        patients = []
        for data in patients_data:
            patient = Patient()
            patient.id = data['id']
            patient.tc_id = data['tc_id']
            patient.name = data['name']
            patient.surname = data['surname']
            patient.birthdate = data['birthdate']
            patient.gender = data['gender']
            patient.email = data['email']
            patient.profile_image = data['profile_image']
            patient.user_type = data['user_type']
            patient.doctor_id = data['doctor_id']
            patient.diagnosis = data['diagnosis']
            patient.diabetes_type = data['diabetes_type']
            patient.diagnosis_date = data['diagnosis_date']
            patients.append(patient)
        
        return patients
    
    
    @staticmethod
    def register_patient(doctor_id, tc_id, name, surname, birthdate, gender, email, 
                        profile_image, diagnosis, diabetes_type, diagnosis_date):
        """
        Hasta kaydeder.
        
        :return: Başarılıysa hasta nesnesi, değilse None
        """
        db = DatabaseConnection.get_instance()
        connection = None
        cursor = None
        
        try:
            # Veritabanı bağlantısı al
            connection = db.get_connection()
            cursor = connection.cursor()
            
            # Rastgele şifre oluştur
            password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            
            # Kullanıcı nesnesi oluştur
            patient = Patient()
            patient.tc_id = tc_id
            patient.password = AuthController.hash_password(password)
            patient.name = name
            patient.surname = surname
            patient.birthdate = birthdate
            patient.gender = gender
            patient.email = email
            
            # Profil resmi işleme - QByteArray sorununu çöz
            if profile_image is not None:
                if hasattr(profile_image, 'data'):
                    # QByteArray için data() metodu kullanılır
                    patient.profile_image = bytes(profile_image.data())
                elif isinstance(profile_image, bytes):
                    # Zaten bytes tipinde ise direkt kullan
                    patient.profile_image = profile_image
                else:
                    # Diğer durumlarda None olarak ayarla
                    patient.profile_image = None
            else:
                patient.profile_image = None
            
            # Transaction başlat
            connection.autocommit = False
            
            # Users tablosuna ekle
            insert_user_query = """
            INSERT INTO users (tc_id, password, name, surname, birthdate, gender, email, profile_image, user_type)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
            """
            
            cursor.execute(insert_user_query, (
                patient.tc_id, 
                patient.password, 
                patient.name, 
                patient.surname, 
                patient.birthdate, 
                patient.gender, 
                patient.email, 
                patient.profile_image, 
                'patient'
            ))
            
            user_id = cursor.fetchone()[0]
            
            if not user_id:
                connection.rollback()
                return None
            
            # Patients tablosuna ekle
            insert_patient_query = """
            INSERT INTO patients (user_id, doctor_id, diagnosis, diabetes_type, diagnosis_date)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
            """
            
            cursor.execute(insert_patient_query, (
                user_id,
                doctor_id,
                diagnosis,
                diabetes_type,
                diagnosis_date
            ))
            
            patient_id = cursor.fetchone()[0]
            
            if not patient_id:
                connection.rollback()
                return None
            
            # Transaction'ı onayla
            connection.commit()
            
            patient.id = patient_id
            
            # Hastaya bilgilendirme e-postası gönder
            subject = "Diyabet Takip Sistemi - Hasta Kaydınız"
            message = f"""
            Sayın {name} {surname},
            
            Diyabet Takip Sistemi'ne kaydınız oluşturulmuştur.
            
            Giriş bilgileriniz:
            TC Kimlik: {tc_id}
            Şifre: {password}
            
            İlk girişinizden sonra güvenliğiniz için lütfen şifrenizi değiştiriniz.
            
            Sağlıklı günler dileriz.
            """
            
            try:
                EmailSender.send_email(email, subject, message)
            except Exception as e:
                pass  # E-posta gönderilemese bile hasta kaydı oluşturuldu
            
            return patient
            
        except Exception as e:
            if connection:
                connection.rollback()
            print(f"Hasta kaydı sırasında hata: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.autocommit = True  # Orijinal duruma geri getir
                db.release_connection(connection)
        
   
    
    @staticmethod
    def get_patient_measurements(patient_id, start_date=None, end_date=None):
        """
        Hastanın ölçümlerini getirir.
        
        :param patient_id: Hasta ID
        :param start_date: Başlangıç tarihi (opsiyonel)
        :param end_date: Bitiş tarihi (opsiyonel)
        :return: Ölçüm listesi
        """
        if start_date and end_date:
            return MeasurementQueries.get_measurements_by_date_range(patient_id, start_date, end_date)
        else:
            return MeasurementQueries.get_measurements_by_patient_id(patient_id)
    
    @staticmethod
    def get_patient_exercises(patient_id, start_date=None, end_date=None):
        """
        Hastanın egzersizlerini getirir.
        
        :param patient_id: Hasta ID
        :param start_date: Başlangıç tarihi (opsiyonel)
        :param end_date: Bitiş tarihi (opsiyonel)
        :return: Egzersiz listesi
        """
        if start_date and end_date:
            return ExerciseQueries.get_exercises_by_date_range(patient_id, start_date, end_date)
        else:
            return ExerciseQueries.get_exercises_by_patient_id(patient_id)
    
    @staticmethod
    def get_patient_diets(patient_id, start_date=None, end_date=None):
        """
        Hastanın diyet planlarını getirir.
        
        :param patient_id: Hasta ID
        :param start_date: Başlangıç tarihi (opsiyonel)
        :param end_date: Bitiş tarihi (opsiyonel)
        :return: Diyet listesi
        """
        if start_date and end_date:
            return DietQueries.get_diets_by_date_range(patient_id, start_date, end_date)
        else:
            return DietQueries.get_diets_by_patient_id(patient_id)
    
    @staticmethod
    def get_patient_symptoms(patient_id, start_date=None, end_date=None, symptom_type=None):
        """
        Hastanın belirtilerini getirir.
        
        :param patient_id: Hasta ID
        :param start_date: Başlangıç tarihi (opsiyonel)
        :param end_date: Bitiş tarihi (opsiyonel)
        :param symptom_type: Belirti türü (opsiyonel)
        :return: Belirti listesi
        """
        if symptom_type:
            return SymptomQueries.get_symptoms_by_type(patient_id, symptom_type)
        elif start_date and end_date:
            return SymptomQueries.get_symptoms_by_date_range(patient_id, start_date, end_date)
        else:
            return SymptomQueries.get_symptoms_by_patient_id(patient_id)
    
    @staticmethod
    def get_patient_alerts(patient_id, start_date=None, end_date=None, alert_type=None, only_unread=False):
        """
        Hastanın uyarılarını getirir.
        
        :param patient_id: Hasta ID
        :param start_date: Başlangıç tarihi (opsiyonel)
        :param end_date: Bitiş tarihi (opsiyonel)
        :param alert_type: Uyarı türü (opsiyonel)
        :param only_unread: Sadece okunmamış uyarılar (opsiyonel)
        :return: Uyarı listesi
        """
        if only_unread:
            return AlertQueries.get_unread_alerts_by_patient_id(patient_id)
        elif alert_type:
            return AlertQueries.get_alerts_by_type(patient_id, alert_type)
        elif start_date and end_date:
            return AlertQueries.get_alerts_by_date_range(patient_id, start_date, end_date)
        else:
            return AlertQueries.get_alerts_by_patient_id(patient_id)
    
    @staticmethod
    def get_exercise_compliance(patient_id, start_date=None, end_date=None):
        """
        Hastanın egzersiz uyum yüzdesini hesaplar.
        
        :param patient_id: Hasta ID
        :param start_date: Başlangıç tarihi (opsiyonel)
        :param end_date: Bitiş tarihi (opsiyonel)
        :return: Uyum yüzdesi (0-100)
        """
        if not start_date:
            start_date = datetime.now().date() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now().date()
            
        return ExerciseQueries.get_exercise_compliance_percentage(patient_id, start_date, end_date)
    
    @staticmethod
    def get_diet_compliance(patient_id, start_date=None, end_date=None):
        """
        Hastanın diyet uyum yüzdesini hesaplar.
        
        :param patient_id: Hasta ID
        :param start_date: Başlangıç tarihi (opsiyonel)
        :param end_date: Bitiş tarihi (opsiyonel)
        :return: Uyum yüzdesi (0-100)
        """
        if not start_date:
            start_date = datetime.now().date() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now().date()
            
        return DietQueries.get_diet_compliance_percentage(patient_id, start_date, end_date)
    
    @staticmethod
    def update_patient_profile(patient_id, name, surname, birthdate, gender, email, profile_image, diagnosis, diabetes_type, diagnosis_date):
        """
        Hastanın profilini günceller.
        :return: Başarılıysa hasta nesnesi, değilse None
        """
        # Hasta verisini al
        patient_data = PatientQueries.get_patient_by_id(patient_id)
        if not patient_data:
            return None

        # User tablosundaki id'yi al
        user_id = patient_data['user_id']

        # Patient nesnesi oluştur
        patient = Patient()
        patient.id = patient_id
        patient.tc_id = patient_data['tc_id']
        patient.name = name
        patient.surname = surname
        patient.birthdate = birthdate
        patient.gender = gender
        patient.email = email
        patient.profile_image = profile_image if profile_image else patient_data['profile_image']
        patient.doctor_id = patient_data['doctor_id']
        patient.diagnosis = diagnosis
        patient.diabetes_type = diabetes_type
        patient.diagnosis_date = diagnosis_date

        # User tablosunu güncelle
        # User modelinin id'si user_id olmalı
        from models.user import User
        user = User()
        user.id = user_id
        user.name = name
        user.surname = surname
        user.birthdate = birthdate
        user.gender = gender
        user.email = email
        user.profile_image = profile_image if profile_image else patient_data['profile_image']

        updated_user_id = UserQueries.update_user(user)
        if not updated_user_id:
            return None

        # Patient tablosunu güncelle
        updated_patient_id = PatientQueries.update_patient(patient)
        if not updated_patient_id:
            return None

        return patient
    
    def filter_patients(self):
        search_text = self.search_input.text().lower()
        
        for i in range(self.patient_list.count()):
            item = self.patient_list.item(i)
            patient_id = item.data(Qt.UserRole)
            patient = PatientController.get_patient_by_id(patient_id)
            
            if (search_text in f"{patient.name} {patient.surname}".lower() or
                search_text in patient.tc_id.lower() or
                (patient.diagnosis and search_text in patient.diagnosis.lower())):
                item.setHidden(False)
            else:
                item.setHidden(True)

    @staticmethod
    def add_manual_recommendation(doctor_id, patient_id, recommendation_type, content):
        """
        Doktorun hastaya manuel öneri eklemesini sağlar.
        """
        from models.manual_recommendation import ManualRecommendation
        recommendation = ManualRecommendation(
            doctor_id=doctor_id,
            patient_id=patient_id,
            recommendation_type=recommendation_type,
            content=content
        )
        return ManualRecommendationQueries.insert_manual_recommendation(recommendation)

    @staticmethod
    def get_manual_recommendations_by_patient(patient_id):
        """
        Hastanın tüm manuel doktor önerilerini getirir.
        """
        return ManualRecommendationQueries.get_manual_recommendations_by_patient(patient_id)