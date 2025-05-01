# database/queries.py
from database.connection import DatabaseConnection

class UserQueries:
    @staticmethod
    def insert_user(user):
        query = """
        INSERT INTO users (tc_id, password, name, surname, birthdate, gender, email, profile_image, user_type)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
        """
        params = (
            user.tc_id, user.password, user.name, user.surname, user.birthdate,
            user.gender, user.email, user.profile_image, user.user_type
        )
        
        db = DatabaseConnection.get_instance()
        result = db.execute_query(query, params)
        return result[0][0] if result else None
    
    @staticmethod
    def update_user(user):
        query = """
        UPDATE users
        SET name = %s, surname = %s, birthdate = %s, gender = %s, email = %s, 
            profile_image = %s, updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
        RETURNING id;
        """
        params = (
            user.name, user.surname, user.birthdate, user.gender, 
            user.email, user.profile_image, user.id
        )
        
        db = DatabaseConnection.get_instance()
        result = db.execute_query(query, params)
        return result[0][0] if result else None
    
    @staticmethod
    def get_user_by_tc_id(tc_id):
        query = """
        SELECT * FROM users WHERE tc_id = %s;
        """
        
        db = DatabaseConnection.get_instance()
        result = db.execute_query(query, (tc_id,))
        return result[0] if result else None
    
    @staticmethod
    def get_user_by_id(user_id):
        query = """
        SELECT * FROM users WHERE id = %s;
        """
        
        db = DatabaseConnection.get_instance()
        result = db.execute_query(query, (user_id,))
        return result[0] if result else None
    
    @staticmethod
    def update_password(user_id, new_password):
        query = """
        UPDATE users
        SET password = %s, updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
        RETURNING id;
        """
        
        db = DatabaseConnection.get_instance()
        result = db.execute_query(query, (new_password, user_id))
        return result[0][0] if result else None


class DoctorQueries:
    @staticmethod
    def insert_doctor(doctor, user_id):
        query = """
        INSERT INTO doctors (user_id, specialty, hospital)
        VALUES (%s, %s, %s)
        RETURNING id;
        """
        params = (user_id, doctor.specialty, doctor.hospital)
        
        db = DatabaseConnection.get_instance()
        result = db.execute_query(query, params)
        return result[0][0] if result else None
    
    @staticmethod
    def update_doctor(doctor):
        query = """
        UPDATE doctors
        SET specialty = %s, hospital = %s
        WHERE id = %s
        RETURNING id;
        """
        params = (doctor.specialty, doctor.hospital, doctor.id)
        
        db = DatabaseConnection.get_instance()
        result = db.execute_query(query, params)
        return result[0][0] if result else None
    
    @staticmethod
    def get_doctor_by_id(doctor_id):
        query = """
        SELECT d.*, u.tc_id, u.name, u.surname, u.birthdate, u.gender, 
               u.email, u.profile_image, u.user_type
        FROM doctors d
        JOIN users u ON d.user_id = u.id
        WHERE d.id = %s;
        """
        
        db = DatabaseConnection.get_instance()
        result = db.execute_query(query, (doctor_id,))
        return result[0] if result else None
    
    @staticmethod
    def get_doctor_by_user_id(user_id):
        query = """
        SELECT d.*, u.tc_id, u.name, u.surname, u.birthdate, u.gender, 
               u.email, u.profile_image, u.user_type
        FROM doctors d
        JOIN users u ON d.user_id = u.id
        WHERE d.user_id = %s;
        """
        
        db = DatabaseConnection.get_instance()
        result = db.execute_query(query, (user_id,))
        return result[0] if result else None
    
    @staticmethod
    def get_doctor_patients(doctor_id):
        query = """
        SELECT p.*, u.tc_id, u.name, u.surname, u.birthdate, u.gender, 
               u.email, u.profile_image, u.user_type
        FROM patients p
        JOIN users u ON p.user_id = u.id
        WHERE p.doctor_id = %s
        ORDER BY u.surname, u.name;
        """
        
        db = DatabaseConnection.get_instance()
        return db.execute_query(query, (doctor_id,))
    
    @staticmethod
    def get_all_doctors():
        query = """
        SELECT d.*, u.tc_id, u.name, u.surname, u.birthdate, u.gender, 
               u.email, u.profile_image, u.user_type
        FROM doctors d
        JOIN users u ON d.user_id = u.id
        ORDER BY u.surname, u.name;
        """
        
        db = DatabaseConnection.get_instance()
        return db.execute_query(query)


class PatientQueries:
    @staticmethod
    def insert_patient(patient, user_id):
        query = """
        INSERT INTO patients (user_id, doctor_id, diagnosis, diabetes_type, diagnosis_date)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id;
        """
        params = (
            user_id, patient.doctor_id, patient.diagnosis, 
            patient.diabetes_type, patient.diagnosis_date
        )
        
        db = DatabaseConnection.get_instance()
        result = db.execute_query(query, params)
        return result[0][0] if result else None
    
    @staticmethod
    def update_patient(patient):
        query = """
        UPDATE patients
        SET doctor_id = %s, diagnosis = %s, diabetes_type = %s, diagnosis_date = %s
        WHERE id = %s
        RETURNING id;
        """
        params = (
            patient.doctor_id, patient.diagnosis, 
            patient.diabetes_type, patient.diagnosis_date, patient.id
        )
        
        db = DatabaseConnection.get_instance()
        result = db.execute_query(query, params)
        return result[0][0] if result else None
    
    @staticmethod
    def get_patient_by_id(patient_id):
        query = """
        SELECT p.*, u.tc_id, u.name, u.surname, u.birthdate, u.gender, 
               u.email, u.profile_image, u.user_type
        FROM patients p
        JOIN users u ON p.user_id = u.id
        WHERE p.id = %s;
        """
        
        db = DatabaseConnection.get_instance()
        result = db.execute_query(query, (patient_id,))
        return result[0] if result else None
    
    @staticmethod
    def get_patient_by_user_id(user_id):
        query = """
        SELECT p.*, u.tc_id, u.name, u.surname, u.birthdate, u.gender, 
               u.email, u.profile_image, u.user_type
        FROM patients p
        JOIN users u ON p.user_id = u.id
        WHERE p.user_id = %s;
        """
        
        db = DatabaseConnection.get_instance()
        result = db.execute_query(query, (user_id,))
        return result[0] if result else None
    
    @staticmethod
    def get_patient_by_tc_id(tc_id):
        query = """
        SELECT p.*, u.tc_id, u.name, u.surname, u.birthdate, u.gender, 
               u.email, u.profile_image, u.user_type
        FROM patients p
        JOIN users u ON p.user_id = u.id
        WHERE u.tc_id = %s;
        """
        
        db = DatabaseConnection.get_instance()
        result = db.execute_query(query, (tc_id,))
        return result[0] if result else None


class MeasurementQueries:
    @staticmethod
    def insert_measurement(measurement):
        query = """
        INSERT INTO measurements (patient_id, glucose_level, measurement_date, 
                                measurement_time, period, notes)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id;
        """
        params = (
            measurement.patient_id, measurement.glucose_level, 
            measurement.measurement_date, measurement.measurement_time,
            measurement.period, measurement.notes
        )
        
        print(f"Sorgu: {query}")
        print(f"Parametreler: {params}")
        
        db = DatabaseConnection.get_instance()
        connection = None
        cursor = None
        
        try:
            connection = db.get_connection()
            print(f"Bağlantı durumu: {connection is not None}")
            cursor = connection.cursor()
            
            cursor.execute(query, params)
            result = cursor.fetchone()
            
            print(f"Sorgu sonucu: {result}")
            
            # Önemli: Commit işlemini burada yap
            connection.commit()
            print("Transaction başarıyla commit edildi")
            
            return result[0] if result else None
        except Exception as e:
            if connection:
                connection.rollback()
            print(f"Ölçüm eklenirken hata: {e}")
            raise  # Hatayı yeniden fırlat
        finally:
            if cursor:
                cursor.close()
            if connection:
                db.release_connection(connection)
    
    @staticmethod
    def get_measurements_by_patient_id(patient_id):
        query = """
        SELECT * FROM measurements 
        WHERE patient_id = %s
        ORDER BY measurement_date DESC, measurement_time DESC;
        """
        
        db = DatabaseConnection.get_instance()
        return db.execute_query(query, (patient_id,))
    
    @staticmethod
    def get_measurements_by_date_range(patient_id, start_date, end_date):
        query = """
        SELECT * FROM measurements 
        WHERE patient_id = %s
        AND measurement_date BETWEEN %s AND %s
        ORDER BY measurement_date, measurement_time;
        """
        
        db = DatabaseConnection.get_instance()
        return db.execute_query(query, (patient_id, start_date, end_date))
    
    @staticmethod
    def get_measurements_by_date(patient_id, date):
        query = """
        SELECT * FROM measurements 
        WHERE patient_id = %s
        AND measurement_date = %s
        ORDER BY measurement_time;
        """
        
        db = DatabaseConnection.get_instance()
        return db.execute_query(query, (patient_id, date))
    
    @staticmethod
    def get_latest_measurements(patient_id, limit=5):
        query = """
        SELECT * FROM measurements 
        WHERE patient_id = %s
        ORDER BY measurement_date DESC, measurement_time DESC
        LIMIT %s;
        """
        
        db = DatabaseConnection.get_instance()
        return db.execute_query(query, (patient_id, limit))
    
    @staticmethod
    def get_avg_glucose_by_date_range(patient_id, start_date, end_date):
        query = """
        SELECT AVG(glucose_level) as average_glucose FROM measurements 
        WHERE patient_id = %s
        AND measurement_date BETWEEN %s AND %s;
        """
        
        db = DatabaseConnection.get_instance()
        result = db.execute_query(query, (patient_id, start_date, end_date))
        return result[0]['average_glucose'] if result else None


class ExerciseQueries:
    @staticmethod
    def insert_exercise(exercise):
        query = """
        INSERT INTO exercises (patient_id, exercise_type, date, is_completed, notes)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id;
        """
        params = (
            exercise.patient_id, exercise.exercise_type, exercise.date,
            exercise.is_completed, exercise.notes
        )
        
        db = DatabaseConnection.get_instance()
        result = db.execute_query(query, params)
        return result[0][0] if result else None
    
    @staticmethod
    def update_exercise(exercise):
        query = """
        UPDATE exercises
        SET exercise_type = %s, date = %s, is_completed = %s, notes = %s, 
            updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
        RETURNING id;
        """
        params = (
            exercise.exercise_type, exercise.date, exercise.is_completed,
            exercise.notes, exercise.id
        )
        
        db = DatabaseConnection.get_instance()
        result = db.execute_query(query, params)
        return result[0][0] if result else None
    
    @staticmethod
    def get_exercises_by_patient_id(patient_id):
        query = """
        SELECT * FROM exercises 
        WHERE patient_id = %s
        ORDER BY date DESC;
        """
        
        db = DatabaseConnection.get_instance()
        return db.execute_query(query, (patient_id,))
    
    @staticmethod
    def get_exercises_by_date_range(patient_id, start_date, end_date):
        query = """
        SELECT * FROM exercises 
        WHERE patient_id = %s
        AND date BETWEEN %s AND %s
        ORDER BY date;
        """
        
        db = DatabaseConnection.get_instance()
        return db.execute_query(query, (patient_id, start_date, end_date))
    
    @staticmethod
    def get_exercise_compliance_percentage(patient_id, start_date, end_date):
        query = """
        SELECT 
            COUNT(*) as total_exercises,
            SUM(CASE WHEN is_completed THEN 1 ELSE 0 END) as completed_exercises
        FROM exercises 
        WHERE patient_id = %s
        AND date BETWEEN %s AND %s;
        """
        
        db = DatabaseConnection.get_instance()
        result = db.execute_query(query, (patient_id, start_date, end_date))
        
        if result and result[0]['total_exercises'] > 0:
            return (result[0]['completed_exercises'] / result[0]['total_exercises']) * 100
        return 0


class DietQueries:
    @staticmethod
    def insert_diet(diet):
        query = """
        INSERT INTO diets (patient_id, diet_type, date, is_followed, notes)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id;
        """
        params = (
            diet.patient_id, diet.diet_type, diet.date,
            diet.is_followed, diet.notes
        )
        
        db = DatabaseConnection.get_instance()
        result = db.execute_query(query, params)
        return result[0][0] if result else None
    
    @staticmethod
    def update_diet(diet):
        query = """
        UPDATE diets
        SET diet_type = %s, date = %s, is_followed = %s, notes = %s, 
            updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
        RETURNING id;
        """
        params = (
            diet.diet_type, diet.date, diet.is_followed,
            diet.notes, diet.id
        )
        
        db = DatabaseConnection.get_instance()
        result = db.execute_query(query, params)
        return result[0][0] if result else None
    
    @staticmethod
    def get_diets_by_patient_id(patient_id):
        query = """
        SELECT * FROM diets 
        WHERE patient_id = %s
        ORDER BY date DESC;
        """
        
        db = DatabaseConnection.get_instance()
        return db.execute_query(query, (patient_id,))
    
    @staticmethod
    def get_diets_by_date_range(patient_id, start_date, end_date):
        query = """
        SELECT * FROM diets 
        WHERE patient_id = %s
        AND date BETWEEN %s AND %s
        ORDER BY date;
        """
        
        db = DatabaseConnection.get_instance()
        return db.execute_query(query, (patient_id, start_date, end_date))
    
    @staticmethod
    def get_diet_compliance_percentage(patient_id, start_date, end_date):
        query = """
        SELECT 
            COUNT(*) as total_diets,
            SUM(CASE WHEN is_followed THEN 1 ELSE 0 END) as followed_diets
        FROM diets 
        WHERE patient_id = %s
        AND date BETWEEN %s AND %s;
        """
        
        db = DatabaseConnection.get_instance()
        result = db.execute_query(query, (patient_id, start_date, end_date))
        
        if result and result[0]['total_diets'] > 0:
            return (result[0]['followed_diets'] / result[0]['total_diets']) * 100
        return 0


class SymptomQueries:
    @staticmethod
    def insert_symptom(symptom):
        query = """
        INSERT INTO symptoms (patient_id, symptom_type, severity, date, notes)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id;
        """
        params = (
            symptom.patient_id, symptom.symptom_type, symptom.severity,
            symptom.date, symptom.notes
        )
        
        db = DatabaseConnection.get_instance()
        result = db.execute_query(query, params)
        return result[0][0] if result else None
    
    @staticmethod
    def get_symptoms_by_patient_id(patient_id):
        query = """
        SELECT * FROM symptoms 
        WHERE patient_id = %s
        ORDER BY date DESC;
        """
        
        db = DatabaseConnection.get_instance()
        return db.execute_query(query, (patient_id,))
    
    @staticmethod
    def get_symptoms_by_date_range(patient_id, start_date, end_date):
        query = """
        SELECT * FROM symptoms 
        WHERE patient_id = %s
        AND date BETWEEN %s AND %s
        ORDER BY date;
        """
        
        db = DatabaseConnection.get_instance()
        return db.execute_query(query, (patient_id, start_date, end_date))
    
    @staticmethod
    def get_symptoms_by_type(patient_id, symptom_type):
        query = """
        SELECT * FROM symptoms 
        WHERE patient_id = %s
        AND symptom_type = %s
        ORDER BY date DESC;
        """
        
        db = DatabaseConnection.get_instance()
        return db.execute_query(query, (patient_id, symptom_type))


class AlertQueries:
    @staticmethod
    def insert_alert(alert):
        query = """
        INSERT INTO alerts (patient_id, alert_type, message, glucose_level, date, is_read)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id;
        """
        params = (
            alert.patient_id, alert.alert_type, alert.message,
            alert.glucose_level, alert.date, alert.is_read
        )
        
        db = DatabaseConnection.get_instance()
        result = db.execute_query(query, params)
        return result[0][0] if result else None
    
    @staticmethod
    def mark_alert_as_read(alert_id):
        query = """
        UPDATE alerts
        SET is_read = TRUE
        WHERE id = %s
        RETURNING id;
        """
        
        db = DatabaseConnection.get_instance()
        result = db.execute_query(query, (alert_id,))
        return result[0][0] if result else None
    
    @staticmethod
    def get_alerts_by_patient_id(patient_id):
        query = """
        SELECT * FROM alerts 
        WHERE patient_id = %s
        ORDER BY date DESC;
        """
        
        db = DatabaseConnection.get_instance()
        return db.execute_query(query, (patient_id,))
    
    @staticmethod
    def get_unread_alerts_by_patient_id(patient_id):
        query = """
        SELECT * FROM alerts 
        WHERE patient_id = %s
        AND is_read = FALSE
        ORDER BY date DESC;
        """
        
        db = DatabaseConnection.get_instance()
        return db.execute_query(query, (patient_id,))
    
    @staticmethod
    def get_alerts_by_date_range(patient_id, start_date, end_date):
        query = """
        SELECT * FROM alerts 
        WHERE patient_id = %s
        AND date BETWEEN %s AND %s
        ORDER BY date DESC;
        """
        
        db = DatabaseConnection.get_instance()
        return db.execute_query(query, (patient_id, start_date, end_date))
    
    @staticmethod
    def get_alerts_by_type(patient_id, alert_type):
        query = """
        SELECT * FROM alerts 
        WHERE patient_id = %s
        AND alert_type = %s
        ORDER BY date DESC;
        """
        
        db = DatabaseConnection.get_instance()
        return db.execute_query(query, (patient_id, alert_type))


class InsulinQueries:
    @staticmethod
    def insert_insulin(insulin):
        query = """
        INSERT INTO insulins (patient_id, recommended_dose, administered_dose, 
                             average_glucose, date, notes)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id;
        """
        params = (
            insulin.patient_id, insulin.recommended_dose, insulin.administered_dose,
            insulin.average_glucose, insulin.date, insulin.notes
        )
        
        db = DatabaseConnection.get_instance()
        result = db.execute_query(query, params)
        return result[0][0] if result else None
    
    @staticmethod
    def update_insulin(insulin):
        query = """
        UPDATE insulins
        SET administered_dose = %s, notes = %s, updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
        RETURNING id;
        """
        params = (insulin.administered_dose, insulin.notes, insulin.id)
        
        db = DatabaseConnection.get_instance()
        result = db.execute_query(query, params)
        return result[0][0] if result else None
    
    @staticmethod
    def get_insulins_by_patient_id(patient_id):
        query = """
        SELECT * FROM insulins 
        WHERE patient_id = %s
        ORDER BY date DESC;
        """
        
        db = DatabaseConnection.get_instance()
        return db.execute_query(query, (patient_id,))
    
    @staticmethod
    def get_insulins_by_date_range(patient_id, start_date, end_date):
        query = """
        SELECT * FROM insulins 
        WHERE patient_id = %s
        AND date BETWEEN %s AND %s
        ORDER BY date;
        """
        
        db = DatabaseConnection.get_instance()
        return db.execute_query(query, (patient_id, start_date, end_date))

