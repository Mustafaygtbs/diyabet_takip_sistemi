from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QTabWidget, QTableWidget,
                            QTableWidgetItem, QFrame, QSplitter, QComboBox,
                            QDateEdit, QMessageBox, QHeaderView, QMenu,
                            QAction, QStackedWidget, QFormLayout, QLineEdit,
                            QTextEdit, QRadioButton, QButtonGroup, QCheckBox,
                            QSpacerItem, QSizePolicy, QScrollArea, QListWidget,
                            QListWidgetItem, QGridLayout, QDialog, QFileDialog,
                            QGroupBox, QSpinBox) 
from PyQt5.QtGui import QIcon, QPixmap, QFont, QColor, QPalette
from PyQt5.QtCore import Qt, QDate

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib as mpl

from models.doctor import Doctor
from models.patient import Patient
from models.measurement import Measurement
from models.exercise import Exercise
from models.diet import Diet
from models.symptom import Symptom
from models.alert import Alert

from controllers.doctor_controller import DoctorController
from controllers.alert_controller import AlertController
from controllers.patient_controller import PatientController

from ui.widgets.glucose_chart import GlucoseChartWidget
from ui.widgets.exercise_chart import ExerciseChartWidget
from ui.widgets.alert_widget import AlertWidget
from ui.patient_form import PatientFormDialog

from utils.date_utils import DateUtils

from datetime import datetime, timedelta

class DoctorPanel(QMainWindow):
    def __init__(self, doctor):
        super().__init__()
        self.doctor = doctor
        
        mpl.style.use('seaborn-v0_8-whitegrid')
        plt.rcParams['font.family'] = 'Segoe UI'
        plt.rcParams['axes.facecolor'] = '#F8F9FA'
        plt.rcParams['figure.facecolor'] = '#FFFFFF'
        plt.rcParams['axes.labelcolor'] = '#333333'
        plt.rcParams['axes.edgecolor'] = '#DDDDDD'
        plt.rcParams['axes.spines.top'] = False
        plt.rcParams['axes.spines.right'] = False
        
        self.initUI()
        self.load_patients()
    
    def initUI(self):
        # Main window settings
        self.setWindowTitle(f"Diyabet Takip Sistemi - Dr. {self.doctor.name} {self.doctor.surname}")
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
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 8px 20px;
                margin-right: 2px;
                color: #666666;
                min-width: 120px;
                max-width: 160px;
                text-align: center;
                font-size: 15px;
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
            QComboBox, QDateEdit, QLineEdit {
                border: 1px solid #E0E0E0;
                border-radius: 5px;
                padding: 6px;
                background-color: white;
                min-height: 25px;
            }
            QComboBox:focus, QDateEdit:focus, QLineEdit:focus {
                border: 1px solid #3949AB;
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
        top_panel.setMaximumHeight(80)
        top_panel.setStyleSheet("""
            background-color: #3949AB;
            color: white;
            border-radius: 5px;
            margin-bottom: 10px;
        """)
        
        # Doctor info
        doctor_info = QWidget()
        doctor_info_layout = QHBoxLayout()
        doctor_info.setLayout(doctor_info_layout)
        
        # Profile picture
        profile_pic = QLabel()
        if self.doctor.profile_image:
            pixmap = QPixmap()
            pixmap.loadFromData(self.doctor.profile_image)
            profile_pic.setPixmap(pixmap.scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            profile_pic.setText("🧑‍⚕️")
            profile_pic.setFont(QFont("Segoe UI", 24))
        
        profile_pic.setAlignment(Qt.AlignCenter)
        profile_pic.setFixedSize(60, 60)
        profile_pic.setStyleSheet("""
            background-color: white;
            border-radius: 30px;
            border: 2px solid #C5CAE9;
            padding: 2px;
        """)
        
        # Doctor name and type
        doctor_name = QLabel(f"Dr. {self.doctor.name} {self.doctor.surname}")
        doctor_name.setFont(QFont("Segoe UI", 14, QFont.Bold))
        
        doctor_specialty = QLabel(self.doctor.specialty or "Doktor")
        doctor_specialty.setFont(QFont("Segoe UI", 12))
        
        doctor_text = QWidget()
        doctor_text_layout = QVBoxLayout()
        doctor_text.setLayout(doctor_text_layout)
        doctor_text_layout.addWidget(doctor_name)
        doctor_text_layout.addWidget(doctor_specialty)
        
        doctor_info_layout.addWidget(profile_pic)
        doctor_info_layout.addWidget(doctor_text)
        
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
        logout_button.setIcon(QIcon("resources/icons/logout.png"))
        logout_button.clicked.connect(self.logout)
        
        # Complete top panel
        top_layout.addWidget(doctor_info)
        top_layout.addStretch(1)
        top_layout.addWidget(logout_button)
        
        # Main section - Patient list and details
        main_section = QSplitter(Qt.Horizontal)
        main_section.setStyleSheet("""
            QSplitter::handle {
                background-color: #E0E0E0;
                width: 1px;
            }
        """)
        
        # Left panel - Patient list and add button
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)
        left_panel.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 5px;
            }
        """)
        
        # Header with title and add patient button
        patients_card = QFrame()
        patients_card.setStyleSheet("""
            QFrame {
                background: #fff;
                border-radius: 12px;
                border: 1.5px solid #E0E0E0;
                box-shadow: 0 2px 8px rgba(60,60,60,0.07);
                margin-bottom: 12px;
                padding: 18px 0 10px 0;
            }
        """)
        patients_card_layout = QVBoxLayout()
        patients_card.setLayout(patients_card_layout)
        patients_label = QLabel("Hastalarım")
        patients_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        patients_label.setStyleSheet("color: #3949AB; margin-bottom: 8px;")
        add_patient_button = QPushButton("Yeni Hasta")
        add_patient_button.setIcon(QIcon("resources/medical-check.png"))
        add_patient_button.setFixedWidth(120)
        add_patient_button.setFixedHeight(32)
        add_patient_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 7px;
                padding: 6px 18px;
                font-weight: bold;
                font-size: 13px;
                margin-top: 2px;
                margin-bottom: 2px;
                box-shadow: 0 2px 8px rgba(60,60,60,0.07);
            }
            QPushButton:hover {
                background-color: #43A047;
            }
            QPushButton:pressed {
                background-color: #388E3C;
            }
        """)
        add_patient_button.clicked.connect(self.open_patient_form)
        patients_card_layout.addWidget(patients_label, alignment=Qt.AlignHCenter)
        patients_card_layout.addWidget(add_patient_button, alignment=Qt.AlignHCenter)
        patients_card_layout.setSpacing(6)
        patients_card_layout.setContentsMargins(0, 0, 0, 0)
        list_header = patients_card
        
        # Search box
        search_layout = QHBoxLayout()
        search_label = QLabel("Ara:")
        search_label.setStyleSheet("font-weight: bold;")
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("İsim, TC Kimlik veya teşhis ara...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #E0E0E0;
                border-radius: 5px;
                padding: 8px;
                background-color: #F5F5F5;
            }
            QLineEdit:focus {
                border: 1px solid #3949AB;
                background-color: white;
            }
        """)
        self.search_input.textChanged.connect(self.filter_patients)
        
        # Patient list
        self.patient_list = QListWidget()
        self.patient_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #E0E0E0;
                border-radius: 5px;
                padding: 5px;
                background-color: white;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #F0F0F0;
                color: #333333;
            }
            QListWidget::item:selected {
                background-color: #E8EAF6;
                color: #3949AB;
                font-weight: bold;
                border-left: 3px solid #3949AB;
            }
            QListWidget::item:hover:!selected {
                background-color: #F5F5F5;
            }
        """)
        self.patient_list.setFixedWidth(210)
        self.patient_list.currentItemChanged.connect(self.on_patient_selected)
        
        left_layout.addWidget(list_header)
        left_layout.addLayout(search_layout)
        left_layout.addWidget(self.patient_list)
        
        # Right panel - Patient details
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_panel.setLayout(right_layout)
        right_panel.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 5px;
            }
        """)
        
        # Patient detail pages
        self.patient_detail_stack = QStackedWidget()
        
        # No patient selected page
        no_patient_page = QWidget()
        no_patient_layout = QVBoxLayout()
        no_patient_page.setLayout(no_patient_layout)
        
        no_patient_icon = QLabel("👨‍⚕️")
        no_patient_icon.setFont(QFont("Segoe UI", 48))
        no_patient_icon.setAlignment(Qt.AlignCenter)
        no_patient_icon.setStyleSheet("color: #9E9E9E;")
        
        no_patient_label = QLabel("Hasta seçilmedi")
        no_patient_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        no_patient_label.setAlignment(Qt.AlignCenter)
        no_patient_label.setStyleSheet("color: #616161;")
        
        no_patient_info = QLabel("Lütfen hasta listesinden bir hasta seçin veya yeni hasta ekleyin.")
        no_patient_info.setAlignment(Qt.AlignCenter)
        no_patient_info.setStyleSheet("color: #757575;")
        
        no_patient_layout.addStretch(1)
        no_patient_layout.addWidget(no_patient_icon)
        no_patient_layout.addWidget(no_patient_label)
        no_patient_layout.addWidget(no_patient_info)
        no_patient_layout.addStretch(1)
        
        self.patient_detail_stack.addWidget(no_patient_page)
        
        # Patient detail page (will be populated when a patient is selected)
        self.patient_detail_page = QWidget()
        self.patient_detail_layout = QVBoxLayout()
        self.patient_detail_page.setLayout(self.patient_detail_layout)
        
        self.patient_detail_stack.addWidget(self.patient_detail_page)
        
        right_layout.addWidget(self.patient_detail_stack)
        
        # Add panels to main section
        main_section.addWidget(left_panel)
        main_section.addWidget(right_panel)
        main_section.setSizes([300, 900])  # Initial widths
        
        # Add components to main layout
        main_layout.addWidget(top_panel)
        main_layout.addWidget(main_section, 1)
        
        # Center window on screen
        self.center()
    
    def center(self):
        screen = self.screen().availableGeometry()
        window_size = self.geometry()
        x = (screen.width() - window_size.width()) // 2
        y = (screen.height() - window_size.height()) // 2
        self.move(x, y)
    
    def logout(self):
        reply = QMessageBox.question(self, "Çıkış", "Çıkış yapmak istediğinize emin misiniz?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            from ui.login_window import LoginWindow
            self.login_window = LoginWindow()
            self.login_window.show()
            self.close()
    
    def load_patients(self):
        self.patient_list.clear()
        
        patients = DoctorController.get_doctor_patients(self.doctor.id)
        
        for patient in patients:
            item = QListWidgetItem(f"{patient.name} {patient.surname}")
            item.setData(Qt.UserRole, patient.id)
            
            # Highlight patients with unread alerts
            unread_alerts = DoctorController.get_patient_alerts(patient.id, only_unread=True)
            if unread_alerts:
                item.setForeground(QColor("#F44336"))  # Red color
                item.setText(f"{patient.name} {patient.surname} ({len(unread_alerts)})")
                item.setIcon(QIcon("resources/icons/alert.png"))
            
            self.patient_list.addItem(item)
    
    def filter_patients(self):
        search_text = self.search_input.text().lower()
        for i in range(self.patient_list.count()):
            item = self.patient_list.item(i)
            patient_id = item.data(Qt.UserRole)
            patient = PatientController.get_patient_by_id(patient_id)
            matches_search = (
                search_text in f"{patient.name} {patient.surname}".lower() or
                search_text in patient.tc_id.lower() or
                (patient.diagnosis and search_text in patient.diagnosis.lower())
            )
            item.setHidden(not matches_search)
    
    def open_patient_form(self):
        dialog = PatientFormDialog(self.doctor.id)
        if dialog.exec_() == QDialog.Accepted:
            self.load_patients()
    
    def on_patient_selected(self, current, previous):
        if not current:
            self.patient_detail_stack.setCurrentIndex(0)  # No patient selected page
            return
        
        patient_id = current.data(Qt.UserRole)
        self.load_patient_details(patient_id)
        self.patient_detail_stack.setCurrentIndex(1)  # Patient detail page
    
    def load_patient_details(self, patient_id):

        # Clear existing content
        for i in reversed(range(self.patient_detail_layout.count())):
            widget = self.patient_detail_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        # Load patient
        patient = PatientController.get_patient_by_id(patient_id)
        
        if not patient:
            QMessageBox.warning(self, "Hata", "Hasta bulunamadı.")
            return
        
        # Patient header info
        header = QWidget()
        header_layout = QHBoxLayout()
        header.setLayout(header_layout)
        header.setStyleSheet("""
            background-color: #E8EAF6;
            border-radius: 5px;
            padding: 5px;
            margin-bottom: 10px;
        """)
        
        # Profile image
        profile_pic = QLabel()
        if patient.profile_image:
            pixmap = QPixmap()
            pixmap.loadFromData(patient.profile_image)
            profile_pic.setPixmap(pixmap.scaled(70, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            profile_pic.setText("👤")
            profile_pic.setFont(QFont("Segoe UI", 30))
            profile_pic.setStyleSheet("color: #757575;")
        
        profile_pic.setAlignment(Qt.AlignCenter)
        profile_pic.setFixedSize(70, 70)
        profile_pic.setStyleSheet("""
            background-color: white;
            border-radius: 35px;
            padding: 5px;
            border: 2px solid #C5CAE9;
        """)
        
        # Patient name and info
        patient_name = QLabel(f"<h2>{patient.name} {patient.surname}</h2>")
        patient_name.setStyleSheet("color: #3949AB;")
        
        patient_info = QLabel(f"TC: {patient.tc_id} | Doğum: {DateUtils.format_date(patient.birthdate)} | Cinsiyet: {'Erkek' if patient.gender == 'E' else 'Kadın'}")
        patient_info.setStyleSheet("color: #616161;")
        
        patient_header = QWidget()
        patient_header_layout = QVBoxLayout()
        patient_header.setLayout(patient_header_layout)
        patient_header_layout.addWidget(patient_name)
        patient_header_layout.addWidget(patient_info)
        
        # Edit button
        edit_button = QPushButton("Düzenle")
        edit_button.setIcon(QIcon("resources/icons/edit.png"))
        edit_button.setStyleSheet("""
            QPushButton {
                background-color: #3949AB;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
                min-height: 36px;
            }
            QPushButton:hover {
                background-color: #303F9F;
            }
            QPushButton:pressed {
                background-color: #283593;
            }
        """)
        edit_button.clicked.connect(lambda: self.edit_patient(patient))
        
        # Complete header
        header_layout.addWidget(profile_pic)
        header_layout.addWidget(patient_header)
        header_layout.addStretch(1)
        header_layout.addWidget(edit_button)
        
        # Tab widget
        tabs = QTabWidget()
        
        # Summary tab
        summary_tab = QScrollArea()
        summary_tab.setWidgetResizable(True)
        summary_content = QWidget()
        summary_layout = QVBoxLayout()
        summary_content.setLayout(summary_layout)
        summary_tab.setWidget(summary_content)
        
        # Diagnosis info
        diagnosis_group = QGroupBox("Teşhis Bilgileri")
        diagnosis_layout = QFormLayout()
        diagnosis_group.setLayout(diagnosis_layout)
        
        diagnosis_type = QLabel(patient.diabetes_type or "-")
        diagnosis_type.setStyleSheet("font-weight: bold; color: #3949AB;")
        
        diagnosis_date = QLabel(DateUtils.format_date(patient.diagnosis_date) or "-")
        diagnosis_text = QLabel(patient.diagnosis or "-")
        diagnosis_text.setWordWrap(True)
        
        diagnosis_layout.addRow("Diyabet Türü:", diagnosis_type)
        diagnosis_layout.addRow("Teşhis Tarihi:", diagnosis_date)
        diagnosis_layout.addRow("Teşhis Detayı:", diagnosis_text)
        
        # Recent measurements
        measurements = DoctorController.get_patient_measurements(patient.id)
        recent_measurements = measurements[:5] if measurements else []
        
        measurements_group = QGroupBox("Son Ölçümler")
        measurements_layout = QVBoxLayout()
        measurements_group.setLayout(measurements_layout)
        
        if recent_measurements:
            measurements_table = QTableWidget()
            measurements_table.setColumnCount(4)
            measurements_table.setHorizontalHeaderLabels(["Tarih", "Saat", "Değer (mg/dL)", "Periyot"])
            measurements_table.setRowCount(len(recent_measurements))
            
            for i, m in enumerate(recent_measurements):
                measurements_table.setItem(i, 0, QTableWidgetItem(DateUtils.format_date(m['measurement_date'])))
                measurements_table.setItem(i, 1, QTableWidgetItem(DateUtils.format_time(m['measurement_time'])))
                
                value_item = QTableWidgetItem(str(m['glucose_level']))
                # Color based on value
                if m['glucose_level'] < 70:
                    value_item.setForeground(QColor("#F44336"))  # Low - red
                elif m['glucose_level'] > 180:
                    value_item.setForeground(QColor("#FF9800"))  # High - orange
                elif 70 <= m['glucose_level'] <= 110:
                    value_item.setForeground(QColor("#4CAF50"))  # Normal - green
                measurements_table.setItem(i, 2, value_item)
                
                period_map = {
                    'morning': 'Sabah',
                    'noon': 'Öğle',
                    'afternoon': 'İkindi',
                    'evening': 'Akşam',
                    'night': 'Gece'
                }
                measurements_table.setItem(i, 3, QTableWidgetItem(period_map.get(m['period'], m['period'])))
            
            measurements_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            measurements_layout.addWidget(measurements_table)
        else:
            no_data_label = QLabel("Henüz ölçüm kaydı bulunmamaktadır.")
            no_data_label.setAlignment(Qt.AlignCenter)
            no_data_label.setStyleSheet("color: #757575; padding: 20px;")
            measurements_layout.addWidget(no_data_label)
        
        # Alerts
        alerts = DoctorController.get_patient_alerts(patient.id, only_unread=True)
        
        alerts_group = QGroupBox("Aktif Uyarılar")
        alerts_layout = QVBoxLayout()
        alerts_group.setLayout(alerts_layout)
        
        if alerts:
            for alert in alerts:
                alert_widget = AlertWidget(alert)
                alert_widget.marked_as_read.connect(self.on_alert_read)
                alerts_layout.addWidget(alert_widget)
        else:
            no_alerts_label = QLabel("Aktif uyarı bulunmamaktadır.")
            no_alerts_label.setAlignment(Qt.AlignCenter)
            no_alerts_label.setStyleSheet("color: #757575; padding: 20px;")
            alerts_layout.addWidget(no_alerts_label)
        
        # Blood glucose chart
        glucose_chart = GlucoseChartWidget(patient_id)
        glucose_chart.setMinimumHeight(300)
        
        # Add components to summary tab
        summary_layout.addWidget(diagnosis_group)
        summary_layout.addWidget(measurements_group)
        summary_layout.addWidget(alerts_group)
        summary_layout.addWidget(glucose_chart)
        summary_layout.addStretch(1)
        
        # Measurements tab
        measurements_tab = QScrollArea()
        measurements_tab.setWidgetResizable(True)
        measurements_content = QWidget()
        measurements_layout = QVBoxLayout()
        measurements_content.setLayout(measurements_layout)
        measurements_tab.setWidget(measurements_content)
        
        # Date filter
        filter_group = QGroupBox("Filtreleme")
        filter_layout = QHBoxLayout()
        filter_group.setLayout(filter_layout)
        
        filter_layout.addWidget(QLabel("Başlangıç:"))
        start_date_edit = QDateEdit()
        start_date_edit.setCalendarPopup(True)
        start_date_edit.setDate(QDate.currentDate().addDays(-30))
        filter_layout.addWidget(start_date_edit)
        
        filter_layout.addWidget(QLabel("Bitiş:"))
        end_date_edit = QDateEdit()
        end_date_edit.setCalendarPopup(True)
        end_date_edit.setDate(QDate.currentDate())
        filter_layout.addWidget(end_date_edit)
        
        filter_layout.addWidget(QLabel("Min. Değer (mg/dL):"))
        min_value_spin = QSpinBox()
        min_value_spin.setRange(0, 1000)
        min_value_spin.setValue(0)
        min_value_spin.setFixedWidth(100)
        filter_layout.addWidget(min_value_spin)

        filter_layout.addWidget(QLabel("Maks. Değer (mg/dL):"))
        max_value_spin = QSpinBox()
        max_value_spin.setRange(0, 1000)
        max_value_spin.setValue(1000)
        max_value_spin.setFixedWidth(100)
        filter_layout.addWidget(max_value_spin)
        
        filter_button = QPushButton("Filtrele")
        filter_button.setStyleSheet("""
            QPushButton {
                background-color: #3949AB;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #303F9F;
            }
            QPushButton:pressed {
                background-color: #283593;
            }
        """)
        filter_layout.addWidget(filter_button)
        filter_layout.addStretch(1)
        
        # Measurement table
        measurements_full_table = QTableWidget()
        measurements_full_table.setColumnCount(5)
        measurements_full_table.setHorizontalHeaderLabels(["Tarih", "Saat", "Değer (mg/dL)", "Periyot", "Notlar"])
        
        # Add components to measurements tab
        measurements_layout.addWidget(filter_group)
        measurements_layout.addWidget(measurements_full_table)
        
        # Load measurements
        def load_filtered_measurements():
            start_date = start_date_edit.date().toPyDate()
            end_date = end_date_edit.date().toPyDate()
            min_value = min_value_spin.value()
            max_value = max_value_spin.value()
            filtered_measurements = DoctorController.get_patient_measurements(patient.id, start_date, end_date)
            # Kan şekeri aralığına göre filtrele
            filtered_measurements = [m for m in filtered_measurements if min_value <= m['glucose_level'] <= max_value]
            measurements_full_table.setRowCount(len(filtered_measurements))
            
            for i, m in enumerate(filtered_measurements):
                measurements_full_table.setItem(i, 0, QTableWidgetItem(DateUtils.format_date(m['measurement_date'])))
                measurements_full_table.setItem(i, 1, QTableWidgetItem(DateUtils.format_time(m['measurement_time'])))
                
                value_item = QTableWidgetItem(str(m['glucose_level']))
                # Color based on value
                if m['glucose_level'] < 70:
                    value_item.setForeground(QColor("#F44336"))  # Low - red
                elif m['glucose_level'] > 180:
                    value_item.setForeground(QColor("#FF9800"))  # High - orange
                elif 70 <= m['glucose_level'] <= 110:
                    value_item.setForeground(QColor("#4CAF50"))  # Normal - green
                measurements_full_table.setItem(i, 2, value_item)
                
                period_map = {
                    'morning': 'Sabah',
                    'noon': 'Öğle',
                    'afternoon': 'İkindi',
                    'evening': 'Akşam',
                    'night': 'Gece'
                }
                measurements_full_table.setItem(i, 3, QTableWidgetItem(period_map.get(m['period'], m['period'])))
                measurements_full_table.setItem(i, 4, QTableWidgetItem(m['notes'] or ""))
            
            measurements_full_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        filter_button.clicked.connect(load_filtered_measurements)
        load_filtered_measurements() 
        # ui/doctor_panel.py (continued)
        # Diet and Exercise tab
        diet_exercise_tab = QScrollArea()
        diet_exercise_tab.setWidgetResizable(True)
        diet_exercise_content = QWidget()
        diet_exercise_layout = QVBoxLayout()
        diet_exercise_content.setLayout(diet_exercise_layout)
        diet_exercise_tab.setWidget(diet_exercise_content)
        
        # Diet tracking
        diet_group = QGroupBox("Diyet Takibi")
        diet_layout = QVBoxLayout()
        diet_group.setLayout(diet_layout)
        
        # Diet compliance chart
        diet_chart_layout = QHBoxLayout()
        
        diet_compliance = DoctorController.get_diet_compliance(patient.id)
        
        diet_chart_figure = Figure(figsize=(4, 3), dpi=100)
        diet_chart_canvas = FigureCanvas(diet_chart_figure)
        diet_chart_layout.addWidget(diet_chart_canvas)
        
        def update_diet_chart():
            diet_chart_figure.clear()
            ax = diet_chart_figure.add_subplot(111)
            
            # Create gradient color based on compliance percentage
            if diet_compliance > 80:
                bar_color = '#4CAF50'  # Green
            elif diet_compliance > 50:
                bar_color = '#FFC107'  # Amber
            else:
                bar_color = '#F44336'  # Red
            
            ax.bar(['Diyet Uyumu'], [diet_compliance], color=bar_color, width=0.6)
            ax.set_ylim(0, 100)
            ax.set_ylabel('Uyum Yüzdesi (%)')
            ax.set_title('Diyet Takip Uyumu', fontweight='bold')
            
            # Add percentage value on the bar
            ax.text(0, diet_compliance + 2, f'%{diet_compliance:.1f}', ha='center', fontweight='bold')
            
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_color('#DDDDDD')
            ax.spines['left'].set_color('#DDDDDD')
            ax.tick_params(colors='#666666')
            
            diet_chart_figure.tight_layout()
            diet_chart_canvas.draw()
        
        update_diet_chart()
        
        # Diet type distribution chart
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        diets = DoctorController.get_patient_diets(patient.id, start_date, end_date)
        
        diet_types_chart_figure = Figure(figsize=(5, 3), dpi=100)
        diet_types_chart_canvas = FigureCanvas(diet_types_chart_figure)
        diet_chart_layout.addWidget(diet_types_chart_canvas)
        
        def update_diet_types_chart():
            diet_types_chart_figure.clear()
            ax = diet_types_chart_figure.add_subplot(111)
            
            if diets:
                # Count diet types
                diet_counts = {'low_sugar': 0, 'no_sugar': 0, 'balanced': 0}
                followed_counts = {'low_sugar': 0, 'no_sugar': 0, 'balanced': 0}
                
                for d in diets:
                    diet_type = d['diet_type']
                    if diet_type in diet_counts:
                        diet_counts[diet_type] += 1
                        if d['is_followed']:
                            followed_counts[diet_type] += 1
                
                # Prepare data for stacked bar chart
                labels = []
                followed = []
                not_followed = []
                
                for diet_type, count in diet_counts.items():
                    if count > 0:
                        diet_type_map = {
                            'low_sugar': 'Az Şekerli',
                            'no_sugar': 'Şekersiz',
                            'balanced': 'Dengeli'
                        }
                        labels.append(diet_type_map.get(diet_type, diet_type))
                        followed.append(followed_counts[diet_type])
                        not_followed.append(count - followed_counts[diet_type])
                
                # Create stacked bar chart
                bar_width = 0.5
                index = range(len(labels))
                
                ax.bar(index, followed, bar_width, label='Uygulandı', color='#4CAF50')
                ax.bar(index, not_followed, bar_width, bottom=followed, label='Uygulanmadı', color='#F44336')
                
                ax.set_ylabel('Gün Sayısı')
                ax.set_title('Diyet Türlerine Göre Dağılım', fontweight='bold')
                ax.set_xticks(index)
                ax.set_xticklabels(labels, rotation=0)
                ax.legend(loc='upper right', frameon=False)
                
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['bottom'].set_color('#DDDDDD')
                ax.spines['left'].set_color('#DDDDDD')
                ax.tick_params(colors='#666666')
            else:
                ax.text(0.5, 0.5, 'Veri bulunamadı', ha='center', va='center', fontsize=12)
                ax.set_xticks([])
                ax.set_yticks([])
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['bottom'].set_visible(False)
                ax.spines['left'].set_visible(False)
            
            diet_types_chart_figure.tight_layout()
            diet_types_chart_canvas.draw()
        
        update_diet_types_chart()
        
        # Diet table
        diet_table = QTableWidget()
        diet_table.setColumnCount(4)
        diet_table.setHorizontalHeaderLabels(["Tarih", "Diyet Türü", "Uygulama Durumu", "Notlar"])
        
        diet_table.setRowCount(len(diets))
        
        for i, d in enumerate(diets):
            diet_table.setItem(i, 0, QTableWidgetItem(DateUtils.format_date(d['date'])))
            
            diet_type_map = {
                'low_sugar': 'Az Şekerli Diyet',
                'no_sugar': 'Şekersiz Diyet',
                'balanced': 'Dengeli Beslenme'
            }
            diet_table.setItem(i, 1, QTableWidgetItem(diet_type_map.get(d['diet_type'], d['diet_type'])))
            
            status_item = QTableWidgetItem('Uygulandı' if d['is_followed'] else 'Uygulanmadı')
            if d['is_followed']:
                status_item.setForeground(QColor("#4CAF50"))  # Green
            else:
                status_item.setForeground(QColor("#F44336"))  # Red
            diet_table.setItem(i, 2, status_item)
            
            diet_table.setItem(i, 3, QTableWidgetItem(d['notes'] or ""))
        
        diet_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        diet_layout.addLayout(diet_chart_layout)
        diet_layout.addWidget(diet_table)
        
        # Exercise tracking
        exercise_group = QGroupBox("Egzersiz Takibi")
        exercise_layout = QVBoxLayout()
        exercise_group.setLayout(exercise_layout)
        
        # Exercise compliance chart
        exercise_chart_layout = QHBoxLayout()
        
        exercise_compliance = DoctorController.get_exercise_compliance(patient.id)
        
        exercise_chart_figure = Figure(figsize=(4, 3), dpi=100)
        exercise_chart_canvas = FigureCanvas(exercise_chart_figure)
        exercise_chart_layout.addWidget(exercise_chart_canvas)
        
        def update_exercise_chart():
            exercise_chart_figure.clear()
            ax = exercise_chart_figure.add_subplot(111)
            
            # Create gradient color based on compliance percentage
            if exercise_compliance > 80:
                bar_color = '#4CAF50'  # Green
            elif exercise_compliance > 50:
                bar_color = '#FFC107'  # Amber
            else:
                bar_color = '#F44336'  # Red
            
            ax.bar(['Egzersiz Uyumu'], [exercise_compliance], color=bar_color, width=0.6)
            ax.set_ylim(0, 100)
            ax.set_ylabel('Uyum Yüzdesi (%)')
            ax.set_title('Egzersiz Takip Uyumu', fontweight='bold')
            
            # Add percentage value on the bar
            ax.text(0, exercise_compliance + 2, f'%{exercise_compliance:.1f}', ha='center', fontweight='bold')
            
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_color('#DDDDDD')
            ax.spines['left'].set_color('#DDDDDD')
            ax.tick_params(colors='#666666')
            
            exercise_chart_figure.tight_layout()
            exercise_chart_canvas.draw()
        
        update_exercise_chart()
        
        # Exercise type distribution chart
        exercises = DoctorController.get_patient_exercises(patient.id, start_date, end_date)
        
        exercise_types_chart_figure = Figure(figsize=(5, 3), dpi=100)
        exercise_types_chart_canvas = FigureCanvas(exercise_types_chart_figure)
        exercise_chart_layout.addWidget(exercise_types_chart_canvas)
        
        def update_exercise_types_chart():
            exercise_types_chart_figure.clear()
            ax = exercise_types_chart_figure.add_subplot(111)
            
            if exercises:
                # Count exercise types
                exercise_counts = {'walking': 0, 'cycling': 0, 'clinical': 0}
                completed_counts = {'walking': 0, 'cycling': 0, 'clinical': 0}
                
                for e in exercises:
                    exercise_type = e['exercise_type']
                    if exercise_type in exercise_counts:
                        exercise_counts[exercise_type] += 1
                        if e['is_completed']:
                            completed_counts[exercise_type] += 1
                
                # Prepare data for stacked bar chart
                labels = []
                completed = []
                not_completed = []
                
                for exercise_type, count in exercise_counts.items():
                    if count > 0:
                        exercise_type_map = {
                            'walking': 'Yürüyüş',
                            'cycling': 'Bisiklet',
                            'clinical': 'Klinik'
                        }
                        labels.append(exercise_type_map.get(exercise_type, exercise_type))
                        completed.append(completed_counts[exercise_type])
                        not_completed.append(count - completed_counts[exercise_type])
                
                # Create stacked bar chart
                bar_width = 0.5
                index = range(len(labels))
                
                ax.bar(index, completed, bar_width, label='Tamamlandı', color='#4CAF50')
                ax.bar(index, not_completed, bar_width, bottom=completed, label='Tamamlanmadı', color='#F44336')
                
                ax.set_ylabel('Gün Sayısı')
                ax.set_title('Egzersiz Türlerine Göre Dağılım', fontweight='bold')
                ax.set_xticks(index)
                ax.set_xticklabels(labels, rotation=0)
                ax.legend(loc='upper right', frameon=False)
                
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['bottom'].set_color('#DDDDDD')
                ax.spines['left'].set_color('#DDDDDD')
                ax.tick_params(colors='#666666')
            else:
                ax.text(0.5, 0.5, 'Veri bulunamadı', ha='center', va='center', fontsize=12)
                ax.set_xticks([])
                ax.set_yticks([])
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['bottom'].set_visible(False)
                ax.spines['left'].set_visible(False)
            
            exercise_types_chart_figure.tight_layout()
            exercise_types_chart_canvas.draw()
        
        update_exercise_types_chart()
        
        # Exercise table
        exercise_table = QTableWidget()
        exercise_table.setColumnCount(4)
        exercise_table.setHorizontalHeaderLabels(["Tarih", "Egzersiz Türü", "Tamamlanma Durumu", "Notlar"])
        
        exercise_table.setRowCount(len(exercises))
        
        for i, e in enumerate(exercises):
            exercise_table.setItem(i, 0, QTableWidgetItem(DateUtils.format_date(e['date'])))
            
            exercise_type_map = {
                'walking': 'Yürüyüş',
                'cycling': 'Bisiklet',
                'clinical': 'Klinik Egzersiz'
            }
            exercise_table.setItem(i, 1, QTableWidgetItem(exercise_type_map.get(e['exercise_type'], e['exercise_type'])))
            
            status_item = QTableWidgetItem('Tamamlandı' if e['is_completed'] else 'Tamamlanmadı')
            if e['is_completed']:
                status_item.setForeground(QColor("#4CAF50"))  # Green
            else:
                status_item.setForeground(QColor("#F44336"))  # Red
            exercise_table.setItem(i, 2, status_item)
            
            exercise_table.setItem(i, 3, QTableWidgetItem(e['notes'] or ""))
        
        exercise_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        exercise_layout.addLayout(exercise_chart_layout)
        exercise_layout.addWidget(exercise_table)
        
        # Add components to Diet and Exercise tab
        diet_exercise_layout.addWidget(diet_group)
        diet_exercise_layout.addWidget(exercise_group)
        
        # Symptoms tab
        symptoms_tab = QScrollArea()
        symptoms_tab.setWidgetResizable(True)
        symptoms_content = QWidget()
        symptoms_layout = QVBoxLayout()
        symptoms_content.setLayout(symptoms_layout)
        symptoms_tab.setWidget(symptoms_content)
        
        # Symptom filter
        symptom_filter_group = QGroupBox("Filtreleme")
        symptom_filter_layout = QHBoxLayout()
        symptom_filter_group.setLayout(symptom_filter_layout)
        
        symptom_filter_layout.addWidget(QLabel("Belirti Türü:"))
        symptom_combo = QComboBox()
        symptom_combo.setMinimumWidth(200)
        symptom_combo.addItem("Tümü", "all")
        symptom_combo.addItem("Poliüri (Sık idrara çıkma)", "polyuria")
        symptom_combo.addItem("Polifaji (Aşırı açlık hissi)", "polyphagia")
        symptom_combo.addItem("Polidipsi (Aşırı susama hissi)", "polydipsia")
        symptom_combo.addItem("Nöropati (El/ayak karıncalanması)", "neuropathy")
        symptom_combo.addItem("Kilo kaybı", "weight_loss")
        symptom_combo.addItem("Yorgunluk", "fatigue")
        symptom_combo.addItem("Yaraların yavaş iyileşmesi", "slow_healing")
        symptom_combo.addItem("Bulanık görme", "blurred_vision")
        symptom_filter_layout.addWidget(symptom_combo)
        
        symptom_filter_layout.addWidget(QLabel("Başlangıç:"))
        symptom_start_date = QDateEdit()
        symptom_start_date.setCalendarPopup(True)
        symptom_start_date.setDate(QDate.currentDate().addDays(-30))
        symptom_filter_layout.addWidget(symptom_start_date)
        
        symptom_filter_layout.addWidget(QLabel("Bitiş:"))
        symptom_end_date = QDateEdit()
        symptom_end_date.setCalendarPopup(True)
        symptom_end_date.setDate(QDate.currentDate())
        symptom_filter_layout.addWidget(symptom_end_date)
        
        symptom_filter_button = QPushButton("Filtrele")
        symptom_filter_button.setStyleSheet("""
            QPushButton {
                background-color: #3949AB;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #303F9F;
            }
            QPushButton:pressed {
                background-color: #283593;
            }
        """)
        symptom_filter_layout.addWidget(symptom_filter_button)
        symptom_filter_layout.addStretch(1)
        
        # Symptoms chart
        symptoms_chart_figure = Figure(figsize=(10, 4), dpi=100)
        symptoms_chart_canvas = FigureCanvas(symptoms_chart_figure)
        
        # Symptoms table
        symptoms_table = QTableWidget()
        symptoms_table.setColumnCount(4)
        symptoms_table.setHorizontalHeaderLabels(["Tarih", "Belirti", "Şiddet", "Notlar"])
        
        # Load symptoms and update chart
        def load_filtered_symptoms():
            start = symptom_start_date.date().toPyDate()
            end = symptom_end_date.date().toPyDate()
            symptom_type = symptom_combo.currentData()
            
            if symptom_type == "all":
                filtered_symptoms = DoctorController.get_patient_symptoms(patient.id, start, end)
            else:
                filtered_symptoms = DoctorController.get_patient_symptoms(patient.id, symptom_type=symptom_type)
            
            # Update table
            symptoms_table.setRowCount(len(filtered_symptoms))
            
            for i, s in enumerate(filtered_symptoms):
                symptoms_table.setItem(i, 0, QTableWidgetItem(DateUtils.format_date(s['date'])))
                
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
                symptoms_table.setItem(i, 1, QTableWidgetItem(symptom_type_map.get(s['symptom_type'], s['symptom_type'])))
                
                severity = s['severity']
                severity_text = f"{severity}/5" if severity else "-"
                
                severity_item = QTableWidgetItem(severity_text)
                if severity and severity >= 4:
                    severity_item.setForeground(QColor("#F44336"))  # Red for high severity
                elif severity and severity >= 3:
                    severity_item.setForeground(QColor("#FF9800"))  # Orange for medium severity
                
                symptoms_table.setItem(i, 2, severity_item)
                symptoms_table.setItem(i, 3, QTableWidgetItem(s['notes'] or ""))
            
            symptoms_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            
            # Update chart
            symptoms_chart_figure.clear()
            
            # All symptoms for the selected date range
            all_symptoms = DoctorController.get_patient_symptoms(patient.id, start, end)
            
            # Group by symptom type
            symptom_counts = {}
            for s in all_symptoms:
                symptom_type = s['symptom_type']
                if symptom_type in symptom_counts:
                    symptom_counts[symptom_type] += 1
                else:
                    symptom_counts[symptom_type] = 1
            
            if symptom_counts:
                ax = symptoms_chart_figure.add_subplot(111)
                
                # Color mapping for symptoms
                colors = {
                    'polyuria': '#3949AB',
                    'polyphagia': '#43A047',
                    'polydipsia': '#FFA000',
                    'neuropathy': '#E53935',
                    'weight_loss': '#5E35B1',
                    'fatigue': '#00897B',
                    'slow_healing': '#F4511E',
                    'blurred_vision': '#6D4C41'
                }
                
                symptom_type_map = {
                    'polyuria': 'Poliüri',
                    'polyphagia': 'Polifaji',
                    'polydipsia': 'Polidipsi',
                    'neuropathy': 'Nöropati',
                    'weight_loss': 'Kilo kaybı',
                    'fatigue': 'Yorgunluk',
                    'slow_healing': 'Yavaş iyileşme',
                    'blurred_vision': 'Bulanık görme'
                }
                
                types = [symptom_type_map.get(s, s) for s in symptom_counts.keys()]
                counts = list(symptom_counts.values())
                bar_colors = [colors.get(s, '#757575') for s in symptom_counts.keys()]
                
                bars = ax.bar(types, counts, color=bar_colors, width=0.6)
                ax.set_ylabel('Sayı', fontsize=10)
                ax.set_title('Belirti Dağılımı', fontweight='bold', fontsize=12)
                
                # Add counts above bars
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                            f'{height:.0f}', ha='center', fontsize=9, fontweight='bold')
                
                # Rotate x labels
                plt.setp(ax.get_xticklabels(), rotation=45, ha='right', fontsize=9)
                
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['bottom'].set_color('#DDDDDD')
                ax.spines['left'].set_color('#DDDDDD')
                ax.tick_params(colors='#666666')
                
                ax.set_ylim(0, max(counts) + 1)  # Add some space above the bars
                
                symptoms_chart_figure.tight_layout()
            else:
                ax = symptoms_chart_figure.add_subplot(111)
                ax.text(0.5, 0.5, 'Veri bulunamadı', ha='center', va='center', fontsize=12)
                ax.set_xticks([])
                ax.set_yticks([])
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['bottom'].set_visible(False)
                ax.spines['left'].set_visible(False)
            
            symptoms_chart_canvas.draw()
        
        symptom_filter_button.clicked.connect(load_filtered_symptoms)
        
        # Add components to Symptoms tab
        symptoms_layout.addWidget(symptom_filter_group)
        symptoms_layout.addWidget(symptoms_chart_canvas)
        symptoms_layout.addWidget(symptoms_table)
        
        load_filtered_symptoms()  # Initial load
        
        # Alerts tab
        alerts_tab = QScrollArea()
        alerts_tab.setWidgetResizable(True)
        alerts_content = QWidget()
        alerts_layout = QVBoxLayout()
        alerts_content.setLayout(alerts_layout)
        alerts_tab.setWidget(alerts_content)
        
        # Alert filter
        alert_filter_group = QGroupBox("Filtreleme")
        alert_filter_layout = QHBoxLayout()
        alert_filter_group.setLayout(alert_filter_layout)
        
        alert_filter_layout.addWidget(QLabel("Uyarı Türü:"))
        alert_combo = QComboBox()
        alert_combo.setMinimumWidth(200)
        alert_combo.addItem("Tümü", "all")
        alert_combo.addItem("Hipoglisemi Riski", Alert.TYPE_HYPOGLYCEMIA)
        alert_combo.addItem("Normal Seviye", Alert.TYPE_NORMAL)
        alert_combo.addItem("Takip Uyarısı", Alert.TYPE_MEDIUM_HIGH)
        alert_combo.addItem("İzleme Uyarısı", Alert.TYPE_HIGH)
        alert_combo.addItem("Acil Müdahale Uyarısı", Alert.TYPE_HYPERGLYCEMIA)
        alert_combo.addItem("Ölçüm Eksik Uyarısı", Alert.TYPE_MISSING_MEASUREMENT)
        alert_combo.addItem("Ölçüm Yetersiz Uyarısı", Alert.TYPE_INSUFFICIENT_MEASUREMENT)
        alert_filter_layout.addWidget(alert_combo)
        
        alert_filter_layout.addWidget(QLabel("Başlangıç:"))
        alert_start_date = QDateEdit()
        alert_start_date.setCalendarPopup(True)
        alert_start_date.setDate(QDate.currentDate().addDays(-30))
        alert_filter_layout.addWidget(alert_start_date)
        
        alert_filter_layout.addWidget(QLabel("Bitiş:"))
        alert_end_date = QDateEdit()
        alert_end_date.setCalendarPopup(True)
        alert_end_date.setDate(QDate.currentDate())
        alert_filter_layout.addWidget(alert_end_date)
        
        alert_filter_layout.addWidget(QLabel("Durum:"))
        alert_status_combo = QComboBox()
        alert_status_combo.addItem("Tümü", "all")
        alert_status_combo.addItem("Okunmamış", "unread")
        alert_status_combo.addItem("Okunmuş", "read")
        alert_filter_layout.addWidget(alert_status_combo)
        
        alert_filter_button = QPushButton("Filtrele")
        alert_filter_button.setStyleSheet("""
            QPushButton {
                background-color: #3949AB;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #303F9F;
            }
            QPushButton:pressed {
                background-color: #283593;
            }
        """)
        alert_filter_layout.addWidget(alert_filter_button)
        alert_filter_layout.addStretch(1)
        
        # Alert list container
        alerts_scroll = QScrollArea()
        alerts_scroll.setWidgetResizable(True)
        alerts_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #E0E0E0;
                border-radius: 5px;
                background-color: white;
            }
        """)
        
        alerts_container = QWidget()
        alerts_container_layout = QVBoxLayout()
        alerts_container.setLayout(alerts_container_layout)
        
        alerts_scroll.setWidget(alerts_container)
        
        # Load alerts
        def load_filtered_alerts():
            start = alert_start_date.date().toPyDate()
            end = alert_end_date.date().toPyDate()
            alert_type = alert_combo.currentData()
            alert_status = alert_status_combo.currentData()
            
            # Clear existing alerts
            for i in reversed(range(alerts_container_layout.count())):
                widget = alerts_container_layout.itemAt(i).widget()
                if widget:
                    widget.deleteLater()
            
            # Get alerts based on status filter
            if alert_status == "unread":
                filtered_alerts = DoctorController.get_patient_alerts(patient.id, only_unread=True)
            else:
                if alert_type == "all":
                    filtered_alerts = DoctorController.get_patient_alerts(patient.id, start, end)
                else:
                    filtered_alerts = DoctorController.get_patient_alerts(patient.id, alert_type=alert_type)
            
            if filtered_alerts:
                for alert in filtered_alerts:
                    alert_widget = AlertWidget(alert)
                    alert_widget.setStyleSheet("""
                        border: 1px solid #E0E0E0;
                        border-radius: 5px;
                        margin-bottom: 8px;
                        background-color: #FAFAFA;
                    """)
                    alert_widget.marked_as_read.connect(self.on_alert_read)
                    alerts_container_layout.addWidget(alert_widget)
            else:
                no_alerts_label = QLabel("Uyarı bulunamadı.")
                no_alerts_label.setAlignment(Qt.AlignCenter)
                no_alerts_label.setStyleSheet("padding: 20px; color: #757575;")
                alerts_container_layout.addWidget(no_alerts_label)
            
            # Add spacer
            alerts_container_layout.addStretch(1)
        
        alert_filter_button.clicked.connect(load_filtered_alerts)
        
        # Add components to Alerts tab
        alerts_layout.addWidget(alert_filter_group)
        alerts_layout.addWidget(alerts_scroll)
        
        load_filtered_alerts()  # Initial load
        
        # Manuel Öneri tab
        manual_recommendation_tab = QWidget()
        manual_layout = QVBoxLayout()
        manual_recommendation_tab.setLayout(manual_layout)

        # Öneri ekleme formu (modern tasarım)
        form_card = QFrame()
        form_card.setStyleSheet("""
            QFrame {
        background: #FFFFFF;
        border-radius: 10px;
        border: 1px solid #E0E0E0;
        padding: 20px;
        margin: 10px 0;
    }
        """)
        form_card_layout = QVBoxLayout()
        form_card.setLayout(form_card_layout)
        # Başlık için kapsül/etiket görünümü
        form_title = QLabel("Yeni Manuel Öneri Ekle")
        form_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        form_title.setStyleSheet("""
         color: #3949AB;
          padding: 0 0 10px 0;
         border: none;
          background: transparent;
            """)
        form_title.setAlignment(Qt.AlignCenter)
        form_title.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        form_card_layout.insertWidget(0, form_title, alignment=Qt.AlignHCenter)
        # Tür
        type_label = QLabel("Öneri Türü")
        type_label.setStyleSheet("font-weight: 500; color: #3949AB; margin-bottom: 2px;")
        type_combo = QComboBox()
        type_combo.addItem("Diyet", "diet")
        type_combo.addItem("Egzersiz", "exercise")
        type_combo.addItem("İnsülin", "insulin")
        type_combo.addItem("Diğer", "other")
        type_combo.setStyleSheet("padding: 6px 10px; border-radius: 6px; border: 1px solid #C5CAE9; background: #F8F9FA; font-size: 13px;")
        form_card_layout.addWidget(type_label)
        form_card_layout.addWidget(type_combo)
        # İçerik
        content_label = QLabel("İçerik")
        content_label.setStyleSheet("font-weight: 500; color: #3949AB; margin-top: 10px; margin-bottom: 2px;")
        content_edit = QTextEdit()
        content_edit.setPlaceholderText("Öneri metni giriniz...")
        content_edit.setFixedHeight(110)
        content_edit.setReadOnly(False)
        content_edit.setEnabled(True)
        content_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        content_edit.setStyleSheet("""
            QTextEdit {
                padding: 5px;
                border-radius: 6px;
                border: 1.5px solid #C5CAE9;
                background: #fff;
                font-size: 15px;
                color: #222;
                line-height: 1.5;
            }
            QTextEdit:focus {
                border: 1.5px solid #3949AB;
                background: #fff;
            }
        """)
        form_card_layout.addWidget(content_label)
        form_card_layout.addWidget(content_edit)
        # Kaydet butonu
        add_button = QPushButton("Kaydet")
        add_button.setStyleSheet("""
            QPushButton {
                background-color: #3949AB;
                color: white;
                font-weight: bold;
                border-radius: 6px;
                padding: 8px 0;
                font-size: 15px;
                min-width: 120px;
                min-height: 38px;
                box-shadow: 0 2px 6px rgba(60,60,60,0.08);
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background-color: #303F9F;
            }
            QPushButton:pressed {
                background-color: #283593;
            }
        """)
        add_button.setFixedWidth(140)
        add_button.setFixedHeight(38)
        add_button.setCursor(Qt.PointingHandCursor)
        form_card_layout.addWidget(add_button, alignment=Qt.AlignRight | Qt.AlignVCenter)
        manual_layout.insertWidget(0, form_card)

        # Geçmiş öneriler tablosu
        table_group = QGroupBox("Geçmiş Manuel Öneriler")
        table_layout = QVBoxLayout()
        table_group.setLayout(table_layout)
        manual_table = QTableWidget()
        manual_table.setColumnCount(4)
        manual_table.setHorizontalHeaderLabels(["Tarih", "Tür", "İçerik", "Doktor"])
        table_layout.addWidget(manual_table)
        manual_layout.addWidget(table_group)

        def load_manual_recommendations():
            recommendations = DoctorController.get_manual_recommendations_by_patient(patient.id)
            manual_table.setRowCount(len(recommendations))
            for i, rec in enumerate(recommendations):
                manual_table.setItem(i, 0, QTableWidgetItem(rec.created_at.strftime("%Y-%m-%d %H:%M")))
                type_map = {"diet": "Diyet", "exercise": "Egzersiz", "insulin": "İnsülin", "other": "Diğer"}
                manual_table.setItem(i, 1, QTableWidgetItem(type_map.get(rec.recommendation_type, rec.recommendation_type)))
                manual_table.setItem(i, 2, QTableWidgetItem(rec.content))
                # Doktor adı için (gerekirse sorgu eklenebilir, burada sadece doktor_id gösteriyoruz)
                manual_table.setItem(i, 3, QTableWidgetItem(str(rec.doctor_id)))
            manual_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        def add_manual_recommendation():
            rec_type = type_combo.currentData()
            content = content_edit.toPlainText().strip()
            if not content:
                QMessageBox.warning(self, "Uyarı", "Öneri metni boş olamaz.")
                return
            DoctorController.add_manual_recommendation(self.doctor.id, patient.id, rec_type, content)
            content_edit.clear()
            load_manual_recommendations()
            QMessageBox.information(self, "Başarılı", "Manuel öneri kaydedildi.")

        add_button.clicked.connect(add_manual_recommendation)
        load_manual_recommendations()

        # Sekmeye ekle
        tabs.addTab(manual_recommendation_tab, "Manuel Öneri")
        
        # Add patient detail components
        self.patient_detail_layout.addWidget(header)
        
        # Add tabs
        tabs.addTab(summary_tab, "Özet")
        tabs.addTab(measurements_tab, "Ölçümler")
        tabs.addTab(diet_exercise_tab, "Diyet & Egzersiz")
        tabs.addTab(symptoms_tab, "Belirtiler")
        tabs.addTab(alerts_tab, "Uyarılar")
        
        # Sekme başlıklarını ortala
        tabs.tabBar().setStyleSheet(tabs.styleSheet())
        
        self.patient_detail_layout.addWidget(tabs)
    
    def edit_patient(self, patient):
        dialog = PatientFormDialog(self.doctor.id, patient)
        if dialog.exec_() == QDialog.Accepted:
            # Refresh patient details
            self.load_patient_details(patient.id)
            # Refresh patient list
            self.load_patients()
    
    def on_alert_read(self):
        # Seçili hastanın ID'sini kaydet
        current_item = self.patient_list.currentItem()
        selected_patient_id = current_item.data(Qt.UserRole) if current_item else None

        # Hasta listesini güncelle
        self.load_patients()

        # Seçili hastayı tekrar seç
        if selected_patient_id is not None:
            for i in range(self.patient_list.count()):
                item = self.patient_list.item(i)
                if item.data(Qt.UserRole) == selected_patient_id:
                    self.patient_list.setCurrentItem(item)
                    self.load_patient_details(selected_patient_id)
                    self.patient_detail_stack.setCurrentIndex(1)
                    break
        

        
