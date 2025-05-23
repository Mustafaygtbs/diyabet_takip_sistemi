
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QComboBox, QLabel, QHBoxLayout
from PyQt5.QtCore import Qt

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from controllers.doctor_controller import DoctorController
from utils.date_utils import DateUtils

from datetime import datetime, timedelta

class ExerciseChartWidget(QWidget):
    def __init__(self, patient_id):
        super().__init__()
        self.patient_id = patient_id
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Chart controls
        controls_layout = QHBoxLayout()
        
        # Period selector
        period_label = QLabel("Gösterim:")
        controls_layout.addWidget(period_label)
        
        self.period_combo = QComboBox()
        self.period_combo.addItem("Son 7 Gün", 7)
        self.period_combo.addItem("Son 30 Gün", 30)
        self.period_combo.addItem("Son 90 Gün", 90)
        self.period_combo.currentIndexChanged.connect(self.update_chart)
        controls_layout.addWidget(self.period_combo)
        
        controls_layout.addStretch(1)
        
        # Chart figure
        self.figure = Figure(figsize=(6, 4))
        self.canvas = FigureCanvas(self.figure)
        
        layout.addLayout(controls_layout)
        layout.addWidget(self.canvas)
        
        # İlk çizimi yap
        self.update_chart()
    
    def update_chart(self):
        # Seçilen parametreleri al
        days = self.period_combo.currentData()
        
        # Tarih aralığını belirle
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Egzersiz verilerini al
        exercises = DoctorController.get_patient_exercises(self.patient_id, start_date, end_date)
        
        # Grafik tipine göre verileri hazırla ve çiz
        self.figure.clear()
        
        if not exercises:
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, 'Bu tarih aralığında veri bulunamadı', 
                    ha='center', va='center', transform=ax.transAxes)
            self.canvas.draw()
            return
        
        # Egzersiz tipine göre grupla
        exercise_types = {
            'walking': {'name': 'Yürüyüş', 'completed': 0, 'total': 0},
            'cycling': {'name': 'Bisiklet', 'completed': 0, 'total': 0},
            'clinical': {'name': 'Klinik Egzersiz', 'completed': 0, 'total': 0}
        }
        
        for e in exercises:
            exercise_type = e['exercise_type']
            if exercise_type in exercise_types:
                exercise_types[exercise_type]['total'] += 1
                if e['is_completed']:
                    exercise_types[exercise_type]['completed'] += 1
        
        # Grafiği çiz
        ax = self.figure.add_subplot(111)
        
        # Her egzersiz tipinin tamamlanma yüzdesi
        labels = []
        percentages = []
        colors = ['#3498db', '#2ecc71', '#9b59b6']
        
        for i, (type_key, data) in enumerate(exercise_types.items()):
            if data['total'] > 0:
                labels.append(data['name'])
                percent = (data['completed'] / data['total']) * 100
                percentages.append(percent)
        
        if labels:
            ax.bar(labels, percentages, color=colors[:len(labels)])
            
            # Yüzde değerlerini grafik üzerine ekle
            for i, v in enumerate(percentages):
                ax.text(i, v + 2, f'%{v:.1f}', ha='center')
            
            ax.set_ylim(0, 105)  # Yüzde değerleri için
            ax.set_xlabel('Egzersiz Türü')
            ax.set_ylabel('Tamamlanma Yüzdesi (%)')
            ax.set_title('Egzersiz Tamamlanma Oranları')
            ax.grid(True, linestyle='--', alpha=0.7)
        else:
            ax.text(0.5, 0.5, 'Egzersiz verisi bulunamadı', 
                    ha='center', va='center')
        
        self.figure.tight_layout()
        self.canvas.draw()