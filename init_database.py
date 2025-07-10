#!/usr/bin/env python3
"""
数据库初始化脚本
用于创建数据库表结构和初始化基础数据
"""

import logging
import json
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

from config import Config
from models.database import (
    init_database, Base, EnvironmentData, PestDiseaseData, 
    PredictionResult, WarningRecord, TreatmentPlan, MarketData,
    ProductTraceability, User, NotificationSetting
)

def create_tables():
    """创建数据库表"""
    try:
        config = Config()
        engine, Session = init_database(config.DATABASE_URL)
        
        # 创建所有表
        Base.metadata.create_all(engine)
        
        logging.info("Database tables created successfully")
        return engine, Session
        
    except Exception as e:
        logging.error(f"Error creating database tables: {e}")
        raise

def create_admin_user(Session):
    """创建管理员用户"""
    try:
        session = Session()
        
        # 检查是否已存在管理员用户
        existing_admin = session.query(User).filter(User.username == 'admin').first()
        
        if not existing_admin:
            admin_user = User(
                username='admin',
                email='admin@langjiayuan.com',
                password_hash=generate_password_hash('admin123'),
                role='admin',
                phone='13800138000'
            )
            
            session.add(admin_user)
            session.commit()
            
            logging.info("Admin user created successfully")
            
            # 创建管理员的通知设置
            notification_settings = [
                NotificationSetting(
                    user_id=admin_user.id,
                    notification_type='email',
                    is_enabled=True,
                    threshold_settings={
                        'temperature_high': 35.0,
                        'temperature_low': 5.0,
                        'pest_risk': 0.7
                    }
                ),
                NotificationSetting(
                    user_id=admin_user.id,
                    notification_type='sms',
                    is_enabled=False,
                    threshold_settings={}
                )
            ]
            
            for setting in notification_settings:
                session.add(setting)
            
            session.commit()
            logging.info("Admin notification settings created")
        
        else:
            logging.info("Admin user already exists")
        
        session.close()
        
    except Exception as e:
        logging.error(f"Error creating admin user: {e}")
        raise

def create_sample_users(Session):
    """创建示例用户"""
    try:
        session = Session()
        
        sample_users = [
            {
                'username': 'farmer1',
                'email': 'farmer1@langjiayuan.com',
                'password': 'farmer123',
                'role': 'user',
                'phone': '13800138001'
            },
            {
                'username': 'technician1',
                'email': 'tech1@langjiayuan.com',
                'password': 'tech123',
                'role': 'user',
                'phone': '13800138002'
            },
            {
                'username': 'manager1',
                'email': 'manager1@langjiayuan.com',
                'password': 'manager123',
                'role': 'admin',
                'phone': '13800138003'
            }
        ]
        
        for user_data in sample_users:
            # 检查用户是否已存在
            existing_user = session.query(User).filter(User.username == user_data['username']).first()
            
            if not existing_user:
                user = User(
                    username=user_data['username'],
                    email=user_data['email'],
                    password_hash=generate_password_hash(user_data['password']),
                    role=user_data['role'],
                    phone=user_data['phone']
                )
                
                session.add(user)
                session.commit()
                
                # 创建默认通知设置
                notification_setting = NotificationSetting(
                    user_id=user.id,
                    notification_type='email',
                    is_enabled=True,
                    threshold_settings={
                        'temperature_high': 35.0,
                        'pest_risk': 0.7
                    }
                )
                
                session.add(notification_setting)
                
                logging.info(f"Created sample user: {user_data['username']}")
        
        session.commit()
        session.close()
        
    except Exception as e:
        logging.error(f"Error creating sample users: {e}")
        raise

def create_sample_environmental_data(Session):
    """创建示例环境数据"""
    try:
        session = Session()
        
        # 检查是否已有数据
        existing_data = session.query(EnvironmentData).first()
        
        if not existing_data:
            import random
            
            # 生成最近30天的模拟数据
            base_date = datetime.now() - timedelta(days=30)
            
            for day in range(30):
                for hour in range(0, 24, 2):  # 每2小时一条记录
                    timestamp = base_date + timedelta(days=day, hours=hour)
                    
                    # 生成模拟的环境数据
                    env_data = EnvironmentData(
                        timestamp=timestamp,
                        temperature=round(random.uniform(15.0, 35.0), 2),
                        humidity=round(random.uniform(30.0, 90.0), 2),
                        soil_moisture=round(random.uniform(20.0, 80.0), 2),
                        light_intensity=round(random.uniform(100.0, 1000.0), 2),
                        wind_speed=round(random.uniform(0.0, 20.0), 2),
                        rainfall=round(random.uniform(0.0, 50.0), 2),
                        air_pressure=round(random.uniform(980.0, 1020.0), 2),
                        location='郎家园示范基地',
                        sensor_id='sensor_001'
                    )
                    
                    session.add(env_data)
            
            session.commit()
            logging.info("Sample environmental data created")
        
        else:
            logging.info("Environmental data already exists")
        
        session.close()
        
    except Exception as e:
        logging.error(f"Error creating sample environmental data: {e}")
        raise

def create_sample_pest_disease_data(Session):
    """创建示例病虫害数据"""
    try:
        session = Session()
        
        # 检查是否已有数据
        existing_data = session.query(PestDiseaseData).first()
        
        if not existing_data:
            import random
            
            pest_types = ['蚜虫', '红蜘蛛', '介壳虫', '金龟子', '食心虫']
            disease_types = ['白粉病', '炭疽病', '褐斑病', '缩叶病', '根腐病']
            
            # 生成最近30天的模拟病虫害数据
            base_date = datetime.now() - timedelta(days=30)
            
            for i in range(50):  # 生成50条记录
                timestamp = base_date + timedelta(days=random.randint(0, 29), hours=random.randint(0, 23))
                
                pest_disease_data = PestDiseaseData(
                    timestamp=timestamp,
                    pest_type=random.choice(pest_types) if random.random() > 0.5 else None,
                    disease_type=random.choice(disease_types) if random.random() > 0.5 else None,
                    severity_level=random.randint(1, 5),
                    location='郎家园示范基地',
                    affected_area=round(random.uniform(0.1, 10.0), 2),
                    detection_method=random.choice(['人工巡查', '诱捕器', '图像识别', '传感器监测']),
                    images=[]
                )
                
                session.add(pest_disease_data)
            
            session.commit()
            logging.info("Sample pest disease data created")
        
        else:
            logging.info("Pest disease data already exists")
        
        session.close()
        
    except Exception as e:
        logging.error(f"Error creating sample pest disease data: {e}")
        raise

def create_sample_market_data(Session):
    """创建示例市场数据"""
    try:
        session = Session()
        
        # 检查是否已有数据
        existing_data = session.query(MarketData).first()
        
        if not existing_data:
            import random
            
            platforms = ['淘宝', '天猫', '京东', '拼多多']
            products = ['冬枣', '和田冬枣', '若羌冬枣', '阿克苏冬枣', '郎家园冬枣']
            
            # 生成最近30天的模拟市场数据
            base_date = datetime.now() - timedelta(days=30)
            
            for i in range(200):  # 生成200条记录
                timestamp = base_date + timedelta(days=random.randint(0, 29), hours=random.randint(0, 23))
                
                market_data = MarketData(
                    timestamp=timestamp,
                    product_name=random.choice(products),
                    platform=random.choice(platforms),
                    price=round(random.uniform(20.0, 200.0), 2),
                    sales_volume=random.randint(100, 10000),
                    rating=round(random.uniform(4.0, 5.0), 1),
                    reviews_count=random.randint(50, 5000),
                    keywords=['冬枣', '新疆', '干果', '营养'],
                    sentiment_score=round(random.uniform(-0.3, 0.8), 2)
                )
                
                session.add(market_data)
            
            session.commit()
            logging.info("Sample market data created")
        
        else:
            logging.info("Market data already exists")
        
        session.close()
        
    except Exception as e:
        logging.error(f"Error creating sample market data: {e}")
        raise

def create_sample_product_traceability(Session):
    """创建示例产品追溯数据"""
    try:
        session = Session()
        
        # 检查是否已有数据
        existing_data = session.query(ProductTraceability).first()
        
        if not existing_data:
            import random
            
            # 生成10个示例产品
            for i in range(10):
                product_id = f"LJY{datetime.now().strftime('%Y%m%d')}{str(i+1).zfill(3)}"
                
                planting_date = datetime.now() - timedelta(days=random.randint(200, 300))
                harvest_date = planting_date + timedelta(days=random.randint(150, 200))
                packaging_date = harvest_date + timedelta(days=random.randint(1, 10))
                
                product = ProductTraceability(
                    product_id=product_id,
                    qr_code=f"qr_code_{product_id}",
                    planting_date=planting_date,
                    harvest_date=harvest_date,
                    packaging_date=packaging_date,
                    location='郎家园示范基地',
                    fertilizer_records=[
                        {
                            'timestamp': (planting_date + timedelta(days=30)).isoformat(),
                            'fertilizer_type': '有机肥',
                            'fertilizer_name': '羊粪肥',
                            'amount': 50,
                            'unit': 'kg',
                            'operator': '张三'
                        },
                        {
                            'timestamp': (planting_date + timedelta(days=60)).isoformat(),
                            'fertilizer_type': '复合肥',
                            'fertilizer_name': 'NPK肥料',
                            'amount': 30,
                            'unit': 'kg',
                            'operator': '李四'
                        }
                    ],
                    pesticide_records=[
                        {
                            'timestamp': (planting_date + timedelta(days=90)).isoformat(),
                            'pesticide_name': '生物农药',
                            'target_pest': '蚜虫',
                            'amount': 200,
                            'unit': 'ml',
                            'safety_interval': 7,
                            'operator': '王五'
                        }
                    ],
                    processing_records=[
                        {
                            'timestamp': harvest_date.isoformat(),
                            'processing_type': '收获',
                            'yield_amount': random.randint(800, 1200),
                            'unit': 'kg',
                            'quality_grade': 'A级',
                            'operator': '赵六'
                        }
                    ],
                    transport_records=[
                        {
                            'timestamp': (packaging_date + timedelta(days=1)).isoformat(),
                            'departure_location': '郎家园基地',
                            'destination': '北京市场',
                            'transport_method': '冷链运输',
                            'vehicle_info': {'license': '京A12345', 'type': '冷藏车'}
                        }
                    ],
                    quality_checks=[
                        {
                            'timestamp': packaging_date.isoformat(),
                            'check_type': '成品检测',
                            'quality_grade': 'A级',
                            'pass_status': True,
                            'test_results': {
                                'sugar_content': round(random.uniform(60.0, 70.0), 1),
                                'moisture_content': round(random.uniform(10.0, 15.0), 1),
                                'size': random.choice(['大果', '中果', '小果'])
                            },
                            'inspector': '质检员'
                        }
                    ]
                )
                
                session.add(product)
            
            session.commit()
            logging.info("Sample product traceability data created")
        
        else:
            logging.info("Product traceability data already exists")
        
        session.close()
        
    except Exception as e:
        logging.error(f"Error creating sample product traceability: {e}")
        raise

def create_sample_predictions(Session):
    """创建示例预测数据"""
    try:
        session = Session()
        
        # 检查是否已有数据
        existing_data = session.query(PredictionResult).first()
        
        if not existing_data:
            import random
            
            # 生成最近7天的预测数据
            base_date = datetime.now() - timedelta(days=7)
            
            for day in range(7):
                for hour in range(0, 24, 6):  # 每6小时一条预测
                    timestamp = base_date + timedelta(days=day, hours=hour)
                    
                    prediction = PredictionResult(
                        timestamp=timestamp,
                        prediction_type='pest_disease',
                        risk_level=round(random.uniform(0.0, 1.0), 3),
                        confidence=round(random.uniform(0.5, 0.95), 3),
                        environmental_factors={
                            'temperature': round(random.uniform(15.0, 35.0), 2),
                            'humidity': round(random.uniform(30.0, 90.0), 2),
                            'rainfall': round(random.uniform(0.0, 50.0), 2)
                        },
                        location='郎家园示范基地',
                        model_version='1.0'
                    )
                    
                    session.add(prediction)
            
            session.commit()
            logging.info("Sample prediction data created")
        
        else:
            logging.info("Prediction data already exists")
        
        session.close()
        
    except Exception as e:
        logging.error(f"Error creating sample predictions: {e}")
        raise

def create_sample_warnings(Session):
    """创建示例预警数据"""
    try:
        session = Session()
        
        # 检查是否已有数据
        existing_data = session.query(WarningRecord).first()
        
        if not existing_data:
            import random
            
            warning_types = ['temperature_high', 'temperature_low', 'humidity_high', 
                           'soil_moisture_low', 'pest_disease_risk']
            severities = ['low', 'medium', 'high']
            
            # 生成最近30天的预警数据
            base_date = datetime.now() - timedelta(days=30)
            
            for i in range(30):  # 生成30条预警记录
                timestamp = base_date + timedelta(days=random.randint(0, 29), hours=random.randint(0, 23))
                
                warning_type = random.choice(warning_types)
                severity = random.choice(severities)
                
                warning = WarningRecord(
                    timestamp=timestamp,
                    warning_type=warning_type,
                    severity=severity,
                    message=f"{warning_type}预警：{severity}级别",
                    location='郎家园示范基地',
                    status=random.choice(['active', 'resolved']),
                    sent_notifications={
                        'email': ['admin@langjiayuan.com'],
                        'sms': [],
                        'push': []
                    }
                )
                
                session.add(warning)
            
            session.commit()
            logging.info("Sample warning data created")
        
        else:
            logging.info("Warning data already exists")
        
        session.close()
        
    except Exception as e:
        logging.error(f"Error creating sample warnings: {e}")
        raise

def main():
    """主函数"""
    try:
        # 配置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        logging.info("Starting database initialization...")
        
        # 创建数据库表
        engine, Session = create_tables()
        
        # 创建基础数据
        create_admin_user(Session)
        create_sample_users(Session)
        
        # 创建示例数据
        create_sample_environmental_data(Session)
        create_sample_pest_disease_data(Session)
        create_sample_market_data(Session)
        create_sample_product_traceability(Session)
        create_sample_predictions(Session)
        create_sample_warnings(Session)
        
        logging.info("Database initialization completed successfully!")
        
        # 输出初始化信息
        print("\n" + "="*50)
        print("数据库初始化完成！")
        print("="*50)
        print("管理员账号:")
        print("  用户名: admin")
        print("  密码: admin123")
        print("  邮箱: admin@langjiayuan.com")
        print("\n示例用户账号:")
        print("  farmer1 / farmer123")
        print("  technician1 / tech123")
        print("  manager1 / manager123")
        print("\n系统功能:")
        print("  - 环境监测与数据采集")
        print("  - 病虫害预测与预警")
        print("  - 绿色防控决策支持")
        print("  - 市场分析与品牌推广")
        print("  - 产品追溯与数据管理")
        print("\n启动应用:")
        print("  python app.py")
        print("  访问: http://localhost:5000")
        print("="*50)
        
    except Exception as e:
        logging.error(f"Database initialization failed: {e}")
        raise

if __name__ == "__main__":
    main() 