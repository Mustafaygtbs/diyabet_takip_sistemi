# ui/login_window.py
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QLineEdit, QPushButton, QMessageBox,
                            QFrame, QFormLayout)
from PyQt5.QtGui import QPixmap, QIcon, QFont
from PyQt5.QtCore import Qt

from controllers.auth_controller import AuthController
from ui.doctor_panel import DoctorPanel
from ui.patient_panel import PatientPanel

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        # Ana pencere ayarları
        self.setWindowTitle("Diyabet Takip Sistemi - Giriş")
        self.setMinimumSize(800, 600)
        self.setWindowIcon(QIcon("resources/icons/app_icon.png"))
        
        # Ana widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Ana layout
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Sol panel (görsel ve logo)
        left_panel = QFrame()
        left_panel.setStyleSheet("background-color: #3498db;")
        left_panel.setMinimumWidth(300)
        
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)
        
        # Logo ve uygulama adı
        logo_label = QLabel()
        logo_pixmap = QPixmap("resources/icons/logo.png")
        logo_label.setPixmap(logo_pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo_label.setAlignment(Qt.AlignCenter)
        
        app_name = QLabel("Diyabet Takip Sistemi")
        app_name.setFont(QFont("Arial", 18, QFont.Bold))
        app_name.setStyleSheet("color: white;")
        app_name.setAlignment(Qt.AlignCenter)
        
        left_layout.addStretch(1)
        left_layout.addWidget(logo_label)
        left_layout.addWidget(app_name)
        left_layout.addStretch(2)
        
        # Sağ panel (giriş formu)
        right_panel = QFrame()
        right_panel.setStyleSheet("background-color: white;")
        
        right_layout = QVBoxLayout()
        right_panel.setLayout(right_layout)
        
        # Giriş formu
        login_form = QWidget()
        form_layout = QFormLayout()
        login_form.setLayout(form_layout)
        
        # Giriş alanları
        self.tc_input = QLineEdit()
        self.tc_input.setPlaceholderText("TC Kimlik Numarası")
        self.tc_input.setMaxLength(11)
        self.tc_input.setMinimumHeight(40)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Şifre")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(40)
        
        form_layout.addRow("TC Kimlik:", self.tc_input)
        form_layout.addRow("Şifre:", self.password_input)
        
        # Giriş butonu
        self.login_button = QPushButton("Giriş Yap")
        self.login_button.setMinimumHeight(50)
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        self.login_button.clicked.connect(self.handle_login)
        
        # Enter tuşuna basılınca giriş yap
        self.tc_input.returnPressed.connect(self.handle_login)
        self.password_input.returnPressed.connect(self.handle_login)
        
        # Sağ panele form ekle
        right_layout.addStretch(1)
        right_layout.addWidget(QLabel("<h2>Kullanıcı Girişi</h2>"))
        right_layout.addWidget(login_form)
        right_layout.addWidget(self.login_button)
        right_layout.addStretch(2)
        
        # Ana layout'a panelleri ekle
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)
        
        # Pencereyi ekranın ortasına yerleştir
        self.center()
    
    def center(self):
        """Pencereyi ekranın ortasına yerleştirir."""
        screen = self.screen().availableGeometry()
        window_size = self.geometry()
        x = (screen.width() - window_size.width()) // 2
        y = (screen.height() - window_size.height()) // 2
        self.move(x, y)
    
    def handle_login(self):
        """Giriş işlemini gerçekleştirir."""
        tc_id = self.tc_input.text()
        password = self.password_input.text()
        
        # Girdi doğrulama
        if not tc_id or not password:
            QMessageBox.warning(self, "Hata", "TC Kimlik ve Şifre alanları boş bırakılamaz.")
            return
        
        # Giriş yapmayı dene
        user = AuthController.login(tc_id, password)
        
        if not user:
            QMessageBox.warning(self, "Hata", "TC Kimlik veya şifre hatalı.")
            return
        
        # Kullanıcı tipine göre ilgili paneli göster
        if user.user_type == 'doctor':
            # Doktor panelini aç
            self.doctor_panel = DoctorPanel(user)
            self.doctor_panel.show()
            self.hide()
        elif user.user_type == 'patient':
            # Hasta panelini aç
            self.patient_panel = PatientPanel(user)
            self.patient_panel.show()
            self.hide()
        else:
            QMessageBox.warning(self, "Hata", "Kullanıcı tipi tanımlanamadı.")