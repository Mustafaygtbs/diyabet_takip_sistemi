# ui/doctor_panel.py
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QTabWidget, QTableWidget,
                            QTableWidgetItem, QFrame, QSplitter, QComboBox,
                            QDateEdit, QMessageBox, QHeaderView, QMenu,
                            QAction, QStackedWidget, QFormLayout, QLineEdit,
                            QTextEdit, QRadioButton, QButtonGroup, QCheckBox,
                            QSpacerItem, QSizePolicy, QScrollArea, QListWidget,
                            QListWidgetItem, QGridLayout, QDialog, QFileDialog)
from PyQt5.QtGui import QIcon, QPixmap, QFont, QColor
from PyQt5.QtCore import Qt, QDate

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from models.doctor import Doctor
from models.patient import Patient
from models.measurement import Measurement
from models.exercise import Exercise
from models.diet import Diet
from models.symptom import Symptom
from models.alert import Alert

from controllers.doctor_controller import DoctorController
from controllers.alert_controller import AlertController

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
        self.initUI()
        self.load_patients()
    
    def initUI(self):
        # Ana pencere ayarları
        self.setWindowTitle(f"Diyabet Takip Sistemi - Dr. {self.doctor.name} {self.doctor.surname}")
        self.setMinimumSize(1200, 800)
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
        
        # Doktor bilgileri
        doctor_info = QWidget()
        doctor_info_layout = QHBoxLayout()
        doctor_info.setLayout(doctor_info_layout)
        
        # Profil resmi
        profile_pic = QLabel()
        if self.doctor.profile_image:
            pixmap = QPixmap()
            pixmap.loadFromData(self.doctor.profile_image)
            profile_pic.setPixmap(pixmap.scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            profile_pic.setText("🧑‍⚕️")
            profile_pic.setFont(QFont("Arial", 24))
        
        profile_pic.setAlignment(Qt.AlignCenter)
        profile_pic.setFixedSize(60, 60)
        profile_pic.setStyleSheet("background-color: white; border-radius: 30px;")
        
        # Doktor adı ve tipi
        doctor_name = QLabel(f"Dr. {self.doctor.name} {self.doctor.surname}")
        doctor_name.setFont(QFont("Arial", 14, QFont.Bold))
        
        doctor_specialty = QLabel(self.doctor.specialty or "Doktor")
        doctor_specialty.setFont(QFont("Arial", 12))
        
        doctor_text = QWidget()
        doctor_text_layout = QVBoxLayout()
        doctor_text.setLayout(doctor_text_layout)
        doctor_text_layout.addWidget(doctor_name)
        doctor_text_layout.addWidget(doctor_specialty)
        
        doctor_info_layout.addWidget(profile_pic)
        doctor_info_layout.addWidget(doctor_text)
        
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
        top_layout.addWidget(doctor_info)
        top_layout.addStretch(1)
        top_layout.addWidget(logout_button)
        
        # Ana bölüm - Hasta listesi ve detayları
        main_section = QSplitter(Qt.Horizontal)
        
        # Sol panel - Hasta listesi ve ekleme düğmesi
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)
        
        patients_label = QLabel("Hastalarım")
        patients_label.setFont(QFont("Arial", 14, QFont.Bold))
        
        # Hasta ekleme düğmesi
        add_patient_button = QPushButton("Yeni Hasta Ekle")
        add_patient_button.setIcon(QIcon("resources/icons/add_patient.png"))
        add_patient_button.setStyleSheet("""
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
        add_patient_button.clicked.connect(self.open_patient_form)
        
        patient_buttons = QHBoxLayout()
        patient_buttons.addWidget(patients_label)
        patient_buttons.addStretch(1)
        patient_buttons.addWidget(add_patient_button)
        
        # Hasta listesi
        self.patient_list = QListWidget()
        self.patient_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #ecf0f1;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #ecf0f1;
            }
        """)
        self.patient_list.currentItemChanged.connect(self.on_patient_selected)
        
        # Arama kutusu
        search_layout = QHBoxLayout()
        search_label = QLabel("Ara:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("İsim, TC Kimlik veya teşhis ara...")
        self.search_input.textChanged.connect(self.filter_patients)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        
        left_layout.addLayout(patient_buttons)
        left_layout.addLayout(search_layout)
        left_layout.addWidget(self.patient_list)
        
        # Sağ panel - Hasta detayları
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_panel.setLayout(right_layout)
        
        # Hasta detay sayfaları
        self.patient_detail_stack = QStackedWidget()
        
        # Hasta seçilmediğinde gösterilecek sayfa
        no_patient_page = QWidget()
        no_patient_layout = QVBoxLayout()
        no_patient_page.setLayout(no_patient_layout)
        
        no_patient_label = QLabel("Hasta seçilmedi")
        no_patient_label.setFont(QFont("Arial", 16))
        no_patient_label.setAlignment(Qt.AlignCenter)
        
        no_patient_info = QLabel("Lütfen hasta listesinden bir hasta seçin veya yeni hasta ekleyin.")
        no_patient_info.setAlignment(Qt.AlignCenter)
        
        no_patient_layout.addStretch(1)
        no_patient_layout.addWidget(no_patient_label)
        no_patient_layout.addWidget(no_patient_info)
        no_patient_layout.addStretch(1)
        
        self.patient_detail_stack.addWidget(no_patient_page)
        
        # Hasta detay sayfası (hasta seçildiğinde bu sayfa doldurulacak)
        self.patient_detail_page = QWidget()
        self.patient_detail_layout = QVBoxLayout()
        self.patient_detail_page.setLayout(self.patient_detail_layout)
        
        self.patient_detail_stack.addWidget(self.patient_detail_page)
        
        right_layout.addWidget(self.patient_detail_stack)
        
        # Ana bölüme panelleri ekle
        main_section.addWidget(left_panel)
        main_section.addWidget(right_panel)
        main_section.setSizes([300, 900])  # Başlangıç genişlikleri
        
        # Ana layout'a bileşenleri ekle
        main_layout.addWidget(top_panel)
        main_layout.addWidget(main_section, 1)
        
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
    
    def load_patients(self):
        """Doktorun hastalarını yükler."""
        self.patient_list.clear()
        
        patients = DoctorController.get_doctor_patients(self.doctor.id)
        
        for patient in patients:
            item = QListWidgetItem(f"{patient.name} {patient.surname}")
            item.setData(Qt.UserRole, patient.id)
            
            # Eğer okunmamış uyarı varsa hastayı vurgula
            unread_alerts = DoctorController.get_patient_alerts(patient.id, only_unread=True)
            if unread_alerts:
                item.setForeground(QColor("#e74c3c"))  # Kırmızı renk
                item.setText(f"{patient.name} {patient.surname} ({len(unread_alerts)})")
            
            self.patient_list.addItem(item)
    
    def filter_patients(self):
        """Hasta listesini filtrelemek için kullanılır."""
        search_text = self.search_input.text().lower()
        
        for i in range(self.patient_list.count()):
            item = self.patient_list.item(i)
            patient_id = item.data(Qt.UserRole)
            patient = PatientController.get_patient_by_id(patient_id)
            
            # İsim, TC Kimlik veya teşhise göre ara
            if (search_text in f"{patient.name} {patient.surname}".lower() or
                search_text in patient.tc_id.lower() or
                (patient.diagnosis and search_text in patient.diagnosis.lower())):
                item.setHidden(False)
            else:
                item.setHidden(True)
    
    def open_patient_form(self):
        """Yeni hasta ekleme formunu açar."""
        dialog = PatientFormDialog(self.doctor.id)
        if dialog.exec_() == QDialog.Accepted:
            # Hasta listesini yenile
            self.load_patients()
    
    def on_patient_selected(self, current, previous):
        """Hasta seçildiğinde detay sayfasını günceller."""
        if not current:
            self.patient_detail_stack.setCurrentIndex(0)  # Hasta seçilmedi sayfası
            return
        
        patient_id = current.data(Qt.UserRole)
        self.load_patient_details(patient_id)
        self.patient_detail_stack.setCurrentIndex(1)  # Hasta detay sayfası
    
    def load_patient_details(self, patient_id):
        """Seçilen hastanın detaylarını yükler."""
        # Mevcut içeriği temizle
        for i in reversed(range(self.patient_detail_layout.count())):
            widget = self.patient_detail_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # Hastayı yükle
        patient = PatientController.get_patient_by_id(patient_id)
        
        if not patient:
            QMessageBox.warning(self, "Hata", "Hasta bulunamadı.")
            return
        
        # Hasta başlık bilgileri
        header = QWidget()
        header_layout = QHBoxLayout()
        header.setLayout(header_layout)
        
        patient_name = QLabel(f"<h2>{patient.name} {patient.surname}</h2>")
        
        patient_info = QLabel(f"TC: {patient.tc_id} | Doğum: {DateUtils.format_date(patient.birthdate)} | Cinsiyet: {'Erkek' if patient.gender == 'E' else 'Kadın'}")
        
        patient_header = QWidget()
        patient_header_layout = QVBoxLayout()
        patient_header.setLayout(patient_header_layout)
        patient_header_layout.addWidget(patient_name)
        patient_header_layout.addWidget(patient_info)
        
        edit_button = QPushButton("Düzenle")
        edit_button.setIcon(QIcon("resources/icons/edit.png"))
        edit_button.clicked.connect(lambda: self.edit_patient(patient))
        
        header_layout.addWidget(patient_header)
        header_layout.addStretch(1)
        header_layout.addWidget(edit_button)
        
        # Sekme widget'ı
        tabs = QTabWidget()
        
        # Özet sekmesi
        summary_tab = QWidget()
        summary_layout = QVBoxLayout()
        summary_tab.setLayout(summary_layout)
        
        # Teşhis bilgileri
        diagnosis_group = QGroupBox("Teşhis Bilgileri")
        diagnosis_layout = QFormLayout()
        diagnosis_group.setLayout(diagnosis_layout)
        
        diagnosis_type = QLabel(patient.diabetes_type or "-")
        diagnosis_date = QLabel(DateUtils.format_date(patient.diagnosis_date) or "-")
        diagnosis_text = QLabel(patient.diagnosis or "-")
        diagnosis_text.setWordWrap(True)
        
        diagnosis_layout.addRow("Diyabet Türü:", diagnosis_type)
        diagnosis_layout.addRow("Teşhis Tarihi:", diagnosis_date)
        diagnosis_layout.addRow("Teşhis Detayı:", diagnosis_text)
        
        # Son ölçümler
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
                # Değere göre renklendirme
                if m['glucose_level'] < 70:
                    value_item.setForeground(QColor("#e74c3c"))  # Düşük - kırmızı
                elif m['glucose_level'] > 180:
                    value_item.setForeground(QColor("#e67e22"))  # Yüksek - turuncu
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
            measurements_layout.addWidget(QLabel("Henüz ölçüm kaydı bulunmamaktadır."))
        
        # Uyarılar
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
            alerts_layout.addWidget(QLabel("Aktif uyarı bulunmamaktadır."))
        
        # Kan şekeri grafiği
        glucose_chart = GlucoseChartWidget(patient_id)
        
        # Özet sekmesine bileşenleri ekle
        summary_layout.addWidget(diagnosis_group)
        summary_layout.addWidget(measurements_group)
        summary_layout.addWidget(alerts_group)
        summary_layout.addWidget(glucose_chart)
        
        # Ölçümler sekmesi
        measurements_tab = QWidget()
        measurements_layout = QVBoxLayout()
        measurements_tab.setLayout(measurements_layout)
        
        # Tarih filtresi
        filter_widget = QWidget()
        filter_layout = QHBoxLayout()
        filter_widget.setLayout(filter_layout)
        
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
        
        filter_button = QPushButton("Filtrele")
        filter_layout.addWidget(filter_button)
        
        # Ölçüm tablosu
        measurements_full_table = QTableWidget()
        measurements_full_table.setColumnCount(5)
        measurements_full_table.setHorizontalHeaderLabels(["Tarih", "Saat", "Değer (mg/dL)", "Periyot", "Notlar"])
        
        # Ölçümler sekmesine bileşenleri ekle
        measurements_layout.addWidget(filter_widget)
        measurements_layout.addWidget(measurements_full_table)
        
        # Ölçümleri yükle
        def load_filtered_measurements():
            start_date = start_date_edit.date().toPyDate()
            end_date = end_date_edit.date().toPyDate()
            
            filtered_measurements = DoctorController.get_patient_measurements(patient.id, start_date, end_date)
            
            measurements_full_table.setRowCount(len(filtered_measurements))
            
            for i, m in enumerate(filtered_measurements):
                measurements_full_table.setItem(i, 0, QTableWidgetItem(DateUtils.format_date(m['measurement_date'])))
                measurements_full_table.setItem(i, 1, QTableWidgetItem(DateUtils.format_time(m['measurement_time'])))
                
                value_item = QTableWidgetItem(str(m['glucose_level']))
                # Değere göre renklendirme
                if m['glucose_level'] < 70:
                    value_item.setForeground(QColor("#e74c3c"))  # Düşük - kırmızı
                elif m['glucose_level'] > 180:
                    value_item.setForeground(QColor("#e67e22"))  # Yüksek - turuncu
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
        load_filtered_measurements()  # İlk yükleme
        
        # Diyet ve Egzersiz sekmesi
        diet_exercise_tab = QWidget()
        diet_exercise_layout = QVBoxLayout()
        diet_exercise_tab.setLayout(diet_exercise_layout)
        
        # Diyet takibi
        diet_group = QGroupBox("Diyet Takibi")
        diet_layout = QVBoxLayout()
        diet_group.setLayout(diet_layout)
        
        # Diyet uyum grafiği
        diet_chart_layout = QHBoxLayout()
        
        diet_chart_widget = QWidget()
        diet_chart_widget.setMinimumHeight(200)
        diet_chart_layout.addWidget(diet_chart_widget)
        
        # Diyet tipine göre uyum yüzdeleri
        diet_compliance = DoctorController.get_diet_compliance(patient.id)
        
        diet_chart_figure = Figure(figsize=(5, 3))
        diet_chart_canvas = FigureCanvas(diet_chart_figure)
        diet_chart_layout.addWidget(diet_chart_canvas)
        
        def update_diet_chart():
            diet_chart_figure.clear()
            ax = diet_chart_figure.add_subplot(111)
            
            ax.bar(['Diyet Uyumu'], [diet_compliance], color='#3498db')
            ax.set_ylim(0, 100)
            ax.set_ylabel('Uyum Yüzdesi (%)')
            ax.set_title('Diyet Takip Uyumu')
            
            # Yüzde değerini grafik üzerine ekle
            ax.text(0, diet_compliance + 5, f'%{diet_compliance:.1f}', ha='center')
            
            diet_chart_figure.tight_layout()
            diet_chart_canvas.draw()
        
        update_diet_chart()
        
        # Diyet tablosu
        diet_table = QTableWidget()
        diet_table.setColumnCount(4)
        diet_table.setHorizontalHeaderLabels(["Tarih", "Diyet Türü", "Uygulama Durumu", "Notlar"])
        
        # Son 30 günlük diyet verilerini getir
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        diets = DoctorController.get_patient_diets(patient.id, start_date, end_date)
        
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
                status_item.setForeground(QColor("#2ecc71"))  # Yeşil
            else:
                status_item.setForeground(QColor("#e74c3c"))  # Kırmızı
            diet_table.setItem(i, 2, status_item)
            
            diet_table.setItem(i, 3, QTableWidgetItem(d['notes'] or ""))
        
        diet_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        diet_layout.addLayout(diet_chart_layout)
        diet_layout.addWidget(diet_table)
        
        # Egzersiz takibi
        exercise_group = QGroupBox("Egzersiz Takibi")
        exercise_layout = QVBoxLayout()
        exercise_group.setLayout(exercise_layout)
        
        # Egzersiz uyum grafiği
        exercise_chart_layout = QHBoxLayout()
        
        exercise_chart_widget = QWidget()
        exercise_chart_widget.setMinimumHeight(200)
        exercise_chart_layout.addWidget(exercise_chart_widget)
        
        # Egzersiz tipine göre uyum yüzdeleri
        exercise_compliance = DoctorController.get_exercise_compliance(patient.id)
        
        exercise_chart_figure = Figure(figsize=(5, 3))
        exercise_chart_canvas = FigureCanvas(exercise_chart_figure)
        exercise_chart_layout.addWidget(exercise_chart_canvas)
        
        def update_exercise_chart():
            exercise_chart_figure.clear()
            ax = exercise_chart_figure.add_subplot(111)
            
            ax.bar(['Egzersiz Uyumu'], [exercise_compliance], color='#2ecc71')
            ax.set_ylim(0, 100)
            ax.set_ylabel('Uyum Yüzdesi (%)')
            ax.set_title('Egzersiz Takip Uyumu')
            
            # Yüzde değerini grafik üzerine ekle
            ax.text(0, exercise_compliance + 5, f'%{exercise_compliance:.1f}', ha='center')
            
            exercise_chart_figure.tight_layout()
            exercise_chart_canvas.draw()
        
        update_exercise_chart()
        
        # Egzersiz tablosu
        exercise_table = QTableWidget()
        exercise_table.setColumnCount(4)
        exercise_table.setHorizontalHeaderLabels(["Tarih", "Egzersiz Türü", "Tamamlanma Durumu", "Notlar"])
        
        # Son 30 günlük egzersiz verilerini getir
        exercises = DoctorController.get_patient_exercises(patient.id, start_date, end_date)
        
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
                status_item.setForeground(QColor("#2ecc71"))  # Yeşil
            else:
                status_item.setForeground(QColor("#e74c3c"))  # Kırmızı
            exercise_table.setItem(i, 2, status_item)
            
            exercise_table.setItem(i, 3, QTableWidgetItem(e['notes'] or ""))
        
        exercise_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        exercise_layout.addLayout(exercise_chart_layout)
        exercise_layout.addWidget(exercise_table)
        
        # Diyet ve Egzersiz sekmesine bileşenleri ekle
        diet_exercise_layout.addWidget(diet_group)
        diet_exercise_layout.addWidget(exercise_group)
        
        # Belirtiler sekmesi
        symptoms_tab = QWidget()
        symptoms_layout = QVBoxLayout()
        symptoms_tab.setLayout(symptoms_layout)
        
        # Belirti filtresi
        symptom_filter_widget = QWidget()
        symptom_filter_layout = QHBoxLayout()
        symptom_filter_widget.setLayout(symptom_filter_layout)
        
        symptom_filter_layout.addWidget(QLabel("Belirti Türü:"))
        symptom_combo = QComboBox()
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
        symptom_filter_layout.addWidget(symptom_filter_button)
        
        # Belirti tablosu
        symptoms_table = QTableWidget()
        symptoms_table.setColumnCount(4)
        symptoms_table.setHorizontalHeaderLabels(["Tarih", "Belirti", "Şiddet", "Notlar"])
        
        # Belirtileri yükle
        def load_filtered_symptoms():
            start = symptom_start_date.date().toPyDate()
            end = symptom_end_date.date().toPyDate()
            symptom_type = symptom_combo.currentData()
            
            if symptom_type == "all":
                filtered_symptoms = DoctorController.get_patient_symptoms(patient.id, start, end)
            else:
                filtered_symptoms = DoctorController.get_patient_symptoms(patient.id, symptom_type=symptom_type)
            
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
                symptoms_table.setItem(i, 2, QTableWidgetItem(severity_text))
                
                symptoms_table.setItem(i, 3, QTableWidgetItem(s['notes'] or ""))
            
            symptoms_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        symptom_filter_button.clicked.connect(load_filtered_symptoms)
        
        # Belirtileri grafiksel olarak göster
        symptoms_chart_widget = QWidget()
        symptoms_chart_widget.setMinimumHeight(300)
        
        symptoms_chart_figure = Figure(figsize=(6, 4))
        symptoms_chart_canvas = FigureCanvas(symptoms_chart_figure)
        
        def update_symptoms_chart():
            start = symptom_start_date.date().toPyDate()
            end = symptom_end_date.date().toPyDate()
            
            # Tüm belirti türlerini al
            all_symptoms = DoctorController.get_patient_symptoms(patient.id, start, end)
            
            # Belirti türlerine göre grupla
            symptom_counts = {}
            for s in all_symptoms:
                symptom_type = s['symptom_type']
                if symptom_type in symptom_counts:
                    symptom_counts[symptom_type] += 1
                else:
                    symptom_counts[symptom_type] = 1
            
            if not symptom_counts:
                symptoms_chart_figure.clear()
                ax = symptoms_chart_figure.add_subplot(111)
                ax.text(0.5, 0.5, 'Belirti kaydı bulunmamaktadır', ha='center', va='center')
                symptoms_chart_figure.tight_layout()
                symptoms_chart_canvas.draw()
                return
            
            # Grafiği oluştur
            symptoms_chart_figure.clear()
            ax = symptoms_chart_figure.add_subplot(111)
            
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
            
            ax.bar(types, counts, color='#9b59b6')
            ax.set_ylabel('Sayı')
            ax.set_title('Belirti Dağılımı')
            
            # X eksenindeki yazıları döndür
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
            
            symptoms_chart_figure.tight_layout()
            symptoms_chart_canvas.draw()
        
        symptom_filter_button.clicked.connect(update_symptoms_chart)
        
        # Belirtiler sekmesine bileşenleri ekle
        symptoms_layout.addWidget(symptom_filter_widget)
        symptoms_layout.addWidget(symptoms_chart_canvas)
        symptoms_layout.addWidget(symptoms_table)
        
        load_filtered_symptoms()  # İlk yükleme
        update_symptoms_chart()   # İlk grafiği çiz
        
        # Uyarılar sekmesi
        alerts_tab = QWidget()
        alerts_layout = QVBoxLayout()
        alerts_tab.setLayout(alerts_layout)
        
        # Uyarı filtresi
        alert_filter_widget = QWidget()
        alert_filter_layout = QHBoxLayout()
        alert_filter_widget.setLayout(alert_filter_layout)
        
        alert_filter_layout.addWidget(QLabel("Uyarı Türü:"))
        alert_combo = QComboBox()
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
        alert_filter_layout.addWidget(alert_filter_button)
        
        # Uyarı listesi (özel widget'lar kullanarak)
        alerts_scroll = QScrollArea()
        alerts_scroll.setWidgetResizable(True)
        
        alerts_container = QWidget()
        alerts_container_layout = QVBoxLayout()
        alerts_container.setLayout(alerts_container_layout)
        
        alerts_scroll.setWidget(alerts_container)
        
        # Uyarıları yükle
        def load_filtered_alerts():
            start = alert_start_date.date().toPyDate()
            end = alert_end_date.date().toPyDate()
            alert_type = alert_combo.currentData()
            alert_status = alert_status_combo.currentData()
            
            # Mevcut uyarıları temizle
            for i in reversed(range(alerts_container_layout.count())):
                widget = alerts_container_layout.itemAt(i).widget()
                if widget:
                    widget.deleteLater()
            
            # Durum filtresine göre uyarıları getir
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
                    alert_widget.marked_as_read.connect(self.on_alert_read)
                    alerts_container_layout.addWidget(alert_widget)
            else:
                no_alerts_label = QLabel("Uyarı bulunamadı.")
                no_alerts_label.setAlignment(Qt.AlignCenter)
                alerts_container_layout.addWidget(no_alerts_label)
            
            # Boşluk ekle
            alerts_container_layout.addStretch(1)
        
        alert_filter_button.clicked.connect(load_filtered_alerts)
        
        # Uyarılar sekmesine bileşenleri ekle
        alerts_layout.addWidget(alert_filter_widget)
        alerts_layout.addWidget(alerts_scroll)
        
        load_filtered_alerts()  # İlk yükleme
        
        # Hasta detay sayfasına bileşenleri ekle
        self.patient_detail_layout.addWidget(header)
        
        # Sekmeleri ekle
        tabs.addTab(summary_tab, "Özet")
        tabs.addTab(measurements_tab, "Ölçümler")
        tabs.addTab(diet_exercise_tab, "Diyet ve Egzersiz")
        tabs.addTab(symptoms_tab, "Belirtiler")
        tabs.addTab(alerts_tab, "Uyarılar")
        
        self.patient_detail_layout.addWidget(tabs)
    
    def edit_patient(self, patient):
        """Hastayı düzenlemek için form açar."""
        dialog = PatientFormDialog(self.doctor.id, patient)
        if dialog.exec_() == QDialog.Accepted:
            # Hasta detaylarını yenile
            self.load_patient_details(patient.id)
            # Hasta listesini yenile
            self.load_patients()
    
    def on_alert_read(self):
        """Uyarı okundu olarak işaretlendiğinde çağrılır."""
        # Hasta listesini yenile
        self.load_patients()
