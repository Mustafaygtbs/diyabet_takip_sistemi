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
        # Main window settings
        self.setWindowTitle("Diyabet Takip Sistemi")
        self.setMinimumSize(800, 600)
        self.setWindowIcon(QIcon("resources/medical-check.png"))
        
        # Main widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Left panel (visual and logo)
        left_panel = QFrame()
        left_panel.setStyleSheet("""
            background-color: #3949AB;
            border-top-left-radius: 10px;
            border-bottom-left-radius: 10px;
        """)
        left_panel.setMinimumWidth(300)
        
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)
        
        # Logo and app name
        logo_label = QLabel()
        logo_pixmap = QPixmap("resources/medical-check.png")
        logo_label.setPixmap(logo_pixmap.scaled(180, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo_label.setAlignment(Qt.AlignCenter)
        
        app_name = QLabel("Diyabet Takip Sistemi")
        app_name.setFont(QFont("Segoe UI", 18, QFont.Bold))
        app_name.setStyleSheet("color: white;")
        app_name.setAlignment(Qt.AlignCenter)
        
        app_subtitle = QLabel("Sağlıklı bir yaşam için kan şekeri takibi")
        app_subtitle.setFont(QFont("Segoe UI", 12))
        app_subtitle.setStyleSheet("color: rgba(255, 255, 255, 0.8);")
        app_subtitle.setAlignment(Qt.AlignCenter)
        
        left_layout.addStretch(1)
        left_layout.addWidget(logo_label)
        left_layout.addWidget(app_name)
        left_layout.addWidget(app_subtitle)
        left_layout.addStretch(2)
        
        # Right panel (login form)
        right_panel = QFrame()
        right_panel.setStyleSheet("""
            background-color: white;
            border-top-right-radius: 10px;
            border-bottom-right-radius: 10px;
        """)
        
        right_layout = QVBoxLayout()
        right_panel.setLayout(right_layout)
        
        # Login form
        login_form = QWidget()
        form_layout = QFormLayout()
        login_form.setLayout(form_layout)
        
        # Form title
        login_title = QLabel("Kullanıcı Girişi")
        login_title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        login_title.setStyleSheet("color: #333333; margin-bottom: 20px;")
        login_title.setAlignment(Qt.AlignCenter)
        
        # Login fields
        self.tc_input = QLineEdit()
        self.tc_input.setPlaceholderText("TC Kimlik Numarası")
        self.tc_input.setMaxLength(11)
        self.tc_input.setMinimumHeight(45)
        self.tc_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #E0E0E0;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                background-color: #F5F5F5;
            }
            QLineEdit:focus {
                border: 1px solid #3949AB;
                background-color: white;
            }
        """)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Şifre")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(45)
        self.password_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #E0E0E0;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                background-color: #F5F5F5;
            }
            QLineEdit:focus {
                border: 1px solid #3949AB;
                background-color: white;
            }
        """)
        
        form_layout.addRow("TC Kimlik:", self.tc_input)
        form_layout.addRow("Şifre:", self.password_input)
        
        # Login button
        self.login_button = QPushButton("Giriş Yap")
        self.login_button.setMinimumHeight(50)
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #3949AB;
                color: white;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #303F9F;
            }
            QPushButton:pressed {
                background-color: #1A237E;
            }
        """)
        
        self.login_button.clicked.connect(self.handle_login)
        
        # Enter key press to login
        self.tc_input.returnPressed.connect(self.handle_login)
        self.password_input.returnPressed.connect(self.handle_login)
        
        # Add form to right panel
        right_layout.addStretch(1)
        right_layout.addWidget(login_title)
        right_layout.addWidget(login_form)
        right_layout.addWidget(self.login_button)
        right_layout.addStretch(2)
        
        # Add panels to main layout
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)
        
        # Position window in center of screen
        self.center()
    
    def center(self):
        screen = self.screen().availableGeometry()
        window_size = self.geometry()
        x = (screen.width() - window_size.width()) // 2
        y = (screen.height() - window_size.height()) // 2
        self.move(x, y)
    
    def handle_login(self):
        tc_id = self.tc_input.text()
        password = self.password_input.text()
        
        # Input validation
        if not tc_id or not password:
            QMessageBox.warning(self, "Hata", "TC Kimlik ve Şifre alanları boş bırakılamaz.")
            return
        
        # Try to login
        user = AuthController.login(tc_id, password)
        
        if not user:
            QMessageBox.warning(self, "Hata", "TC Kimlik veya şifre hatalı.")
            return
        
        # Show appropriate panel based on user type
        if user.user_type == 'doctor':
            self.doctor_panel = DoctorPanel(user)
            self.doctor_panel.show()
            self.hide()
        elif user.user_type == 'patient':
            self.patient_panel = PatientPanel(user)
            self.patient_panel.show()
            self.hide()
        else:
            QMessageBox.warning(self, "Hata", "Kullanıcı tipi tanımlanamadı.")