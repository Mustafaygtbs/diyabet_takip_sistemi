# ui/widgets/glucose_chart.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib as mpl

from controllers.patient_controller import PatientController
from utils.date_utils import DateUtils

from datetime import datetime, timedelta

class GlucoseChartWidget(QWidget):
    def __init__(self, patient_id, parent=None):
        super().__init__(parent)
        self.patient_id = patient_id
        
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
    
    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Title and time range selector
        header_layout = QHBoxLayout()
        
        title = QLabel("Kan Şekeri Grafiği")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet("color: #3949AB;")
        header_layout.addWidget(title)
        
        # Time range selector
        range_selector = QComboBox()
        range_selector.addItem("Son 7 Gün", 7)
        range_selector.addItem("Son 14 Gün", 14)
        range_selector.addItem("Son 30 Gün", 30)
        range_selector.currentIndexChanged.connect(self.update_chart)
        header_layout.addWidget(range_selector)
        
        layout.addLayout(header_layout)
        
        # Figure for chart
        self.figure = Figure(figsize=(8, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        self.range_selector = range_selector
        self.update_chart()
    
    def update_chart(self):
        """Update chart based on selected time range."""
        days = self.range_selector.currentData()
        
        # Date range
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days-1)
        
        # Get measurements
        measurements = PatientController.get_measurements_by_date_range(self.patient_id, start_date, end_date)
        
        # Clear the figure
        self.figure.clear()
        
        # If there are measurements, create chart
        if measurements:
            # Prepare data by date and period
            data_by_date = {}
            data_by_date_period = {}
            
            for m in measurements:
                date_str = DateUtils.format_date(m['measurement_date'])
                
                # Group by date for trend line
                if date_str not in data_by_date:
                    data_by_date[date_str] = []
                data_by_date[date_str].append(m['glucose_level'])
                
                # Group by date and period for scatter plot
                period = m['period']
                if date_str not in data_by_date_period:
                    data_by_date_period[date_str] = {}
                if period not in data_by_date_period[date_str]:
                    data_by_date_period[date_str][period] = []
                data_by_date_period[date_str][period].append(m['glucose_level'])
            
            # Calculate daily averages for trend line
            dates = []
            averages = []
            
            for date_str in sorted(data_by_date.keys()):
                dates.append(date_str)
                avg = sum(data_by_date[date_str]) / len(data_by_date[date_str])
                averages.append(avg)
            
            # Create plot with daily trend and period measurements
            ax = self.figure.add_subplot(111)
            
            # Plot trend line
            ax.plot(dates, averages, '-', color='#3949AB', linewidth=2, label='Günlük Ortalama')
            
            # Plot scatter points for each period
            period_colors = {
                'morning': '#4CAF50',  # Green
                'noon': '#FF9800',     # Orange
                'afternoon': '#F44336',# Red
                'evening': '#9C27B0',  # Purple
                'night': '#2196F3'     # Blue
            }
            
            period_markers = {
                'morning': 'o',   # Circle
                'noon': 's',      # Square
                'afternoon': '^', # Triangle up
                'evening': 'D',   # Diamond
                'night': '*'      # Star
            }
            
            period_names = {
                'morning': 'Sabah',
                'noon': 'Öğle',
                'afternoon': 'İkindi',
                'evening': 'Akşam',
                'night': 'Gece'
            }
            
            # Plot scatter points for each period
            for period, color in period_colors.items():
                period_x = []
                period_y = []
                
                for date_str in sorted(data_by_date_period.keys()):
                    if period in data_by_date_period[date_str]:
                        for value in data_by_date_period[date_str][period]:
                            period_x.append(date_str)
                            period_y.append(value)
                
                if period_x:
                    ax.scatter(period_x, period_y, color=color, marker=period_markers[period], 
                              s=60, alpha=0.7, label=period_names[period])
            
            # Show safe ranges
            ax.axhspan(70, 110, alpha=0.2, color='#4CAF50', label='Normal')
            ax.axhspan(0, 70, alpha=0.2, color='#F44336', label='Hipoglisemi')
            ax.axhspan(180, max(300, max([max(values) for values in data_by_date.values()]) + 20), 
                      alpha=0.2, color='#FF9800', label='Hiperglisemi')
            
            # Set labels and title
            ax.set_xlabel('Tarih', fontsize=10)
            ax.set_ylabel('Kan Şekeri (mg/dL)', fontsize=10)
            ax.set_title(f'Son {days} Günlük Kan Şekeri Takibi', fontweight='bold', fontsize=12)
            
            # Customize appearance
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_color('#DDDDDD')
            ax.spines['left'].set_color('#DDDDDD')
            ax.tick_params(colors='#666666')
            
            # Rotate x labels
            plt.setp(ax.get_xticklabels(), rotation=30, ha='right')
            
            # Add legend
            ax.legend(loc='upper right', frameon=False, fontsize=9)
            
            # Set y-axis limits
            all_values = [value for values in data_by_date.values() for value in values]
            ax.set_ylim(max(0, min(all_values) - 20), max(all_values) + 20)
            
            # Add grid
            ax.grid(True, linestyle='--', alpha=0.7)
            
            # Add value labels to trend line
            for i, (x, y) in enumerate(zip(dates, averages)):
                ax.annotate(f'{y:.1f}', xy=(x, y), xytext=(0, 5),
                          textcoords='offset points', ha='center', fontsize=8,
                          fontweight='bold')
            
            self.figure.tight_layout()
        else:
            # No data
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, 'Veri bulunamadı', ha='center', va='center', 
                   fontsize=12, color='#757575')
            ax.set_xticks([])
            ax.set_yticks([])
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            ax.spines['left'].set_visible(False)
        
        # Update canvas
        self.canvas.draw()