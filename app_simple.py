from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import json
import logging
import os
import sqlite3
import random

# 创建Flask应用
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['DATABASE_URL'] = 'sqlite:///agriculture.db'

# 启用CORS
CORS(app)

def init_demo_data():
    """初始化演示数据"""
    try:
        conn = sqlite3.connect('agriculture.db')
        cursor = conn.cursor()
        
        # 创建表格
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
        
        # 检查是否已有数据
        cursor.execute('SELECT COUNT(*) FROM environmental_data')
        count = cursor.fetchone()[0]
        
        if count == 0:
            # 生成演示数据
            for i in range(168):  # 一周的小时数据
                timestamp = datetime.now() - timedelta(hours=i)
                temperature = round(random.uniform(15, 35), 1)
                humidity = round(random.uniform(40, 80), 1)
                soil_moisture = round(random.uniform(30, 80), 1)
                light_intensity = round(random.uniform(200, 1000), 1)
                wind_speed = round(random.uniform(0, 15), 1)
                rainfall = round(random.uniform(0, 5) if random.random() < 0.2 else 0, 1)
                air_pressure = round(random.uniform(995, 1025), 2)
                
                cursor.execute('''
                    INSERT INTO environmental_data 
                    (timestamp, temperature, humidity, soil_moisture, light_intensity, 
                     wind_speed, rainfall, air_pressure)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (timestamp, temperature, humidity, soil_moisture, light_intensity,
                      wind_speed, rainfall, air_pressure))
        
        conn.commit()
        conn.close()
        print("✅ 演示数据初始化完成")
        
    except Exception as e:
        print(f"❌ 数据初始化失败: {e}")

def ensure_database():
    """确保数据库和表格存在"""
    try:
        if not os.path.exists('agriculture.db') or os.path.getsize('agriculture.db') == 0:
            print("🔄 正在初始化演示数据...")
            init_demo_data()
        else:
            # 确保表格存在
            conn = sqlite3.connect('agriculture.db')
            cursor = conn.cursor()
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
            conn.commit()
            conn.close()
            print("✅ 数据库表格检查完成")
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")

# 应用启动时立即初始化数据库
ensure_database()

@app.route('/')
def index():
    """首页"""
    try:
        # 模拟系统状态
        system_status = {
            'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'data_collection': 'normal',
            'warning_system': 'normal',
            'database': 'normal'
        }
        
        # 模拟最新数据
        latest_data = {
            'temperature': 25.5,
            'humidity': 65.0,
            'soil_moisture': 70.0,
            'light_intensity': 850,
            'wind_speed': 5.2,
            'rainfall': 0.0,
            'air_pressure': 1013.25
        }
        
        # 模拟当前风险预测
        current_risk = {
            "risk_level": "medium", 
            "probability": 0.5, 
            "details": "当前环境条件适中，建议加强监控"
        }
        
        # 模拟市场摘要
        market_summary = {
            'average_price': 35.6,
            'total_sales': 1234
        }
        
        # 模拟生产摘要
        production_summary = {
            'total_products': 1234,
            'quality_rate': 98.5
        }
        
        # 模拟预警数量
        warnings_count = 2
        
        return render_template('index.html', 
                             system_status=system_status,
                             latest_data=latest_data,
                             current_risk=current_risk,
                             market_summary=market_summary,
                             production_summary=production_summary,
                             warnings_count=warnings_count)
    except Exception as e:
        logging.error(f"Error in index route: {e}")
        return render_template('error.html', error=str(e))

@app.route('/dashboard')
def dashboard():
    """仪表板"""
    try:
        # 模拟数据
        dashboard_data = {
            'latest_data': {
                'temperature': 25.5,
                'humidity': 65.0,
                'soil_moisture': 70.0,
                'light_intensity': 850,
                'wind_speed': 5.2,
                'rainfall': 0.0,
                'air_pressure': 1013.25
            },
            'warnings': [
                {'type': 'pest', 'message': '蚜虫风险中等', 'level': 'warning'},
                {'type': 'environment', 'message': '土壤湿度偏低', 'level': 'info'}
            ],
            'market_summary': {
                'average_price': 35.6,
                'total_sales': 1234
            },
            'production_summary': {
                'total_products': 1234,
                'quality_rate': 98.5
            },
            'current_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return render_template('dashboard.html', **dashboard_data)
    except Exception as e:
        logging.error(f"Error in dashboard route: {e}")
        return render_template('error.html', error=str(e))

@app.route('/api/environmental-data')
def api_environmental_data():
    """获取环境数据API"""
    try:
        days = request.args.get('days', 7, type=int)
        
        # 确保数据库和表格存在
        ensure_database()
        
        conn = sqlite3.connect('agriculture.db')
        cursor = conn.cursor()
        
        start_date = datetime.now() - timedelta(days=days)
        cursor.execute('''
            SELECT timestamp, temperature, humidity, soil_moisture, 
                   light_intensity, wind_speed, rainfall, air_pressure
            FROM environmental_data 
            WHERE timestamp >= ? 
            ORDER BY timestamp
        ''', (start_date,))
        
        data = cursor.fetchall()
        conn.close()
        
        if not data:
            return jsonify({'error': 'No data available'})
        
        # 格式化数据
        timestamps = [row[0] for row in data]
        temperatures = [row[1] for row in data]
        humidities = [row[2] for row in data]
        soil_moistures = [row[3] for row in data]
        light_intensities = [row[4] for row in data]
        wind_speeds = [row[5] for row in data]
        rainfalls = [row[6] for row in data]
        air_pressures = [row[7] for row in data]
        
        return jsonify({
            'timestamps': timestamps,
            'temperature': temperatures,
            'humidity': humidities,
            'soil_moisture': soil_moistures,
            'light_intensity': light_intensities,
            'wind_speed': wind_speeds,
            'rainfall': rainfalls,
            'air_pressure': air_pressures
        })
    except Exception as e:
        logging.error(f"Error in environmental data API: {e}")
        return jsonify({'error': str(e)})

@app.route('/api/predictions')
def api_predictions():
    """获取预测结果API"""
    try:
        prediction = {
            "timestamp": datetime.now().isoformat(),
            "pest_risk": {
                "aphids": 0.7,
                "spider_mites": 0.3,
                "scale_insects": 0.2
            },
            "disease_risk": {
                "powdery_mildew": 0.6,
                "rust": 0.4,
                "leaf_spot": 0.3
            },
            "overall_risk": 0.5,
            "risk_level": "medium"
        }
        
        return jsonify(prediction)
    except Exception as e:
        logging.error(f"Error in predictions API: {e}")
        return jsonify({'error': str(e)})

@app.route('/api/warnings')
def api_warnings():
    """获取预警信息API"""
    try:
        warnings = [
            {
                'id': 1,
                'type': 'pest',
                'level': 'warning',
                'message': '蚜虫风险中等，建议加强监控',
                'timestamp': datetime.now().isoformat()
            },
            {
                'id': 2,
                'type': 'environment',
                'level': 'info',
                'message': '土壤湿度偏低，建议适当浇水',
                'timestamp': (datetime.now() - timedelta(hours=2)).isoformat()
            }
        ]
        
        return jsonify(warnings)
    except Exception as e:
        logging.error(f"Error in warnings API: {e}")
        return jsonify({'error': str(e)})

@app.route('/api/market-analysis')
def api_market_analysis():
    """获取市场分析API"""
    try:
        analysis = {
            'average_price': 35.6,
            'total_sales': 1234,
            'market_trend': 'stable',
            'recommendations': ['优化产品质量', '扩大销售渠道']
        }
        
        return jsonify(analysis)
    except Exception as e:
        logging.error(f"Error in market analysis API: {e}")
        return jsonify({'error': str(e)})

@app.route('/monitoring')
def monitoring():
    """环境监测页面"""
    try:
        return render_template('monitoring.html')
    except Exception as e:
        logging.error(f"Error in monitoring route: {e}")
        return render_template('error.html', error=str(e))

@app.route('/predictions')
def predictions():
    """预测分析页面"""
    try:
        return render_template('predictions.html')
    except Exception as e:
        logging.error(f"Error in predictions route: {e}")
        return render_template('error.html', error=str(e))

@app.route('/warnings')
def warnings():
    """预警系统页面"""
    try:
        return render_template('warnings.html')
    except Exception as e:
        logging.error(f"Error in warnings route: {e}")
        return render_template('error.html', error=str(e))

@app.route('/pest-control')
def pest_control_page():
    """绿色防控页面"""
    try:
        return render_template('pest_control.html')
    except Exception as e:
        logging.error(f"Error in pest control route: {e}")
        return render_template('error.html', error=str(e))

@app.route('/market-analysis')
def market_analysis():
    """市场分析页面"""
    try:
        return render_template('market_analysis.html')
    except Exception as e:
        logging.error(f"Error in market analysis route: {e}")
        return render_template('error.html', error=str(e))

@app.route('/traceability')
def traceability():
    """产品追溯页面"""
    try:
        return render_template('traceability.html')
    except Exception as e:
        logging.error(f"Error in traceability route: {e}")
        return render_template('error.html', error=str(e))

@app.route('/settings')
def settings():
    """系统设置页面"""
    try:
        return render_template('settings.html')
    except Exception as e:
        logging.error(f"Error in settings route: {e}")
        return render_template('error.html', error=str(e))

@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', error='页面未找到'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error='内部服务器错误'), 500

if __name__ == '__main__':
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 启动应用
    port = int(os.environ.get('PORT', 8080))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False
    ) 