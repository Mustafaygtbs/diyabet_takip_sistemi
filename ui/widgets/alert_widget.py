# ui/widgets/alert_widget.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtGui import QIcon, QFont, QColor
from PyQt5.QtCore import Qt, pyqtSignal

from models.alert import Alert
from controllers.alert_controller import AlertController
from utils.date_utils import DateUtils

class AlertWidget(QWidget):
    # Signal when alert is marked as read
    marked_as_read = pyqtSignal()
    
    def __init__(self, alert_data, parent=None):
        super().__init__(parent)
        self.alert_data = alert_data
        self._main_layout = QVBoxLayout()
        self.setLayout(self._main_layout)
        self.initUI()
    
    def initUI(self):
        # Layout'u temizle
        while self._main_layout.count():
            item = self._main_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())
        
        # Alert container
        alert_type = self.alert_data['alert_type']
        
        # Set style based on alert type
        if alert_type == Alert.TYPE_HYPOGLYCEMIA or alert_type == Alert.TYPE_HYPERGLYCEMIA:
            self.setStyleSheet("""
                QWidget {
                    background-color: #FFEBEE;
                    border: 1px solid #FFCDD2;
                    border-left: 5px solid #F44336;
                    border-radius: 5px;
                    padding: 10px;
                }
            """)
        elif alert_type == Alert.TYPE_MISSING_MEASUREMENT or alert_type == Alert.TYPE_INSUFFICIENT_MEASUREMENT:
            self.setStyleSheet("""
                QWidget {
                    background-color: #FFF3E0;
                    border: 1px solid #FFE0B2;
                    border-left: 5px solid #FF9800;
                    border-radius: 5px;
                    padding: 10px;
                }
            """)
        elif alert_type == Alert.TYPE_MEDIUM_HIGH or alert_type == Alert.TYPE_HIGH:
            self.setStyleSheet("""
                QWidget {
                    background-color: #E3F2FD;
                    border: 1px solid #BBDEFB;
                    border-left: 5px solid #2196F3;
                    border-radius: 5px;
                    padding: 10px;
                }
            """)
        else:
            self.setStyleSheet("""
                QWidget {
                    background-color: #E8F5E9;
                    border: 1px solid #C8E6C9;
                    border-left: 5px solid #4CAF50;
                    border-radius: 5px;
                    padding: 10px;
                }
            """)
        
        # Header with alert type and date
        header_layout = QHBoxLayout()
        
        # Alert type
        alert_type_label = QLabel(self.get_alert_type_name())
        alert_type_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        
        # Set text color based on alert type
        if alert_type == Alert.TYPE_HYPOGLYCEMIA or alert_type == Alert.TYPE_HYPERGLYCEMIA:
            alert_type_label.setStyleSheet("color: #D32F2F;")
        elif alert_type == Alert.TYPE_MISSING_MEASUREMENT or alert_type == Alert.TYPE_INSUFFICIENT_MEASUREMENT:
            alert_type_label.setStyleSheet("color: #F57C00;")
        elif alert_type == Alert.TYPE_MEDIUM_HIGH or alert_type == Alert.TYPE_HIGH:
            alert_type_label.setStyleSheet("color: #1976D2;")
        else:
            alert_type_label.setStyleSheet("color: #388E3C;")
        
        header_layout.addWidget(alert_type_label)
        
        # Date
        date_label = QLabel(DateUtils.format_datetime(self.alert_data['date']))
        date_label.setStyleSheet("color: #757575; font-size: 11px;")
        date_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        header_layout.addWidget(date_label)
        
        self._main_layout.addLayout(header_layout)
        
        # Alert message
        message_label = QLabel(self.alert_data['message'])
        message_label.setWordWrap(True)
        message_label.setStyleSheet("color: #333333; margin-top: 5px;")
        self._main_layout.addWidget(message_label)
        
        # Action buttons
        if not self.alert_data['is_read']:
            action_layout = QHBoxLayout()
            action_layout.setContentsMargins(0, 10, 0, 0)
            
            # Mark as read button
            read_button = QPushButton("Okundu Olarak İşaretle")
            read_button.setCursor(Qt.PointingHandCursor)
            read_button.setStyleSheet("""
                QPushButton {
                    background-color: #FFFFFF;
                    border: 1px solid #E0E0E0;
                    border-radius: 4px;
                    padding: 5px 10px;
                    color: #333333;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #F5F5F5;
                }
            """)
            read_button.clicked.connect(self.mark_as_read)
            
            action_layout.addStretch(1)
            action_layout.addWidget(read_button)
            
            self._main_layout.addLayout(action_layout)
    
    def get_alert_type_name(self):
        """Get display name for alert type."""
        alert_type = self.alert_data['alert_type']
        
        if alert_type == Alert.TYPE_HYPOGLYCEMIA:
            return "⚠️ Hipoglisemi Riski"
        elif alert_type == Alert.TYPE_NORMAL:
            return "✅ Normal Seviye"
        elif alert_type == Alert.TYPE_MEDIUM_HIGH:
            return "ℹ️ Takip Uyarısı"
        elif alert_type == Alert.TYPE_HIGH:
            return "⚠️ İzleme Uyarısı"
        elif alert_type == Alert.TYPE_HYPERGLYCEMIA:
            return "🚨 Acil Müdahale Uyarısı"
        elif alert_type == Alert.TYPE_MISSING_MEASUREMENT:
            return "⚠️ Ölçüm Eksik Uyarısı"
        elif alert_type == Alert.TYPE_INSUFFICIENT_MEASUREMENT:
            return "⚠️ Ölçüm Yetersiz Uyarısı"
        
        return alert_type.capitalize()
    
    def mark_as_read(self):
        """Mark alert as read."""
        alert_id = self.alert_data['id']
        success = AlertController.mark_alert_as_read(alert_id)
        
        if success:
            # Update local alert data
            self.alert_data['is_read'] = True
            
            # Emit signal
            self.marked_as_read.emit()
            
            # Update UI
            self.initUI()

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())