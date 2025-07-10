from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_cors import CORS
from datetime import datetime, timedelta
import json
import logging
import os

from config import Config
from models.database import init_database
from modules.data_collection import DataCollector
from modules.data_preprocessing import DataPreprocessor
# from modules.ml_models import PestDiseasePredictor
from modules.warning_system import WarningSystem
from modules.pest_control import PestControlDecisionSupport
from modules.market_analysis import MarketAnalyzer, BrandPromotion
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
data_collector = DataCollector(config)
data_preprocessor = DataPreprocessor(config)
# ml_predictor = PestDiseasePredictor(config)
warning_system = WarningSystem(config)
pest_control = PestControlDecisionSupport(config)
market_analyzer = MarketAnalyzer(config)
brand_promotion = BrandPromotion(config)
traceability_manager = TraceabilityManager(config)

# 加载机器学习模型
# ml_predictor.load_models()

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
        # 模拟数据，避免依赖可能不存在的方法
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
        
        df = data_preprocessor.load_data_from_db(
            start_date=datetime.now() - timedelta(days=days)
        )
        
        if df.empty:
            return jsonify({'error': 'No data available'})
        
        # 按小时聚合数据
        df['hour'] = df['timestamp'].dt.floor('H')
        hourly_data = df.groupby('hour').agg({
            'temperature': 'mean',
            'humidity': 'mean',
            'soil_moisture': 'mean',
            'light_intensity': 'mean',
            'wind_speed': 'mean',
            'rainfall': 'sum',
            'air_pressure': 'mean'
        }).round(2)
        
        return jsonify({
            'timestamps': hourly_data.index.strftime('%Y-%m-%d %H:%M').tolist(),
            'temperature': hourly_data['temperature'].tolist(),
            'humidity': hourly_data['humidity'].tolist(),
            'soil_moisture': hourly_data['soil_moisture'].tolist(),
            'light_intensity': hourly_data['light_intensity'].tolist(),
            'wind_speed': hourly_data['wind_speed'].tolist(),
            'rainfall': hourly_data['rainfall'].tolist(),
            'air_pressure': hourly_data['air_pressure'].tolist()
        })
    except Exception as e:
        logging.error(f"Error in environmental data API: {e}")
        return jsonify({'error': str(e)})

@app.route('/api/predictions')
def api_predictions():
    """获取预测结果API"""
    try:
        # prediction = ml_predictor.predict_current_risk()
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
        
        if not prediction:
            return jsonify({'error': 'No prediction available'})
        
        return jsonify(prediction)
    except Exception as e:
        logging.error(f"Error in predictions API: {e}")
        return jsonify({'error': str(e)})

@app.route('/api/warnings')
def api_warnings():
    """获取预警信息API"""
    try:
        env_warnings = warning_system.check_environmental_thresholds()
        pest_warnings = warning_system.check_pest_disease_risk()
        
        all_warnings = env_warnings + pest_warnings
        
        return jsonify({
            'warnings': all_warnings,
            'count': len(all_warnings),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logging.error(f"Error in warnings API: {e}")
        return jsonify({'error': str(e)})

@app.route('/api/treatment-plan', methods=['POST'])
def api_treatment_plan():
    """获取防治方案API"""
    try:
        data = request.get_json()
        
        pest_type = data.get('pest_type')
        disease_type = data.get('disease_type')
        severity_level = data.get('severity_level', 3)
        
        treatment_plan = pest_control.generate_integrated_treatment_plan(
            pest_type=pest_type,
            disease_type=disease_type,
            severity_level=severity_level
        )
        
        return jsonify(treatment_plan)
    except Exception as e:
        logging.error(f"Error in treatment plan API: {e}")
        return jsonify({'error': str(e)})

@app.route('/api/market-analysis')
def api_market_analysis():
    """获取市场分析API"""
    try:
        report = market_analyzer.generate_market_report()
        return jsonify(report)
    except Exception as e:
        logging.error(f"Error in market analysis API: {e}")
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
        
        product_info = {
            'planting_date': datetime.fromisoformat(data['planting_date']) if data.get('planting_date') else None,
            'harvest_date': datetime.fromisoformat(data['harvest_date']) if data.get('harvest_date') else None,
            'packaging_date': datetime.fromisoformat(data['packaging_date']) if data.get('packaging_date') else None,
            'location': data.get('location', ''),
            'fertilizer_records': data.get('fertilizer_records', []),
            'pesticide_records': data.get('pesticide_records', []),
            'processing_records': data.get('processing_records', []),
            'transport_records': data.get('transport_records', []),
            'quality_checks': data.get('quality_checks', [])
        }
        
        product_id = traceability_manager.create_product_record(product_info)
        
        return jsonify({
            'success': True,
            'product_id': product_id,
            'message': '产品记录创建成功'
        })
    except Exception as e:
        logging.error(f"Error in product create API: {e}")
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

# 辅助函数
def get_system_status():
    """获取系统状态"""
    try:
        # 检查各模块状态
        status = {
            'data_collection': 'normal',
            'ml_models': 'normal',
            'warning_system': 'normal',
            'database': 'normal',
            'last_update': datetime.now().isoformat()
        }
        
        # 检查最新数据
        latest_data = data_preprocessor.load_data_from_db(
            start_date=datetime.now() - timedelta(hours=1)
        )
        
        if latest_data.empty:
            status['data_collection'] = 'warning'
        
        return status
    except Exception as e:
        logging.error(f"Error getting system status: {e}")
        return {'error': str(e)}

def get_latest_environmental_data():
    """获取最新环境数据"""
    try:
        df = data_preprocessor.load_data_from_db(
            start_date=datetime.now() - timedelta(hours=1)
        )
        
        if df.empty:
            return {}
        
        latest_row = df.iloc[-1]
        
        return {
            'timestamp': latest_row['timestamp'].isoformat(),
            'temperature': latest_row['temperature'],
            'humidity': latest_row['humidity'],
            'soil_moisture': latest_row['soil_moisture'],
            'light_intensity': latest_row['light_intensity'],
            'wind_speed': latest_row['wind_speed'],
            'rainfall': latest_row['rainfall'],
            'air_pressure': latest_row['air_pressure']
        }
    except Exception as e:
        logging.error(f"Error getting latest environmental data: {e}")
        return {}

def get_market_summary(market_data):
    """获取市场摘要"""
    try:
        if market_data.empty:
            return {}
        
        return {
            'total_products': len(market_data),
            'average_price': round(market_data['price'].mean(), 2),
            'average_rating': round(market_data['rating'].mean(), 2),
            'total_sales': int(market_data['sales_volume'].sum()),
            'platforms': market_data['platform'].nunique()
        }
    except Exception as e:
        logging.error(f"Error getting market summary: {e}")
        return {}

def get_production_summary():
    """获取生产摘要"""
    try:
        # 获取产品追溯统计
        products = traceability_manager.search_products({})
        
        total_products = len(products)
        products_with_quality = len([p for p in products if p.get('has_quality_checks')])
        
        return {
            'total_products': total_products,
            'products_with_quality_checks': products_with_quality,
            'quality_rate': round(products_with_quality / total_products * 100, 2) if total_products > 0 else 0
        }
    except Exception as e:
        logging.error(f"Error getting production summary: {e}")
        return {}

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
    
    # 创建必要的目录
    os.makedirs('static/uploads', exist_ok=True)
    os.makedirs('models', exist_ok=True)
    
    # 初始化演示数据（仅在第一次部署时）
    try:
        if not os.path.exists('agriculture.db') or os.path.getsize('agriculture.db') == 0:
            print("🔄 正在初始化演示数据...")
            from init_demo_data import init_demo_data
            init_demo_data()
    except Exception as e:
        print(f"⚠️ 演示数据初始化失败: {e}")
    
    # 启动应用
    port = int(os.environ.get('PORT', 8080))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False
    ) 