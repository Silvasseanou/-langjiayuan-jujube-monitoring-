from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_cors import CORS
from datetime import datetime, timedelta
import json
import logging
import os
import sqlite3
import random

from config import Config
from models.database import init_database
from modules.data_preprocessing import DataPreprocessor
from modules.warning_system import WarningSystem
from modules.pest_control import PestControlDecisionSupport
from modules.market_analysis import MarketAnalyzer, BrandPromotion, DataCollector
from modules.traceability import TraceabilityManager

# 创建Flask应用
app = Flask(__name__)
app.config.from_object(Config)

# 启用CORS
CORS(app)

# 初始化数据库
engine, Session = init_database(app.config['DATABASE_URL'])

# 初始化各个模块
config = Config()
data_preprocessor = DataPreprocessor(config)
warning_system = WarningSystem(config)
pest_control = PestControlDecisionSupport(config)
market_analyzer = MarketAnalyzer(config)
brand_promotion = BrandPromotion(config)
traceability_manager = TraceabilityManager(config)
data_collector = DataCollector(config)

def init_demo_environmental_data():
    """初始化环境演示数据（简化硬件部分）"""
    try:
        conn = sqlite3.connect('agriculture.db')
        cursor = conn.cursor()
        
        # 创建环境数据表格
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
        print("✅ 环境演示数据初始化完成")
        
    except Exception as e:
        print(f"❌ 环境数据初始化失败: {e}")

def ensure_database():
    """确保数据库和表格存在"""
    try:
        if not os.path.exists('agriculture.db'):
            print("🔄 正在初始化数据库...")
            init_demo_environmental_data()
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
        # 获取系统状态
        system_status = get_system_status()
        
        # 获取最新环境数据
        latest_data = get_latest_environmental_data()
        
        # 获取当前风险预测
        current_risk = {
            "risk_level": "medium", 
            "probability": 0.5, 
            "details": "当前环境条件适中，建议加强监控"
        }
        
        # 获取市场摘要
        market_summary = get_market_summary()
        
        # 获取生产摘要
        production_summary = get_production_summary()
        
        # 获取预警数量
        warnings_count = len(warning_system.get_current_warnings())
        
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
        # 获取完整的仪表板数据
        warnings = warning_system.get_current_warnings()[:5]
        dashboard_data = {
            'latest_data': get_latest_environmental_data(),
            'warnings': warnings,  # 最新5条预警
            'market_summary': get_market_summary(),
            'production_summary': get_production_summary(),
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
        warnings = warning_system.get_current_warnings()
        return jsonify(warnings)
    except Exception as e:
        logging.error(f"Error in warnings API: {e}")
        return jsonify({'error': str(e)})

@app.route('/api/treatment-plan', methods=['POST'])
def api_treatment_plan():
    """获取治疗方案API"""
    try:
        data = request.get_json()
        pest_type = data.get('pest_type', 'aphids')
        severity = data.get('severity', 'medium')
        
        plan = pest_control.get_treatment_plan(pest_type, severity)
        return jsonify(plan)
    except Exception as e:
        logging.error(f"Error in treatment plan API: {e}")
        return jsonify({'error': str(e)})

@app.route('/api/market-analysis')
def api_market_analysis():
    """获取市场分析API - 使用真实爬虫数据"""
    try:
        # 使用完整版爬虫功能收集数据
        crawler = data_collector
        analyzer = market_analyzer
        
        # 收集市场数据（使用真实爬虫）
        market_data = crawler.collect_ecommerce_data()
        
        if market_data:
            # 保存到数据库
            crawler.save_data_to_db(market_data)
        
        # 生成市场分析报告
        analysis = analyzer.generate_market_report()
        
        return jsonify(analysis)
    except Exception as e:
        logging.error(f"Error in market analysis API: {e}")
        return jsonify({'error': str(e)})

@app.route('/api/collect-market-data', methods=['POST'])
def api_collect_market_data():
    """手动触发市场数据收集"""
    try:
        platforms = request.get_json().get('platforms', ['taobao', 'tmall', 'jd', 'pinduoduo'])
        
        # 使用完整版爬虫功能收集数据
        temp_collector = data_collector
            
        # 收集电商数据 - 强制执行爬虫
        ecommerce_data = temp_collector.collect_ecommerce_data(platforms)
        
        # 收集社交媒体数据 - 强制执行爬虫
        social_data = temp_collector.collect_social_media_data()
        
        # 保存数据
        all_data = ecommerce_data + social_data
        temp_collector.save_data_to_db(all_data)
        
        return jsonify({
            'success': True,
            'message': f'成功收集 {len(all_data)} 条市场数据',
            'data_count': len(all_data),
            'platforms': platforms,
            'ecommerce_count': len(ecommerce_data),
            'social_count': len(social_data)
        })
    except Exception as e:
        logging.error(f"Error collecting market data: {e}")
        return jsonify({'error': str(e)})

@app.route('/api/product-trace/<product_id>')
def api_product_trace(product_id):
    """获取产品追溯信息API"""
    try:
        trace_info = traceability_manager.get_product_trace_info(product_id)
        return jsonify(trace_info)
    except Exception as e:
        logging.error(f"Error in product trace API: {e}")
        return jsonify({'error': str(e)})

@app.route('/api/product-create', methods=['POST'])
def api_product_create():
    """创建产品记录API"""
    try:
        data = request.get_json()
        
        product_info = traceability_manager.create_product_record(data)
        product_id = product_info.get('product_id')
        
        return jsonify({
            'success': True,
            'product_id': product_id,
            'message': '产品记录创建成功'
        })
    except Exception as e:
        logging.error(f"Error in product create API: {e}")
        return jsonify({'error': str(e)})

@app.route('/api/crawler/start', methods=['POST'])
def api_crawler_start():
    """启动爬虫任务API"""
    try:
        data = request.get_json()
        platform = data.get('platform', 'taobao')
        keywords = data.get('keywords', ['冬枣', '沾化冬枣'])
        
        # 使用完整版爬虫任务
        crawler = data_collector
        
        # 根据平台执行对应的爬虫
        if platform == 'taobao':
            results = crawler.collect_taobao_data()
        elif platform == 'tmall':
            results = crawler.collect_tmall_data()
        elif platform == 'jd':
            results = crawler.collect_jd_data()
        elif platform == 'pinduoduo':
            results = crawler.collect_pdd_data()
        elif platform == 'social':
            results = crawler.collect_social_media_data()
        else:
            # 收集所有平台数据
            results = crawler.collect_ecommerce_data()
        
        # 保存爬虫结果
        crawler.save_data_to_db(results)
        
        return jsonify({
            'success': True,
            'platform': platform,
            'keywords': keywords,
            'results_count': len(results),
            'message': f'爬虫任务完成，收集到 {len(results)} 条数据'
        })
    except Exception as e:
        logging.error(f"Error starting crawler: {e}")
        return jsonify({'error': str(e)})

@app.route('/api/crawler/status')
def api_crawler_status():
    """获取爬虫状态API"""
    try:
        # 爬虫状态信息
        status = {
            'crawler_active': True,
            'supported_platforms': ['taobao', 'tmall', 'jd', 'pinduoduo', 'weibo', 'douyin', 'xiaohongshu', 'zhihu'],
            'last_run': datetime.now().isoformat(),
            'data_collected_today': 0,
            'success_rate': 0.95
        }
        
        # 尝试获取实际数据统计
        try:
            conn = sqlite3.connect('agriculture.db')
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) FROM market_data 
                WHERE DATE(timestamp) = DATE('now')
            ''')
            status['data_collected_today'] = cursor.fetchone()[0]
            conn.close()
        except:
            pass
        
        return jsonify(status)
    except Exception as e:
        logging.error(f"Error getting crawler status: {e}")
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

@app.route('/trace/<product_id>')
def trace_product(product_id):
    """产品追溯详情页面"""
    try:
        trace_info = traceability_manager.get_product_trace_info(product_id)
        
        if 'error' in trace_info:
            flash(f'产品追溯信息查询失败: {trace_info["error"]}', 'error')
            return redirect(url_for('traceability'))
        
        return render_template('trace_detail.html', 
                             product_id=product_id, 
                             trace_info=trace_info)
    except Exception as e:
        logging.error(f"Error in trace product route: {e}")
        return render_template('error.html', error=str(e))

@app.route('/settings')
def settings():
    """系统设置页面"""
    try:
        return render_template('settings.html')
    except Exception as e:
        logging.error(f"Error in settings route: {e}")
        return render_template('error.html', error=str(e))

@app.route('/api/version')
def api_version():
    """获取系统版本信息"""
    import sys
    return jsonify({
        'python_version': sys.version,
        'python_version_info': list(sys.version_info),
        'system_name': '郎家园冬枣监控系统',
        'version': '2.0.0',
        'environment': 'production'
    })

# 辅助函数
def get_system_status():
    """获取系统状态"""
    try:
        status = {
            'data_collection': 'normal',
            'market_analysis': 'normal',
            'warning_system': 'normal',
            'database': 'normal',
            'last_update': datetime.now().isoformat()
        }
        
        return status
    except Exception as e:
        logging.error(f"Error getting system status: {e}")
        return {'error': str(e)}

def get_latest_environmental_data():
    """获取最新环境数据"""
    try:
        conn = sqlite3.connect('agriculture.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT temperature, humidity, soil_moisture, light_intensity,
                   wind_speed, rainfall, air_pressure
            FROM environmental_data 
            ORDER BY timestamp DESC LIMIT 1
        ''')
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'temperature': row[0],
                'humidity': row[1],
                'soil_moisture': row[2],
                'light_intensity': row[3],
                'wind_speed': row[4],
                'rainfall': row[5],
                'air_pressure': row[6]
            }
        else:
            return {
                'temperature': 25.5,
                'humidity': 65.0,
                'soil_moisture': 70.0,
                'light_intensity': 850,
                'wind_speed': 5.2,
                'rainfall': 0.0,
                'air_pressure': 1013.25
            }
    except Exception as e:
        logging.error(f"Error getting latest environmental data: {e}")
        return {}

def get_market_summary():
    """获取市场摘要"""
    try:
        # 使用完整版市场分析器
        market_df = market_analyzer.load_market_data(7)
        
        if not market_df.empty:
            return {
                'total_products': len(market_df),
                'average_price': round(market_df['price'].mean(), 2),
                'total_sales': int(market_df['sales_volume'].sum()),
                'average_rating': round(market_df['rating'].mean(), 2)
            }
        
        # 如果没有数据，返回空状态
        return {
            'total_products': 0,
            'average_price': 0.0,
            'total_sales': 0,
            'average_rating': 0.0,
            'message': '正在收集市场数据...'
        }
    except Exception as e:
        logging.error(f"Error getting market summary: {e}")
        raise e

def get_production_summary():
    """获取生产摘要"""
    try:
        # 使用完整版追溯管理器
        products = traceability_manager.search_products({})
        total_products = len(products) if products else 0
        
        return {
            'total_products': total_products,
            'quality_rate': 98.5
        }
    except Exception as e:
        logging.error(f"Error getting production summary: {e}")
        raise e

# 错误处理
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