# controllers/patient_controller.py
from datetime import datetime, timedelta
from models.patient import Patient
from models.measurement import Measurement
from models.exercise import Exercise
from models.diet import Diet
from models.symptom import Symptom
from models.insulin import Insulin
from database.queries import (
    PatientQueries, MeasurementQueries, ExerciseQueries, 
    DietQueries, SymptomQueries, InsulinQueries
)
from controllers.measurement_controller import MeasurementController
from controllers.alert_controller import AlertController

class PatientController:
    @staticmethod
    def get_patient_by_id(patient_id):
        patient_data = PatientQueries.get_patient_by_id(patient_id)
        
        if not patient_data:
            return None
        
        patient = Patient()
        patient.id = patient_data['id']
        patient.tc_id = patient_data['tc_id']
        patient.name = patient_data['name']
        patient.surname = patient_data['surname']
        patient.birthdate = patient_data['birthdate']
        patient.gender = patient_data['gender']
        patient.email = patient_data['email']
        patient.profile_image = patient_data['profile_image']
        patient.user_type = patient_data['user_type']
        patient.doctor_id = patient_data['doctor_id']
        patient.diagnosis = patient_data['diagnosis']
        patient.diabetes_type = patient_data['diabetes_type']
        patient.diagnosis_date = patient_data['diagnosis_date']
        
        return patient
    
    @staticmethod
    def add_measurement(patient_id, glucose_level, measurement_date, measurement_time, period=None, notes=None):
        """
        Hasta için kan şekeri ölçümü ekler.
        
        :return: Ölçüm ID
        """
        measurement = Measurement()
        measurement.patient_id = patient_id
        measurement.glucose_level = glucose_level
        measurement.measurement_date = measurement_date
        measurement.measurement_time = measurement_time
        
        # Periyodu otomatik tespit et
        if not period:
            period = Measurement.get_period_from_time(measurement_time)
        
        measurement.period = period
        measurement.notes = notes
        
        # Veritabanına ekle
        measurement_id = MeasurementQueries.insert_measurement(measurement)
        measurement.id = measurement_id
        
        # Ölçüme göre uyarı oluştur
        AlertController.create_glucose_alert(patient_id, glucose_level, period)
        
        # Gün sonunda ortalama hesapla ve insülin öner
        MeasurementController.calculate_daily_average_and_recommend_insulin(patient_id, measurement_date)
        
        return measurement_id
    
    @staticmethod
    def add_exercise_status(patient_id, exercise_type, date, is_completed, notes=None):
        """
        Hasta için egzersiz durumu ekler.
        
        :return: Egzersiz ID
        """
        exercise = Exercise()
        exercise.patient_id = patient_id
        exercise.exercise_type = exercise_type
        exercise.date = date
        exercise.is_completed = is_completed
        exercise.notes = notes
        
        # Veritabanına ekle
        exercise_id = ExerciseQueries.insert_exercise(exercise)
        
        return exercise_id
    
    @staticmethod
    def add_diet_status(patient_id, diet_type, date, is_followed, notes=None):
        """
        Hasta için diyet durumu ekler.
        
        :return: Diyet ID
        """
        diet = Diet()
        diet.patient_id = patient_id
        diet.diet_type = diet_type
        diet.date = date
        diet.is_followed = is_followed
        diet.notes = notes
        
        # Veritabanına ekle
        diet_id = DietQueries.insert_diet(diet)
        
        return diet_id
    
    @staticmethod
    def add_symptom(patient_id, symptom_type, severity, date, notes=None):
        """
        Hasta için belirti ekler.
        
        :return: Belirti ID
        """
        symptom = Symptom()
        symptom.patient_id = patient_id
        symptom.symptom_type = symptom_type
        symptom.severity = severity
        symptom.date = date
        symptom.notes = notes
        
        # Veritabanına ekle
        symptom_id = SymptomQueries.insert_symptom(symptom)
        
        return symptom_id
    
    @staticmethod
    def administer_insulin(insulin_id, administered_dose, notes=None):
        """
        İnsülin uygulama durumunu günceller.
        
        :return: Güncellenen insülin ID
        """
        # İnsülin kaydını al
        insulin = Insulin()
        insulin.id = insulin_id
        insulin.administered_dose = administered_dose
        insulin.notes = notes
        
        # Veritabanında güncelle
        updated_id = InsulinQueries.update_insulin(insulin)
        
        return updated_id
    
    @staticmethod
    def get_daily_measurements(patient_id, date=None):
        """
        Hastanın günlük ölçümlerini getirir.
        
        :param patient_id: Hasta ID
        :param date: Tarih (varsayılan: bugün)
        :return: Ölçüm listesi
        """
        if not date:
            date = datetime.now().date()
            
        return MeasurementQueries.get_measurements_by_date(patient_id, date)
    
    @staticmethod
    def get_glucose_average(patient_id, start_date=None, end_date=None):
        """
        Hastanın ortalama kan şekerini hesaplar.
        
        :param patient_id: Hasta ID
        :param start_date: Başlangıç tarihi
        :param end_date: Bitiş tarihi
        :return: Ortalama kan şekeri değeri
        """
        if not start_date:
            start_date = datetime.now().date() - timedelta(days=7)
        if not end_date:
            end_date = datetime.now().date()
            
        return MeasurementQueries.get_avg_glucose_by_date_range(patient_id, start_date, end_date)
    
    @staticmethod
    def get_insulin_recommendations(patient_id, start_date=None, end_date=None):
        """
        Hastanın insülin önerilerini getirir.
        
        :param patient_id: Hasta ID
        :param start_date: Başlangıç tarihi
        :param en
        """
        if not start_date:
            start_date = datetime.now().date() - timedelta(days=7)
        if not end_date:
            end_date = datetime.now().date()
            
        return InsulinQueries.get_insulins_by_date_range(patient_id, start_date, end_date)
    
    @staticmethod
    def get_current_recommendations(patient_id):
        """
        Hastanın mevcut durumuna göre öneriler sunar.
        
        :param patient_id: Hasta ID
        :return: Öneri bilgilerini içeren sözlük
        """
        # Son ölçümleri ve belirtileri al
        latest_measurements = MeasurementQueries.get_latest_measurements(patient_id, 5)
        
        if not latest_measurements:
            return None
        
        # Son ölçümü al
        latest_glucose = latest_measurements[0]['glucose_level']
        
        # Bugünkü belirtileri al
        today = datetime.now().date()
        symptoms_data = SymptomQueries.get_symptoms_by_date_range(patient_id, today, today)
        
        symptoms = []
        for s in symptoms_data:
            symptoms.append(s['symptom_type'])
        
        # Kurallar tablosuna göre uygun diyet ve egzersiz önerilerini belirle
        diet_type, exercise_type = PatientController._get_recommendations_by_rules(latest_glucose, symptoms)
        
        return {
            'glucose_level': latest_glucose,
            'diet_recommendation': diet_type,
            'exercise_recommendation': exercise_type
        }
    
    @staticmethod
    def _get_recommendations_by_rules(glucose_level, symptoms):
        """
        Kan şekeri ve belirtilere göre diyet ve egzersiz önerilerini belirler.
        
        :param glucose_level: Kan şekeri seviyesi
        :param symptoms: Belirti listesi
        :return: (diyet_türü, egzersiz_türü) çifti
        """
        # Projedeki kurallara göre önerileri belirle
        
        # Hipoglisemi: < 70 mg/dL
        if glucose_level < 70:
            if set(['neuropathy', 'polyphagia', 'fatigue']).intersection(symptoms):
                return Diet.TYPE_BALANCED, None
            return Diet.TYPE_BALANCED, None
        
        # Normal - Alt Düzey: 70-110 mg/dL
        elif 70 <= glucose_level <= 110:
            if set(['fatigue', 'weight_loss']).intersection(symptoms):
                return Diet.TYPE_LOW_SUGAR, Exercise.TYPE_WALKING
            elif set(['polyphagia', 'polydipsia']).intersection(symptoms):
                return Diet.TYPE_BALANCED, Exercise.TYPE_WALKING
            return Diet.TYPE_LOW_SUGAR, Exercise.TYPE_WALKING
        
        # Normal - Üst Düzey / Hafif Yüksek: 110-180 mg/dL
        elif 110 < glucose_level <= 180:
            if set(['blurred_vision', 'neuropathy']).intersection(symptoms):
                return Diet.TYPE_LOW_SUGAR, Exercise.TYPE_CLINICAL
            elif set(['polyuria', 'polydipsia']).intersection(symptoms):
                return Diet.TYPE_NO_SUGAR, Exercise.TYPE_CLINICAL
            elif set(['fatigue', 'neuropathy', 'blurred_vision']).intersection(symptoms):
                return Diet.TYPE_LOW_SUGAR, Exercise.TYPE_WALKING
            return Diet.TYPE_LOW_SUGAR, Exercise.TYPE_CLINICAL
        
        # Hiperglisemi: > 180 mg/dL
        else:
            if set(['slow_healing', 'polyphagia', 'polydipsia']).intersection(symptoms):
                return Diet.TYPE_NO_SUGAR, Exercise.TYPE_CLINICAL
            elif set(['slow_healing', 'weight_loss']).intersection(symptoms):
                return Diet.TYPE_NO_SUGAR, Exercise.TYPE_WALKING
            return Diet.TYPE_NO_SUGAR, Exercise.TYPE_CLINICAL
        
    @staticmethod
    def get_measurements_by_date_range(patient_id, start_date, end_date):
        """
        Belirlenen tarih aralığındaki ölçümleri getirir.
        
        :param patient_id: Hasta ID
        :param start_date: Başlangıç tarihi
        :param end_date: Bitiş tarihi
        :return: Ölçüm listesi
        """
        return MeasurementQueries.get_measurements_by_date_range(patient_id, start_date, end_date)
    @staticmethod
    def get_patient_measurements(patient_id, limit=None):
        """
        Hastanın ölçümlerini getirir.
        
        :param patient_id: Hasta ID
        :param limit: Maksimum ölçüm sayısı (varsayılan: None, tüm ölçümler)
        :return: Ölçüm listesi
        """
        measurements = MeasurementQueries.get_measurements_by_patient_id(patient_id)
        if limit and len(measurements) > limit:
            return measurements[:limit]
        return measurements
    @staticmethod
    def get_patient_diets(patient_id, limit=None):
        """
        Hastanın diyet kayıtlarını getirir.

        :param patient_id: Hasta ID
        :param limit: Maksimum kayıt sayısı (varsayılan: None, tüm kayıtlar)
        :return: Diyet kaydı listesi
        """
        diets = DietQueries.get_diets_by_patient_id(patient_id)
        return diets[:limit] if limit and diets else diets
    
    
    @staticmethod
    def get_patient_exercises(patient_id,limit=None):
        exercises = ExerciseQueries.get_exercises_by_patient_id(patient_id)
        return exercises[:limit] if limit and exercises else exercises
    
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