# models/measurement.py
from datetime import datetime

class Measurement:
    PERIOD_MORNING = 'morning'
    PERIOD_NOON = 'noon'
    PERIOD_AFTERNOON = 'afternoon'
    PERIOD_EVENING = 'evening'
    PERIOD_NIGHT = 'night'
    
    PERIODS = [
        PERIOD_MORNING, 
        PERIOD_NOON, 
        PERIOD_AFTERNOON, 
        PERIOD_EVENING, 
        PERIOD_NIGHT
    ]
    
    PERIOD_TIME_RANGES = {
        PERIOD_MORNING: ('07:00', '08:00'),
        PERIOD_NOON: ('12:00', '13:00'),
        PERIOD_AFTERNOON: ('15:00', '16:00'),
        PERIOD_EVENING: ('18:00', '19:00'),
        PERIOD_NIGHT: ('22:00', '23:00')
    }
    
    def __init__(self, patient_id=None, glucose_level=None, measurement_date=None, 
                 measurement_time=None, period=None, notes=None, id=None):
        self.id = id
        self.patient_id = patient_id
        self.glucose_level = glucose_level  # mg/dL
        self.measurement_date = measurement_date or datetime.now().date()
        self.measurement_time = measurement_time or datetime.now().time()
        self.period = period
        self.notes = notes
        self.created_at = datetime.now()
    
    @staticmethod
    def get_period_from_time(time_obj):
        if not time_obj:
            return None
        
        time_str = time_obj.strftime('%H:%M')
        
        for period, (start, end) in Measurement.PERIOD_TIME_RANGES.items():
            if start <= time_str <= end:
                return period
        
        return None
    
    @property
    def is_valid_period_time(self):
        if not self.period or not self.measurement_time:
            return False
        
        time_str = self.measurement_time.strftime('%H:%M')
        start, end = self.PERIOD_TIME_RANGES.get(self.period, ('00:00', '00:00'))
        
        return start <= time_str <= end
    
    @property
    def level_category(self):
        if self.glucose_level is None:
            return None
        if self.glucose_level < 70:
            return 'hypoglycemia'
        elif 70 <= self.glucose_level <= 99:
            return 'normal'
        elif 100 <= self.glucose_level <= 125:
            return 'prediabetes'
        else:
            return 'diabetes'
    
    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'glucose_level': self.glucose_level,
            'measurement_date': self.measurement_date,
            'measurement_time': self.measurement_time,
            'period': self.period,
            'notes': self.notes,
            'created_at': self.created_at
        }
    
    @staticmethod
    def from_dict(data):
        measurement = Measurement()
        measurement.id = data.get('id')
        measurement.patient_id = data.get('patient_id')
        measurement.glucose_level = data.get('glucose_level')
        measurement.measurement_date = data.get('measurement_date')
        measurement.measurement_time = data.get('measurement_time')
        measurement.period = data.get('period')
        measurement.notes = data.get('notes')
        measurement.created_at = data.get('created_at', datetime.now())
        return measurement