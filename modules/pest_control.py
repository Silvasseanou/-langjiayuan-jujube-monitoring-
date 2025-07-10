import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json

from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

from config import Config
from models.database import PestDiseaseData, TreatmentPlan, init_database

class PestControlDecisionSupport:
    """绿色防控决策支持系统"""
    
    def __init__(self, config: Config):
        self.config = config
        self.engine, self.Session = init_database(config.DATABASE_URL)
        
        # 防治方法知识库
        self.treatment_knowledge_base = {
            'biological': {
                'aphids': {
                    'methods': ['释放瓢虫', '释放草蛉', '使用昆虫病原菌'],
                    'effectiveness': 0.75,
                    'cost': 30,
                    'environmental_impact': 0.1,
                    'application_conditions': {
                        'temperature': (15, 30),
                        'humidity': (40, 80),
                        'season': ['spring', 'summer']
                    }
                },
                'spider_mites': {
                    'methods': ['释放捕食螨', '使用苏云金芽孢杆菌'],
                    'effectiveness': 0.70,
                    'cost': 25,
                    'environmental_impact': 0.1,
                    'application_conditions': {
                        'temperature': (20, 35),
                        'humidity': (30, 70),
                        'season': ['spring', 'summer', 'autumn']
                    }
                },
                'scale_insects': {
                    'methods': ['释放寄生蜂', '使用白僵菌'],
                    'effectiveness': 0.65,
                    'cost': 35,
                    'environmental_impact': 0.1,
                    'application_conditions': {
                        'temperature': (18, 28),
                        'humidity': (50, 80),
                        'season': ['spring', 'summer']
                    }
                }
            },
            'physical': {
                'general_pests': {
                    'methods': ['防虫网', '黏虫板', '诱虫灯'],
                    'effectiveness': 0.60,
                    'cost': 20,
                    'environmental_impact': 0.05,
                    'application_conditions': {
                        'temperature': (10, 40),
                        'humidity': (20, 90),
                        'season': ['spring', 'summer', 'autumn']
                    }
                },
                'flying_insects': {
                    'methods': ['诱虫灯', '信息素诱捕器', '反光薄膜'],
                    'effectiveness': 0.55,
                    'cost': 25,
                    'environmental_impact': 0.05,
                    'application_conditions': {
                        'temperature': (12, 35),
                        'humidity': (30, 80),
                        'season': ['spring', 'summer', 'autumn']
                    }
                }
            },
            'chemical': {
                'severe_infestation': {
                    'methods': ['低毒农药', '生物农药', '植物源农药'],
                    'effectiveness': 0.90,
                    'cost': 40,
                    'environmental_impact': 0.6,
                    'application_conditions': {
                        'temperature': (10, 35),
                        'humidity': (20, 90),
                        'season': ['spring', 'summer', 'autumn']
                    }
                }
            }
        }
        
        # 疾病防治知识库
        self.disease_treatment_knowledge = {
            'biological': {
                'powdery_mildew': {
                    'methods': ['枯草芽孢杆菌', '木霉菌', '酵母菌'],
                    'effectiveness': 0.70,
                    'cost': 25,
                    'environmental_impact': 0.1,
                    'application_conditions': {
                        'temperature': (15, 30),
                        'humidity': (40, 70),
                        'season': ['spring', 'summer']
                    }
                },
                'bacterial_spot': {
                    'methods': ['拮抗细菌', '生物制剂'],
                    'effectiveness': 0.65,
                    'cost': 30,
                    'environmental_impact': 0.1,
                    'application_conditions': {
                        'temperature': (18, 28),
                        'humidity': (50, 80),
                        'season': ['spring', 'summer', 'autumn']
                    }
                }
            },
            'physical': {
                'general_diseases': {
                    'methods': ['通风降湿', '修剪病枝', '土壤改良'],
                    'effectiveness': 0.50,
                    'cost': 15,
                    'environmental_impact': 0.05,
                    'application_conditions': {
                        'temperature': (5, 40),
                        'humidity': (20, 90),
                        'season': ['spring', 'summer', 'autumn', 'winter']
                    }
                }
            },
            'chemical': {
                'severe_disease': {
                    'methods': ['铜制剂', '生物杀菌剂', '植物源杀菌剂'],
                    'effectiveness': 0.85,
                    'cost': 35,
                    'environmental_impact': 0.5,
                    'application_conditions': {
                        'temperature': (10, 35),
                        'humidity': (20, 90),
                        'season': ['spring', 'summer', 'autumn']
                    }
                }
            }
        }
        
        # 训练决策树模型
        self.decision_model = None
        self.train_decision_model()
    
    def get_current_environment(self) -> Dict:
        """获取当前环境条件"""
        try:
            # 使用模拟数据代替实际数据
            import pandas as pd
            
            # 模拟当前环境数据
            current_time = datetime.now()
            month = current_time.month
            
            # 确定当前季节
            if month in [12, 1, 2]:
                season = 'winter'
            elif month in [3, 4, 5]:
                season = 'spring'
            elif month in [6, 7, 8]:
                season = 'summer'
            else:
                season = 'autumn'
            
            # 返回模拟环境数据
            return {
                'temperature': 25.5,
                'humidity': 65.0,
                'season': season,
                'timestamp': current_time
            }
            
        except Exception as e:
            logging.error(f"Error getting current environment: {e}")
            return {}
    
    def check_application_conditions(self, treatment_info: Dict, current_env: Dict) -> bool:
        """检查应用条件是否满足"""
        try:
            conditions = treatment_info.get('application_conditions', {})
            
            # 检查温度条件
            if 'temperature' in conditions and current_env.get('temperature'):
                temp_range = conditions['temperature']
                if not (temp_range[0] <= current_env['temperature'] <= temp_range[1]):
                    return False
            
            # 检查湿度条件
            if 'humidity' in conditions and current_env.get('humidity'):
                humidity_range = conditions['humidity']
                if not (humidity_range[0] <= current_env['humidity'] <= humidity_range[1]):
                    return False
            
            # 检查季节条件
            if 'season' in conditions and current_env.get('season'):
                if current_env['season'] not in conditions['season']:
                    return False
            
            return True
            
        except Exception as e:
            logging.error(f"Error checking application conditions: {e}")
            return False
    
    def generate_pest_treatment_plan(self, pest_type: str, severity_level: int, 
                                   current_env: Dict) -> List[Dict]:
        """生成害虫防治方案"""
        try:
            treatment_plans = []
            
            # 根据严重程度确定防治策略
            if severity_level <= 2:  # 轻微
                # 优先使用生物防治和物理防治
                preferred_methods = ['biological', 'physical']
            elif severity_level <= 4:  # 中等
                # 组合使用生物、物理和化学防治
                preferred_methods = ['biological', 'physical', 'chemical']
            else:  # 严重
                # 需要化学防治配合其他方法
                preferred_methods = ['chemical', 'biological', 'physical']
            
            # 查找适合的防治方法
            for method_type in preferred_methods:
                if method_type in self.treatment_knowledge_base:
                    method_db = self.treatment_knowledge_base[method_type]
                    
                    # 寻找针对特定害虫的方法
                    if pest_type in method_db:
                        treatment_info = method_db[pest_type]
                    else:
                        # 使用通用方法
                        treatment_info = method_db.get('general_pests', 
                                                     method_db.get('severe_infestation', {}))
                    
                    if treatment_info and self.check_application_conditions(treatment_info, current_env):
                        # 计算适用性评分
                        suitability_score = self.calculate_suitability_score(
                            treatment_info, severity_level, current_env
                        )
                        
                        plan = {
                            'treatment_type': method_type,
                            'pest_type': pest_type,
                            'methods': treatment_info['methods'],
                            'effectiveness': treatment_info['effectiveness'],
                            'cost': treatment_info['cost'],
                            'environmental_impact': treatment_info['environmental_impact'],
                            'suitability_score': suitability_score,
                            'severity_level': severity_level,
                            'application_conditions': treatment_info['application_conditions'],
                            'recommendations': self.generate_specific_recommendations(
                                method_type, pest_type, severity_level, current_env
                            )
                        }
                        
                        treatment_plans.append(plan)
            
            # 按适用性评分排序
            treatment_plans.sort(key=lambda x: x['suitability_score'], reverse=True)
            
            return treatment_plans
            
        except Exception as e:
            logging.error(f"Error generating pest treatment plan: {e}")
            return []
    
    def generate_disease_treatment_plan(self, disease_type: str, severity_level: int,
                                      current_env: Dict) -> List[Dict]:
        """生成疾病防治方案"""
        try:
            treatment_plans = []
            
            # 根据严重程度确定防治策略
            if severity_level <= 2:  # 轻微
                preferred_methods = ['physical', 'biological']
            elif severity_level <= 4:  # 中等
                preferred_methods = ['biological', 'physical', 'chemical']
            else:  # 严重
                preferred_methods = ['chemical', 'biological', 'physical']
            
            # 查找适合的防治方法
            for method_type in preferred_methods:
                if method_type in self.disease_treatment_knowledge:
                    method_db = self.disease_treatment_knowledge[method_type]
                    
                    # 寻找针对特定疾病的方法
                    if disease_type in method_db:
                        treatment_info = method_db[disease_type]
                    else:
                        # 使用通用方法
                        treatment_info = method_db.get('general_diseases',
                                                     method_db.get('severe_disease', {}))
                    
                    if treatment_info and self.check_application_conditions(treatment_info, current_env):
                        suitability_score = self.calculate_suitability_score(
                            treatment_info, severity_level, current_env
                        )
                        
                        plan = {
                            'treatment_type': method_type,
                            'disease_type': disease_type,
                            'methods': treatment_info['methods'],
                            'effectiveness': treatment_info['effectiveness'],
                            'cost': treatment_info['cost'],
                            'environmental_impact': treatment_info['environmental_impact'],
                            'suitability_score': suitability_score,
                            'severity_level': severity_level,
                            'application_conditions': treatment_info['application_conditions'],
                            'recommendations': self.generate_specific_recommendations(
                                method_type, disease_type, severity_level, current_env
                            )
                        }
                        
                        treatment_plans.append(plan)
            
            # 按适用性评分排序
            treatment_plans.sort(key=lambda x: x['suitability_score'], reverse=True)
            
            return treatment_plans
            
        except Exception as e:
            logging.error(f"Error generating disease treatment plan: {e}")
            return []
    
    def calculate_suitability_score(self, treatment_info: Dict, severity_level: int,
                                  current_env: Dict) -> float:
        """计算适用性评分"""
        try:
            score = 0.0
            
            # 基础有效性评分 (40%)
            score += treatment_info['effectiveness'] * 0.4
            
            # 成本效益评分 (20%)
            # 成本越低评分越高
            cost_score = max(0, (100 - treatment_info['cost']) / 100)
            score += cost_score * 0.2
            
            # 环境友好性评分 (20%)
            # 环境影响越低评分越高
            env_score = 1 - treatment_info['environmental_impact']
            score += env_score * 0.2
            
            # 严重程度匹配度 (10%)
            if severity_level <= 2:
                # 轻微问题，优先生物和物理防治
                if treatment_info.get('treatment_type') in ['biological', 'physical']:
                    score += 0.1
            elif severity_level >= 4:
                # 严重问题，化学防治可能更有效
                if treatment_info.get('treatment_type') == 'chemical':
                    score += 0.1
            
            # 环境条件匹配度 (10%)
            if self.check_application_conditions(treatment_info, current_env):
                score += 0.1
            
            return min(1.0, score)
            
        except Exception as e:
            logging.error(f"Error calculating suitability score: {e}")
            return 0.0
    
    def generate_specific_recommendations(self, method_type: str, pest_disease: str,
                                        severity_level: int, current_env: Dict) -> List[str]:
        """生成具体建议"""
        try:
            recommendations = []
            
            # 通用建议
            recommendations.append(f"监测{pest_disease}的发展情况，定期检查")
            
            if method_type == 'biological':
                recommendations.extend([
                    "选择合适的生物防治剂，注意保存条件",
                    "避免与化学农药同时使用",
                    "适当的温湿度条件下释放天敌",
                    "建立天敌昆虫的栖息环境"
                ])
            elif method_type == 'physical':
                recommendations.extend([
                    "定期检查和维护物理防治设施",
                    "合理布置诱捕器或防护网",
                    "及时清理捕获的害虫",
                    "结合环境改良措施"
                ])
            elif method_type == 'chemical':
                recommendations.extend([
                    "严格按照说明书使用农药",
                    "选择对天敌影响小的农药",
                    "注意农药的安全间隔期",
                    "轮换使用不同机理的农药"
                ])
            
            # 基于严重程度的建议
            if severity_level >= 4:
                recommendations.append("问题较严重，建议组合使用多种防治方法")
                recommendations.append("加强监测频率，及时调整防治策略")
            
            # 基于环境条件的建议
            if current_env.get('temperature', 0) > 30:
                recommendations.append("高温条件下，注意选择耐高温的防治方法")
            if current_env.get('humidity', 0) > 80:
                recommendations.append("高湿条件下，加强通风，防止疾病蔓延")
            
            return recommendations
            
        except Exception as e:
            logging.error(f"Error generating specific recommendations: {e}")
            return []
    
    def train_decision_model(self):
        """训练决策树模型"""
        try:
            # 创建模拟训练数据
            training_data = self.create_training_data()
            
            if len(training_data) > 0:
                df = pd.DataFrame(training_data)
                
                # 特征列
                feature_cols = ['temperature', 'humidity', 'severity_level', 'season_encoded']
                X = df[feature_cols]
                
                # 标签（防治方法类型）
                y = df['treatment_type_encoded']
                
                # 训练决策树
                self.decision_model = DecisionTreeClassifier(
                    max_depth=10,
                    min_samples_split=5,
                    random_state=42
                )
                
                self.decision_model.fit(X, y)
                
                logging.info("Decision tree model trained successfully")
            
        except Exception as e:
            logging.error(f"Error training decision model: {e}")
    
    def create_training_data(self) -> List[Dict]:
        """创建训练数据"""
        try:
            training_data = []
            
            # 模拟不同条件下的防治方法选择
            seasons = ['spring', 'summer', 'autumn', 'winter']
            season_encoding = {'spring': 1, 'summer': 2, 'autumn': 3, 'winter': 4}
            
            for temp in range(5, 36, 5):
                for humidity in range(20, 91, 10):
                    for severity in range(1, 6):
                        for season in seasons:
                            # 决策逻辑
                            if severity <= 2:
                                if temp >= 15 and humidity >= 40:
                                    treatment_type = 'biological'
                                else:
                                    treatment_type = 'physical'
                            elif severity <= 4:
                                if temp >= 10 and humidity <= 80:
                                    treatment_type = 'biological'
                                else:
                                    treatment_type = 'physical'
                            else:
                                treatment_type = 'chemical'
                            
                            # 编码处理
                            treatment_encoding = {'biological': 1, 'physical': 2, 'chemical': 3}
                            
                            training_data.append({
                                'temperature': temp,
                                'humidity': humidity,
                                'severity_level': severity,
                                'season': season,
                                'season_encoded': season_encoding[season],
                                'treatment_type': treatment_type,
                                'treatment_type_encoded': treatment_encoding[treatment_type]
                            })
            
            return training_data
            
        except Exception as e:
            logging.error(f"Error creating training data: {e}")
            return []
    
    def predict_treatment_type(self, temperature: float, humidity: float,
                             severity_level: int, season: str) -> str:
        """预测最适合的防治方法类型"""
        try:
            if not self.decision_model:
                return 'biological'  # 默认返回生物防治
            
            season_encoding = {'spring': 1, 'summer': 2, 'autumn': 3, 'winter': 4}
            season_encoded = season_encoding.get(season, 1)
            
            # 预测
            features = [[temperature, humidity, severity_level, season_encoded]]
            prediction = self.decision_model.predict(features)[0]
            
            # 解码
            treatment_decoding = {1: 'biological', 2: 'physical', 3: 'chemical'}
            return treatment_decoding.get(prediction, 'biological')
            
        except Exception as e:
            logging.error(f"Error predicting treatment type: {e}")
            return 'biological'
    
    def generate_integrated_treatment_plan(self, pest_type: str = None, 
                                         disease_type: str = None,
                                         severity_level: int = 3) -> Dict:
        """生成综合防治方案"""
        try:
            # 获取当前环境条件
            current_env = self.get_current_environment()
            
            if not current_env:
                logging.warning("No current environment data available")
                current_env = {
                    'temperature': 25.0,
                    'humidity': 60.0,
                    'season': 'spring'
                }
            
            integrated_plan = {
                'timestamp': datetime.now().isoformat(),
                'environmental_conditions': current_env,
                'pest_treatments': [],
                'disease_treatments': [],
                'integrated_recommendations': []
            }
            
            # 生成害虫防治方案
            if pest_type:
                pest_plans = self.generate_pest_treatment_plan(
                    pest_type, severity_level, current_env
                )
                integrated_plan['pest_treatments'] = pest_plans
            
            # 生成疾病防治方案
            if disease_type:
                disease_plans = self.generate_disease_treatment_plan(
                    disease_type, severity_level, current_env
                )
                integrated_plan['disease_treatments'] = disease_plans
            
            # 生成综合建议
            integrated_plan['integrated_recommendations'] = self.generate_integrated_recommendations(
                pest_type, disease_type, severity_level, current_env
            )
            
            return integrated_plan
            
        except Exception as e:
            logging.error(f"Error generating integrated treatment plan: {e}")
            return {}
    
    def generate_integrated_recommendations(self, pest_type: str, disease_type: str,
                                          severity_level: int, current_env: Dict) -> List[str]:
        """生成综合建议"""
        try:
            recommendations = []
            
            # 基础建议
            recommendations.append("建立综合防治体系，优先使用生物防治")
            recommendations.append("定期监测病虫害发展情况")
            
            # 基于严重程度的建议
            if severity_level >= 4:
                recommendations.append("问题严重，建议立即采取防治措施")
                recommendations.append("可能需要使用化学防治配合其他方法")
            else:
                recommendations.append("问题较轻，可优先使用环保方法")
            
            # 基于环境条件的建议
            temp = current_env.get('temperature', 25)
            humidity = current_env.get('humidity', 60)
            
            if temp > 30:
                recommendations.append("高温条件下，注意选择耐高温的防治方法")
                recommendations.append("避免在高温时段施药")
            
            if humidity > 80:
                recommendations.append("高湿条件下，加强通风，防止病害扩散")
                recommendations.append("可能需要使用除湿设备")
            
            # 季节性建议
            season = current_env.get('season', 'spring')
            if season == 'spring':
                recommendations.append("春季是病虫害防治的关键期")
                recommendations.append("加强预防措施，减少后期防治压力")
            elif season == 'summer':
                recommendations.append("夏季高温高湿，注意疾病防控")
                recommendations.append("及时清除病虫源")
            elif season == 'autumn':
                recommendations.append("秋季做好越冬害虫的防控")
                recommendations.append("清理田间残留物")
            
            # 综合防治建议
            recommendations.append("结合农业防治、生物防治、物理防治和化学防治")
            recommendations.append("建立长期监测体系")
            recommendations.append("记录防治效果，不断优化防治策略")
            
            return recommendations
            
        except Exception as e:
            logging.error(f"Error generating integrated recommendations: {e}")
            return []
    
    def save_treatment_plan(self, treatment_plan: Dict, pest_disease_id: int = None):
        """保存防治方案到数据库"""
        try:
            session = self.Session()
            
            # 保存主要的防治方案
            for plan in treatment_plan.get('pest_treatments', []) + treatment_plan.get('disease_treatments', []):
                treatment_record = TreatmentPlan(
                    pest_disease_id=pest_disease_id,
                    treatment_type=plan['treatment_type'],
                    treatment_method=json.dumps(plan['methods']),
                    effectiveness=plan['effectiveness'],
                    cost=plan['cost'],
                    environmental_impact=plan['environmental_impact']
                )
                
                session.add(treatment_record)
            
            session.commit()
            session.close()
            
            logging.info("Treatment plan saved to database")
            
        except Exception as e:
            logging.error(f"Error saving treatment plan: {e}")

# 使用示例
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    config = Config()
    pest_control = PestControlDecisionSupport(config)
    
    # 生成综合防治方案
    treatment_plan = pest_control.generate_integrated_treatment_plan(
        pest_type='aphids',
        disease_type='powdery_mildew',
        severity_level=3
    )
    
    print("综合防治方案:")
    print(json.dumps(treatment_plan, indent=2, ensure_ascii=False)) 