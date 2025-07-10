import time
import json
import logging
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional
import schedule
import requests

# 树莓派GPIO库（在非树莓派环境中会模拟）
try:
    import RPi.GPIO as GPIO
    import spidev
except ImportError:
    print("RPi.GPIO not available, using mock GPIO")
    class MockGPIO:
        def setmode(self, mode): pass
        def setup(self, pin, mode): pass
        def input(self, pin): return 0.5
        def output(self, pin, value): pass
        def cleanup(self): pass
        BCM = 'BCM'
        IN = 'IN'
        OUT = 'OUT'
    GPIO = MockGPIO()
    
    class MockSpiDev:
        def open(self, bus, device): pass
        def xfer(self, data): return [128, 0]
        def close(self): pass
    spidev = type('MockSpiDev', (), {'SpiDev': MockSpiDev})()

from config import Config
from models.database import EnvironmentData, init_database

class SensorManager:
    """传感器管理器"""
    
    def __init__(self, config: Config):
        self.config = config
        self.sensors = {}
        self.setup_sensors()
        
    def setup_sensors(self):
        """初始化传感器"""
        GPIO.setmode(GPIO.BCM)
        
        # 初始化各类传感器
        for sensor_name, sensor_config in self.config.SENSOR_CONFIG.items():
            if sensor_config['type'] == 'DS18B20':
                self.sensors[sensor_name] = DS18B20Sensor(sensor_config['pin'])
            elif sensor_config['type'] == 'DHT22':
                self.sensors[sensor_name] = DHT22Sensor(sensor_config['pin'])
            elif sensor_config['type'] == 'capacitive':
                self.sensors[sensor_name] = CapacitiveSensor(sensor_config['pin'])
            elif sensor_config['type'] == 'photoresistor':
                self.sensors[sensor_name] = PhotoresistorSensor(sensor_config['pin'])
    
    def read_all_sensors(self) -> Dict:
        """读取所有传感器数据"""
        data = {}
        for sensor_name, sensor in self.sensors.items():
            try:
                data[sensor_name] = sensor.read()
            except Exception as e:
                logging.error(f"Error reading sensor {sensor_name}: {e}")
                data[sensor_name] = None
        return data
    
    def cleanup(self):
        """清理GPIO资源"""
        GPIO.cleanup()

class DS18B20Sensor:
    """DS18B20温度传感器"""
    
    def __init__(self, pin: int):
        self.pin = pin
        self.device_file = f'/sys/bus/w1/devices/28-*/w1_slave'
        
    def read(self) -> float:
        """读取温度值"""
        try:
            # 实际硬件中会读取文件
            # 这里返回模拟值
            import random
            return round(random.uniform(20.0, 30.0), 2)
        except Exception as e:
            logging.error(f"DS18B20 read error: {e}")
            return None

class DHT22Sensor:
    """DHT22温湿度传感器"""
    
    def __init__(self, pin: int):
        self.pin = pin
        GPIO.setup(pin, GPIO.IN)
        
    def read(self) -> tuple:
        """读取温湿度值"""
        try:
            # 实际硬件中会通过GPIO读取DHT22数据
            # 这里返回模拟值
            import random
            temperature = round(random.uniform(18.0, 35.0), 2)
            humidity = round(random.uniform(40.0, 80.0), 2)
            return temperature, humidity
        except Exception as e:
            logging.error(f"DHT22 read error: {e}")
            return None, None

class CapacitiveSensor:
    """电容式土壤湿度传感器"""
    
    def __init__(self, pin: int):
        self.pin = pin
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        
    def read(self) -> float:
        """读取土壤湿度值"""
        try:
            # 通过SPI读取ADC值
            adc_value = self.spi.xfer([1, 8, 0])
            moisture = ((adc_value[1] & 3) << 8) + adc_value[2]
            # 转换为百分比
            moisture_percent = (moisture / 1023.0) * 100
            return round(moisture_percent, 2)
        except Exception as e:
            logging.error(f"Capacitive sensor read error: {e}")
            return None

class PhotoresistorSensor:
    """光敏电阻传感器"""
    
    def __init__(self, pin: int):
        self.pin = pin
        
    def read(self) -> float:
        """读取光照强度"""
        try:
            # 实际硬件中会读取ADC值
            # 这里返回模拟值
            import random
            return round(random.uniform(100.0, 1000.0), 2)
        except Exception as e:
            logging.error(f"Photoresistor read error: {e}")
            return None

class WeatherDataCollector:
    """天气数据收集器"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        
    def get_weather_data(self, location: str = "Beijing") -> Dict:
        """获取天气数据"""
        try:
            # 模拟天气数据，实际应用中应使用真实的天气API
            import random
            return {
                'wind_speed': round(random.uniform(0.0, 20.0), 2),
                'rainfall': round(random.uniform(0.0, 50.0), 2),
                'air_pressure': round(random.uniform(980.0, 1020.0), 2),
                'location': location
            }
        except Exception as e:
            logging.error(f"Weather data collection error: {e}")
            return {}

class DataCollector:
    """数据收集器主类"""
    
    def __init__(self, config: Config):
        self.config = config
        self.sensor_manager = SensorManager(config)
        self.weather_collector = WeatherDataCollector()
        self.engine, self.Session = init_database(config.DATABASE_URL)
        
    def collect_data(self) -> Dict:
        """收集所有数据"""
        try:
            # 收集传感器数据
            sensor_data = self.sensor_manager.read_all_sensors()
            
            # 收集天气数据
            weather_data = self.weather_collector.get_weather_data()
            
            # 合并数据
            all_data = {
                'timestamp': datetime.utcnow(),
                'temperature': sensor_data.get('temperature'),
                'humidity': sensor_data.get('humidity', (None, None))[1],
                'soil_moisture': sensor_data.get('soil_moisture'),
                'light_intensity': sensor_data.get('light'),
                'wind_speed': weather_data.get('wind_speed'),
                'rainfall': weather_data.get('rainfall'),
                'air_pressure': weather_data.get('air_pressure'),
                'location': weather_data.get('location', 'Default'),
                'sensor_id': 'sensor_001'
            }
            
            logging.info(f"Collected data: {all_data}")
            return all_data
            
        except Exception as e:
            logging.error(f"Data collection error: {e}")
            return {}
    
    def save_to_database(self, data: Dict):
        """保存数据到数据库"""
        try:
            session = self.Session()
            
            env_data = EnvironmentData(
                timestamp=data['timestamp'],
                temperature=data['temperature'],
                humidity=data['humidity'],
                soil_moisture=data['soil_moisture'],
                light_intensity=data['light_intensity'],
                wind_speed=data['wind_speed'],
                rainfall=data['rainfall'],
                air_pressure=data['air_pressure'],
                location=data['location'],
                sensor_id=data['sensor_id']
            )
            
            session.add(env_data)
            session.commit()
            session.close()
            
            logging.info("Data saved to database successfully")
            
        except Exception as e:
            logging.error(f"Database save error: {e}")
    
    def collect_and_save(self):
        """收集并保存数据"""
        data = self.collect_data()
        if data:
            self.save_to_database(data)
    
    def start_scheduled_collection(self, interval_minutes: int = 10):
        """启动定时数据收集"""
        schedule.every(interval_minutes).minutes.do(self.collect_and_save)
        
        logging.info(f"Started scheduled data collection every {interval_minutes} minutes")
        
        while True:
            schedule.run_pending()
            time.sleep(1)
    
    def cleanup(self):
        """清理资源"""
        self.sensor_manager.cleanup()

# 使用示例
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    config = Config()
    collector = DataCollector(config)
    
    try:
        # 收集一次数据
        collector.collect_and_save()
        
        # 启动定时收集（可选）
        # collector.start_scheduled_collection(interval_minutes=5)
        
    except KeyboardInterrupt:
        logging.info("Data collection stopped by user")
    finally:
        collector.cleanup() 