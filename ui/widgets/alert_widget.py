# ui/widgets/alert_widget.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt, pyqtSignal

from controllers.alert_controller import AlertController
from utils.date_utils import DateUtils

class AlertWidget(QWidget):
    marked_as_read = pyqtSignal()
    
    def __init__(self, alert):
        super().__init__()
        self.alert = alert
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Widget stilini belirle
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        
        # Üst kısım (başlık ve tarih)
        header_layout = QHBoxLayout()
        
        # Uyarı tipine göre ikon
        type_icon = QLabel()
        if self.alert['alert_type'] in ['hypoglycemia', 'hyperglycemia']:
            type_icon.setText("⚠️")
        elif self.alert['alert_type'] in ['missing_measurement', 'insufficient_measurement']:
            type_icon.setText("⚠️")
        else:
            type_icon.setText("ℹ️")
        
        type_icon.setFont(QFont("Arial", 14))
        
        # Uyarı başlığı
        alert_type_map = {
            'hypoglycemia': "Hipoglisemi Riski",
            'normal': "Normal Seviye",
            'medium_high': "Takip Uyarısı",
            'high': "İzleme Uyarısı",
            'hyperglycemia': "Acil Müdahale Uyarısı",
            'missing_measurement': "Ölçüm Eksik Uyarısı",
            'insufficient_measurement': "Ölçüm Yetersiz Uyarısı"
        }
        
        title_label = QLabel(alert_type_map.get(self.alert['alert_type'], str(self.alert['alert_type'])))
        title_label.setFont(QFont("Arial", 11, QFont.Bold))
        
        # Uyarı seviyesine göre renklendirme
        if self.alert['alert_type'] in ['hypoglycemia', 'hyperglycemia']:
            title_label.setStyleSheet("color: #e74c3c;")  # Kırmızı
        elif self.alert['alert_type'] in ['missing_measurement', 'insufficient_measurement']:
            title_label.setStyleSheet("color: #e67e22;")  # Turuncu
        
        # Uyarı tarih ve saati
        date_label = QLabel(DateUtils.format_datetime(self.alert['date']))
        date_label.setStyleSheet("color: #7f8c8d; font-size: 10px;")
        
        header_layout.addWidget(type_icon)
        header_layout.addWidget(title_label)
        header_layout.addStretch(1)
        header_layout.addWidget(date_label)
        
        # Uyarı mesajı
        message_label = QLabel(self.alert['message'])
        message_label.setWordWrap(True)
        
        # Alt kısım (kan şekeri değeri ve okundu butonu)
        footer_layout = QHBoxLayout()
        
        # Kan şekeri değeri
        if self.alert['glucose_level'] is not None:
            glucose_label = QLabel(f"Kan Şekeri: {self.alert['glucose_level']} mg/dL")
            
            # Değere göre renklendirme
            if self.alert['glucose_level'] < 70:
                glucose_label.setStyleSheet("color: #e74c3c;")  # Düşük - kırmızı
            elif self.alert['glucose_level'] > 180:
                glucose_label.setStyleSheet("color: #e67e22;")  # Yüksek - turuncu
                
            footer_layout.addWidget(glucose_label)
        
        footer_layout.addStretch(1)
        
        # Okundu butonu
        if not self.alert['is_read']:
            read_button = QPushButton("Okundu İşaretle")
            read_button.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border-radius: 3px;
                    padding: 5px 10px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            read_button.clicked.connect(self.mark_as_read)
            footer_layout.addWidget(read_button)
        
        # Layout'a bileşenleri ekle
        layout.addLayout(header_layout)
        layout.addWidget(message_label)
        layout.addLayout(footer_layout)
    
    def mark_as_read(self):
        """Uyarıyı okundu olarak işaretler."""
        success = AlertController.mark_alert_as_read(self.alert['id'])
        
        if success:
            self.alert['is_read'] = True
            self.marked_as_read.emit()
            
            # Widget'ı güncelle (okundu butonunu kaldır)
            for i in reversed(range(self.layout().count())):
                item = self.layout().itemAt(i)
                if item.layout():
                    for j in reversed(range(item.layout().count())):
                        widget = item.layout().itemAt(j).widget()
                        if isinstance(widget, QPushButton) and widget.text() == "Okundu İşaretle":
                            widget.deleteLater()