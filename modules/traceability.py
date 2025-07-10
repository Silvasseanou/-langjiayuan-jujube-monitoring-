import qrcode
import uuid
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from PIL import Image, ImageDraw, ImageFont
import io
import base64

from config import Config
from models.database import ProductTraceability, init_database

class TraceabilityManager:
    """产品追溯管理器"""
    
    def __init__(self, config: Config):
        self.config = config
        self.engine, self.Session = init_database(config.DATABASE_URL)
        
    def generate_product_id(self, prefix: str = "LJY") -> str:
        """生成产品唯一ID"""
        try:
            # 生成格式：LJY + 年月日 + 6位随机数
            date_str = datetime.now().strftime("%Y%m%d")
            random_str = str(uuid.uuid4()).replace('-', '')[:6].upper()
            return f"{prefix}{date_str}{random_str}"
        except Exception as e:
            logging.error(f"Error generating product ID: {e}")
            return f"{prefix}{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"
    
    def create_product_record(self, product_info: Dict) -> str:
        """创建产品记录"""
        try:
            # 生成产品ID
            product_id = self.generate_product_id()
            
            # 生成二维码
            qr_code_data = self.generate_qr_code(product_id)
            
            # 创建数据库记录
            session = self.Session()
            
            product_record = ProductTraceability(
                product_id=product_id,
                qr_code=qr_code_data,
                planting_date=product_info.get('planting_date'),
                harvest_date=product_info.get('harvest_date'),
                location=product_info.get('location', ''),
                fertilizer_records=product_info.get('fertilizer_records', []),
                pesticide_records=product_info.get('pesticide_records', []),
                processing_records=product_info.get('processing_records', []),
                packaging_date=product_info.get('packaging_date'),
                transport_records=product_info.get('transport_records', []),
                quality_checks=product_info.get('quality_checks', [])
            )
            
            session.add(product_record)
            session.commit()
            session.close()
            
            logging.info(f"Created product record with ID: {product_id}")
            return product_id
            
        except Exception as e:
            logging.error(f"Error creating product record: {e}")
            return ""
    
    def generate_qr_code(self, product_id: str) -> str:
        """生成二维码"""
        try:
            # 创建二维码内容
            qr_data = {
                'product_id': product_id,
                'trace_url': f"https://trace.langjiayuan.com/product/{product_id}",
                'timestamp': datetime.now().isoformat()
            }
            
            # 生成二维码
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(json.dumps(qr_data))
            qr.make(fit=True)
            
            # 创建二维码图片
            qr_img = qr.make_image(fill_color="black", back_color="white")
            
            # 转换为base64字符串
            buffer = io.BytesIO()
            qr_img.save(buffer, format='PNG')
            qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            return qr_code_base64
            
        except Exception as e:
            logging.error(f"Error generating QR code: {e}")
            return ""
    
    def add_planting_record(self, product_id: str, planting_data: Dict) -> bool:
        """添加种植记录"""
        try:
            session = self.Session()
            
            product = session.query(ProductTraceability).filter(
                ProductTraceability.product_id == product_id
            ).first()
            
            if not product:
                logging.error(f"Product not found: {product_id}")
                return False
            
            # 更新种植数据
            product.planting_date = planting_data.get('planting_date')
            product.location = planting_data.get('location', product.location)
            
            # 添加详细种植记录
            planting_record = {
                'timestamp': datetime.now().isoformat(),
                'plot_number': planting_data.get('plot_number', ''),
                'seed_variety': planting_data.get('seed_variety', ''),
                'planting_method': planting_data.get('planting_method', ''),
                'soil_conditions': planting_data.get('soil_conditions', {}),
                'weather_conditions': planting_data.get('weather_conditions', {}),
                'operator': planting_data.get('operator', ''),
                'notes': planting_data.get('notes', '')
            }
            
            # 如果没有处理记录，创建新的
            if not product.processing_records:
                product.processing_records = []
            
            product.processing_records.append(planting_record)
            
            session.commit()
            session.close()
            
            logging.info(f"Added planting record for product: {product_id}")
            return True
            
        except Exception as e:
            logging.error(f"Error adding planting record: {e}")
            return False
    
    def add_fertilizer_record(self, product_id: str, fertilizer_data: Dict) -> bool:
        """添加施肥记录"""
        try:
            session = self.Session()
            
            product = session.query(ProductTraceability).filter(
                ProductTraceability.product_id == product_id
            ).first()
            
            if not product:
                logging.error(f"Product not found: {product_id}")
                return False
            
            fertilizer_record = {
                'timestamp': datetime.now().isoformat(),
                'application_date': fertilizer_data.get('application_date', ''),
                'fertilizer_type': fertilizer_data.get('fertilizer_type', ''),
                'fertilizer_name': fertilizer_data.get('fertilizer_name', ''),
                'amount': fertilizer_data.get('amount', 0),
                'unit': fertilizer_data.get('unit', 'kg'),
                'method': fertilizer_data.get('method', ''),
                'operator': fertilizer_data.get('operator', ''),
                'weather_conditions': fertilizer_data.get('weather_conditions', {}),
                'notes': fertilizer_data.get('notes', '')
            }
            
            # 如果没有施肥记录，创建新的
            if not product.fertilizer_records:
                product.fertilizer_records = []
            
            product.fertilizer_records.append(fertilizer_record)
            
            session.commit()
            session.close()
            
            logging.info(f"Added fertilizer record for product: {product_id}")
            return True
            
        except Exception as e:
            logging.error(f"Error adding fertilizer record: {e}")
            return False
    
    def add_pesticide_record(self, product_id: str, pesticide_data: Dict) -> bool:
        """添加农药使用记录"""
        try:
            session = self.Session()
            
            product = session.query(ProductTraceability).filter(
                ProductTraceability.product_id == product_id
            ).first()
            
            if not product:
                logging.error(f"Product not found: {product_id}")
                return False
            
            pesticide_record = {
                'timestamp': datetime.now().isoformat(),
                'application_date': pesticide_data.get('application_date', ''),
                'pesticide_name': pesticide_data.get('pesticide_name', ''),
                'active_ingredient': pesticide_data.get('active_ingredient', ''),
                'concentration': pesticide_data.get('concentration', ''),
                'amount': pesticide_data.get('amount', 0),
                'unit': pesticide_data.get('unit', 'ml'),
                'target_pest': pesticide_data.get('target_pest', ''),
                'application_method': pesticide_data.get('application_method', ''),
                'safety_interval': pesticide_data.get('safety_interval', 0),
                'operator': pesticide_data.get('operator', ''),
                'operator_certification': pesticide_data.get('operator_certification', ''),
                'weather_conditions': pesticide_data.get('weather_conditions', {}),
                'notes': pesticide_data.get('notes', '')
            }
            
            # 如果没有农药记录，创建新的
            if not product.pesticide_records:
                product.pesticide_records = []
            
            product.pesticide_records.append(pesticide_record)
            
            session.commit()
            session.close()
            
            logging.info(f"Added pesticide record for product: {product_id}")
            return True
            
        except Exception as e:
            logging.error(f"Error adding pesticide record: {e}")
            return False
    
    def add_harvest_record(self, product_id: str, harvest_data: Dict) -> bool:
        """添加收获记录"""
        try:
            session = self.Session()
            
            product = session.query(ProductTraceability).filter(
                ProductTraceability.product_id == product_id
            ).first()
            
            if not product:
                logging.error(f"Product not found: {product_id}")
                return False
            
            # 更新收获日期
            product.harvest_date = harvest_data.get('harvest_date')
            
            harvest_record = {
                'timestamp': datetime.now().isoformat(),
                'harvest_date': harvest_data.get('harvest_date', ''),
                'harvest_method': harvest_data.get('harvest_method', ''),
                'yield_amount': harvest_data.get('yield_amount', 0),
                'unit': harvest_data.get('unit', 'kg'),
                'quality_grade': harvest_data.get('quality_grade', ''),
                'moisture_content': harvest_data.get('moisture_content', 0),
                'sugar_content': harvest_data.get('sugar_content', 0),
                'operator': harvest_data.get('operator', ''),
                'weather_conditions': harvest_data.get('weather_conditions', {}),
                'storage_conditions': harvest_data.get('storage_conditions', {}),
                'notes': harvest_data.get('notes', '')
            }
            
            # 如果没有处理记录，创建新的
            if not product.processing_records:
                product.processing_records = []
            
            product.processing_records.append(harvest_record)
            
            session.commit()
            session.close()
            
            logging.info(f"Added harvest record for product: {product_id}")
            return True
            
        except Exception as e:
            logging.error(f"Error adding harvest record: {e}")
            return False
    
    def add_processing_record(self, product_id: str, processing_data: Dict) -> bool:
        """添加加工记录"""
        try:
            session = self.Session()
            
            product = session.query(ProductTraceability).filter(
                ProductTraceability.product_id == product_id
            ).first()
            
            if not product:
                logging.error(f"Product not found: {product_id}")
                return False
            
            processing_record = {
                'timestamp': datetime.now().isoformat(),
                'processing_date': processing_data.get('processing_date', ''),
                'processing_type': processing_data.get('processing_type', ''),
                'processing_method': processing_data.get('processing_method', ''),
                'equipment_used': processing_data.get('equipment_used', []),
                'temperature': processing_data.get('temperature', 0),
                'humidity': processing_data.get('humidity', 0),
                'processing_time': processing_data.get('processing_time', 0),
                'input_amount': processing_data.get('input_amount', 0),
                'output_amount': processing_data.get('output_amount', 0),
                'loss_rate': processing_data.get('loss_rate', 0),
                'operator': processing_data.get('operator', ''),
                'quality_check': processing_data.get('quality_check', {}),
                'notes': processing_data.get('notes', '')
            }
            
            # 如果没有处理记录，创建新的
            if not product.processing_records:
                product.processing_records = []
            
            product.processing_records.append(processing_record)
            
            session.commit()
            session.close()
            
            logging.info(f"Added processing record for product: {product_id}")
            return True
            
        except Exception as e:
            logging.error(f"Error adding processing record: {e}")
            return False
    
    def add_packaging_record(self, product_id: str, packaging_data: Dict) -> bool:
        """添加包装记录"""
        try:
            session = self.Session()
            
            product = session.query(ProductTraceability).filter(
                ProductTraceability.product_id == product_id
            ).first()
            
            if not product:
                logging.error(f"Product not found: {product_id}")
                return False
            
            # 更新包装日期
            product.packaging_date = packaging_data.get('packaging_date')
            
            packaging_record = {
                'timestamp': datetime.now().isoformat(),
                'packaging_date': packaging_data.get('packaging_date', ''),
                'packaging_type': packaging_data.get('packaging_type', ''),
                'packaging_material': packaging_data.get('packaging_material', ''),
                'package_size': packaging_data.get('package_size', ''),
                'batch_number': packaging_data.get('batch_number', ''),
                'expiry_date': packaging_data.get('expiry_date', ''),
                'label_information': packaging_data.get('label_information', {}),
                'operator': packaging_data.get('operator', ''),
                'quality_check': packaging_data.get('quality_check', {}),
                'notes': packaging_data.get('notes', '')
            }
            
            # 如果没有处理记录，创建新的
            if not product.processing_records:
                product.processing_records = []
            
            product.processing_records.append(packaging_record)
            
            session.commit()
            session.close()
            
            logging.info(f"Added packaging record for product: {product_id}")
            return True
            
        except Exception as e:
            logging.error(f"Error adding packaging record: {e}")
            return False
    
    def add_transport_record(self, product_id: str, transport_data: Dict) -> bool:
        """添加运输记录"""
        try:
            session = self.Session()
            
            product = session.query(ProductTraceability).filter(
                ProductTraceability.product_id == product_id
            ).first()
            
            if not product:
                logging.error(f"Product not found: {product_id}")
                return False
            
            transport_record = {
                'timestamp': datetime.now().isoformat(),
                'departure_date': transport_data.get('departure_date', ''),
                'arrival_date': transport_data.get('arrival_date', ''),
                'departure_location': transport_data.get('departure_location', ''),
                'destination': transport_data.get('destination', ''),
                'transport_method': transport_data.get('transport_method', ''),
                'vehicle_info': transport_data.get('vehicle_info', {}),
                'driver_info': transport_data.get('driver_info', {}),
                'transport_conditions': transport_data.get('transport_conditions', {}),
                'route_info': transport_data.get('route_info', []),
                'delivery_confirmation': transport_data.get('delivery_confirmation', {}),
                'notes': transport_data.get('notes', '')
            }
            
            # 如果没有运输记录，创建新的
            if not product.transport_records:
                product.transport_records = []
            
            product.transport_records.append(transport_record)
            
            session.commit()
            session.close()
            
            logging.info(f"Added transport record for product: {product_id}")
            return True
            
        except Exception as e:
            logging.error(f"Error adding transport record: {e}")
            return False
    
    def add_quality_check_record(self, product_id: str, quality_data: Dict) -> bool:
        """添加质量检查记录"""
        try:
            session = self.Session()
            
            product = session.query(ProductTraceability).filter(
                ProductTraceability.product_id == product_id
            ).first()
            
            if not product:
                logging.error(f"Product not found: {product_id}")
                return False
            
            quality_record = {
                'timestamp': datetime.now().isoformat(),
                'check_date': quality_data.get('check_date', ''),
                'check_type': quality_data.get('check_type', ''),
                'check_stage': quality_data.get('check_stage', ''),
                'inspector': quality_data.get('inspector', ''),
                'inspection_items': quality_data.get('inspection_items', []),
                'test_results': quality_data.get('test_results', {}),
                'quality_grade': quality_data.get('quality_grade', ''),
                'pass_status': quality_data.get('pass_status', True),
                'defects_found': quality_data.get('defects_found', []),
                'corrective_actions': quality_data.get('corrective_actions', []),
                'certificates': quality_data.get('certificates', []),
                'notes': quality_data.get('notes', '')
            }
            
            # 如果没有质量检查记录，创建新的
            if not product.quality_checks:
                product.quality_checks = []
            
            product.quality_checks.append(quality_record)
            
            session.commit()
            session.close()
            
            logging.info(f"Added quality check record for product: {product_id}")
            return True
            
        except Exception as e:
            logging.error(f"Error adding quality check record: {e}")
            return False
    
    def get_product_trace_info(self, product_id: str) -> Dict:
        """获取产品追溯信息"""
        try:
            session = self.Session()
            
            product = session.query(ProductTraceability).filter(
                ProductTraceability.product_id == product_id
            ).first()
            
            if not product:
                session.close()
                return {'error': '产品未找到'}
            
            trace_info = {
                'product_id': product.product_id,
                'basic_info': {
                    'planting_date': product.planting_date.isoformat() if product.planting_date else None,
                    'harvest_date': product.harvest_date.isoformat() if product.harvest_date else None,
                    'packaging_date': product.packaging_date.isoformat() if product.packaging_date else None,
                    'location': product.location
                },
                'fertilizer_records': product.fertilizer_records or [],
                'pesticide_records': product.pesticide_records or [],
                'processing_records': product.processing_records or [],
                'transport_records': product.transport_records or [],
                'quality_checks': product.quality_checks or [],
                'qr_code': product.qr_code
            }
            
            session.close()
            return trace_info
            
        except Exception as e:
            logging.error(f"Error getting product trace info: {e}")
            return {'error': str(e)}
    
    def generate_trace_report(self, product_id: str) -> Dict:
        """生成追溯报告"""
        try:
            trace_info = self.get_product_trace_info(product_id)
            
            if 'error' in trace_info:
                return trace_info
            
            # 生成详细报告
            report = {
                'product_id': product_id,
                'report_date': datetime.now().isoformat(),
                'basic_information': trace_info['basic_info'],
                'production_timeline': self.generate_timeline(trace_info),
                'input_materials': self.summarize_inputs(trace_info),
                'quality_summary': self.summarize_quality(trace_info),
                'compliance_check': self.check_compliance(trace_info),
                'recommendations': self.generate_recommendations(trace_info)
            }
            
            return report
            
        except Exception as e:
            logging.error(f"Error generating trace report: {e}")
            return {'error': str(e)}
    
    def generate_timeline(self, trace_info: Dict) -> List[Dict]:
        """生成生产时间线"""
        try:
            timeline = []
            
            # 种植阶段
            if trace_info['basic_info']['planting_date']:
                timeline.append({
                    'date': trace_info['basic_info']['planting_date'],
                    'stage': '种植',
                    'description': f"在{trace_info['basic_info']['location']}开始种植",
                    'details': [record for record in trace_info['processing_records'] if 'planting' in record.get('processing_type', '')]
                })
            
            # 施肥记录
            for record in trace_info['fertilizer_records']:
                timeline.append({
                    'date': record.get('application_date', ''),
                    'stage': '施肥',
                    'description': f"施用{record.get('fertilizer_name', '肥料')} {record.get('amount', 0)}{record.get('unit', '')}",
                    'details': record
                })
            
            # 农药使用记录
            for record in trace_info['pesticide_records']:
                timeline.append({
                    'date': record.get('application_date', ''),
                    'stage': '防治',
                    'description': f"使用{record.get('pesticide_name', '农药')}防治{record.get('target_pest', '病虫害')}",
                    'details': record
                })
            
            # 收获阶段
            if trace_info['basic_info']['harvest_date']:
                timeline.append({
                    'date': trace_info['basic_info']['harvest_date'],
                    'stage': '收获',
                    'description': "产品收获完成",
                    'details': [record for record in trace_info['processing_records'] if 'harvest' in record.get('processing_type', '')]
                })
            
            # 加工记录
            for record in trace_info['processing_records']:
                if record.get('processing_type') not in ['planting', 'harvest']:
                    timeline.append({
                        'date': record.get('processing_date', ''),
                        'stage': '加工',
                        'description': f"{record.get('processing_type', '加工')} - {record.get('processing_method', '')}",
                        'details': record
                    })
            
            # 包装阶段
            if trace_info['basic_info']['packaging_date']:
                timeline.append({
                    'date': trace_info['basic_info']['packaging_date'],
                    'stage': '包装',
                    'description': "产品包装完成",
                    'details': [record for record in trace_info['processing_records'] if 'packaging' in record.get('processing_type', '')]
                })
            
            # 运输记录
            for record in trace_info['transport_records']:
                timeline.append({
                    'date': record.get('departure_date', ''),
                    'stage': '运输',
                    'description': f"从{record.get('departure_location', '')}运输到{record.get('destination', '')}",
                    'details': record
                })
            
            # 按日期排序
            timeline.sort(key=lambda x: x['date'] if x['date'] else '1900-01-01')
            
            return timeline
            
        except Exception as e:
            logging.error(f"Error generating timeline: {e}")
            return []
    
    def summarize_inputs(self, trace_info: Dict) -> Dict:
        """汇总投入品信息"""
        try:
            inputs = {
                'fertilizers': [],
                'pesticides': [],
                'processing_materials': []
            }
            
            # 汇总肥料
            for record in trace_info['fertilizer_records']:
                inputs['fertilizers'].append({
                    'name': record.get('fertilizer_name', ''),
                    'type': record.get('fertilizer_type', ''),
                    'amount': record.get('amount', 0),
                    'unit': record.get('unit', ''),
                    'date': record.get('application_date', '')
                })
            
            # 汇总农药
            for record in trace_info['pesticide_records']:
                inputs['pesticides'].append({
                    'name': record.get('pesticide_name', ''),
                    'active_ingredient': record.get('active_ingredient', ''),
                    'amount': record.get('amount', 0),
                    'unit': record.get('unit', ''),
                    'date': record.get('application_date', ''),
                    'safety_interval': record.get('safety_interval', 0)
                })
            
            # 汇总加工材料
            for record in trace_info['processing_records']:
                if record.get('equipment_used'):
                    inputs['processing_materials'].extend(record['equipment_used'])
            
            return inputs
            
        except Exception as e:
            logging.error(f"Error summarizing inputs: {e}")
            return {}
    
    def summarize_quality(self, trace_info: Dict) -> Dict:
        """汇总质量信息"""
        try:
            quality_summary = {
                'total_checks': len(trace_info['quality_checks']),
                'passed_checks': 0,
                'failed_checks': 0,
                'quality_grades': [],
                'defects': [],
                'certificates': []
            }
            
            for record in trace_info['quality_checks']:
                if record.get('pass_status'):
                    quality_summary['passed_checks'] += 1
                else:
                    quality_summary['failed_checks'] += 1
                
                if record.get('quality_grade'):
                    quality_summary['quality_grades'].append(record['quality_grade'])
                
                if record.get('defects_found'):
                    quality_summary['defects'].extend(record['defects_found'])
                
                if record.get('certificates'):
                    quality_summary['certificates'].extend(record['certificates'])
            
            return quality_summary
            
        except Exception as e:
            logging.error(f"Error summarizing quality: {e}")
            return {}
    
    def check_compliance(self, trace_info: Dict) -> Dict:
        """检查合规性"""
        try:
            compliance = {
                'overall_status': 'compliant',
                'issues': [],
                'recommendations': []
            }
            
            # 检查农药安全间隔期
            for record in trace_info['pesticide_records']:
                safety_interval = record.get('safety_interval', 0)
                application_date = record.get('application_date', '')
                
                if safety_interval > 0 and application_date:
                    # 这里应该检查实际的收获日期是否符合安全间隔期
                    # 简化处理
                    compliance['recommendations'].append(f"确保{record.get('pesticide_name', '农药')}的安全间隔期({safety_interval}天)得到遵守")
            
            # 检查质量检查完整性
            if not trace_info['quality_checks']:
                compliance['issues'].append("缺少质量检查记录")
                compliance['overall_status'] = 'non_compliant'
            
            # 检查记录完整性
            if not trace_info['basic_info']['planting_date']:
                compliance['issues'].append("缺少种植日期记录")
            
            if not trace_info['basic_info']['harvest_date']:
                compliance['issues'].append("缺少收获日期记录")
            
            return compliance
            
        except Exception as e:
            logging.error(f"Error checking compliance: {e}")
            return {}
    
    def generate_recommendations(self, trace_info: Dict) -> List[str]:
        """生成建议"""
        try:
            recommendations = []
            
            # 记录完整性建议
            if not trace_info['fertilizer_records']:
                recommendations.append("建议完善施肥记录，有助于提高产品追溯的完整性")
            
            if not trace_info['quality_checks']:
                recommendations.append("建议增加质量检查环节，确保产品质量")
            
            # 安全建议
            if trace_info['pesticide_records']:
                recommendations.append("建议严格遵守农药安全间隔期，确保产品安全")
            
            # 优化建议
            recommendations.append("建议实施数字化记录系统，提高追溯效率")
            recommendations.append("建议建立标准化操作流程，确保记录的一致性")
            
            return recommendations
            
        except Exception as e:
            logging.error(f"Error generating recommendations: {e}")
            return []
    
    def search_products(self, search_criteria: Dict) -> List[Dict]:
        """搜索产品"""
        try:
            session = self.Session()
            
            query = session.query(ProductTraceability)
            
            # 按产品ID搜索
            if search_criteria.get('product_id'):
                query = query.filter(ProductTraceability.product_id.like(f"%{search_criteria['product_id']}%"))
            
            # 按位置搜索
            if search_criteria.get('location'):
                query = query.filter(ProductTraceability.location.like(f"%{search_criteria['location']}%"))
            
            # 按日期范围搜索
            if search_criteria.get('start_date'):
                query = query.filter(ProductTraceability.planting_date >= search_criteria['start_date'])
            
            if search_criteria.get('end_date'):
                query = query.filter(ProductTraceability.planting_date <= search_criteria['end_date'])
            
            results = query.all()
            session.close()
            
            # 转换为字典格式
            products = []
            for product in results:
                products.append({
                    'product_id': product.product_id,
                    'location': product.location,
                    'planting_date': product.planting_date.isoformat() if product.planting_date else None,
                    'harvest_date': product.harvest_date.isoformat() if product.harvest_date else None,
                    'packaging_date': product.packaging_date.isoformat() if product.packaging_date else None,
                    'has_fertilizer_records': bool(product.fertilizer_records),
                    'has_pesticide_records': bool(product.pesticide_records),
                    'has_quality_checks': bool(product.quality_checks)
                })
            
            return products
            
        except Exception as e:
            logging.error(f"Error searching products: {e}")
            return []

# 使用示例
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    config = Config()
    tracer = TraceabilityManager(config)
    
    # 创建产品记录
    product_info = {
        'planting_date': datetime(2024, 3, 15),
        'harvest_date': datetime(2024, 9, 20),
        'location': '新疆阿克苏地区',
        'packaging_date': datetime(2024, 9, 25)
    }
    
    product_id = tracer.create_product_record(product_info)
    print(f"Created product: {product_id}")
    
    # 添加施肥记录
    fertilizer_data = {
        'application_date': '2024-04-10',
        'fertilizer_type': '有机肥',
        'fertilizer_name': '羊粪肥',
        'amount': 50,
        'unit': 'kg',
        'method': '撒施',
        'operator': '张三'
    }
    
    tracer.add_fertilizer_record(product_id, fertilizer_data)
    
    # 添加质量检查记录
    quality_data = {
        'check_date': '2024-09-25',
        'check_type': '成品检测',
        'check_stage': '包装前',
        'inspector': '质检员李四',
        'quality_grade': 'A级',
        'pass_status': True,
        'test_results': {
            'sugar_content': 65.5,
            'moisture_content': 12.3,
            'size': '大果'
        }
    }
    
    tracer.add_quality_check_record(product_id, quality_data)
    
    # 获取追溯信息
    trace_info = tracer.get_product_trace_info(product_id)
    print("追溯信息:")
    print(json.dumps(trace_info, indent=2, ensure_ascii=False))
    
    # 生成追溯报告
    report = tracer.generate_trace_report(product_id)
    print("\n追溯报告:")
    print(json.dumps(report, indent=2, ensure_ascii=False)) 