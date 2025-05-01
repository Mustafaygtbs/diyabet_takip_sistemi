# ui/widgets/glucose_chart.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QComboBox, QLabel, QHBoxLayout
from PyQt5.QtCore import Qt

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from controllers.patient_controller import PatientController
from utils.date_utils import DateUtils

from datetime import datetime, timedelta
import numpy as np

class GlucoseChartWidget(QWidget):
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
        
        # View type selector
        view_label = QLabel("Görünüm:")
        controls_layout.addWidget(view_label)
        
        self.view_combo = QComboBox()
        self.view_combo.addItem("Günlük Ortalama", "daily")
        self.view_combo.addItem("Tüm Ölçümler", "all")
        self.view_combo.addItem("Periyotlara Göre", "period")
        self.view_combo.currentIndexChanged.connect(self.update_chart)
        controls_layout.addWidget(self.view_combo)
        
        controls_layout.addStretch(1)
        
        # Chart figure
        self.figure = Figure(figsize=(8, 5))
        self.canvas = FigureCanvas(self.figure)
        
        layout.addLayout(controls_layout)
        layout.addWidget(self.canvas)
        
        # İlk çizimi yap
        self.update_chart()
    
    def get_date_range(self):
        """
        Seçilen periyoda göre tarih aralığı döndürür.
        """
        end_date = datetime.now().date()
        days = self.period_combo.currentData()
        start_date = end_date - timedelta(days=days)
        return start_date, end_date
    
    def update_chart(self):
        """
        Seçilen görünüm tipine göre grafiği günceller.
        """
        try:
            # Figürü temizle
            self.figure.clear()
            
            # Tarih aralığını al
            start_date, end_date = self.get_date_range()
            
            # Ölçümleri getir
            measurements = PatientController.get_measurements_by_date_range(self.patient_id, start_date, end_date)
            
            # Görünüm tipine göre grafiği çiz
            view_type = self.view_combo.currentData()
            
            if not measurements:
                # Ölçüm yoksa boş grafik göster
                ax = self.figure.add_subplot(111)
                ax.text(0.5, 0.5, 'Bu tarih aralığında ölçüm bulunamadı', 
                        ha='center', va='center', transform=ax.transAxes)
                self.canvas.draw()
                return
            
            if view_type == "daily":
                self.plot_daily_average(measurements)
            elif view_type == "all":
                self.plot_all_measurements(measurements)
            elif view_type == "period":
                self.plot_period_measurements(measurements)
            
            # Grafiği güncelle
            self.canvas.draw()
            
        except Exception as e:
            print(f"Grafik güncellenirken hata: {e}")
            # Hata mesajı göster
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, f'Grafik oluşturulurken hata: {str(e)}', 
                    ha='center', va='center', transform=ax.transAxes)
            self.canvas.draw()
    
    def plot_daily_average(self, measurements):
        """
        Günlük ortalama kan şekeri grafiği oluşturur.
        """
        # Ölçümleri tarihe göre grupla
        daily_values = {}
        
        for m in measurements:
            date_str = DateUtils.format_date(m['measurement_date'])
            if date_str in daily_values:
                daily_values[date_str].append(float(m['glucose_level']))
            else:
                daily_values[date_str] = [float(m['glucose_level'])]
        
        # Günlük ortalamaları hesapla
        dates = []
        averages = []
        
        for date_str in sorted(daily_values.keys()):
            dates.append(date_str)
            avg = sum(daily_values[date_str]) / len(daily_values[date_str])
            averages.append(avg)
        
        # Grafiği çiz
        ax = self.figure.add_subplot(111)
        ax.plot(dates, averages, 'o-', color='#3498db', linewidth=2)
        
        # Güvenli aralıkları göster
        ax.axhspan(70, 110, alpha=0.2, color='green', label='Normal')
        ax.axhspan(0, 70, alpha=0.2, color='red', label='Hipoglisemi')
        ax.axhspan(180, 300, alpha=0.2, color='orange', label='Hiperglisemi')
        
        ax.set_xlabel('Tarih')
        ax.set_ylabel('Kan Şekeri (mg/dL)')
        ax.set_title('Günlük Ortalama Kan Şekeri')
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.legend()
        
        # X eksenindeki yazıları döndür
        plt.setp(ax.get_xticklabels(), rotation=30, ha='right')
        
        self.figure.tight_layout()
    
    def plot_all_measurements(self, measurements):
        """
        Tüm kan şekeri ölçümlerini gösteren grafik oluşturur.
        """
        # Tüm ölçümleri tarih ve saate göre sırala
        dates = []
        values = []
        colors = []
        
        for m in measurements:
            date_time = f"{DateUtils.format_date(m['measurement_date'])} {DateUtils.format_time(m['measurement_time'])}"
            dates.append(date_time)
            value = float(m['glucose_level'])
            values.append(value)
            
            # Değere göre renklendirme
            if value < 70:
                colors.append('red')
            elif value > 180:
                colors.append('orange')
            else:
                colors.append('#3498db')
        
        # Grafiği çiz
        ax = self.figure.add_subplot(111)
        ax.scatter(range(len(dates)), values, c=colors, alpha=0.8)
        
        # Her 10 noktada bir tarih göster (çok kalabalık olmaması için)
        step = max(1, len(dates) // 10)
        ax.set_xticks(range(0, len(dates), step))
        ax.set_xticklabels([dates[i] for i in range(0, len(dates), step)])
        
        # Güvenli aralıkları göster
        ax.axhspan(70, 110, alpha=0.2, color='green', label='Normal')
        ax.axhspan(0, 70, alpha=0.2, color='red', label='Hipoglisemi')
        ax.axhspan(180, 300, alpha=0.2, color='orange', label='Hiperglisemi')
        
        ax.set_xlabel('Tarih ve Saat')
        ax.set_ylabel('Kan Şekeri (mg/dL)')
        ax.set_title('Tüm Kan Şekeri Ölçümleri')
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.legend()
        
        # X eksenindeki yazıları döndür
        plt.setp(ax.get_xticklabels(), rotation=90, ha='right')
        
        self.figure.tight_layout()
    
    def plot_period_measurements(self, measurements):
        """
        Periyotlara göre kan şekeri ölçümlerini gösteren grafik oluşturur.
        """
        # Ölçümleri periyoda göre grupla
        period_values = {
            'morning': [],
            'noon': [],
            'afternoon': [],
            'evening': [],
            'night': []
        }
        
        for m in measurements:
            period = m['period']
            if period in period_values:
                period_values[period].append(float(m['glucose_level']))
        
        # Periyot ortalamalarını hesapla
        period_names = {
            'morning': 'Sabah',
            'noon': 'Öğle',
            'afternoon': 'İkindi',
            'evening': 'Akşam',
            'night': 'Gece'
        }
        
        periods = []
        averages = []
        std_devs = []
        
        for period, values in period_values.items():
            if values:  # Boş değilse
                periods.append(period_names.get(period, period))
                averages.append(sum(values) / len(values))
                
                # Standart sapma
                mean = sum(values) / len(values)
                variance = sum((x - mean) ** 2 for x in values) / len(values)
                std_devs.append((variance ** 0.5) / 2)  # Yarı standart sapma (görsel amaçlı)
        
        # Grafiği çiz
        ax = self.figure.add_subplot(111)
        
        if periods:
            ax.bar(periods, averages, yerr=std_devs, capsize=5, color='#3498db', alpha=0.7)
            
            # Güvenli aralıkları göster
            ax.axhspan(70, 110, alpha=0.2, color='green', label='Normal')
            ax.axhspan(0, 70, alpha=0.2, color='red', label='Hipoglisemi')
            ax.axhspan(180, 300, alpha=0.2, color='orange', label='Hiperglisemi')
            
            ax.set_xlabel('Periyot')
            ax.set_ylabel('Kan Şekeri (mg/dL)')
            ax.set_title('Periyotlara Göre Ortalama Kan Şekeri')
            ax.grid(True, linestyle='--', alpha=0.7)
            ax.legend()
        else:
            ax.text(0.5, 0.5, 'Periyot verisi bulunamadı', 
                    ha='center', va='center', transform=ax.transAxes)
        
        self.figure.tight_layout()