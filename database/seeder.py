# database/seeder.py
from datetime import date
from models.doctor import Doctor
from controllers.auth_controller import AuthController
from database.connection import DatabaseConnection

class DataSeeder:
    @staticmethod
    def seed_database():
        """
        Veritabanına başlangıç verilerini ekler.
        """
        try:
            print("Veritabanına başlangıç verileri ekleniyor...")
            # Admin doktor ekleme
            DataSeeder.seed_admin_doctor()
            print("Veritabanı başlangıç verileri başarıyla eklendi.")
            return True
        except Exception as e:
            print(f"Veritabanı başlangıç verileri eklenirken hata: {e}")
            return False

    @staticmethod
    def seed_admin_doctor():
        """
        Admin doktor ekler (eğer yoksa).
        """
        admin_tc = "12345678910"  # Admin doktor TC
        
        # Kullanıcı zaten var mı kontrol et
        db = DatabaseConnection.get_instance()
        connection = None
        cursor = None
        
        try:
            connection = db.get_connection()
            cursor = connection.cursor()
            
            # TC kimliğine göre kullanıcıyı kontrol et
            cursor.execute("SELECT COUNT(*) FROM users WHERE tc_id = %s", (admin_tc,))
            result = cursor.fetchone()
            
            if result[0] > 0:
                print("Admin doktor zaten mevcut.")
                return
            
            # Transaction başlat
            cursor.execute("BEGIN;")
            
            # Users tablosuna ekle
            cursor.execute("""
                INSERT INTO users (tc_id, password, name, surname, birthdate, gender, email, profile_image, user_type)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
            """, (
                admin_tc,
                AuthController.hash_password("admin123"),
                "Admin",
                "Doktor",
                date(1980, 1, 1),
                "E",
                "admin@diyabet.com",
                None,
                "doctor"
            ))
            
            user_id = cursor.fetchone()[0]
            
            # Doctors tablosuna ekle
            cursor.execute("""
                INSERT INTO doctors (user_id, specialty, hospital)
                VALUES (%s, %s, %s)
                RETURNING id;
            """, (
                user_id,
                "Endokrinoloji",
                "Merkez Hastanesi"
            ))
            
            doctor_id = cursor.fetchone()[0]
            
            # İşlemleri onayla
            cursor.execute("COMMIT;")
            
            print(f"Admin doktor başarıyla oluşturuldu. ID: {doctor_id}")
            
        except Exception as e:
            if cursor:
                cursor.execute("ROLLBACK;")
            print(f"Admin doktor oluşturulurken hata: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                db.release_connection(connection)