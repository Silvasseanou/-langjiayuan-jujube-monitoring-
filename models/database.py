from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

Base = declarative_base()

# 环境数据表
class EnvironmentData(Base):
    __tablename__ = 'environment_data'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    temperature = Column(Float)
    humidity = Column(Float)
    soil_moisture = Column(Float)
    light_intensity = Column(Float)
    wind_speed = Column(Float)
    rainfall = Column(Float)
    air_pressure = Column(Float)
    location = Column(String(100))
    sensor_id = Column(String(50))

# 病虫害数据表
class PestDiseaseData(Base):
    __tablename__ = 'pest_disease_data'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    pest_type = Column(String(100))
    disease_type = Column(String(100))
    severity_level = Column(Integer)  # 1-5 严重程度
    location = Column(String(100))
    affected_area = Column(Float)  # 受影响面积
    detection_method = Column(String(50))  # 检测方法
    images = Column(JSON)  # 图片路径列表
    
# 预测模型结果表
class PredictionResult(Base):
    __tablename__ = 'prediction_results'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    prediction_type = Column(String(50))  # pest, disease
    risk_level = Column(Float)  # 风险等级 0-1
    confidence = Column(Float)  # 置信度
    environmental_factors = Column(JSON)
    location = Column(String(100))
    model_version = Column(String(20))

# 预警记录表
class WarningRecord(Base):
    __tablename__ = 'warning_records'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    warning_type = Column(String(50))
    severity = Column(String(20))  # low, medium, high
    message = Column(Text)
    location = Column(String(100))
    status = Column(String(20), default='active')  # active, resolved
    sent_notifications = Column(JSON)  # 已发送的通知方式

# 防治方案表
class TreatmentPlan(Base):
    __tablename__ = 'treatment_plans'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    pest_disease_id = Column(Integer, ForeignKey('pest_disease_data.id'))
    treatment_type = Column(String(50))  # biological, physical, chemical
    treatment_method = Column(Text)
    effectiveness = Column(Float)
    cost = Column(Float)
    environmental_impact = Column(Float)  # 环境影响评分
    
    pest_disease = relationship("PestDiseaseData")

# 市场数据表
class MarketData(Base):
    __tablename__ = 'market_data'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    product_name = Column(String(100))
    platform = Column(String(50))  # 平台名称
    price = Column(Float)
    sales_volume = Column(Integer)
    rating = Column(Float)
    reviews_count = Column(Integer)
    keywords = Column(JSON)  # 关键词列表
    sentiment_score = Column(Float)  # 情感分数

# 产品追溯表
class ProductTraceability(Base):
    __tablename__ = 'product_traceability'
    
    id = Column(Integer, primary_key=True)
    product_id = Column(String(100), unique=True)
    qr_code = Column(String(200))
    planting_date = Column(DateTime)
    harvest_date = Column(DateTime)
    location = Column(String(100))
    fertilizer_records = Column(JSON)
    pesticide_records = Column(JSON)
    processing_records = Column(JSON)
    packaging_date = Column(DateTime)
    transport_records = Column(JSON)
    quality_checks = Column(JSON)
    
# 用户管理表
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(128))
    role = Column(String(20), default='user')  # admin, user, viewer
    phone = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

# 通知设置表
class NotificationSetting(Base):
    __tablename__ = 'notification_settings'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    notification_type = Column(String(50))  # email, sms, push
    is_enabled = Column(Boolean, default=True)
    threshold_settings = Column(JSON)
    
    user = relationship("User")

# 创建数据库引擎和会话
def init_database(database_url):
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return engine, Session 