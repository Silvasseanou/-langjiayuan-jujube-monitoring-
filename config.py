import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    
    # 数据库配置
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///agriculture.db'
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Redis配置
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379'
    
    # 邮件配置
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Twilio短信配置
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')
    
    # 传感器配置
    SENSOR_CONFIG = {
        'temperature': {
            'pin': 4,
            'type': 'DS18B20'
        },
        'humidity': {
            'pin': 17,
            'type': 'DHT22'
        },
        'soil_moisture': {
            'pin': 18,
            'type': 'capacitive'
        },
        'light': {
            'pin': 19,
            'type': 'photoresistor'
        }
    }
    
    # 预警阈值
    WARNING_THRESHOLDS = {
        'pest_risk': 0.7,
        'disease_risk': 0.6,
        'temperature_high': 35.0,
        'temperature_low': 5.0,
        'humidity_high': 90.0,
        'humidity_low': 30.0,
        'soil_moisture_low': 20.0
    }
    
    # API键配置
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    
    # 上传文件配置
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size 