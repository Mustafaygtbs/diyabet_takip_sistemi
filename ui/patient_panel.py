# ui/patient_panel.py
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QTabWidget, QTableWidget,
                            QTableWidgetItem, QFrame, QSplitter, QComboBox,
                            QDateEdit, QMessageBox, QHeaderView, QMenu,
                            QAction, QStackedWidget, QFormLayout, QLineEdit,
                            QTextEdit, QRadioButton, QButtonGroup, QCheckBox,
                            QSpacerItem, QSizePolicy, QScrollArea, QListWidget,
                            QListWidgetItem, QGridLayout, QDialog, QFileDialog,
                            QGroupBox, QTimeEdit)
from PyQt5.QtGui import QIcon, QPixmap, QFont, QColor
from PyQt5.QtCore import Qt, QDate, QTime

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from models.patient import Patient
from models.measurement import Measurement
from models.exercise import Exercise
from models.diet import Diet
from models.symptom import Symptom
from models.insulin import Insulin

from controllers.patient_controller import PatientController
from controllers.auth_controller import AuthController

from ui.widgets.glucose_chart import GlucoseChartWidget

from utils.date_utils import DateUtils
from utils.validators import Validators

from datetime import datetime, timedelta, time

class PatientPanel(QMainWindow):
    def __init__(self, patient):
        super().__init__()
        self.patient = patient
        self.initUI()
        self.load_dashboard()
    
    def initUI(self):
        # Ana pencere ayarları
        self.setWindowTitle(f"Diyabet Takip Sistemi - {self.patient.name} {self.patient.surname}")
        self.setMinimumSize(1024, 768)
        self.setWindowIcon(QIcon("resources/icons/app_icon.png"))
        
        # Ana widget ve layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Üst panel - Kullanıcı bilgileri ve çıkış düğmesi
        top_panel = QWidget()
        top_layout = QHBoxLayout()
        top_panel.setLayout(top_layout)
        top_panel.setMaximumHeight(80)
        top_panel.setStyleSheet("background-color: #3498db; color: white;")
        
        # Hasta bilgileri
        patient_info = QWidget()
        patient_info_layout = QHBoxLayout()
        patient_info.setLayout(patient_info_layout)
        
        # Profil resmi
        profile_pic = QLabel()
        if self.patient.profile_image:
            pixmap = QPixmap()
            pixmap.loadFromData(self.patient.profile_image)
            profile_pic.setPixmap(pixmap.scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            profile_pic.setText("👤")
            profile_pic.setFont(QFont("Arial", 24))
        
        profile_pic.setAlignment(Qt.AlignCenter)
        profile_pic.setFixedSize(60, 60)
        profile_pic.setStyleSheet("background-color: white; border-radius: 30px;")
        
        # Hasta adı ve tipi
        patient_name = QLabel(f"{self.patient.name} {self.patient.surname}")
        patient_name.setFont(QFont("Arial", 14, QFont.Bold))
        
        patient_type = QLabel(self.patient.diabetes_type or "Hasta")
        patient_type.setFont(QFont("Arial", 12))
        
        patient_text = QWidget()
        patient_text_layout = QVBoxLayout()
        patient_text.setLayout(patient_text_layout)
        patient_text_layout.addWidget(patient_name)
        patient_text_layout.addWidget(patient_type)
        
        patient_info_layout.addWidget(profile_pic)
        patient_info_layout.addWidget(patient_text)
        
        # Çıkış düğmesi
        logout_button = QPushButton("Çıkış Yap")
        logout_button.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #3498db;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f1f1f1;
            }
        """)
        logout_button.clicked.connect(self.logout)
        
        # Üst paneli tamamla
        top_layout.addWidget(patient_info)
        top_layout.addStretch(1)
        top_layout.addWidget(logout_button)
        
        # Ana içerik - Sekmeler
        tabs = QTabWidget()
        
        # Dashboard sekmesi
        dashboard_tab = QWidget()
        dashboard_layout = QVBoxLayout()
        dashboard_tab.setLayout(dashboard_layout)
        
        # Dashboard içeriği dinamik olarak yüklenecek
        self.dashboard_content = QWidget()
        self.dashboard_layout = QVBoxLayout()
        self.dashboard_content.setLayout(self.dashboard_layout)
        
        dashboard_layout.addWidget(self.dashboard_content)
        
        # Kan Şekeri Ölçümü sekmesi
        glucose_tab = QWidget()
        glucose_layout = QVBoxLayout()
        glucose_tab.setLayout(glucose_layout)
        
        # Ölçüm formu
        measurement_form = QGroupBox("Yeni Kan Şekeri Ölçümü")
        form_layout = QFormLayout()
        measurement_form.setLayout(form_layout)
        
        # Tarih seçici
        self.measurement_date = QDateEdit()
        self.measurement_date.setCalendarPopup(True)
        self.measurement_date.setDate(QDate.currentDate())
        form_layout.addRow("Tarih:", self.measurement_date)
        
        # Saat seçici
        self.measurement_time = QTimeEdit()
        self.measurement_time.setDisplayFormat("HH:mm")
        self.measurement_time.setTime(QTime.currentTime())
        form_layout.addRow("Saat:", self.measurement_time)
        
        # Periyot seçici
        self.measurement_period = QComboBox()
        self.measurement_period.addItem("Sabah (07:00-08:00)", "morning")
        self.measurement_period.addItem("Öğle (12:00-13:00)", "noon")
        self.measurement_period.addItem("İkindi (15:00-16:00)", "afternoon")
        self.measurement_period.addItem("Akşam (18:00-19:00)", "evening")
        self.measurement_period.addItem("Gece (22:00-23:00)", "night")
        
        # Saate göre periyodu otomatik seç
        current_time = QTime.currentTime()
        if QTime(7, 0) <= current_time <= QTime(8, 0):
            self.measurement_period.setCurrentIndex(0)
        elif QTime(12, 0) <= current_time <= QTime(13, 0):
            self.measurement_period.setCurrentIndex(1)
        elif QTime(15, 0) <= current_time <= QTime(16, 0):
            self.measurement_period.setCurrentIndex(2)
        elif QTime(18, 0) <= current_time <= QTime(19, 0):
            self.measurement_period.setCurrentIndex(3)
        elif QTime(22, 0) <= current_time <= QTime(23, 0):
            self.measurement_period.setCurrentIndex(4)
        
        form_layout.addRow("Periyot:", self.measurement_period)
        
        # Değer giriş alanı
        self.glucose_value = QLineEdit()
        self.glucose_value.setPlaceholderText("mg/dL")
        self.glucose_value.setInputMask("999")
        form_layout.addRow("Kan Şekeri:", self.glucose_value)
        
        # Notlar
        self.measurement_notes = QTextEdit()
        self.measurement_notes.setPlaceholderText("Ölçüm hakkında notlar...")
        self.measurement_notes.setMaximumHeight(100)
        form_layout.addRow("Notlar:", self.measurement_notes)
        
# Kaydet butonu
        save_measurement_button = QPushButton("Ölçümü Kaydet")
        save_measurement_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        save_measurement_button.clicked.connect(self.save_measurement)
        
        form_layout.addRow("", save_measurement_button)
        
        # Son ölçümleri gösteren tablo
        measurements_table_group = QGroupBox("Son Ölçümlerim")
        measurements_table_layout = QVBoxLayout()
        measurements_table_group.setLayout(measurements_table_layout)
        
        self.measurements_table = QTableWidget()
        self.measurements_table.setColumnCount(5)
        self.measurements_table.setHorizontalHeaderLabels(["Tarih", "Saat", "Periyot", "Değer (mg/dL)", "Notlar"])
        
        measurements_table_layout.addWidget(self.measurements_table)
        
        # Kan şekeri grafiği
        glucose_chart = GlucoseChartWidget(self.patient.id)
        
        glucose_layout.addWidget(measurement_form)
        glucose_layout.addWidget(measurements_table_group)
        glucose_layout.addWidget(glucose_chart)
        
        # Ölçüm verilerini yükle
        self.load_measurements()
        
        # Diyet ve Egzersiz sekmesi
        diet_exercise_tab = QWidget()
        diet_exercise_layout = QVBoxLayout()
        diet_exercise_tab.setLayout(diet_exercise_layout)
        
        # Diyet takibi
        diet_group = QGroupBox("Diyet Takibi")
        diet_layout = QVBoxLayout()
        diet_group.setLayout(diet_layout)
        
        # Diyet formu
        diet_form_layout = QFormLayout()
        
        # Tarih seçici
        self.diet_date = QDateEdit()
        self.diet_date.setCalendarPopup(True)
        self.diet_date.setDate(QDate.currentDate())
        diet_form_layout.addRow("Tarih:", self.diet_date)
        
        # Diyet türü
        self.diet_type = QComboBox()
        self.diet_type.addItem("Az Şekerli Diyet", Diet.TYPE_LOW_SUGAR)
        self.diet_type.addItem("Şekersiz Diyet", Diet.TYPE_NO_SUGAR)
        self.diet_type.addItem("Dengeli Beslenme", Diet.TYPE_BALANCED)
        diet_form_layout.addRow("Diyet Türü:", self.diet_type)
        
        # Diyet durumu
        self.diet_status = QRadioButton("Uygulandı")
        self.diet_status.setChecked(True)
        diet_not_followed = QRadioButton("Uygulanmadı")
        
        diet_status_layout = QHBoxLayout()
        diet_status_layout.addWidget(self.diet_status)
        diet_status_layout.addWidget(diet_not_followed)
        
        diet_form_layout.addRow("Durum:", diet_status_layout)
        
        # Diyet notları
        self.diet_notes = QTextEdit()
        self.diet_notes.setPlaceholderText("Diyet hakkında notlar...")
        self.diet_notes.setMaximumHeight(100)
        diet_form_layout.addRow("Notlar:", self.diet_notes)
        
        # Diyet kaydet butonu
        save_diet_button = QPushButton("Diyet Durumunu Kaydet")
        save_diet_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        save_diet_button.clicked.connect(self.save_diet)
        
        diet_form_layout.addRow("", save_diet_button)
        
        # Diyet tablosu
        self.diet_table = QTableWidget()
        self.diet_table.setColumnCount(4)
        self.diet_table.setHorizontalHeaderLabels(["Tarih", "Diyet Türü", "Durum", "Notlar"])
        
        diet_layout.addLayout(diet_form_layout)
        diet_layout.addWidget(self.diet_table)
        
        # Diyet verilerini yükle
        self.load_diets()
        
        # Egzersiz takibi
        exercise_group = QGroupBox("Egzersiz Takibi")
        exercise_layout = QVBoxLayout()
        exercise_group.setLayout(exercise_layout)
        
        # Egzersiz formu
        exercise_form_layout = QFormLayout()
        
        # Tarih seçici
        self.exercise_date = QDateEdit()
        self.exercise_date.setCalendarPopup(True)
        self.exercise_date.setDate(QDate.currentDate())
        exercise_form_layout.addRow("Tarih:", self.exercise_date)
        
        # Egzersiz türü
        self.exercise_type = QComboBox()
        self.exercise_type.addItem("Yürüyüş", Exercise.TYPE_WALKING)
        self.exercise_type.addItem("Bisiklet", Exercise.TYPE_CYCLING)
        self.exercise_type.addItem("Klinik Egzersiz", Exercise.TYPE_CLINICAL)
        exercise_form_layout.addRow("Egzersiz Türü:", self.exercise_type)
        
        # Egzersiz durumu
        self.exercise_status = QRadioButton("Tamamlandı")
        self.exercise_status.setChecked(True)
        exercise_not_completed = QRadioButton("Tamamlanmadı")
        
        exercise_status_layout = QHBoxLayout()
        exercise_status_layout.addWidget(self.exercise_status)
        exercise_status_layout.addWidget(exercise_not_completed)
        
        exercise_form_layout.addRow("Durum:", exercise_status_layout)
        
        # Egzersiz notları
        self.exercise_notes = QTextEdit()
        self.exercise_notes.setPlaceholderText("Egzersiz hakkında notlar...")
        self.exercise_notes.setMaximumHeight(100)
        exercise_form_layout.addRow("Notlar:", self.exercise_notes)
        
        # Egzersiz kaydet butonu
        save_exercise_button = QPushButton("Egzersiz Durumunu Kaydet")
        save_exercise_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        save_exercise_button.clicked.connect(self.save_exercise)
        
        exercise_form_layout.addRow("", save_exercise_button)
        
        # Egzersiz tablosu
        self.exercise_table = QTableWidget()
        self.exercise_table.setColumnCount(4)
        self.exercise_table.setHorizontalHeaderLabels(["Tarih", "Egzersiz Türü", "Durum", "Notlar"])
        
        exercise_layout.addLayout(exercise_form_layout)
        exercise_layout.addWidget(self.exercise_table)
        
        # Egzersiz verilerini yükle
        self.load_exercises()
        
        diet_exercise_layout.addWidget(diet_group)
        diet_exercise_layout.addWidget(exercise_group)
        
        # Belirti Takibi sekmesi
        symptoms_tab = QWidget()
        symptoms_layout = QVBoxLayout()
        symptoms_tab.setLayout(symptoms_layout)
        
        # Belirti formu
        symptom_form = QGroupBox("Belirti Bildirimi")
        symptom_form_layout = QFormLayout()
        symptom_form.setLayout(symptom_form_layout)
        
        # Tarih seçici
        self.symptom_date = QDateEdit()
        self.symptom_date.setCalendarPopup(True)
        self.symptom_date.setDate(QDate.currentDate())
        symptom_form_layout.addRow("Tarih:", self.symptom_date)
        
        # Belirti türü
        self.symptom_type = QComboBox()
        self.symptom_type.addItem("Poliüri (Sık idrara çıkma)", Symptom.TYPE_POLYURIA)
        self.symptom_type.addItem("Polifaji (Aşırı açlık hissi)", Symptom.TYPE_POLYPHAGIA)
        self.symptom_type.addItem("Polidipsi (Aşırı susama hissi)", Symptom.TYPE_POLYDIPSIA)
        self.symptom_type.addItem("Nöropati (El/ayak karıncalanması)", Symptom.TYPE_NEUROPATHY)
        self.symptom_type.addItem("Kilo kaybı", Symptom.TYPE_WEIGHT_LOSS)
        self.symptom_type.addItem("Yorgunluk", Symptom.TYPE_FATIGUE)
        self.symptom_type.addItem("Yaraların yavaş iyileşmesi", Symptom.TYPE_SLOW_HEALING)
        self.symptom_type.addItem("Bulanık görme", Symptom.TYPE_BLURRED_VISION)
        symptom_form_layout.addRow("Belirti Türü:", self.symptom_type)
        
        # Belirti şiddeti
        self.symptom_severity = QComboBox()
        self.symptom_severity.addItem("1 - Çok Hafif", 1)
        self.symptom_severity.addItem("2 - Hafif", 2)
        self.symptom_severity.addItem("3 - Orta", 3)
        self.symptom_severity.addItem("4 - Şiddetli", 4)
        self.symptom_severity.addItem("5 - Çok Şiddetli", 5)
        self.symptom_severity.setCurrentIndex(2)  # Varsayılan orta şiddet
        symptom_form_layout.addRow("Şiddet:", self.symptom_severity)
        
        # Belirti notları
        self.symptom_notes = QTextEdit()
        self.symptom_notes.setPlaceholderText("Belirti hakkında notlar...")
        self.symptom_notes.setMaximumHeight(100)
        symptom_form_layout.addRow("Notlar:", self.symptom_notes)
        
        # Belirti kaydet butonu
        save_symptom_button = QPushButton("Belirtiyi Kaydet")
        save_symptom_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        save_symptom_button.clicked.connect(self.save_symptom)
        
        symptom_form_layout.addRow("", save_symptom_button)
        
        # Belirti tablosu
        self.symptom_table = QTableWidget()
        self.symptom_table.setColumnCount(4)
        self.symptom_table.setHorizontalHeaderLabels(["Tarih", "Belirti", "Şiddet", "Notlar"])
        
        symptoms_layout.addWidget(symptom_form)
        symptoms_layout.addWidget(self.symptom_table)
        
        # Belirti verilerini yükle
        self.load_symptoms()
        
        # İnsülin sekmesi
        insulin_tab = QWidget()
        insulin_layout = QVBoxLayout()
        insulin_tab.setLayout(insulin_layout)
        
        # İnsülin takibi
        insulin_group = QGroupBox("İnsülin Takibi")
        insulin_table_layout = QVBoxLayout()
        insulin_group.setLayout(insulin_table_layout)
        
        # Tarih filtresi
        filter_widget = QWidget()
        filter_layout = QHBoxLayout()
        filter_widget.setLayout(filter_layout)
        
        filter_layout.addWidget(QLabel("Başlangıç:"))
        self.insulin_start_date = QDateEdit()
        self.insulin_start_date.setCalendarPopup(True)
        self.insulin_start_date.setDate(QDate.currentDate().addDays(-30))
        filter_layout.addWidget(self.insulin_start_date)
        
        filter_layout.addWidget(QLabel("Bitiş:"))
        self.insulin_end_date = QDateEdit()
        self.insulin_end_date.setCalendarPopup(True)
        self.insulin_end_date.setDate(QDate.currentDate())
        filter_layout.addWidget(self.insulin_end_date)
        
        insulin_filter_button = QPushButton("Filtrele")
        filter_layout.addWidget(insulin_filter_button)
        
        # İnsülin tablosu
        self.insulin_table = QTableWidget()
        self.insulin_table.setColumnCount(5)
        self.insulin_table.setHorizontalHeaderLabels(["Tarih", "Ortalama Şeker", "Öneri (ml)", "Uygulanan (ml)", "Notlar"])
        
        insulin_table_layout.addLayout(filter_layout)
        insulin_table_layout.addWidget(self.insulin_table)
        
        # İnsülin uygulama
        insulin_application_group = QGroupBox("İnsülin Uygulama")
        insulin_application_layout = QFormLayout()
        insulin_application_group.setLayout(insulin_application_layout)
        
        # İnsülin seçici
        self.insulin_id_combo = QComboBox()
        insulin_application_layout.addRow("İnsülin Önerisi:", self.insulin_id_combo)
        
        # Uygulanan miktar
        self.insulin_amount = QLineEdit()
        self.insulin_amount.setPlaceholderText("ml")
        self.insulin_amount.setInputMask("9.9")
        insulin_application_layout.addRow("Uygulanan Miktar:", self.insulin_amount)
        
        # Notlar
        self.insulin_notes = QTextEdit()
        self.insulin_notes.setPlaceholderText("İnsülin uygulaması hakkında notlar...")
        self.insulin_notes.setMaximumHeight(100)
        insulin_application_layout.addRow("Notlar:", self.insulin_notes)
        
        # Uygula butonu
        apply_insulin_button = QPushButton("İnsülin Uygulamasını Kaydet")
        apply_insulin_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        apply_insulin_button.clicked.connect(self.apply_insulin)
        
        insulin_application_layout.addRow("", apply_insulin_button)
        
        insulin_layout.addWidget(insulin_group)
        insulin_layout.addWidget(insulin_application_group)
        
        # İnsülin verilerini yükle
        def load_filtered_insulins():
            start_date = self.insulin_start_date.date().toPyDate()
            end_date = self.insulin_end_date.date().toPyDate()
            self.load_insulins(start_date, end_date)
        
        insulin_filter_button.clicked.connect(load_filtered_insulins)
        load_filtered_insulins()  # İlk yükleme
        
        # Ayarlar sekmesi
        settings_tab = QWidget()
        settings_layout = QVBoxLayout()
        settings_tab.setLayout(settings_layout)
        
        # Profil bilgileri
        profile_group = QGroupBox("Profil Bilgileri")
        profile_layout = QFormLayout()
        profile_group.setLayout(profile_layout)
        
        profile_layout.addRow("TC Kimlik:", QLabel(self.patient.tc_id))
        profile_layout.addRow("Ad:", QLabel(self.patient.name))
        profile_layout.addRow("Soyad:", QLabel(self.patient.surname))
        profile_layout.addRow("Doğum Tarihi:", QLabel(DateUtils.format_date(self.patient.birthdate)))
        profile_layout.addRow("Cinsiyet:", QLabel('Erkek' if self.patient.gender == 'E' else 'Kadın'))
        profile_layout.addRow("E-posta:", QLabel(self.patient.email))
        
        # Şifre değiştirme
        password_group = QGroupBox("Şifre Değiştirme")
        password_layout = QFormLayout()
        password_group.setLayout(password_layout)
        
        self.current_password = QLineEdit()
        self.current_password.setPlaceholderText("Mevcut şifreniz")
        self.current_password.setEchoMode(QLineEdit.Password)
        password_layout.addRow("Mevcut Şifre:", self.current_password)
        
        self.new_password = QLineEdit()
        self.new_password.setPlaceholderText("Yeni şifreniz")
        self.new_password.setEchoMode(QLineEdit.Password)
        password_layout.addRow("Yeni Şifre:", self.new_password)
        
        self.confirm_password = QLineEdit()
        self.confirm_password.setPlaceholderText("Yeni şifrenizi tekrar girin")
        self.confirm_password.setEchoMode(QLineEdit.Password)
        password_layout.addRow("Şifre Tekrar:", self.confirm_password)
        
        change_password_button = QPushButton("Şifreyi Değiştir")
        change_password_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        change_password_button.clicked.connect(self.change_password)
        
        password_layout.addRow("", change_password_button)
        
        settings_layout.addWidget(profile_group)
        settings_layout.addWidget(password_group)
        settings_layout.addStretch(1)
        
        # Sekmeleri ekle
        tabs.addTab(dashboard_tab, "Dashboard")
        tabs.addTab(glucose_tab, "Kan Şekeri Ölçümü")
        tabs.addTab(diet_exercise_tab, "Diyet ve Egzersiz")
        tabs.addTab(symptoms_tab, "Belirti Takibi")
        tabs.addTab(insulin_tab, "İnsülin Takibi")
        tabs.addTab(settings_tab, "Ayarlar")
        
        # Ana layout'a bileşenleri ekle
        main_layout.addWidget(top_panel)
        main_layout.addWidget(tabs, 1)
        
        # Pencereyi ekranın ortasına yerleştir
        self.center()
    
    def center(self):
        """Pencereyi ekranın ortasına yerleştirir."""
        screen = self.screen().availableGeometry()
        window_size = self.geometry()
        x = (screen.width() - window_size.width()) // 2
        y = (screen.height() - window_size.height()) // 2
        self.move(x, y)
    
    def logout(self):
        """Kullanıcı çıkışını gerçekleştirir."""
        reply = QMessageBox.question(self, "Çıkış", "Çıkış yapmak istediğinize emin misiniz?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            from ui.login_window import LoginWindow
            self.login_window = LoginWindow()
            self.login_window.show()
            self.close()
    
    def load_dashboard(self):
        """Dashboard içeriğini yükler."""
        # Mevcut içeriği temizle
        for i in reversed(range(self.dashboard_layout.count())):
            widget = self.dashboard_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # Günlük ölçüm durumu
        measurements_group = QGroupBox("Günlük Ölçüm Durumu")
        measurements_layout = QVBoxLayout()
        measurements_group.setLayout(measurements_layout)
        
        # Bugünkü ölçümleri al
        today = datetime.now().date()
        daily_measurements = PatientController.get_daily_measurements(self.patient.id, today)
        
        # Periyot tabanlı tablo
        periods_table = QTableWidget()
        periods_table.setColumnCount(3)
        periods_table.setRowCount(5)
        periods_table.setHorizontalHeaderLabels(["Periyot", "Zaman", "Değer (mg/dL)"])
        
        periods = {
            "morning": {"name": "Sabah", "time": "07:00-08:00", "value": None},
            "noon": {"name": "Öğle", "time": "12:00-13:00", "value": None},
            "afternoon": {"name": "İkindi", "time": "15:00-16:00", "value": None},
            "evening": {"name": "Akşam", "time": "18:00-19:00", "value": None},
            "night": {"name": "Gece", "time": "22:00-23:00", "value": None}
        }
        
        # Ölçümleri periyotlara yerleştir
        for m in daily_measurements:
            period = m['period']
            if period in periods:
                periods[period]["value"] = m['glucose_level']
        
        # Tablo satırlarını doldur
        for i, period_key in enumerate(["morning", "noon", "afternoon", "evening", "night"]):
            period = periods[period_key]
            
            periods_table.setItem(i, 0, QTableWidgetItem(period["name"]))
            periods_table.setItem(i, 1, QTableWidgetItem(period["time"]))
            
            if period["value"] is not None:
                value_item = QTableWidgetItem(str(period["value"]))
                
                # Değere göre renklendirme
                if period["value"] < 70:
                    value_item.setForeground(QColor("#e74c3c"))  # Düşük - kırmızı
                elif period["value"] > 180:
                    value_item.setForeground(QColor("#e67e22"))  # Yüksek - turuncu
                elif 70 <= period["value"] <= 110:
                    value_item.setForeground(QColor("#2ecc71"))  # Normal - yeşil
                
                periods_table.setItem(i, 2, value_item)
            else:
                periods_table.setItem(i, 2, QTableWidgetItem("Ölçüm yok"))
        
        periods_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        measurements_layout.addWidget(periods_table)
        
        # Günlük ortalama
        avg_values = [periods[p]["value"] for p in periods if periods[p]["value"] is not None]
        daily_avg = sum(avg_values) / len(avg_values) if avg_values else None
        
        avg_layout = QHBoxLayout()
        avg_label = QLabel("Günlük Ortalama:")
        avg_label.setFont(QFont("Arial", 12, QFont.Bold))
        
        avg_value = QLabel(f"{daily_avg:.1f} mg/dL" if daily_avg is not None else "Ölçüm yok")
        avg_value.setFont(QFont("Arial", 12))
        
        if daily_avg is not None:
            if daily_avg < 70:
                avg_value.setStyleSheet("color: #e74c3c;")  # Düşük - kırmızı
            elif daily_avg > 180:
                avg_value.setStyleSheet("color: #e67e22;")  # Yüksek - turuncu
            elif 70 <= daily_avg <= 110:
                avg_value.setStyleSheet("color: #2ecc71;")  # Normal - yeşil
        
        avg_layout.addWidget(avg_label)
        avg_layout.addWidget(avg_value)
        avg_layout.addStretch(1)
        
        measurements_layout.addLayout(avg_layout)
        
        # Bugünkü durum
        today_group = QGroupBox("Bugünkü Durum")
        today_layout = QVBoxLayout()
        today_group.setLayout(today_layout)
        
        # Tavsiyeler
        recommendations = PatientController.get_current_recommendations(self.patient.id)
        
        if recommendations:
            glucose_level = recommendations.get('glucose_level')
            diet_recommendation = recommendations.get('diet_recommendation')
            exercise_recommendation = recommendations.get('exercise_recommendation')
            
            # Kan şekeri durumu
            status_label = QLabel()
            status_label.setFont(QFont("Arial", 12, QFont.Bold))
            
            if glucose_level < 70:
                status_label.setText("Hipoglisemi Riski!")
                status_label.setStyleSheet("color: #e74c3c;")  # Kırmızı
            elif glucose_level > 180:
                status_label.setText("Hiperglisemi Durumu!")
                status_label.setStyleSheet("color: #e67e22;")  # Turuncu
            else:
                status_label.setText("Normal Kan Şekeri Seviyesi")
                status_label.setStyleSheet("color: #2ecc71;")  # Yeşil
            
            today_layout.addWidget(status_label)
            
            # Günlük öneriler
            recommendations_label = QLabel("Tavsiyeler:")
            recommendations_label.setFont(QFont("Arial", 12, QFont.Bold))
            today_layout.addWidget(recommendations_label)
            
            # Diyet önerisi
            diet_map = {
                Diet.TYPE_LOW_SUGAR: "Az Şekerli Diyet",
                Diet.TYPE_NO_SUGAR: "Şekersiz Diyet",
                Diet.TYPE_BALANCED: "Dengeli Beslenme"
            }
            
            diet_label = QLabel(f"• Diyet: {diet_map.get(diet_recommendation, 'Öneri yok')}")
            today_layout.addWidget(diet_label)
            
            # Egzersiz önerisi
            exercise_map = {
                Exercise.TYPE_WALKING: "Yürüyüş",
                Exercise.TYPE_CYCLING: "Bisiklet",
                Exercise.TYPE_CLINICAL: "Klinik Egzersiz"
            }
            
            if exercise_recommendation:
                exercise_label = QLabel(f"• Egzersiz: {exercise_map.get(exercise_recommendation, 'Öneri yok')}")
            else:
                exercise_label = QLabel("• Egzersiz: Önerilmiyor")
            today_layout.addWidget(exercise_label)
        else:
            no_data_label = QLabel("Henüz yeterli veri bulunmamaktadır.")
            no_data_label.setAlignment(Qt.AlignCenter)
            today_layout.addWidget(no_data_label)
        
        # Son 7 günlük kan şekeri grafiği
        chart_group = QGroupBox("Son 7 Günlük Kan Şekeri Grafiği")
        chart_layout = QVBoxLayout()
        chart_group.setLayout(chart_layout)
        
        # Tarih aralığı
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=6)  # Son 7 gün
        
        # Ölçümleri al
        measurements = PatientController.get_measurements_by_date_range(self.patient.id, start_date, end_date)
        
        # Grafiği oluştur
        chart_figure = Figure(figsize=(8, 4))
        chart_canvas = FigureCanvas(chart_figure)
        chart_layout.addWidget(chart_canvas)
        
        # Ölçümleri tarihe göre grupla
        daily_averages = {}
        for m in measurements:
            date_str = DateUtils.format_date(m['measurement_date'])
            if date_str in daily_averages:
                daily_averages[date_str].append(m['glucose_level'])
            else:
                daily_averages[date_str] = [m['glucose_level']]
        
        # Günlük ortalamaları hesapla
        dates = []
        averages = []
        
        for date_str in sorted(daily_averages.keys()):
            dates.append(date_str)
            avg = sum(daily_averages[date_str]) / len(daily_averages[date_str])
            averages.append(avg)
        
        # Grafik çiz
        if dates and averages:
            ax = chart_figure.add_subplot(111)
            ax.plot(dates, averages, 'o-', color='#3498db', linewidth=2)
            
            # Güvenli aralıkları göster
            ax.axhspan(70, 110, alpha=0.2, color='green', label='Normal')
            ax.axhspan(0, 70, alpha=0.2, color='red', label='Hipoglisemi')
            ax.axhspan(180, 300, alpha=0.2, color='orange', label='Hiperglisemi')
            
            ax.set_xlabel('Tarih')
            ax.set_ylabel('Kan Şekeri (mg/dL)')
            ax.set_title('Son 7 Günlük Kan Şekeri Ortalaması')
            ax.grid(True, linestyle='--', alpha=0.7)
            ax.legend()
            
            # X eksenindeki yazıları döndür
            plt.setp(ax.get_xticklabels(), rotation=30, ha='right')
            
            chart_figure.tight_layout()
            chart_canvas.draw()
        else:
            no_data_label = QLabel("Henüz yeterli veri bulunmamaktadır.")
            no_data_label.setAlignment(Qt.AlignCenter)
            chart_layout.addWidget(no_data_label)
        
        # Bileşenleri dashboard'a ekle
        self.dashboard_layout.addWidget(measurements_group)
        self.dashboard_layout.addWidget(today_group)
        self.dashboard_layout.addWidget(chart_group)
        self.dashboard_layout.addStretch(1)
    
    def load_measurements(self):
        """Ölçüm verilerini tabloya yükler."""
        # Son 10 ölçümü al
        measurements = PatientController.get_patient_measurements(self.patient.id)
        recent_measurements = measurements[:10] if measurements else []
        
        self.measurements_table.setRowCount(len(recent_measurements))
        
        for i, m in enumerate(recent_measurements):
            self.measurements_table.setItem(i, 0, QTableWidgetItem(DateUtils.format_date(m['measurement_date'])))
            self.measurements_table.setItem(i, 1, QTableWidgetItem(DateUtils.format_time(m['measurement_time'])))
            
            period_map = {
                'morning': 'Sabah',
                'noon': 'Öğle',
                'afternoon': 'İkindi',
                'evening': 'Akşam',
                'night': 'Gece'
            }
            self.measurements_table.setItem(i, 2, QTableWidgetItem(period_map.get(m['period'], m['period'])))
            
            value_item = QTableWidgetItem(str(m['glucose_level']))
            # Değere göre renklendirme
            if m['glucose_level'] < 70:
                value_item.setForeground(QColor("#e74c3c"))  # Düşük - kırmızı
            elif m['glucose_level'] > 180:
                value_item.setForeground(QColor("#e67e22"))  # Yüksek - turuncu
            self.measurements_table.setItem(i, 3, value_item)
            
            self.measurements_table.setItem(i, 4, QTableWidgetItem(m['notes'] or ""))
        
        self.measurements_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    
    def load_diets(self):
        """Diyet verilerini tabloya yükler."""
        # Son 10 diyet kaydını al
        diets = PatientController.get_patient_diets(self.patient.id)
        recent_diets = diets[:10] if diets else []
        
        self.diet_table.setRowCount(len(recent_diets))
        
        for i, d in enumerate(recent_diets):
            self.diet_table.setItem(i, 0, QTableWidgetItem(DateUtils.format_date(d['date'])))
            
            diet_type_map = {
                'low_sugar': 'Az Şekerli Diyet',
                'no_sugar': 'Şekersiz Diyet',
                'balanced': 'Dengeli Beslenme'
            }
            self.diet_table.setItem(i, 1, QTableWidgetItem(diet_type_map.get(d['diet_type'], d['diet_type'])))
            
            status_item = QTableWidgetItem('Uygulandı' if d['is_followed'] else 'Uygulanmadı')
            if d['is_followed']:
                status_item.setForeground(QColor("#2ecc71"))  # Yeşil
            else:
                status_item.setForeground(QColor("#e74c3c"))  # Kırmızı
            self.diet_table.setItem(i, 2, status_item)
            
            self.diet_table.setItem(i, 3, QTableWidgetItem(d['notes'] or ""))
        
        self.diet_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    
    def load_exercises(self):
        """Egzersiz verilerini tabloya yükler."""
        # Son 10 egzersiz kaydını al
        exercises = PatientController.get_patient_exercises(self.patient.id)
        recent_exercises = exercises[:10] if exercises else []
        
        self.exercise_table.setRowCount(len(recent_exercises))
        
        for i, e in enumerate(recent_exercises):
            self.exercise_table.setItem(i, 0, QTableWidgetItem(DateUtils.format_date(e['date'])))
            
            exercise_type_map = {
                'walking': 'Yürüyüş',
                'cycling': 'Bisiklet',
                'clinical': 'Klinik Egzersiz'
            }
            self.exercise_table.setItem(i, 1, QTableWidgetItem(exercise_type_map.get(e['exercise_type'], e['exercise_type'])))
            
            status_item = QTableWidgetItem('Tamamlandı' if e['is_completed'] else 'Tamamlanmadı')
            if e['is_completed']:
                status_item.setForeground(QColor("#2ecc71"))  # Yeşil
            else:
                status_item.setForeground(QColor("#e74c3c"))  # Kırmızı
            self.exercise_table.setItem(i, 2, status_item)
            
            self.exercise_table.setItem(i, 3, QTableWidgetItem(e['notes'] or ""))
        
        self.exercise_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    
    def load_symptoms(self):
        """Belirti verilerini tabloya yükler."""
        # Son 10 belirti kaydını al
        symptoms = PatientController.get_patient_symptoms(self.patient.id)
        recent_symptoms = symptoms[:10] if symptoms else []
        
        self.symptom_table.setRowCount(len(recent_symptoms))
        
        for i, s in enumerate(recent_symptoms):
            self.symptom_table.setItem(i, 0, QTableWidgetItem(DateUtils.format_date(s['date'])))
            
            symptom_type_map = {
                'polyuria': 'Poliüri (Sık idrara çıkma)',
                'polyphagia': 'Polifaji (Aşırı açlık hissi)',
                'polydipsia': 'Polidipsi (Aşırı susama hissi)',
                'neuropathy': 'Nöropati (El/ayak karıncalanması)',
                'weight_loss': 'Kilo kaybı',
                'fatigue': 'Yorgunluk',
                'slow_healing': 'Yaraların yavaş iyileşmesi',
                'blurred_vision': 'Bulanık görme'
            }
            self.symptom_table.setItem(i, 1, QTableWidgetItem(symptom_type_map.get(s['symptom_type'], s['symptom_type'])))
            
            severity = s['severity']
            severity_text = f"{severity}/5" if severity else "-"
            self.symptom_table.setItem(i, 2, QTableWidgetItem(severity_text))
            
            self.symptom_table.setItem(i, 3, QTableWidgetItem(s['notes'] or ""))
        
        self.symptom_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    
    def load_insulins(self, start_date=None, end_date=None):
        """İnsülin verilerini tabloya yükler."""
        # İnsülin kayıtlarını al
        if start_date and end_date:
            insulins = PatientController.get_insulin_recommendations(self.patient.id, start_date, end_date)
        else:
            insulins = PatientController.get_insulin_recommendations(self.patient.id)
        
        # İnsülin combo box'ı temizle ve yeniden doldur
        self.insulin_id_combo.clear()
        
        if insulins:
            # Tabloyu doldur
            self.insulin_table.setRowCount(len(insulins))
            
            for i, insulin in enumerate(insulins):
                # Tarih
                self.insulin_table.setItem(i, 0, QTableWidgetItem(DateUtils.format_datetime(insulin['date'])))
                
                # Ortalama şeker
                avg_glucose = insulin['average_glucose']
                avg_text = f"{avg_glucose:.1f} mg/dL" if avg_glucose else "-"
                self.insulin_table.setItem(i, 1, QTableWidgetItem(avg_text))
                
                # Öneri
                recommended = insulin['recommended_dose']
                recommended_text = f"{recommended} ml" if recommended is not None else "-"
                self.insulin_table.setItem(i, 2, QTableWidgetItem(recommended_text))
                
                # Uygulanan
                administered = insulin['administered_dose']
                administered_text = f"{administered} ml" if administered is not None else "Uygulanmadı"
                
                administered_item = QTableWidgetItem(administered_text)
                if administered is not None:
                    administered_item.setForeground(QColor("#2ecc71"))  # Yeşil
                self.insulin_table.setItem(i, 3, administered_item)
                
                # Notlar
                self.insulin_table.setItem(i, 4, QTableWidgetItem(insulin['notes'] or ""))
                
                # Henüz uygulanmamış insülinleri combo box'a ekle
                if administered is None:
                    display_text = f"{DateUtils.format_date(insulin['date'])} - {recommended} ml"
                    self.insulin_id_combo.addItem(display_text, insulin['id'])
        else:
            self.insulin_table.setRowCount(0)
        
        self.insulin_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    
    def save_measurement(self):
        """Ölçüm bilgilerini kaydeder."""
        # Form verilerini al
        measurement_date = self.measurement_date.date().toPyDate()
        measurement_time = self.measurement_time.time().toPyTime()
        period = self.measurement_period.currentData()
        glucose_level_text = self.glucose_value.text()
        notes = self.measurement_notes.toPlainText()
        
        # Doğrulama
        if not glucose_level_text:
            QMessageBox.warning(self, "Hata", "Kan şekeri değeri boş olamaz.")
            return
        
        try:
            glucose_level = float(glucose_level_text)
        except ValueError:
            QMessageBox.warning(self, "Hata", "Kan şekeri değeri geçerli bir sayı olmalıdır.")
            return
        
        if not Validators.validate_glucose_level(glucose_level):
            QMessageBox.warning(self, "Hata", "Kan şekeri değeri geçersiz. (20-600 mg/dL arası olmalıdır)")
            return
        
        # Periyot ile saat uyumunu kontrol et
        if not Validators.validate_period_time(period, measurement_time):
            reply = QMessageBox.question(
                self, 
                "Zaman Aralığı Uyarısı", 
                f"Seçtiğiniz periyot ({self.measurement_period.currentText()}) ve saat uyumsuz görünüyor. Yine de kaydetmek istiyor musunuz?",
                QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                return
        
        # Ölçümü kaydet
        try:
            PatientController.add_measurement(
                self.patient.id,
                glucose_level,
                measurement_date,
                measurement_time,
                period,
                notes
            )
            
            QMessageBox.information(self, "Başarılı", "Kan şekeri ölçümü başarıyla kaydedildi.")
            
            # Formu temizle
            self.glucose_value.clear()
            self.measurement_notes.clear()
            
            # Tabloyu güncelle
            self.load_measurements()
            
            # Dashboard'ı güncelle
            self.load_dashboard()
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Ölçüm kaydedilirken bir hata oluştu: {str(e)}")
    
    def save_diet(self):
        """Diyet durumunu kaydeder."""
        # Form verilerini al
        diet_date = self.diet_date.date().toPyDate()
        diet_type = self.diet_type.currentData()
        is_followed = self.diet_status.isChecked()
        notes = self.diet_notes.toPlainText()
        
        # Diyeti kaydet
        try:
            PatientController.add_diet_status(
                self.patient.id,
                diet_type,
                diet_date,
                is_followed,
                notes
            )
            
            QMessageBox.information(self, "Başarılı", "Diyet durumu başarıyla kaydedildi.")
            
            # Formu temizle
            self.diet_notes.clear()
            
            # Tabloyu güncelle
            self.load_diets()
            
            # Dashboard'ı güncelle
            self.load_dashboard()
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Diyet durumu kaydedilirken bir hata oluştu: {str(e)}")
    
    def save_exercise(self):
        """Egzersiz durumunu kaydeder."""
        # Form verilerini al
        exercise_date = self.exercise_date.date().toPyDate()
        exercise_type = self.exercise_type.currentData()
        is_completed = self.exercise_status.isChecked()
        notes = self.exercise_notes.toPlainText()
        
        # Egzersizi kaydet
        try:
            PatientController.add_exercise_status(
                self.patient.id,
                exercise_type,
                exercise_date,
                is_completed,
                notes
            )
            
            QMessageBox.information(self, "Başarılı", "Egzersiz durumu başarıyla kaydedildi.")
            
            # Formu temizle
            self.exercise_notes.clear()
            
            # Tabloyu güncelle
            self.load_exercises()
            
            # Dashboard'ı güncelle
            self.load_dashboard()
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Egzersiz durumu kaydedilirken bir hata oluştu: {str(e)}")
    
    def save_symptom(self):
        """Belirti bilgilerini kaydeder."""
        # Form verilerini al
        symptom_date = self.symptom_date.date().toPyDate()
        symptom_type = self.symptom_type.currentData()
        severity = self.symptom_severity.currentData()
        notes = self.symptom_notes.toPlainText()
        
        # Belirtiyi kaydet
        try:
            PatientController.add_symptom(
                self.patient.id,
                symptom_type,
                severity,
                symptom_date,
                notes
            )
            
            QMessageBox.information(self, "Başarılı", "Belirti başarıyla kaydedildi.")
            
            # Formu temizle
            self.symptom_notes.clear()
            
            # Tabloyu güncelle
            self.load_symptoms()
            
            # Dashboard'ı güncelle
            self.load_dashboard()
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Belirti kaydedilirken bir hata oluştu: {str(e)}")
    
    def apply_insulin(self):
        """İnsülin uygulamasını kaydeder."""
        # Form verilerini al
        if self.insulin_id_combo.count() == 0:
            QMessageBox.warning(self, "Uyarı", "Kaydedilecek insülin önerisi bulunmuyor.")
            return
        
        insulin_id = self.insulin_id_combo.currentData()
        amount_text = self.insulin_amount.text()
        notes = self.insulin_notes.toPlainText()
        
        # Doğrulama
        if not amount_text:
            QMessageBox.warning(self, "Hata", "Uygulanan miktar boş olamaz.")
            return
        
        try:
            amount = float(amount_text)
        except ValueError:
            QMessageBox.warning(self, "Hata", "Miktar geçerli bir sayı olmalıdır.")
            return
        
        # İnsülin uygulamasını kaydet
        try:
            PatientController.administer_insulin(
                insulin_id,
                amount,
                notes
            )
            
            QMessageBox.information(self, "Başarılı", "İnsülin uygulaması başarıyla kaydedildi.")
            
            # Formu temizle
            self.insulin_amount.clear()
            self.insulin_notes.clear()
            
            # Tabloyu güncelle
            self.load_insulins(
                self.insulin_start_date.date().toPyDate(),
                self.insulin_end_date.date().toPyDate()
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"İnsülin uygulaması kaydedilirken bir hata oluştu: {str(e)}")
    
    def change_password(self):
        """Şifre değiştirme işlemini gerçekleştirir."""
        current_password = self.current_password.text()
        new_password = self.new_password.text()
        confirm_password = self.confirm_password.text()
        
        # Doğrulama
        if not current_password or not new_password or not confirm_password:
            QMessageBox.warning(self, "Hata", "Tüm şifre alanları doldurulmalıdır.")
            return
        
        if new_password != confirm_password:
            QMessageBox.warning(self, "Hata", "Yeni şifre ve tekrarı eşleşmiyor.")
            return
        
        if len(new_password) < 6:
            QMessageBox.warning(self, "Hata", "Yeni şifre en az 6 karakter olmalıdır.")
            return
        
        # Şifreyi değiştir
        success = AuthController.change_password(self.patient.id, current_password, new_password)
        
        if success:
            QMessageBox.information(self, "Başarılı", "Şifreniz başarıyla değiştirildi.")
            
            # Formu temizle
            self.current_password.clear()
            self.new_password.clear()
            self.confirm_password.clear()
        else:
            QMessageBox.warning(self, "Hata", "Mevcut şifreniz hatalı.")

                                              