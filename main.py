# main.py
import sys
from PyQt5.QtWidgets import QApplication
from database.connection import DatabaseConnection
from database.models import setup_database
from database.seeder import DataSeeder  
from ui.login_window import LoginWindow

def main():
    # PyQt uygulamasını başlat
    app = QApplication(sys.argv)
    
    try:
        # Veritabanı bağlantısını başlat
        db = DatabaseConnection.get_instance()
        
        # Veritabanı bağlantısını test et
        if not db.test_connection():
            raise Exception("Veritabanı bağlantısı kurulamadı.")
        
        # Veritabanı şemasını oluştur
        setup_database()
        
        # Veritabanı başlangıç verilerini ekle (Yeni eklenen kısım)
        DataSeeder.seed_database()
        
        # Giriş ekranını göster
        login_window = LoginWindow()
        login_window.show()
        
        # Uygulamayı çalıştır
        sys.exit(app.exec_())
        
    except Exception as e:
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.critical(None, "Hata", f"Uygulama başlatılırken bir hata oluştu:\n{str(e)}")
        sys.exit(1)
    finally:
        # Uygulama kapanırken veritabanı bağlantılarını kapat
        try:
            db = DatabaseConnection.get_instance()
            db.close_all_connections()
        except:
            pass

if __name__ == "__main__":
    main()