#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
演示数据初始化脚本
用于在部署后生成示例数据
"""

import sqlite3
import random
from datetime import datetime, timedelta

def init_demo_data():
    """初始化演示数据"""
    try:
        # 连接数据库
        conn = sqlite3.connect('agriculture.db')
        cursor = conn.cursor()
        
        # 创建表格（如果不存在）
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
                air_pressure REAL NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS warnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                level TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                status TEXT DEFAULT 'active',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                variety TEXT NOT NULL,
                planting_date DATE NOT NULL,
                harvest_date DATE,
                quality_grade TEXT,
                weight REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 生成过去30天的环境数据
        print("正在生成环境数据...")
        for i in range(30 * 24):  # 30天，每小时一条记录
            timestamp = datetime.now() - timedelta(hours=i)
            
            # 生成合理的数据范围
            temperature = round(random.uniform(15, 35), 1)
            humidity = round(random.uniform(40, 80), 1)
            soil_moisture = round(random.uniform(30, 80), 1)
            light_intensity = round(random.uniform(200, 1000), 1)
            wind_speed = round(random.uniform(0, 15), 1)
            rainfall = round(random.uniform(0, 10) if random.random() < 0.2 else 0, 1)
            air_pressure = round(random.uniform(995, 1025), 2)
            
            cursor.execute('''
                INSERT OR REPLACE INTO environmental_data 
                (timestamp, temperature, humidity, soil_moisture, light_intensity, 
                 wind_speed, rainfall, air_pressure)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (timestamp, temperature, humidity, soil_moisture, light_intensity,
                  wind_speed, rainfall, air_pressure))
        
        # 生成预警信息
        print("正在生成预警信息...")
        warnings = [
            ('pest', 'warning', '蚜虫风险中等，建议加强监控'),
            ('disease', 'info', '枣疯病风险较低，环境条件良好'),
            ('environment', 'warning', '土壤湿度偏低，建议适当浇水'),
            ('weather', 'info', '未来3天天气晴朗，适合采摘'),
            ('pest', 'alert', '红蜘蛛密度增加，建议及时防治'),
        ]
        
        for warning_type, level, message in warnings:
            timestamp = datetime.now() - timedelta(hours=random.randint(1, 48))
            cursor.execute('''
                INSERT OR REPLACE INTO warnings (type, level, message, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (warning_type, level, message, timestamp))
        
        # 生成产品追溯信息
        print("正在生成产品追溯信息...")
        varieties = ['金丝小枣', '冬枣', '灰枣', '骏枣', '梨枣']
        
        for i in range(50):
            product_id = f"LJY{datetime.now().year}{i+1:04d}"
            name = f"郎家园{random.choice(varieties)}"
            variety = random.choice(varieties)
            planting_date = datetime.now() - timedelta(days=random.randint(100, 300))
            harvest_date = planting_date + timedelta(days=random.randint(180, 250))
            quality_grade = random.choice(['A', 'B', 'C'])
            weight = round(random.uniform(0.5, 5.0), 2)
            
            cursor.execute('''
                INSERT OR REPLACE INTO products 
                (product_id, name, variety, planting_date, harvest_date, 
                 quality_grade, weight)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (product_id, name, variety, planting_date, harvest_date,
                  quality_grade, weight))
        
        # 提交事务
        conn.commit()
        conn.close()
        
        print("✅ 演示数据初始化完成！")
        print(f"📊 已生成 {30 * 24} 条环境数据")
        print(f"⚠️  已生成 {len(warnings)} 条预警信息")
        print(f"🏷️  已生成 50 条产品追溯信息")
        
    except Exception as e:
        print(f"❌ 数据初始化失败: {e}")
        
if __name__ == "__main__":
    init_demo_data() 