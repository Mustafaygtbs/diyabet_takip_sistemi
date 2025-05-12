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
from PyQt5.QtGui import QIcon, QPixmap, QFont, QColor, QCursor
from PyQt5.QtCore import Qt, QDate, QTime

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib as mpl
from PyQt5.QtCore import Qt, QDate, QTime, QSize

from models.patient import Patient
from models.measurement import Measurement
from models.exercise import Exercise
from models.diet import Diet
from models.symptom import Symptom
from models.insulin import Insulin

from controllers.patient_controller import PatientController
from controllers.auth_controller import AuthController
from controllers.doctor_controller import DoctorController

from ui.widgets.glucose_chart import GlucoseChartWidget

from utils.date_utils import DateUtils
from utils.validators import Validators

from datetime import datetime, timedelta, time

class PatientPanel(QMainWindow):
    def __init__(self, patient):
        super().__init__()
        self.patient = patient
        
        # Set modern chart style
        mpl.style.use('seaborn-v0_8-whitegrid')
        plt.rcParams['font.family'] = 'Segoe UI'
        plt.rcParams['axes.facecolor'] = '#F8F9FA'
        plt.rcParams['figure.facecolor'] = '#FFFFFF'
        plt.rcParams['axes.labelcolor'] = '#333333'
        plt.rcParams['axes.edgecolor'] = '#DDDDDD'
        plt.rcParams['axes.spines.top'] = False
        plt.rcParams['axes.spines.right'] = False
        
        self.initUI()
        self.load_dashboard()
    
    def initUI(self):
        # Main window settings
        self.setWindowTitle(f"Diyabet Takip Sistemi - {self.patient.name} {self.patient.surname}")
        self.setMinimumSize(1280, 800)
        self.setWindowIcon(QIcon("resources/medical-check.png"))
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F5F5F5;
            }
            QTabWidget::pane {
                border: 1px solid #E0E0E0;
                border-radius: 5px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #F5F5F5;
                border: 1px solid #E0E0E0;
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                padding: 14px 36px;
                margin-right: 8px;
                color: #666666;
                min-width: 190px;
                max-width: 270px;
                text-align: center;
                font-size: 16px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: none;
                font-weight: bold;
                color: #3949AB;
            }
            QTabBar::tab:!selected {
                color: #666666;
            }
            QTabBar::tab:hover {
                background-color: #E8EAF6;
            }
            QGroupBox {
                border: 1px solid #E0E0E0;
                border-radius: 5px;
                margin-top: 14px;
                font-weight: bold;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 10px;
                padding: 0 5px;
                color: #3949AB;
            }
            QTableWidget {
                border: 1px solid #E0E0E0;
                border-radius: 5px;
                gridline-color: #F0F0F0;
                selection-background-color: #E8EAF6;
                selection-color: #333333;
            }
            QTableWidget::item {
                padding: 5px;
                border-bottom: 1px solid #F0F0F0;
            }
            QTableWidget::item:selected {
                background-color: #E8EAF6;
                color: #333333;
            }
            QHeaderView::section {
                background-color: #F5F5F5;
                border: none;
                border-right: 1px solid #E0E0E0;
                border-bottom: 1px solid #E0E0E0;
                padding: 6px;
                font-weight: bold;
                color: #555555;
            }
            QComboBox, QDateEdit, QTimeEdit, QLineEdit {
                border: 1px solid #E0E0E0;
                border-radius: 5px;
                padding: 6px;
                background-color: white;
                min-height: 25px;
            }
            QComboBox:focus, QDateEdit:focus, QTimeEdit:focus, QLineEdit:focus {
                border: 1px solid #3949AB;
            }
            QTextEdit {
                border: 1px solid #E0E0E0;
                border-radius: 5px;
                padding: 6px;
                background-color: white;
            }
            QTextEdit:focus {
                border: 1px solid #3949AB;
            }
            QRadioButton {
                spacing: 8px;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
            }
            QRadioButton::indicator:checked {
                image: url(resources/icons/radio_checked.png);
            }
            QRadioButton::indicator:unchecked {
                image: url(resources/icons/radio_unchecked.png);
            }
        """)
        
        # Main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Top panel - User info and logout button
        top_panel = QWidget()
        top_layout = QHBoxLayout()
        top_panel.setLayout(top_layout)
        top_panel.setMaximumHeight(160)
        top_panel.setStyleSheet("""
            background-color: #3949AB;
            color: white;
            border-radius: 8px;
            margin-bottom: 10px;
        """)
        
        # Patient info
        patient_info = QWidget()
        patient_info_layout = QHBoxLayout()
        patient_info_layout.setSpacing(18)
        patient_info_layout.setContentsMargins(20, 20, 20, 20)
        patient_info.setLayout(patient_info_layout)
        patient_info.setFixedHeight(120)
        
        # Profil resmi (solda)
        profile_pic = QLabel()
        if self.patient.profile_image:
            pixmap = QPixmap()
            pixmap.loadFromData(self.patient.profile_image)
            profile_pic.setPixmap(pixmap.scaled(90, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            profile_pic.setText("👤")
            profile_pic.setFont(QFont("Segoe UI", 40))
        profile_pic.setAlignment(Qt.AlignCenter)
        profile_pic.setFixedSize(90, 90)
        profile_pic.setStyleSheet("background-color: white; border-radius: 45px; border: 3px solid #C5CAE9;")
        
        # Ad-soyadı ve tip bilgisi (sağda, alt alta)
        name_type_layout = QVBoxLayout()
        name_type_layout.setSpacing(6)
        patient_name = QLabel(f"{self.patient.name} {self.patient.surname}")
        patient_name.setFont(QFont("Segoe UI", 20, QFont.Bold))
        patient_name.setStyleSheet("color: white;")
        patient_name.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        patient_name.setFixedWidth(320)
        patient_type = QLabel(self.patient.diabetes_type or "Hasta")
        patient_type.setFont(QFont("Segoe UI", 14))
        patient_type.setStyleSheet("color: #C5CAE9;")
        patient_type.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        name_type_layout.addWidget(patient_name)
        name_type_layout.addWidget(patient_type)
        
        patient_info_layout.addWidget(profile_pic)
        patient_info_layout.addLayout(name_type_layout)
        patient_info_layout.addStretch(1)
        
        # Logout button
        logout_button = QPushButton("Çıkış Yap")
        logout_button.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #3949AB;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
                min-height: 36px;
            }
            QPushButton:hover {
                background-color: #F5F5F5;
            }
            QPushButton:pressed {
                background-color: #E0E0E0;
            }
        """)
        logout_button.setIcon(QIcon("resources/medical-check.png"))
        logout_button.clicked.connect(self.logout)
        
        top_layout.addWidget(patient_info)
        top_layout.addStretch(1)
        top_layout.addWidget(logout_button)
        
        # Main content - Tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #E0E0E0;
                border-radius: 5px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #F5F5F5;
                border: 1px solid #E0E0E0;
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 16px 48px;
                margin-right: 10px;
                color: #666666;
                min-width: 220px;
                max-width: 320px;
                text-align: center;
                font-size: 17px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: none;
                font-weight: bold;
                color: #3949AB;
            }
            QTabBar::tab:!selected {
                color: #666666;
            }
            QTabBar::tab:hover {
                background-color: #E8EAF6;
            }
        """)
        
        # Dashboard tab
        dashboard_tab = QScrollArea()
        dashboard_tab.setWidgetResizable(True)
        dashboard_tab.setFrameShape(QFrame.NoFrame)
        dashboard_content = QWidget()
        dashboard_layout = QVBoxLayout()
        dashboard_content.setLayout(dashboard_layout)
        dashboard_tab.setWidget(dashboard_content)
        
        # Dashboard content will be loaded dynamically
        self.dashboard_content = QWidget()
        self.dashboard_layout = QVBoxLayout()
        self.dashboard_content.setLayout(self.dashboard_layout)
        
        dashboard_layout.addWidget(self.dashboard_content)
        dashboard_layout.addStretch(1)
        
        # Blood Glucose Measurement tab
        glucose_tab = QScrollArea()
        glucose_tab.setWidgetResizable(True)
        glucose_tab.setFrameShape(QFrame.NoFrame)
        glucose_content = QWidget()
        glucose_layout = QVBoxLayout()
        glucose_content.setLayout(glucose_layout)
        glucose_tab.setWidget(glucose_content)
        
        # Measurement form
        measurement_form = QGroupBox("Yeni Kan Şekeri Ölçümü")
        form_layout = QFormLayout()
        measurement_form.setLayout(form_layout)
        
        # Date selector
        self.measurement_date = QDateEdit()
        self.measurement_date.setCalendarPopup(True)
        self.measurement_date.setDate(QDate.currentDate())
        self.measurement_date.setStyleSheet("""
            QDateEdit {
                padding: 8px;
                min-height: 36px;
            }
        """)
        form_layout.addRow("Tarih:", self.measurement_date)
        
        # Time selector
        self.measurement_time = QTimeEdit()
        self.measurement_time.setDisplayFormat("HH:mm")
        self.measurement_time.setTime(QTime.currentTime())
        self.measurement_time.setStyleSheet("""
            QTimeEdit {
                padding: 8px;
                min-height: 36px;
            }
        """)
        form_layout.addRow("Saat:", self.measurement_time)
        
        # Period selector
        self.measurement_period = QComboBox()
        self.measurement_period.addItem("Sabah (07:00-08:00)", "morning")
        self.measurement_period.addItem("Öğle (12:00-13:00)", "noon")
        self.measurement_period.addItem("İkindi (15:00-16:00)", "afternoon")
        self.measurement_period.addItem("Akşam (18:00-19:00)", "evening")
        self.measurement_period.addItem("Gece (22:00-23:00)", "night")
        self.measurement_period.setStyleSheet("""
            QComboBox {
                padding: 8px;
                min-height: 36px;
            }
        """)
        
        # Automatically select period based on time
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
        
        # Value input field
        self.glucose_value = QLineEdit()
        self.glucose_value.setPlaceholderText("mg/dL")
        self.glucose_value.setInputMask("999")
        self.glucose_value.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                min-height: 36px;
            }
        """)
        form_layout.addRow("Kan Şekeri:", self.glucose_value)
        
        # Notes
        self.measurement_notes = QTextEdit()
        self.measurement_notes.setPlaceholderText("Ölçüm hakkında notlar...")
        self.measurement_notes.setMaximumHeight(100)
        form_layout.addRow("Notlar:", self.measurement_notes)
        
        # Save button
        save_measurement_button = QPushButton("Ölçümü Kaydet")
        save_measurement_button.setCursor(QCursor(Qt.PointingHandCursor))
        save_measurement_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
                padding: 10px 15px;
                font-weight: bold;
                min-height: 40px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #43A047;
            }
            QPushButton:pressed {
                background-color: #388E3C;
            }
        """)
        save_measurement_button.setIcon(QIcon("resources/icons/save.png"))
        save_measurement_button.clicked.connect(self.save_measurement)
        
        form_layout.addRow("", save_measurement_button)
        
        # Recent measurements table
        measurements_table_group = QGroupBox("Son Ölçümlerim")
        measurements_table_layout = QVBoxLayout()
        measurements_table_group.setLayout(measurements_table_layout)
        
        self.measurements_table = QTableWidget()
        self.measurements_table.setColumnCount(5)
        self.measurements_table.setHorizontalHeaderLabels(["Tarih", "Saat", "Periyot", "Değer (mg/dL)", "Notlar"])
        self.measurements_table.setMinimumHeight(180)  # Yüksekliği artır
        self.measurements_table.setRowCount(5)  # En az 5 satır göster
        measurements_table_layout.addWidget(self.measurements_table)
        
        # Blood glucose chart
        glucose_chart = GlucoseChartWidget(self.patient.id)
        glucose_chart.setMinimumHeight(300)
        
        glucose_layout.addWidget(measurement_form)
        glucose_layout.addWidget(measurements_table_group)
        glucose_layout.addWidget(glucose_chart)
        
        # Load measurement data
        self.load_measurements()
        
        # Diet and Exercise tab
        diet_exercise_tab = QScrollArea()
        diet_exercise_tab.setWidgetResizable(True)
        diet_exercise_tab.setFrameShape(QFrame.NoFrame)
        diet_exercise_content = QWidget()
        diet_exercise_layout = QVBoxLayout()
        diet_exercise_content.setLayout(diet_exercise_layout)
        diet_exercise_tab.setWidget(diet_exercise_content)
        
        # Diet tracking
        diet_group = QGroupBox("Diyet Takibi")
        diet_layout = QVBoxLayout()
        diet_group.setLayout(diet_layout)
        
        # Diet tracking instructions
        diet_info = QLabel("Günlük diyet durumunuzu kaydedin. Doktorunuz tarafından önerilen diyeti takip edin.")
        diet_info.setStyleSheet("color: #757575; margin-bottom: 10px;")
        diet_layout.addWidget(diet_info)
        
        # Diet form
        diet_form_layout = QGridLayout()
        diet_form_layout.setVerticalSpacing(15)
        diet_form_layout.setHorizontalSpacing(15)
        
        # Date selector
        date_label = QLabel("Tarih:")
        date_label.setStyleSheet("font-weight: bold;")
        diet_form_layout.addWidget(date_label, 0, 0)
        
        self.diet_date = QDateEdit()
        self.diet_date.setCalendarPopup(True)
        self.diet_date.setDate(QDate.currentDate())
        self.diet_date.setStyleSheet("""
            QDateEdit {
                padding: 8px;
                min-height: 36px;
            }
        """)
        diet_form_layout.addWidget(self.diet_date, 0, 1)
        
        # Diet type
        diet_type_label = QLabel("Diyet Türü:")
        diet_type_label.setStyleSheet("font-weight: bold;")
        diet_form_layout.addWidget(diet_type_label, 1, 0)
        
        self.diet_type = QComboBox()
        self.diet_type.addItem("Az Şekerli Diyet", Diet.TYPE_LOW_SUGAR)
        self.diet_type.addItem("Şekersiz Diyet", Diet.TYPE_NO_SUGAR)
        self.diet_type.addItem("Dengeli Beslenme", Diet.TYPE_BALANCED)
        self.diet_type.setStyleSheet("""
            QComboBox {
                padding: 8px;
                min-height: 36px;
            }
        """)
        diet_form_layout.addWidget(self.diet_type, 1, 1)
        
        # Diet status
        status_label = QLabel("Durum:")
        status_label.setStyleSheet("font-weight: bold;")
        diet_form_layout.addWidget(status_label, 2, 0)
        
        status_widget = QWidget()
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_widget.setLayout(status_layout)
        
        self.diet_status = QRadioButton("Uygulandı")
        self.diet_status.setChecked(True)
        self.diet_status.setStyleSheet("""
            QRadioButton {
                font-size: 14px;
            }
            QRadioButton:checked {
                color: #4CAF50;
            }
        """)
        
        diet_not_followed = QRadioButton("Uygulanmadı")
        diet_not_followed.setStyleSheet("""
            QRadioButton {
                font-size: 14px;
            }
            QRadioButton:checked {
                color: #F44336;
            }
        """)
        
        status_layout.addWidget(self.diet_status)
        status_layout.addWidget(diet_not_followed)
        status_layout.addStretch(1)
        
        diet_form_layout.addWidget(status_widget, 2, 1)
        
        # Diet notes
        notes_label = QLabel("Notlar:")
        notes_label.setStyleSheet("font-weight: bold;")
        diet_form_layout.addWidget(notes_label, 3, 0)
        
        self.diet_notes = QTextEdit()
        self.diet_notes.setPlaceholderText("Diyet hakkında notlar...")
        self.diet_notes.setMaximumHeight(80)
        diet_form_layout.addWidget(self.diet_notes, 3, 1, 1, 3)
        
        # Diet save button
        save_diet_button = QPushButton("Diyet Durumunu Kaydet")
        save_diet_button.setCursor(QCursor(Qt.PointingHandCursor))
        save_diet_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
                padding: 10px 15px;
                font-weight: bold;
                min-height: 40px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #43A047;
            }
            QPushButton:pressed {
                background-color: #388E3C;
            }
        """)
        save_diet_button.setIcon(QIcon("resources/icons/save.png"))
        save_diet_button.clicked.connect(self.save_diet)
        
        diet_form_layout.addWidget(save_diet_button, 4, 0, 1, 4, Qt.AlignCenter)
        
        # Diet table
        diet_table_label = QLabel("Önceki Diyet Kayıtlarım")
        diet_table_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #3949AB; margin-top: 20px;")
        
        self.diet_table = QTableWidget()
        self.diet_table.setColumnCount(4)
        self.diet_table.setHorizontalHeaderLabels(["Tarih", "Diyet Türü", "Durum", "Notlar"])
        self.diet_table.setMinimumHeight(180)
        self.diet_table.setRowCount(5)
        
        diet_layout.addLayout(diet_form_layout)
        diet_layout.addWidget(diet_table_label)
        diet_layout.addWidget(self.diet_table)
        
        # Load diet data
        self.load_diets()
        
        # Exercise tracking
        exercise_group = QGroupBox("Egzersiz Takibi")
        exercise_layout = QVBoxLayout()
        exercise_group.setLayout(exercise_layout)
        
        # Exercise tracking instructions
        exercise_info = QLabel("Günlük egzersiz durumunuzu kaydedin. Sağlık durumunuza uygun egzersizleri doktorunuza danışarak yapın.")
        exercise_info.setStyleSheet("color: #757575; margin-bottom: 10px;")
        exercise_layout.addWidget(exercise_info)
        
        # Exercise form
        exercise_form_layout = QGridLayout()
        exercise_form_layout.setVerticalSpacing(15)
        exercise_form_layout.setHorizontalSpacing(15)
        
        # Exercise date
        ex_date_label = QLabel("Tarih:")
        ex_date_label.setStyleSheet("font-weight: bold;")
        exercise_form_layout.addWidget(ex_date_label, 0, 0)
        
        self.exercise_date = QDateEdit()
        self.exercise_date.setCalendarPopup(True)
        self.exercise_date.setDate(QDate.currentDate())
        self.exercise_date.setStyleSheet("""
            QDateEdit {
                padding: 8px;
                min-height: 36px;
            }
        """)
        exercise_form_layout.addWidget(self.exercise_date, 0, 1)
        
        # Exercise type
        ex_type_label = QLabel("Egzersiz Türü:")
        ex_type_label.setStyleSheet("font-weight: bold;")
        exercise_form_layout.addWidget(ex_type_label, 1, 0)
        
        self.exercise_type = QComboBox()
        self.exercise_type.addItem("Yürüyüş", Exercise.TYPE_WALKING)
        self.exercise_type.addItem("Bisiklet", Exercise.TYPE_CYCLING)
        self.exercise_type.addItem("Klinik Egzersiz", Exercise.TYPE_CLINICAL)
        self.exercise_type.setStyleSheet("""
            QComboBox {
                padding: 8px;
                min-height: 36px;
            }
        """)
        exercise_form_layout.addWidget(self.exercise_type, 1, 1)
        
        # Exercise status
        ex_status_label = QLabel("Durum:")
        ex_status_label.setStyleSheet("font-weight: bold;")
        exercise_form_layout.addWidget(ex_status_label, 2, 0)
        
        ex_status_widget = QWidget()
        ex_status_layout = QHBoxLayout()
        ex_status_layout.setContentsMargins(0, 0, 0, 0)
        ex_status_widget.setLayout(ex_status_layout)
        
        self.exercise_status = QRadioButton("Tamamlandı")
        self.exercise_status.setChecked(True)
        self.exercise_status.setStyleSheet("""
            QRadioButton {
                font-size: 14px;
            }
            QRadioButton:checked {
                color: #4CAF50;
            }
        """)
        
        exercise_not_completed = QRadioButton("Tamamlanmadı")
        exercise_not_completed.setStyleSheet("""
            QRadioButton {
                font-size: 14px;
            }
            QRadioButton:checked {
                color: #F44336;
            }
        """)
        
        ex_status_layout.addWidget(self.exercise_status)
        ex_status_layout.addWidget(exercise_not_completed)
        ex_status_layout.addStretch(1)
        
        exercise_form_layout.addWidget(ex_status_widget, 2, 1)
        
        # Exercise notes
        ex_notes_label = QLabel("Notlar:")
        ex_notes_label.setStyleSheet("font-weight: bold;")
        exercise_form_layout.addWidget(ex_notes_label, 3, 0)
        
        self.exercise_notes = QTextEdit()
        self.exercise_notes.setPlaceholderText("Egzersiz hakkında notlar...")
        self.exercise_notes.setMaximumHeight(80)
        exercise_form_layout.addWidget(self.exercise_notes, 3, 1, 1, 3)
        
        # Exercise save button
        save_exercise_button = QPushButton("Egzersiz Durumunu Kaydet")
        save_exercise_button.setCursor(QCursor(Qt.PointingHandCursor))
        save_exercise_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
                padding: 10px 15px;
                font-weight: bold;
                min-height: 40px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #43A047;
            }
            QPushButton:pressed {
                background-color: #388E3C;
            }
        """)
        save_exercise_button.setIcon(QIcon("resources/icons/save.png"))
        save_exercise_button.clicked.connect(self.save_exercise)
        
        exercise_form_layout.addWidget(save_exercise_button, 4, 0, 1, 4, Qt.AlignCenter)
        
        # Exercise table
        exercise_table_label = QLabel("Önceki Egzersiz Kayıtlarım")
        exercise_table_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #3949AB; margin-top: 20px;")
        
        self.exercise_table = QTableWidget()
        self.exercise_table.setColumnCount(4)
        self.exercise_table.setHorizontalHeaderLabels(["Tarih", "Egzersiz Türü", "Durum", "Notlar"])
        self.exercise_table.setMinimumHeight(180)
        self.exercise_table.setRowCount(5)
        
        exercise_layout.addLayout(exercise_form_layout)
        exercise_layout.addWidget(exercise_table_label)
        exercise_layout.addWidget(self.exercise_table)
        
        # Load exercise data
        self.load_exercises()
        
        diet_exercise_layout.addWidget(diet_group)
        diet_exercise_layout.addWidget(exercise_group)
        # ui/patient_panel.py (continued)
        # Symptom Tracking tab
        symptoms_tab = QScrollArea()
        symptoms_tab.setWidgetResizable(True)
        symptoms_tab.setFrameShape(QFrame.NoFrame)
        symptoms_content = QWidget()
        symptoms_layout = QVBoxLayout()
        symptoms_content.setLayout(symptoms_layout)
        symptoms_tab.setWidget(symptoms_content)
        
        # Symptom form
        symptom_form = QGroupBox("Belirti Bildirimi")
        symptom_form_layout = QGridLayout()
        symptom_form_layout.setVerticalSpacing(15)
        symptom_form_layout.setHorizontalSpacing(15)
        symptom_form.setLayout(symptom_form_layout)
        
        # Symptom tracking instructions
        symptom_info = QLabel("Yaşadığınız belirtileri bildirin. Bu bilgiler doktorunuzun tedavinizi planlamasına yardımcı olur.")
        symptom_info.setStyleSheet("color: #757575; margin-bottom: 10px;")
        symptom_form_layout.addWidget(symptom_info, 0, 0, 1, 4)
        
        # Symptom date
        symptom_date_label = QLabel("Tarih:")
        symptom_date_label.setStyleSheet("font-weight: bold;")
        symptom_form_layout.addWidget(symptom_date_label, 1, 0)
        
        self.symptom_date = QDateEdit()
        self.symptom_date.setCalendarPopup(True)
        self.symptom_date.setDate(QDate.currentDate())
        self.symptom_date.setStyleSheet("""
            QDateEdit {
                padding: 8px;
                min-height: 36px;
            }
        """)
        symptom_form_layout.addWidget(self.symptom_date, 1, 1)
        
        # Symptom type
        symptom_type_label = QLabel("Belirti Türü:")
        symptom_type_label.setStyleSheet("font-weight: bold;")
        symptom_form_layout.addWidget(symptom_type_label, 2, 0)
        
        self.symptom_type = QComboBox()
        self.symptom_type.addItem("Poliüri (Sık idrara çıkma)", Symptom.TYPE_POLYURIA)
        self.symptom_type.addItem("Polifaji (Aşırı açlık hissi)", Symptom.TYPE_POLYPHAGIA)
        self.symptom_type.addItem("Polidipsi (Aşırı susama hissi)", Symptom.TYPE_POLYDIPSIA)
        self.symptom_type.addItem("Nöropati (El/ayak karıncalanması)", Symptom.TYPE_NEUROPATHY)
        self.symptom_type.addItem("Kilo kaybı", Symptom.TYPE_WEIGHT_LOSS)
        self.symptom_type.addItem("Yorgunluk", Symptom.TYPE_FATIGUE)
        self.symptom_type.addItem("Yaraların yavaş iyileşmesi", Symptom.TYPE_SLOW_HEALING)
        self.symptom_type.addItem("Bulanık görme", Symptom.TYPE_BLURRED_VISION)
        self.symptom_type.setStyleSheet("""
            QComboBox {
                padding: 8px;
                min-height: 36px;
            }
        """)
        symptom_form_layout.addWidget(self.symptom_type, 2, 1, 1, 3)
        
        # Symptom severity
        severity_label = QLabel("Şiddet:")
        severity_label.setStyleSheet("font-weight: bold;")
        symptom_form_layout.addWidget(severity_label, 3, 0)
        
        self.symptom_severity = QComboBox()
        self.symptom_severity.addItem("1 - Çok Hafif", 1)
        self.symptom_severity.addItem("2 - Hafif", 2)
        self.symptom_severity.addItem("3 - Orta", 3)
        self.symptom_severity.addItem("4 - Şiddetli", 4)
        self.symptom_severity.addItem("5 - Çok Şiddetli", 5)
        self.symptom_severity.setCurrentIndex(2)  # Default medium severity
        self.symptom_severity.setStyleSheet("""
            QComboBox {
                padding: 8px;
                min-height: 36px;
            }
        """)
        symptom_form_layout.addWidget(self.symptom_severity, 3, 1)
        
        # Symptom notes
        notes_label = QLabel("Notlar:")
        notes_label.setStyleSheet("font-weight: bold;")
        symptom_form_layout.addWidget(notes_label, 4, 0)
        
        self.symptom_notes = QTextEdit()
        self.symptom_notes.setPlaceholderText("Belirti hakkında detaylar...")
        self.symptom_notes.setMaximumHeight(80)
        symptom_form_layout.addWidget(self.symptom_notes, 4, 1, 1, 3)
        
        # Symptom save button
        save_symptom_button = QPushButton("Belirtiyi Kaydet")
        save_symptom_button.setCursor(QCursor(Qt.PointingHandCursor))
        save_symptom_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
                padding: 10px 15px;
                font-weight: bold;
                min-height: 40px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #43A047;
            }
            QPushButton:pressed {
                background-color: #388E3C;
            }
        """)
        save_symptom_button.setIcon(QIcon("resources/icons/save.png"))
        save_symptom_button.clicked.connect(self.save_symptom)
        
        symptom_form_layout.addWidget(save_symptom_button, 5, 0, 1, 4, Qt.AlignCenter)
        
        # Symptom table
        symptom_table_label = QLabel("Önceki Belirti Kayıtlarım")
        symptom_table_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #3949AB; margin-top: 20px;")
        
        self.symptom_table = QTableWidget()
        self.symptom_table.setColumnCount(4)
        self.symptom_table.setHorizontalHeaderLabels(["Tarih", "Belirti", "Şiddet", "Notlar"])
        
        symptoms_layout.addWidget(symptom_form)
        symptoms_layout.addWidget(symptom_table_label)
        symptoms_layout.addWidget(self.symptom_table)
        
        # Load symptom data
        self.load_symptoms()
        
        # Insulin tab
        insulin_tab = QScrollArea()
        insulin_tab.setWidgetResizable(True)
        insulin_tab.setFrameShape(QFrame.NoFrame)
        insulin_content = QWidget()
        insulin_layout = QVBoxLayout()
        insulin_content.setLayout(insulin_layout)
        insulin_tab.setWidget(insulin_content)
        
        # Insulin tracking
        insulin_group = QGroupBox("İnsülin Takibi")
        insulin_table_layout = QVBoxLayout()
        insulin_group.setLayout(insulin_table_layout)
        
        # Insulin tracking instructions
        insulin_info = QLabel("Sistem, kan şekeri ölçümlerinize göre insülin önerileri oluşturur. Aşağıda önerilen ve uygulanan insülin dozlarını görebilirsiniz.")
        insulin_info.setStyleSheet("color: #757575; margin-bottom: 10px;")
        insulin_info.setWordWrap(True)
        insulin_table_layout.addWidget(insulin_info)
        
        # Date filter
        filter_widget = QWidget()
        filter_layout = QHBoxLayout()
        filter_layout.setContentsMargins(0, 0, 0, 0)
        filter_widget.setLayout(filter_layout)
        
        date_range_label = QLabel("Tarih Aralığı: ")
        date_range_label.setStyleSheet("font-weight: bold;")
        filter_layout.addWidget(date_range_label)
        
        self.insulin_start_date = QDateEdit()
        self.insulin_start_date.setCalendarPopup(True)
        self.insulin_start_date.setDate(QDate.currentDate().addDays(-30))
        self.insulin_start_date.setStyleSheet("""
            QDateEdit {
                padding: 6px;
                min-height: 30px;
            }
        """)
        filter_layout.addWidget(self.insulin_start_date)
        
        filter_layout.addWidget(QLabel("-"))
        
        self.insulin_end_date = QDateEdit()
        self.insulin_end_date.setCalendarPopup(True)
        self.insulin_end_date.setDate(QDate.currentDate())
        self.insulin_end_date.setStyleSheet("""
            QDateEdit {
                padding: 6px;
                min-height: 30px;
            }
        """)
        filter_layout.addWidget(self.insulin_end_date)
        
        insulin_filter_button = QPushButton("Filtrele")
        insulin_filter_button.setCursor(QCursor(Qt.PointingHandCursor))
        insulin_filter_button.setStyleSheet("""
            QPushButton {
                background-color: #3949AB;
                color: white;
                border-radius: 5px;
                padding: 6px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #303F9F;
            }
            QPushButton:pressed {
                background-color: #283593;
            }
        """)
        filter_layout.addWidget(insulin_filter_button)
        filter_layout.addStretch(1)
        
        insulin_table_layout.addWidget(filter_widget)
        
        # Insulin table
        self.insulin_table = QTableWidget()
        self.insulin_table.setColumnCount(5)
        self.insulin_table.setHorizontalHeaderLabels(["Tarih", "Ortalama Şeker", "Öneri (ml)", "Uygulanan (ml)", "Notlar"])
        
        insulin_table_layout.addWidget(self.insulin_table)
        
        # Insulin application
        insulin_application_group = QGroupBox("İnsülin Uygulama")
        insulin_application_layout = QGridLayout()
        insulin_application_layout.setVerticalSpacing(15)
        insulin_application_layout.setHorizontalSpacing(15)
        insulin_application_group.setLayout(insulin_application_layout)
        
        # Insulin application instructions
        insulin_app_info = QLabel("Doktor önerisi doğrultusunda uygulanan insülin dozunu kaydedin.")
        insulin_app_info.setStyleSheet("color: #757575; margin-bottom: 10px;")
        insulin_application_layout.addWidget(insulin_app_info, 0, 0, 1, 3)
        
        # Insulin selector
        insulin_id_label = QLabel("İnsülin Önerisi:")
        insulin_id_label.setStyleSheet("font-weight: bold;")
        insulin_application_layout.addWidget(insulin_id_label, 1, 0)
        
        self.insulin_id_combo = QComboBox()
        self.insulin_id_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                min-height: 36px;
            }
        """)
        insulin_application_layout.addWidget(self.insulin_id_combo, 1, 1, 1, 2)
        
        # Applied amount
        amount_label = QLabel("Uygulanan Miktar:")
        amount_label.setStyleSheet("font-weight: bold;")
        insulin_application_layout.addWidget(amount_label, 2, 0)
        
        self.insulin_amount = QLineEdit()
        self.insulin_amount.setPlaceholderText("ml")
        self.insulin_amount.setInputMask("9.9")
        self.insulin_amount.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                min-height: 36px;
            }
        """)
        insulin_application_layout.addWidget(self.insulin_amount, 2, 1)
        
        amount_unit = QLabel("ml")
        insulin_application_layout.addWidget(amount_unit, 2, 2)
        
        # Notes
        insulin_notes_label = QLabel("Notlar:")
        insulin_notes_label.setStyleSheet("font-weight: bold;")
        insulin_application_layout.addWidget(insulin_notes_label, 3, 0)
        
        self.insulin_notes = QTextEdit()
        self.insulin_notes.setPlaceholderText("İnsülin uygulaması hakkında notlar...")
        self.insulin_notes.setMaximumHeight(80)
        insulin_application_layout.addWidget(self.insulin_notes, 3, 1, 1, 2)
        
        # Apply button
        apply_insulin_button = QPushButton("İnsülin Uygulamasını Kaydet")
        apply_insulin_button.setCursor(QCursor(Qt.PointingHandCursor))
        apply_insulin_button.setStyleSheet("""
            QPushButton {
                background-color: #3949AB;
                color: white;
                border-radius: 5px;
                padding: 10px 15px;
                font-weight: bold;
                min-height: 40px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #303F9F;
            }
            QPushButton:pressed {
                background-color: #283593;
            }
        """)
        apply_insulin_button.setIcon(QIcon("resources/icons/insulin.png"))
        apply_insulin_button.clicked.connect(self.apply_insulin)
        
        insulin_application_layout.addWidget(apply_insulin_button, 4, 0, 1, 3, Qt.AlignCenter)
        
        insulin_layout.addWidget(insulin_group)
        insulin_layout.addWidget(insulin_application_group)
        
        # Load insulin data
        def load_filtered_insulins():
            start_date = self.insulin_start_date.date().toPyDate()
            end_date = self.insulin_end_date.date().toPyDate()
            self.load_insulins(start_date, end_date)
        
        insulin_filter_button.clicked.connect(load_filtered_insulins)
        load_filtered_insulins()  # Initial load
        
        # Settings tab
        settings_tab = QScrollArea()
        settings_tab.setWidgetResizable(True)
        settings_tab.setFrameShape(QFrame.NoFrame)
        settings_content = QWidget()
        settings_layout = QVBoxLayout()
        settings_content.setLayout(settings_layout)
        settings_tab.setWidget(settings_content)
        
        # Profile info
        profile_group = QGroupBox("Profil Bilgileri")
        profile_layout = QGridLayout()
        profile_layout.setVerticalSpacing(15)
        profile_layout.setHorizontalSpacing(15)
        profile_group.setLayout(profile_layout)
        
        # Profile picture
        profile_pic_label = QLabel()
        if self.patient.profile_image:
            pixmap = QPixmap()
            pixmap.loadFromData(self.patient.profile_image)
            profile_pic_label.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            profile_pic_label.setText("👤")
            profile_pic_label.setFont(QFont("Segoe UI", 40))
            profile_pic_label.setStyleSheet("color: #757575;")
        profile_pic_label.setAlignment(Qt.AlignCenter)
        profile_pic_label.setFixedSize(100, 100)
        profile_pic_label.setStyleSheet("""
            background-color: white;
            border-radius: 50px;
            padding: 5px;
            border: 2px solid #E0E0E0;
        """)
        profile_layout.addWidget(profile_pic_label, 0, 0, 3, 1, Qt.AlignTop | Qt.AlignHCenter)

        # Profil resmi güncelleme fonksiyonu
        def update_profile_image():
            file_dialog = QFileDialog()
            file_dialog.setNameFilter("Resim Dosyaları (*.png *.jpg *.jpeg *.bmp)")
            if file_dialog.exec_():
                file_path = file_dialog.selectedFiles()[0]
                pixmap = QPixmap(file_path)
                if not pixmap.isNull():
                    profile_pic_label.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                    with open(file_path, "rb") as f:
                        image_bytes = f.read()
                    try:
                        DoctorController.update_patient_profile(
                            self.patient.id,
                            self.patient.name,
                            self.patient.surname,
                            self.patient.birthdate,
                            self.patient.gender,
                            self.patient.email,
                            image_bytes,
                            self.patient.diagnosis,
                            self.patient.diabetes_type,
                            self.patient.diagnosis_date
                        )
                        QMessageBox.information(self, "Başarılı", "Profil resmi güncellendi.")
                        self.patient.profile_image = image_bytes
                    except Exception as e:
                        QMessageBox.warning(self, "Hata", f"Profil resmi güncellenemedi: {str(e)}")
        profile_pic_label.mousePressEvent = lambda event: update_profile_image()
        
        # Basic info fields with styling
        tc_label = QLabel("TC Kimlik:")
        tc_label.setStyleSheet("font-weight: bold;")
        profile_layout.addWidget(tc_label, 0, 1)
        
        tc_value = QLabel(self.patient.tc_id)
        tc_value.setStyleSheet("color: #333333;")
        profile_layout.addWidget(tc_value, 0, 2)
        
        name_label = QLabel("Ad:")
        name_label.setStyleSheet("font-weight: bold;")
        profile_layout.addWidget(name_label, 1, 1)
        
        name_value = QLabel(self.patient.name)
        name_value.setStyleSheet("color: #333333;")
        profile_layout.addWidget(name_value, 1, 2)
        
        surname_label = QLabel("Soyad:")
        surname_label.setStyleSheet("font-weight: bold;")
        profile_layout.addWidget(surname_label, 2, 1)
        
        surname_value = QLabel(self.patient.surname)
        surname_value.setStyleSheet("color: #333333;")
        profile_layout.addWidget(surname_value, 2, 2)
        
        birthdate_label = QLabel("Doğum Tarihi:")
        birthdate_label.setStyleSheet("font-weight: bold;")
        profile_layout.addWidget(birthdate_label, 3, 1)
        
        birthdate_value = QLabel(DateUtils.format_date(self.patient.birthdate))
        birthdate_value.setStyleSheet("color: #333333;")
        profile_layout.addWidget(birthdate_value, 3, 2)
        
        gender_label = QLabel("Cinsiyet:")
        gender_label.setStyleSheet("font-weight: bold;")
        profile_layout.addWidget(gender_label, 4, 1)
        
        gender_value = QLabel('Erkek' if self.patient.gender == 'E' else 'Kadın')
        gender_value.setStyleSheet("color: #333333;")
        profile_layout.addWidget(gender_value, 4, 2)
        
        email_label = QLabel("E-posta:")
        email_label.setStyleSheet("font-weight: bold;")
        profile_layout.addWidget(email_label, 5, 1)
        
        email_value = QLabel(self.patient.email)
        email_value.setStyleSheet("color: #333333;")
        profile_layout.addWidget(email_value, 5, 2)
        
        # Patient diagnosis info
        diagnosis_group = QGroupBox("Teşhis Bilgileri")
        diagnosis_layout = QGridLayout()
        diagnosis_layout.setVerticalSpacing(15)
        diagnosis_layout.setHorizontalSpacing(15)
        diagnosis_group.setLayout(diagnosis_layout)
        
        diabetes_type_label = QLabel("Diyabet Türü:")
        diabetes_type_label.setStyleSheet("font-weight: bold;")
        diagnosis_layout.addWidget(diabetes_type_label, 0, 0)
        
        diabetes_type_value = QLabel(self.patient.diabetes_type or "-")
        diabetes_type_value.setStyleSheet("color: #333333;")
        diagnosis_layout.addWidget(diabetes_type_value, 0, 1)
        
        diagnosis_date_label = QLabel("Teşhis Tarihi:")
        diagnosis_date_label.setStyleSheet("font-weight: bold;")
        diagnosis_layout.addWidget(diagnosis_date_label, 1, 0)
        
        diagnosis_date_value = QLabel(DateUtils.format_date(self.patient.diagnosis_date) if self.patient.diagnosis_date else "-")
        diagnosis_date_value.setStyleSheet("color: #333333;")
        diagnosis_layout.addWidget(diagnosis_date_value, 1, 1)
        
        diagnosis_label = QLabel("Teşhis:")
        diagnosis_label.setStyleSheet("font-weight: bold;")
        diagnosis_layout.addWidget(diagnosis_label, 2, 0, Qt.AlignTop)
        
        diagnosis_value = QLabel(self.patient.diagnosis or "-")
        diagnosis_value.setWordWrap(True)
        diagnosis_value.setStyleSheet("color: #333333;")
        diagnosis_layout.addWidget(diagnosis_value, 2, 1)
        
        # Password change
        password_group = QGroupBox("Şifre Değiştirme")
        password_layout = QGridLayout()
        password_layout.setVerticalSpacing(15)
        password_layout.setHorizontalSpacing(15)
        password_group.setLayout(password_layout)
        
        # Current password
        current_password_label = QLabel("Mevcut Şifre:")
        current_password_label.setStyleSheet("font-weight: bold;")
        password_layout.addWidget(current_password_label, 0, 0)
        
        self.current_password = QLineEdit()
        self.current_password.setPlaceholderText("Mevcut şifreniz")
        self.current_password.setEchoMode(QLineEdit.Password)
        self.current_password.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                min-height: 36px;
            }
        """)
        password_layout.addWidget(self.current_password, 0, 1)
        
        # New password
        new_password_label = QLabel("Yeni Şifre:")
        new_password_label.setStyleSheet("font-weight: bold;")
        password_layout.addWidget(new_password_label, 1, 0)
        
        self.new_password = QLineEdit()
        self.new_password.setPlaceholderText("Yeni şifreniz (en az 6 karakter)")
        self.new_password.setEchoMode(QLineEdit.Password)
        self.new_password.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                min-height: 36px;
            }
        """)
        password_layout.addWidget(self.new_password, 1, 1)
        
        # Confirm password
        confirm_password_label = QLabel("Şifre Tekrar:")
        confirm_password_label.setStyleSheet("font-weight: bold;")
        password_layout.addWidget(confirm_password_label, 2, 0)
        
        self.confirm_password = QLineEdit()
        self.confirm_password.setPlaceholderText("Yeni şifrenizi tekrar girin")
        self.confirm_password.setEchoMode(QLineEdit.Password)
        self.confirm_password.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                min-height: 36px;
            }
        """)
        password_layout.addWidget(self.confirm_password, 2, 1)
        
        # Change password button
        change_password_button = QPushButton("Şifreyi Değiştir")
        change_password_button.setCursor(QCursor(Qt.PointingHandCursor))
        change_password_button.setStyleSheet("""
            QPushButton {
                background-color: #3949AB;
                color: white;
                border-radius: 5px;
                padding: 10px 15px;
                font-weight: bold;
                min-height: 40px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #303F9F;
            }
            QPushButton:pressed {
                background-color: #283593;
            }
        """)
        change_password_button.setIcon(QIcon("resources/icons/key.png"))
        change_password_button.clicked.connect(self.change_password)
        
        password_layout.addWidget(change_password_button, 3, 0, 1, 2, Qt.AlignCenter)
        
        # Add components to Settings tab
        settings_layout.addWidget(profile_group)
        settings_layout.addWidget(diagnosis_group)
        settings_layout.addWidget(password_group)
        settings_layout.addStretch(1)
        
        # Add tabs to main layout
        self.tabs.addTab(dashboard_tab, "Dashboard")
        self.tabs.addTab(glucose_tab, "Kan Şekeri Ölçümü")
        self.tabs.addTab(diet_exercise_tab, "Diyet ve Egzersiz")
        self.tabs.addTab(symptoms_tab, "Belirti Takibi")
        self.tabs.addTab(insulin_tab, "İnsülin Takibi")
        self.tabs.addTab(settings_tab, "Ayarlar")
        
        # Add components to main layout
        main_layout.addWidget(top_panel)
        main_layout.addWidget(self.tabs, 1)
        
        # Center window on screen
        self.center()
    
    def center(self):
        """Center window on screen."""
        screen = self.screen().availableGeometry()
        window_size = self.geometry()
        x = (screen.width() - window_size.width()) // 2
        y = (screen.height() - window_size.height()) // 2
        self.move(x, y)
    
    def logout(self):
        """Handle logout process."""
        reply = QMessageBox.question(
            self, 
            "Çıkış", 
            "Çıkış yapmak istediğinize emin misiniz?",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            from ui.login_window import LoginWindow
            self.login_window = LoginWindow()
            self.login_window.show()
            self.close()
    
    def load_dashboard(self):
        """Load dashboard content."""
        # Clear existing content
        for i in reversed(range(self.dashboard_layout.count())):
            widget = self.dashboard_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # Dashboard welcome card
        welcome_card = QWidget()
        welcome_card.setStyleSheet("""
            background-color: #E8EAF6;
            border-radius: 8px;
            padding: 15px;
        """)
        welcome_layout = QVBoxLayout()
        welcome_card.setLayout(welcome_layout)
        
        welcome_title = QLabel(f"Hoş geldiniz, {self.patient.name}!")
        welcome_title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        welcome_title.setStyleSheet("color: #3949AB;")
        
        today_date = QLabel(f"Bugün: {DateUtils.format_date(datetime.now().date())}")
        today_date.setFont(QFont("Segoe UI", 12))
        today_date.setStyleSheet("color: #5C6BC0;")
        
        welcome_layout.addWidget(welcome_title)
        welcome_layout.addWidget(today_date)
        
        # Daily measurement status
        measurements_group = QGroupBox("Günlük Ölçüm Durumu")
        measurements_layout = QVBoxLayout()
        measurements_group.setLayout(measurements_layout)
        
        # Get today's measurements
        today = datetime.now().date()
        daily_measurements = PatientController.get_daily_measurements(self.patient.id, today)
        
        # Period-based table
        periods_table = QTableWidget()
        periods_table.setColumnCount(3)
        periods_table.setRowCount(5)  # En az 5 satır
        periods_table.setMinimumHeight(180)  # Yüksekliği artır
        periods_table.setHorizontalHeaderLabels(["Periyot", "Zaman", "Değer (mg/dL)"])
        periods_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        periods_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 5px;
                gridline-color: #F0F0F0;
            }
            QTableWidget::item {
                padding: 8px;
            }
        """)
        
        periods = {
            "morning": {"name": "Sabah", "time": "07:00-08:00", "value": None},
            "noon": {"name": "Öğle", "time": "12:00-13:00", "value": None},
            "afternoon": {"name": "İkindi", "time": "15:00-16:00", "value": None},
            "evening": {"name": "Akşam", "time": "18:00-19:00", "value": None},
            "night": {"name": "Gece", "time": "22:00-23:00", "value": None}
        }
        
        # Place measurements in periods
        for m in daily_measurements:
            period = m['period']
            if period in periods:
                periods[period]["value"] = m['glucose_level']
        
        # Fill table rows
        for i, period_key in enumerate(["morning", "noon", "afternoon", "evening", "night"]):
            period = periods[period_key]
            
            period_item = QTableWidgetItem(period["name"])
            period_item.setFont(QFont("Segoe UI", 10, QFont.Bold))
            periods_table.setItem(i, 0, period_item)
            
            time_item = QTableWidgetItem(period["time"])
            periods_table.setItem(i, 1, time_item)
            
            if period["value"] is not None:
                value_item = QTableWidgetItem(str(period["value"]))
                value_item.setFont(QFont("Segoe UI", 10, QFont.Bold))
                
                # Color based on value
                if period["value"] < 70:
                    value_item.setForeground(QColor("#F44336"))  # Low - red
                    value_item.setBackground(QColor(255, 235, 238, 100))  # Light red
                    # ui/patient_panel.py (continued)
                elif period["value"] > 180:
                    value_item.setForeground(QColor("#FF9800"))  # High - orange
                    value_item.setBackground(QColor(255, 243, 224, 100))  # Light orange
                elif 70 <= period["value"] <= 110:
                    value_item.setForeground(QColor("#4CAF50"))  # Normal - green
                    value_item.setBackground(QColor(232, 245, 233, 100))  # Light green
                
                periods_table.setItem(i, 2, value_item)
            else:
                not_measured = QTableWidgetItem("Ölçüm yok")
                not_measured.setForeground(QColor("#757575"))  # Gray
                periods_table.setItem(i, 2, not_measured)
        
        measurements_layout.addWidget(periods_table)
        
        # Daily average
        avg_values = [periods[p]["value"] for p in periods if periods[p]["value"] is not None]
        daily_avg = sum(avg_values) / len(avg_values) if avg_values else None
        
        avg_card = QWidget()
        avg_card.setStyleSheet("""
            background-color: #FAFAFA;
            border: 1px solid #E0E0E0;
            border-radius: 5px;
            padding: 15px;
            margin-top: 10px;
        """)
        avg_layout = QHBoxLayout()
        avg_card.setLayout(avg_layout)
        
        avg_label = QLabel("Günlük Ortalama:")
        avg_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        
        avg_value = QLabel(f"{daily_avg:.1f} mg/dL" if daily_avg is not None else "Ölçüm yok")
        avg_value.setFont(QFont("Segoe UI", 14, QFont.Bold))
        
        if daily_avg is not None:
            if daily_avg < 70:
                avg_value.setStyleSheet("color: #F44336;")  # Low - red
            elif daily_avg > 180:
                avg_value.setStyleSheet("color: #FF9800;")  # High - orange
            elif 70 <= daily_avg <= 110:
                avg_value.setStyleSheet("color: #4CAF50;")  # Normal - green
        
        avg_layout.addWidget(avg_label)
        avg_layout.addWidget(avg_value)
        avg_layout.addStretch(1)
        
        measurements_layout.addWidget(avg_card)
        
        # Status and recommendations
        today_group = QGroupBox("Bugünkü Durum ve Öneriler")
        today_layout = QVBoxLayout()
        today_group.setLayout(today_layout)
        
        # Get recommendations
        recommendations = PatientController.get_current_recommendations(self.patient.id)
        
        if recommendations:
            glucose_level = recommendations.get('glucose_level')
            diet_recommendation = recommendations.get('diet_recommendation')
            exercise_recommendation = recommendations.get('exercise_recommendation')
            
            # Blood glucose status
            status_card = QWidget()
            status_card.setStyleSheet("""
                border-radius: 5px;
                padding: 10px;
                margin-bottom: 10px;
            """)
            
            status_layout = QVBoxLayout()
            status_card.setLayout(status_layout)
            
            status_label = QLabel()
            status_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
            status_label.setAlignment(Qt.AlignCenter)
            
            if glucose_level < 70:
                status_label.setText("⚠️ Hipoglisemi Riski!")
                status_label.setStyleSheet("color: #F44336;")
                status_card.setStyleSheet(status_card.styleSheet() + "background-color: #FFEBEE;")
            elif glucose_level > 180:
                status_label.setText("⚠️ Hiperglisemi Durumu!")
                status_label.setStyleSheet("color: #FF9800;")
                status_card.setStyleSheet(status_card.styleSheet() + "background-color: #FFF3E0;")
            else:
                status_label.setText("✅ Normal Kan Şekeri Seviyesi")
                status_label.setStyleSheet("color: #4CAF50;")
                status_card.setStyleSheet(status_card.styleSheet() + "background-color: #E8F5E9;")
            
            status_layout.addWidget(status_label)
            today_layout.addWidget(status_card)
            
            # Daily recommendations
            recommendations_label = QLabel("Öneriler:")
            recommendations_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
            recommendations_label.setStyleSheet("color: #3949AB; margin-top: 10px;")
            today_layout.addWidget(recommendations_label)
            
            # Diet recommendation
            diet_map = {
                Diet.TYPE_LOW_SUGAR: "Az Şekerli Diyet",
                Diet.TYPE_NO_SUGAR: "Şekersiz Diyet",
                Diet.TYPE_BALANCED: "Dengeli Beslenme"
            }
            
            diet_card = QWidget()
            diet_card.setStyleSheet("""
                background-color: #E8EAF6;
                border-radius: 5px;
                padding: 10px;
                margin-bottom: 5px;
            """)
            diet_card_layout = QHBoxLayout()
            diet_card.setLayout(diet_card_layout)
            
            diet_icon = QLabel("🍎")
            diet_icon.setFont(QFont("Segoe UI", 16))
            diet_card_layout.addWidget(diet_icon)
            
            diet_label = QLabel(f"Diyet: {diet_map.get(diet_recommendation, 'Öneri yok')}")
            diet_label.setFont(QFont("Segoe UI", 11))
            diet_card_layout.addWidget(diet_label)
            diet_card_layout.addStretch(1)
            
            today_layout.addWidget(diet_card)
            
            # Exercise recommendation
            exercise_map = {
                Exercise.TYPE_WALKING: "Yürüyüş",
                Exercise.TYPE_CYCLING: "Bisiklet",
                Exercise.TYPE_CLINICAL: "Klinik Egzersiz"
            }
            
            exercise_card = QWidget()
            exercise_card.setStyleSheet("""
                background-color: #E8EAF6;
                border-radius: 5px;
                padding: 10px;
                margin-bottom: 5px;
            """)
            exercise_card_layout = QHBoxLayout()
            exercise_card.setLayout(exercise_card_layout)
            
            exercise_icon = QLabel("🏃")
            exercise_icon.setFont(QFont("Segoe UI", 16))
            exercise_card_layout.addWidget(exercise_icon)
            
            if exercise_recommendation:
                exercise_label = QLabel(f"Egzersiz: {exercise_map.get(exercise_recommendation, 'Öneri yok')}")
            else:
                exercise_label = QLabel("Egzersiz: Önerilmiyor")
            
            exercise_label.setFont(QFont("Segoe UI", 11))
            exercise_card_layout.addWidget(exercise_label)
            exercise_card_layout.addStretch(1)
            
            today_layout.addWidget(exercise_card)
        else:
            no_data = QLabel("Henüz yeterli veri bulunmamaktadır.")
            no_data.setAlignment(Qt.AlignCenter)
            no_data.setStyleSheet("color: #757575; padding: 20px;")
            today_layout.addWidget(no_data)
        
        # 7-day blood glucose chart
        chart_group = QGroupBox("Son 7 Günlük Kan Şekeri Grafiği")
        chart_group.setMinimumHeight(260)
        chart_layout = QVBoxLayout()
        chart_group.setLayout(chart_layout)
        
        # Date range
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=6)  # Last 7 days
        
        # Get measurements
        measurements = PatientController.get_measurements_by_date_range(self.patient.id, start_date, end_date)
        
        # Create chart
        chart_figure = Figure(figsize=(8, 4), dpi=100)
        chart_canvas = FigureCanvas(chart_figure)
        chart_canvas.setMinimumHeight(220)
        chart_layout.addWidget(chart_canvas)
        
        # Group measurements by date
        daily_averages = {}
        for m in measurements:
            date_str = DateUtils.format_date(m['measurement_date'])
            if date_str in daily_averages:
                daily_averages[date_str].append(m['glucose_level'])
            else:
                daily_averages[date_str] = [m['glucose_level']]
        
        # Calculate daily averages
        dates = []
        averages = []
        
        for date_str in sorted(daily_averages.keys()):
            dates.append(date_str)
            avg = sum(daily_averages[date_str]) / len(daily_averages[date_str])
            averages.append(avg)
        
        # Draw chart
        if dates and averages:
            ax = chart_figure.add_subplot(111)
            ax.plot(dates, averages, 'o-', color='#3949AB', linewidth=2, markersize=8)
            
            # Show safe ranges
            ax.axhspan(70, 110, alpha=0.2, color='#4CAF50', label='Normal')
            ax.axhspan(0, 70, alpha=0.2, color='#F44336', label='Hipoglisemi')
            ax.axhspan(180, max(300, max(averages) + 50), alpha=0.2, color='#FF9800', label='Hiperglisemi')
            
            ax.set_xlabel('Tarih', fontsize=10)
            ax.set_ylabel('Kan Şekeri (mg/dL)', fontsize=10)
            ax.set_title('Son 7 Günlük Kan Şekeri Ortalaması', fontweight='bold', fontsize=12)
            ax.grid(True, linestyle='--', alpha=0.7)
            ax.legend(frameon=False)
            
            # Add value labels above points
            for i, (x, y) in enumerate(zip(dates, averages)):
                ax.annotate(f'{y:.1f}', xy=(x, y), xytext=(0, 10),
                            textcoords='offset points', ha='center', fontsize=9,
                            fontweight='bold')
            
            # Rotate x labels
            plt.setp(ax.get_xticklabels(), rotation=30, ha='right')
            
            # Customize chart appearance
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_color('#DDDDDD')
            ax.spines['left'].set_color('#DDDDDD')
            ax.tick_params(colors='#666666')
            
            chart_figure.tight_layout()
            chart_canvas.draw()
        else:
            no_data_label = QLabel("Henüz yeterli veri bulunmamaktadır.")
            no_data_label.setAlignment(Qt.AlignCenter)
            no_data_label.setStyleSheet("color: #757575; padding: 20px;")
            chart_layout.addWidget(no_data_label)
        
        # Next measurement reminder
        reminder_card = QWidget()
        reminder_card.setStyleSheet("""
            background-color: #FFECB3;
            border-radius: 8px;
            padding: 15px;
            margin-top: 20px;
        """)
        reminder_layout = QHBoxLayout()
        reminder_card.setLayout(reminder_layout)
        
        reminder_icon = QLabel("⏰")
        reminder_icon.setFont(QFont("Segoe UI", 24))
        reminder_layout.addWidget(reminder_icon)
        
        next_period = None
        current_time = datetime.now().time()
        
        if current_time < time(7, 0):
            next_period = "Sabah (07:00-08:00)"
        elif current_time < time(12, 0):
            next_period = "Öğle (12:00-13:00)"
        elif current_time < time(15, 0):
            next_period = "İkindi (15:00-16:00)"
        elif current_time < time(18, 0):
            next_period = "Akşam (18:00-19:00)"
        elif current_time < time(22, 0):
            next_period = "Gece (22:00-23:00)"
        else:
            next_period = "Sabah (07:00-08:00) - Yarın"
        
        reminder_text = QLabel(f"Sonraki Ölçüm Zamanı: {next_period}")
        reminder_text.setFont(QFont("Segoe UI", 12, QFont.Bold))
        reminder_text.setStyleSheet("color: #FF6F00;")
        reminder_layout.addWidget(reminder_text)
        reminder_layout.addStretch(1)
        
        # Quick actions
        actions_group = QGroupBox("Hızlı İşlemler")
        actions_layout = QHBoxLayout()
        actions_group.setLayout(actions_layout)
        
        # Measure glucose action
        measure_action = QPushButton("Ölçüm Ekle")
        measure_action.setCursor(QCursor(Qt.PointingHandCursor))
        measure_action.setStyleSheet("""
            QPushButton {
                background-color: #3949AB;
                color: white;
                border-radius: 5px;
                padding: 15px;
                font-weight: bold;
                font-size: 14px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #303F9F;
            }
        """)
        measure_action.setIcon(QIcon("resources/icons/measurement.png"))
        measure_action.setIconSize(QSize(24, 24))
        measure_action.clicked.connect(lambda: self.tabs.setCurrentIndex(1))  # Switch to glucose tab
        
        # Diet & Exercise action (merged)
        diet_exercise_action = QPushButton("Diyet & Egzersiz Kaydet")
        diet_exercise_action.setCursor(QCursor(Qt.PointingHandCursor))
        diet_exercise_action.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
                padding: 15px;
                font-weight: bold;
                font-size: 14px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #43A047;
            }
        """)
        diet_exercise_action.setIcon(QIcon("resources/icons/diet.png"))
        diet_exercise_action.setIconSize(QSize(24, 24))
        diet_exercise_action.clicked.connect(lambda: self.tabs.setCurrentIndex(2))  # Switch to diet & exercise tab
        
        actions_layout.addWidget(measure_action)
        actions_layout.addWidget(diet_exercise_action)
        
        # Add components to dashboard
        self.dashboard_layout.addWidget(welcome_card)
        self.dashboard_layout.addWidget(actions_group)
        self.dashboard_layout.addWidget(measurements_group)
        self.dashboard_layout.addWidget(today_group)
        self.dashboard_layout.addWidget(reminder_card)
        self.dashboard_layout.addWidget(chart_group)
    
    def load_measurements(self):
        """Load measurement data into table."""
        # Get last 10 measurements
        measurements = PatientController.get_patient_measurements(self.patient.id)
        recent_measurements = measurements[:10] if measurements else []
        row_count = max(5, len(recent_measurements))
        self.measurements_table.setRowCount(row_count)
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
            if m['glucose_level'] < 70:
                value_item.setForeground(QColor("#F44336"))
            elif m['glucose_level'] > 180:
                value_item.setForeground(QColor("#FF9800"))
            elif 70 <= m['glucose_level'] <= 110:
                value_item.setForeground(QColor("#4CAF50"))
            self.measurements_table.setItem(i, 3, value_item)
            self.measurements_table.setItem(i, 4, QTableWidgetItem(m['notes'] or ""))
        self.measurements_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    
    def load_diets(self):
        """Load diet data into table."""
        # Get last 10 diet records
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
                status_item.setForeground(QColor("#4CAF50"))  # Green
            else:
                status_item.setForeground(QColor("#F44336"))  # Red
            self.diet_table.setItem(i, 2, status_item)
            
            self.diet_table.setItem(i, 3, QTableWidgetItem(d['notes'] or ""))
        
        self.diet_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    
    def load_exercises(self):
        """Load exercise data into table."""
        # Get last 10 exercise records
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
                status_item.setForeground(QColor("#4CAF50"))  # Green
            else:
                status_item.setForeground(QColor("#F44336"))  # Red
            self.exercise_table.setItem(i, 2, status_item)
            
            self.exercise_table.setItem(i, 3, QTableWidgetItem(e['notes'] or ""))
        
        self.exercise_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    
    def load_symptoms(self):
        """Load symptom data into table."""
        # Get last 10 symptom records
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
            
            severity_item = QTableWidgetItem(severity_text)
            if severity and severity >= 4:
                severity_item.setForeground(QColor("#F44336"))  # Red for high severity
            elif severity and severity >= 3:
                severity_item.setForeground(QColor("#FF9800"))  # Orange for medium severity
                
            self.symptom_table.setItem(i, 2, severity_item)
            self.symptom_table.setItem(i, 3, QTableWidgetItem(s['notes'] or ""))
        
        self.symptom_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    
    def load_insulins(self, start_date=None, end_date=None):
        """Load insulin data into table and combobox."""
        # Get insulin records
        if start_date and end_date:
            insulins = PatientController.get_insulin_recommendations(self.patient.id, start_date, end_date)
        else:
            insulins = PatientController.get_insulin_recommendations(self.patient.id)
        
        # Clear insulin combobox and refill
        self.insulin_id_combo.clear()
        
        if insulins:
            # Fill table
            self.insulin_table.setRowCount(len(insulins))
            
            for i, insulin in enumerate(insulins):
                # Date
                self.insulin_table.setItem(i, 0, QTableWidgetItem(DateUtils.format_datetime(insulin['date'])))
                
                # Average glucose
                avg_glucose = insulin['average_glucose']
                avg_text = f"{avg_glucose:.1f} mg/dL" if avg_glucose else "-"
                self.insulin_table.setItem(i, 1, QTableWidgetItem(avg_text))
                
                # Recommendation
                recommended = insulin['recommended_dose']
                recommended_text = f"{recommended} ml" if recommended is not None else "-"
                self.insulin_table.setItem(i, 2, QTableWidgetItem(recommended_text))
                
                # Administered
                administered = insulin['administered_dose']
                administered_text = f"{administered} ml" if administered is not None else "Uygulanmadı"
                
                administered_item = QTableWidgetItem(administered_text)
                if administered is not None:
                    administered_item.setForeground(QColor("#4CAF50"))  # Green
                else:
                    administered_item.setForeground(QColor("#F44336"))  # Red
                    
                self.insulin_table.setItem(i, 3, administered_item)
                
                # Notes
                self.insulin_table.setItem(i, 4, QTableWidgetItem(insulin['notes'] or ""))
                
                # Add unapplied insulins to combobox
                if administered is None:
                    display_text = f"{DateUtils.format_date(insulin['date'])} - {recommended} ml"
                    self.insulin_id_combo.addItem(display_text, insulin['id'])
        else:
            self.insulin_table.setRowCount(0)
        
        self.insulin_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    
    def save_measurement(self):
        """Save glucose measurement."""
        # Get form data
        measurement_date = self.measurement_date.date().toPyDate()
        measurement_time = self.measurement_time.time().toPyTime()
        period = self.measurement_period.currentData()
        glucose_level_text = self.glucose_value.text()
        notes = self.measurement_notes.toPlainText()
        
        # Validation
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
        
        # Check period-time compatibility
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
        
        # Save measurement
        try:
            measurement_id = PatientController.add_measurement(
                patient_id=self.patient.id,
                glucose_level=glucose_level,
                measurement_date=measurement_date,
                measurement_time=measurement_time,
                period=period,
                notes=notes
            )
            
            if measurement_id:
                QMessageBox.information(self, "Başarılı", "Kan şekeri ölçümü başarıyla kaydedildi.")
                
                # Clear form
                self.glucose_value.clear()
                self.measurement_notes.clear()
                
                # Update table
                self.load_measurements()
                
                # Update dashboard
                self.load_dashboard()
            else:
                QMessageBox.warning(self, "Hata", "Ölçüm kaydedilemedi. Veritabanı hatası oluştu.")
                
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Ölçüm kaydedilirken bir hata oluştu: {str(e)}")
    
    def save_diet(self):
        """Save diet status."""
        # Get form data
        diet_date = self.diet_date.date().toPyDate()
        diet_type = self.diet_type.currentData()
        is_followed = self.diet_status.isChecked()
        notes = self.diet_notes.toPlainText()
        
        # Save diet
        try:
            PatientController.add_diet_status(
                self.patient.id,
                diet_type,
                diet_date,
                is_followed,
                notes
            )
            
            QMessageBox.information(self, "Başarılı", "Diyet durumu başarıyla kaydedildi.")
            
            # Clear form
            self.diet_notes.clear()
            
            # Update table
            self.load_diets()
            
            # Update dashboard
            self.load_dashboard()
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Diyet durumu kaydedilirken bir hata oluştu: {str(e)}")
    
    def save_exercise(self):
        """Save exercise status."""
        # Get form data
        exercise_date = self.exercise_date.date().toPyDate()
        exercise_type = self.exercise_type.currentData()
        is_completed = self.exercise_status.isChecked()
        notes = self.exercise_notes.toPlainText()
        
        # Save exercise
        try:
            PatientController.add_exercise_status(
                self.patient.id,
                exercise_type,
                exercise_date,
                is_completed,
                notes
            )
            
            QMessageBox.information(self, "Başarılı", "Egzersiz durumu başarıyla kaydedildi.")
            
            # Clear form
            self.exercise_notes.clear()
            
            # Update table
            self.load_exercises()
            
            # ui/patient_panel.py (continued)
            # Update dashboard
            self.load_dashboard()
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Egzersiz durumu kaydedilirken bir hata oluştu: {str(e)}")
    
    def save_symptom(self):
        """Save symptom information."""
        # Get form data
        symptom_date = self.symptom_date.date().toPyDate()
        symptom_type = self.symptom_type.currentData()
        severity = self.symptom_severity.currentData()
        notes = self.symptom_notes.toPlainText()
        
        # Save symptom
        try:
            PatientController.add_symptom(
                self.patient.id,
                symptom_type,
                severity,
                symptom_date,
                notes
            )
            
            QMessageBox.information(self, "Başarılı", "Belirti başarıyla kaydedildi.")
            
            # Clear form
            self.symptom_notes.clear()
            
            # Update table
            self.load_symptoms()
            
            # Update dashboard
            self.load_dashboard()
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Belirti kaydedilirken bir hata oluştu: {str(e)}")
    
    def apply_insulin(self):
        """Record insulin application."""
        # Get form data
        if self.insulin_id_combo.count() == 0:
            QMessageBox.warning(self, "Uyarı", "Kaydedilecek insülin önerisi bulunmuyor.")
            return
        
        insulin_id = self.insulin_id_combo.currentData()
        amount_text = self.insulin_amount.text()
        notes = self.insulin_notes.toPlainText()
        
        # Validation
        if not amount_text:
            QMessageBox.warning(self, "Hata", "Uygulanan miktar boş olamaz.")
            return
        
        try:
            amount = float(amount_text)
        except ValueError:
            QMessageBox.warning(self, "Hata", "Miktar geçerli bir sayı olmalıdır.")
            return
        
        # Save insulin application
        try:
            PatientController.administer_insulin(
                insulin_id,
                amount,
                notes
            )
            
            QMessageBox.information(self, "Başarılı", "İnsülin uygulaması başarıyla kaydedildi.")
            
            # Clear form
            self.insulin_amount.clear()
            self.insulin_notes.clear()
            
            # Update table
            self.load_insulins(
                self.insulin_start_date.date().toPyDate(),
                self.insulin_end_date.date().toPyDate()
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"İnsülin uygulaması kaydedilirken bir hata oluştu: {str(e)}")
    
    def change_password(self):
        """Handle password change."""
        current_password = self.current_password.text()
        new_password = self.new_password.text()
        confirm_password = self.confirm_password.text()
        
        # Validation
        if not current_password or not new_password or not confirm_password:
            QMessageBox.warning(self, "Hata", "Tüm şifre alanları doldurulmalıdır.")
            return
        
        if new_password != confirm_password:
            QMessageBox.warning(self, "Hata", "Yeni şifre ve tekrarı eşleşmiyor.")
            return
        
        if len(new_password) < 6:
            QMessageBox.warning(self, "Hata", "Yeni şifre en az 6 karakter olmalıdır.")
            return
        
        # Change password
        success = AuthController.change_password(self.patient.id, current_password, new_password)
        
        if success:
            QMessageBox.information(self, "Başarılı", "Şifreniz başarıyla değiştirildi.")
            
            # Clear form
            self.current_password.clear()
            self.new_password.clear()
            self.confirm_password.clear()
        else:
            QMessageBox.warning(self, "Hata", "Mevcut şifreniz hatalı.")
            

