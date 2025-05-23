# models/user.py
from datetime import datetime

class User:
    def __init__(self, tc_id=None, password=None, name=None, surname=None, 
                 birthdate=None, gender=None, email=None, profile_image=None, 
                 user_type=None, id=None):
        self.id = id
        self.tc_id = tc_id
        self.password = password
        self.name = name
        self.surname = surname
        self.birthdate = birthdate  
        self.gender = gender  
        self.email = email
        self.profile_image = profile_image  
        self.user_type = user_type  
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    @property
    def full_name(self):
        return f"{self.name} {self.surname}"
    
    def to_dict(self):
        return {
            'id': self.id,
            'tc_id': self.tc_id,
            'name': self.name,
            'surname': self.surname,
            'birthdate': self.birthdate,
            'gender': self.gender,
            'email': self.email,
            'user_type': self.user_type,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @staticmethod
    def from_dict(data):
        user = User()
        user.id = data.get('id')
        user.tc_id = data.get('tc_id')
        user.password = data.get('password')
        user.name = data.get('name')
        user.surname = data.get('surname')
        user.birthdate = data.get('birthdate')
        user.gender = data.get('gender')
        user.email = data.get('email')
        user.profile_image = data.get('profile_image')
        user.user_type = data.get('user_type')
        user.created_at = data.get('created_at', datetime.now())
        user.updated_at = data.get('updated_at', datetime.now())
        return user