import sqlite3
import logging
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
import time

class HardwareSensorManager:
    """硬件传感器管理器（简化版 - 使用模拟数据）"""
    
    def __init__(self, config):
        self.config = config
        self.sensors = {
            'temperature': True,
            'humidity': True, 
            'soil_moisture': True,
            'light_intensity': True,
            'wind_speed': True,
            'rainfall': True,
            'air_pressure': True
        }
        
        # 模拟传感器状态
        self.sensor_status = {
            'temperature': 'active',
            'humidity': 'active',
            'soil_moisture': 'active', 
            'light_intensity': 'active',
            'wind_speed': 'active',
            'rainfall': 'active',
            'air_pressure': 'active'
        }
        
        logging.info("硬件传感器管理器初始化完成（模拟模式）")
    
    def read_temperature(self) -> float:
        """读取温度传感器数据（模拟）"""
        try:
            # 模拟温度数据，考虑时间因素
            current_hour = datetime.now().hour
            if 6 <= current_hour <= 18:  # 白天
                base_temp = 25 + (current_hour - 12) * 0.5
            else:  # 夜间
                base_temp = 18 + random.uniform(-2, 2)
            
            temperature = base_temp + random.uniform(-3, 3)
            return round(temperature, 1)
        except Exception as e:
            logging.error(f"温度传感器读取失败: {e}")
            return 25.0
    
    def read_humidity(self) -> float:
        """读取湿度传感器数据（模拟）"""
        try:
            # 模拟湿度数据
            humidity = random.uniform(45, 85)
            return round(humidity, 1)
        except Exception as e:
            logging.error(f"湿度传感器读取失败: {e}")
            return 65.0
    
    def read_soil_moisture(self) -> float:
        """读取土壤湿度传感器数据（模拟）"""
        try:
            # 模拟土壤湿度
            soil_moisture = random.uniform(40, 85)
            return round(soil_moisture, 1)
        except Exception as e:
            logging.error(f"土壤湿度传感器读取失败: {e}")
            return 70.0
    
    def read_light_intensity(self) -> float:
        """读取光照强度传感器数据（模拟）"""
        try:
            current_hour = datetime.now().hour
            if 6 <= current_hour <= 18:  # 白天
                light_intensity = random.uniform(600, 1200)
            else:  # 夜间
                light_intensity = random.uniform(0, 50)
            
            return round(light_intensity, 1)
        except Exception as e:
            logging.error(f"光照强度传感器读取失败: {e}")
            return 800.0
    
    def read_wind_speed(self) -> float:
        """读取风速传感器数据（模拟）"""
        try:
            wind_speed = random.uniform(0, 12)
            return round(wind_speed, 1)
        except Exception as e:
            logging.error(f"风速传感器读取失败: {e}")
            return 5.0
    
    def read_rainfall(self) -> float:
        """读取降雨传感器数据（模拟）"""
        try:
            # 降雨概率较低
            if random.random() < 0.15:
                rainfall = random.uniform(0.1, 8.0)
            else:
                rainfall = 0.0
            return round(rainfall, 1)
        except Exception as e:
            logging.error(f"降雨传感器读取失败: {e}")
            return 0.0
    
    def read_air_pressure(self) -> float:
        """读取气压传感器数据（模拟）"""
        try:
            air_pressure = random.uniform(990, 1030)
            return round(air_pressure, 2)
        except Exception as e:
            logging.error(f"气压传感器读取失败: {e}")
            return 1013.25
    
    def collect_all_sensor_data(self) -> Dict:
        """收集所有传感器数据"""
        try:
            data = {
                'timestamp': datetime.now().isoformat(),
                'temperature': self.read_temperature(),
                'humidity': self.read_humidity(),
                'soil_moisture': self.read_soil_moisture(),
                'light_intensity': self.read_light_intensity(),
                'wind_speed': self.read_wind_speed(),
                'rainfall': self.read_rainfall(),
                'air_pressure': self.read_air_pressure()
            }
            
            logging.info(f"传感器数据收集完成: {data}")
            return data
        except Exception as e:
            logging.error(f"传感器数据收集失败: {e}")
            return {}
    
    def get_sensor_status(self) -> Dict:
        """获取传感器状态"""
        return self.sensor_status
    
    def test_all_sensors(self) -> Dict:
        """测试所有传感器"""
        try:
            test_results = {}
            
            for sensor_name in self.sensors:
                try:
                    # 模拟传感器测试
                    test_results[sensor_name] = {
                        'status': 'ok',
                        'value': getattr(self, f'read_{sensor_name}')(),
                        'message': '传感器工作正常'
                    }
                except Exception as e:
                    test_results[sensor_name] = {
                        'status': 'error',
                        'value': None,
                        'message': f'传感器测试失败: {e}'
                    }
            
            return test_results
        except Exception as e:
            logging.error(f"传感器测试失败: {e}")
            return {}

class DataCollector:
    """数据收集器（简化硬件，保留其他功能）"""
    
    def __init__(self, config):
        self.config = config
        self.sensor_manager = HardwareSensorManager(config)
        self.database_path = config.DATABASE_URL.replace('sqlite:///', '')
        
        # 初始化数据库
        self.init_database()
        
        logging.info("数据收集器初始化完成")
    
    def init_database(self):
        """初始化数据库"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # 创建环境数据表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS environmental_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    temperature REAL NOT NULL,
                    humidity REAL NOT NULL,
                    soil_moisture REAL NOT NULL,
                    light_intensity REAL NOT NULL,
                    wind_speed REAL NOT NULL,
                    rainfall REAL NOT NULL,
                    air_pressure REAL NOT NULL
                )
            ''')
            
            # 创建设备状态表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS device_status (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    device_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    message TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logging.info("数据库初始化完成")
        except Exception as e:
            logging.error(f"数据库初始化失败: {e}")
    
    def collect_environmental_data(self) -> Dict:
        """收集环境数据"""
        try:
            # 使用简化的传感器管理器
            data = self.sensor_manager.collect_all_sensor_data()
            
            if data:
                # 保存到数据库
                self.save_environmental_data(data)
                
                logging.info(f"环境数据收集完成: {data}")
                return data
            else:
                logging.warning("环境数据收集失败")
                return {}
        except Exception as e:
            logging.error(f"环境数据收集失败: {e}")
            return {}
    
    def save_environmental_data(self, data: Dict):
        """保存环境数据到数据库"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO environmental_data 
                (timestamp, temperature, humidity, soil_moisture, light_intensity, 
                 wind_speed, rainfall, air_pressure)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data['timestamp'],
                data['temperature'],
                data['humidity'],
                data['soil_moisture'],
                data['light_intensity'],
                data['wind_speed'],
                data['rainfall'],
                data['air_pressure']
            ))
            
            conn.commit()
            conn.close()
            
            logging.info("环境数据保存成功")
        except Exception as e:
            logging.error(f"环境数据保存失败: {e}")
    
    def get_recent_data(self, hours: int = 24) -> List[Dict]:
        """获取最近的环境数据"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            start_time = datetime.now() - timedelta(hours=hours)
            
            cursor.execute('''
                SELECT timestamp, temperature, humidity, soil_moisture, 
                       light_intensity, wind_speed, rainfall, air_pressure
                FROM environmental_data 
                WHERE timestamp >= ?
                ORDER BY timestamp DESC
            ''', (start_time.isoformat(),))
            
            rows = cursor.fetchall()
            conn.close()
            
            data = []
            for row in rows:
                data.append({
                    'timestamp': row[0],
                    'temperature': row[1],
                    'humidity': row[2],
                    'soil_moisture': row[3],
                    'light_intensity': row[4],
                    'wind_speed': row[5],
                    'rainfall': row[6],
                    'air_pressure': row[7]
                })
            
            return data
        except Exception as e:
            logging.error(f"获取历史数据失败: {e}")
            return []
    
    def get_sensor_status(self) -> Dict:
        """获取传感器状态"""
        try:
            return self.sensor_manager.get_sensor_status()
        except Exception as e:
            logging.error(f"获取传感器状态失败: {e}")
            return {}
    
    def test_all_sensors(self) -> Dict:
        """测试所有传感器"""
        try:
            return self.sensor_manager.test_all_sensors()
        except Exception as e:
            logging.error(f"传感器测试失败: {e}")
            return {}
    
    def save_device_status(self, device_name: str, status: str, message: str = ""):
        """保存设备状态"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO device_status (timestamp, device_name, status, message)
                VALUES (?, ?, ?, ?)
            ''', (datetime.now().isoformat(), device_name, status, message))
            
            conn.commit()
            conn.close()
            
            logging.info(f"设备状态保存成功: {device_name} - {status}")
        except Exception as e:
            logging.error(f"设备状态保存失败: {e}")
    
    def get_device_status_history(self, device_name: str = None, hours: int = 24) -> List[Dict]:
        """获取设备状态历史"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            start_time = datetime.now() - timedelta(hours=hours)
            
            if device_name:
                cursor.execute('''
                    SELECT timestamp, device_name, status, message
                    FROM device_status 
                    WHERE device_name = ? AND timestamp >= ?
                    ORDER BY timestamp DESC
                ''', (device_name, start_time.isoformat()))
            else:
                cursor.execute('''
                    SELECT timestamp, device_name, status, message
                    FROM device_status 
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                ''', (start_time.isoformat(),))
            
            rows = cursor.fetchall()
            conn.close()
            
            data = []
            for row in rows:
                data.append({
                    'timestamp': row[0],
                    'device_name': row[1],
                    'status': row[2],
                    'message': row[3]
                })
            
            return data
        except Exception as e:
            logging.error(f"获取设备状态历史失败: {e}")
            return []
    
    def start_continuous_collection(self, interval: int = 300):
        """开始连续数据收集（5分钟间隔）"""
        try:
            logging.info(f"开始连续数据收集，间隔: {interval}秒")
            
            while True:
                # 收集环境数据
                environmental_data = self.collect_environmental_data()
                
                if environmental_data:
                    logging.info(f"数据收集成功: {environmental_data['timestamp']}")
                else:
                    logging.warning("数据收集失败")
                
                # 记录设备状态
                self.save_device_status("data_collector", "running", "数据收集正常")
                
                # 等待下一次收集
                time.sleep(interval)
                
        except KeyboardInterrupt:
            logging.info("数据收集停止")
        except Exception as e:
            logging.error(f"连续数据收集失败: {e}")
            self.save_device_status("data_collector", "error", str(e))
    
    def generate_test_data(self, days: int = 7):
        """生成测试数据"""
        try:
            logging.info(f"开始生成 {days} 天的测试数据")
            
            start_time = datetime.now() - timedelta(days=days)
            
            for i in range(days * 24):  # 每小时一个数据点
                timestamp = start_time + timedelta(hours=i)
                
                # 生成符合现实的模拟数据
                data = {
                    'timestamp': timestamp.isoformat(),
                    'temperature': round(20 + 10 * (0.5 + 0.5 * random.random()), 1),
                    'humidity': round(50 + 30 * random.random(), 1),
                    'soil_moisture': round(40 + 40 * random.random(), 1),
                    'light_intensity': round(500 + 500 * random.random(), 1),
                    'wind_speed': round(10 * random.random(), 1),
                    'rainfall': round(5 * random.random() if random.random() < 0.2 else 0, 1),
                    'air_pressure': round(1000 + 30 * random.random(), 2)
                }
                
                self.save_environmental_data(data)
            
            logging.info(f"测试数据生成完成，共 {days * 24} 个数据点")
            
        except Exception as e:
            logging.error(f"生成测试数据失败: {e}") 