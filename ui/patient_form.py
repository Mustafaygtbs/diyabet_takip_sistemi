# ui/patient_form.py
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit, 
                            QDateEdit, QComboBox, QTextEdit, QPushButton,
                            QLabel, QMessageBox, QFileDialog, QHBoxLayout,
                            QGroupBox)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QDate, QBuffer, QIODevice

from controllers.doctor_controller import DoctorController
from utils.validators import Validators
from utils.date_utils import DateUtils

from datetime import datetime
import os

class PatientFormDialog(QDialog):
    def __init__(self, doctor_id, patient=None):
        super().__init__()
        self.doctor_id = doctor_id
        self.patient = patient  # Düzenleme modunda hasta nesnesi
        self.edit_mode = patient is not None
        self.profile_image_data = patient.profile_image if self.edit_mode else None
        
        self.initUI()
        
        if self.edit_mode:
            self.fill_form()
    
    def initUI(self):
        # Dialog ayarları
        title = "Hasta Düzenle" if self.edit_mode else "Yeni Hasta Ekle"
        self.setWindowTitle(title)
        self.setMinimumWidth(500)
        
        # Ana layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Kişisel bilgiler grubu
        personal_group = QGroupBox("Kişisel Bilgiler")
        personal_layout = QFormLayout()
        personal_group.setLayout(personal_layout)
        
        # TC Kimlik
        self.tc_input = QLineEdit()
        self.tc_input.setMaxLength(11)
        self.tc_input.setPlaceholderText("11 haneli TC Kimlik No")
        personal_layout.addRow("TC Kimlik No:", self.tc_input)
        
        # Ad
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Hastanın adı")
        personal_layout.addRow("Ad:", self.name_input)
        
        # Soyad
        self.surname_input = QLineEdit()
        self.surname_input.setPlaceholderText("Hastanın soyadı")
        personal_layout.addRow("Soyad:", self.surname_input)
        
        # Doğum tarihi
        self.birthdate_input = QDateEdit()
        self.birthdate_input.setCalendarPopup(True)
        self.birthdate_input.setDate(QDate.currentDate().addYears(-30))
        personal_layout.addRow("Doğum Tarihi:", self.birthdate_input)
        
        # Cinsiyet
        self.gender_input = QComboBox()
        self.gender_input.addItem("Erkek", "E")
        self.gender_input.addItem("Kadın", "K")
        personal_layout.addRow("Cinsiyet:", self.gender_input)
        
        # E-posta
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("ornek@email.com")
        personal_layout.addRow("E-posta:", self.email_input)
        
        # Profil resmi
        self.image_layout = QHBoxLayout()
        
        self.image_label = QLabel()
        self.image_label.setFixedSize(100, 100)
        self.image_label.setStyleSheet("border: 1px solid #ccc; background-color: #f9f9f9;")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setText("Resim yok")
        
        self.select_image_button = QPushButton("Resim Seç")
        self.select_image_button.clicked.connect(self.select_image)
        
        self.image_layout.addWidget(self.image_label)
        self.image_layout.addWidget(self.select_image_button)
        self.image_layout.addStretch(1)
        
        personal_layout.addRow("Profil Resmi:", self.image_layout)
        
        # Tıbbi bilgiler grubu
        medical_group = QGroupBox("Tıbbi Bilgiler")
        medical_layout = QFormLayout()
        medical_group.setLayout(medical_layout)
        
        # Diyabet türü
        self.diabetes_type_input = QComboBox()
        self.diabetes_type_input.addItem("Tip 1 Diyabet", "Tip 1")
        self.diabetes_type_input.addItem("Tip 2 Diyabet", "Tip 2")
        self.diabetes_type_input.addItem("Gestasyonel Diyabet", "Gestasyonel")
        self.diabetes_type_input.addItem("Diğer", "Diğer")
        medical_layout.addRow("Diyabet Türü:", self.diabetes_type_input)
        
        # Teşhis tarihi
        self.diagnosis_date_input = QDateEdit()
        self.diagnosis_date_input.setCalendarPopup(True)
        self.diagnosis_date_input.setDate(QDate.currentDate())
        medical_layout.addRow("Teşhis Tarihi:", self.diagnosis_date_input)
        
        # Teşhis detayı
        self.diagnosis_input = QTextEdit()
        self.diagnosis_input.setPlaceholderText("Teşhis ve tedavi detayları")
        self.diagnosis_input.setMaximumHeight(100)
        medical_layout.addRow("Teşhis Detayı:", self.diagnosis_input)
        
        # Butonlar
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Kaydet")
        self.save_button.setStyleSheet("""
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
        self.save_button.clicked.connect(self.save_patient)
        
        self.cancel_button = QPushButton("İptal")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)
        
        # Ana layout'a bileşenleri ekle
        layout.addWidget(personal_group)
        layout.addWidget(medical_group)
        layout.addLayout(button_layout)
    
    def fill_form(self):
        """Düzenleme modunda form alanlarını doldurur."""
        self.tc_input.setText(self.patient.tc_id)
        self.tc_input.setReadOnly(True)  # TC değiştirilemez
        
        self.name_input.setText(self.patient.name)
        self.surname_input.setText(self.patient.surname)
        
        if self.patient.birthdate:
            self.birthdate_input.setDate(QDate(
                self.patient.birthdate.year,
                self.patient.birthdate.month,
                self.patient.birthdate.day
            ))
        
        gender_index = 0 if self.patient.gender == 'E' else 1
        self.gender_input.setCurrentIndex(gender_index)
        
        self.email_input.setText(self.patient.email)
        
        if self.patient.profile_image:
            pixmap = QPixmap()
            pixmap.loadFromData(self.patient.profile_image)
            self.image_label.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.image_label.setText("")
        
        # Diyabet türü
        if self.patient.diabetes_type:
            index = self.diabetes_type_input.findData(self.patient.diabetes_type)
            if index >= 0:
                self.diabetes_type_input.setCurrentIndex(index)
        
        # Teşhis tarihi
        if self.patient.diagnosis_date:
            self.diagnosis_date_input.setDate(QDate(
                self.patient.diagnosis_date.year,
                self.patient.diagnosis_date.month,
                self.patient.diagnosis_date.day
            ))
        
        # Teşhis detayı
        if self.patient.diagnosis:
            self.diagnosis_input.setText(self.patient.diagnosis)
    
    def select_image(self):
        """Profil resmi seçme işlemini gerçekleştirir."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Profil Resmi Seç", "", "Resim Dosyaları (*.png *.jpg *.jpeg *.bmp)"
        )
        
        if file_path:
            # Resmi yükle ve göster
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                # Resmi binary veriye dönüştür
                image = QImage(file_path)
                buffer = QBuffer()
                buffer.open(QIODevice.WriteOnly)
                image.save(buffer, "PNG")
                self.profile_image_data = buffer.data()
                
                # Resmi göster
                self.image_label.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                self.image_label.setText("")
    
    def save_patient(self):
        """Hasta bilgilerini kaydeder."""
        # Form verilerini al
        tc_id = self.tc_input.text()
        name = self.name_input.text()
        surname = self.surname_input.text()
        birthdate = self.birthdate_input.date().toPyDate()
        gender = self.gender_input.currentData()
        email = self.email_input.text()
        
        diabetes_type = self.diabetes_type_input.currentData()
        diagnosis_date = self.diagnosis_date_input.date().toPyDate()
        diagnosis = self.diagnosis_input.toPlainText()
        
        # Doğrulama
        if not tc_id or not name or not surname or not email:
            QMessageBox.warning(self, "Hata", "TC Kimlik, Ad, Soyad ve E-posta alanları boş bırakılamaz.")
            return
        
        if not Validators.validate_tc_id(tc_id):
            QMessageBox.warning(self, "Hata", "Geçerli bir TC Kimlik Numarası giriniz.")
            return
        
        if not Validators.validate_email(email):
            QMessageBox.warning(self, "Hata", "Geçerli bir e-posta adresi giriniz.")
            return
        
        try:
            if self.edit_mode:
                # Hastayı güncelle
                # Not: Hastanın TC Kimlik numarası değiştirilemez
                success = DoctorController.update_patient_profile(
                    self.patient.id,
                    name,
                    surname,
                    birthdate,
                    gender,
                    email,
                    self.profile_image_data,
                    diagnosis,
                    diabetes_type,
                    diagnosis_date
                )
                
                if success:
                    QMessageBox.information(self, "Başarılı", f"{name} {surname} isimli hasta başarıyla güncellendi.")
                    self.accept()
                else:
                    QMessageBox.critical(self, "Hata", "Hasta güncellenirken bir hata oluştu.")
            else:
                # Yeni hasta ekle
                # Rastgele şifre otomatik oluşturulacak ve hastaya e-posta gönderilecek
                patient = DoctorController.register_patient(
                    self.doctor_id,
                    tc_id,
                    name,
                    surname,
                    birthdate,
                    gender,
                    email,
                    self.profile_image_data,
                    diagnosis,
                    diabetes_type,
                    diagnosis_date
                )
                
                if patient:
                    QMessageBox.information(
                        self, 
                        "Başarılı", 
                        f"{name} {surname} isimli hasta başarıyla eklendi. Giriş bilgileri e-posta adresine gönderildi."
                    )
                    self.accept()
                else:
                    QMessageBox.critical(self, "Hata", "Hasta eklenirken bir hata oluştu.")
        
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"İşlem sırasında bir hata oluştu: {str(e)}")