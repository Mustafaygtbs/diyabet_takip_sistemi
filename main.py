import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from database.connection import DatabaseConnection
from database.models import setup_database
from database.seeder import DataSeeder  
from ui.login_window import LoginWindow

def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("resources/medical-check.png"))  
    
    try:

        db = DatabaseConnection.get_instance()
        

        if not db.test_connection():
            raise Exception("Veritabanı bağlantısı kurulamadı.")
        

        setup_database()
        
        DataSeeder.seed_database()
        
 
        login_window = LoginWindow()
        login_window.setWindowIcon(QIcon("resources/medical-check.png"))  
        login_window.show()
        
 
        sys.exit(app.exec_())
        
    except Exception as e:
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.critical(None, "Hata", f"Uygulama başlatılırken bir hata oluştu:\n{str(e)}")
        sys.exit(1)
    finally:
 
        try:
            db = DatabaseConnection.get_instance()
            db.close_all_connections()
        except:
            pass

if __name__ == "__main__":
    main()