import smtplib
import logging
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional, Tuple
import json

# 第三方通知服务
from twilio.rest import Client as TwilioClient
import requests

from config import Config
from models.database import WarningRecord, User, NotificationSetting, init_database
# from modules.ml_models import PestDiseasePredictor

class NotificationManager:
    """通知管理器"""
    
    def __init__(self, config: Config):
        self.config = config
        self.engine, self.Session = init_database(config.DATABASE_URL)
        
        # 初始化通知服务
        self.setup_email_client()
        self.setup_sms_client()
        
    def setup_email_client(self):
        """设置邮件客户端"""
        try:
            self.smtp_server = self.config.MAIL_SERVER
            self.smtp_port = self.config.MAIL_PORT
            self.smtp_username = self.config.MAIL_USERNAME
            self.smtp_password = self.config.MAIL_PASSWORD
            self.smtp_use_tls = self.config.MAIL_USE_TLS
            
            logging.info("Email client configured")
            
        except Exception as e:
            logging.error(f"Error setting up email client: {e}")
    
    def setup_sms_client(self):
        """设置短信客户端"""
        try:
            if self.config.TWILIO_ACCOUNT_SID and self.config.TWILIO_AUTH_TOKEN:
                self.twilio_client = TwilioClient(
                    self.config.TWILIO_ACCOUNT_SID,
                    self.config.TWILIO_AUTH_TOKEN
                )
                self.twilio_phone = self.config.TWILIO_PHONE_NUMBER
                logging.info("SMS client configured")
            else:
                self.twilio_client = None
                logging.warning("SMS client not configured - missing Twilio credentials")
                
        except Exception as e:
            logging.error(f"Error setting up SMS client: {e}")
            self.twilio_client = None
    
    def send_email(self, to_email: str, subject: str, body: str, html_body: str = None) -> bool:
        """发送邮件"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.smtp_username
            msg['To'] = to_email
            
            # 纯文本版本
            text_part = MIMEText(body, 'plain', 'utf-8')
            msg.attach(text_part)
            
            # HTML版本
            if html_body:
                html_part = MIMEText(html_body, 'html', 'utf-8')
                msg.attach(html_part)
            
            # 发送邮件
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            if self.smtp_use_tls:
                server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)
            server.quit()
            
            logging.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logging.error(f"Error sending email to {to_email}: {e}")
            return False
    
    def send_sms(self, to_phone: str, message: str) -> bool:
        """发送短信"""
        try:
            if not self.twilio_client:
                logging.warning("SMS client not available")
                return False
            
            message = self.twilio_client.messages.create(
                body=message,
                from_=self.twilio_phone,
                to=to_phone
            )
            
            logging.info(f"SMS sent successfully to {to_phone}, SID: {message.sid}")
            return True
            
        except Exception as e:
            logging.error(f"Error sending SMS to {to_phone}: {e}")
            return False
    
    def send_push_notification(self, user_token: str, title: str, body: str) -> bool:
        """发送推送通知（示例实现）"""
        try:
            # 这里可以集成Firebase、个推等推送服务
            # 示例使用Firebase Cloud Messaging
            
            url = 'https://fcm.googleapis.com/fcm/send'
            headers = {
                'Authorization': f'key={self.config.FCM_SERVER_KEY}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'to': user_token,
                'notification': {
                    'title': title,
                    'body': body
                },
                'data': {
                    'timestamp': datetime.now().isoformat()
                }
            }
            
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                logging.info(f"Push notification sent successfully to {user_token}")
                return True
            else:
                logging.error(f"Failed to send push notification: {response.text}")
                return False
                
        except Exception as e:
            logging.error(f"Error sending push notification: {e}")
            return False

class WarningSystem:
    """预警系统"""
    
    def __init__(self, config: Config):
        self.config = config
        self.engine, self.Session = init_database(config.DATABASE_URL)
        self.notification_manager = NotificationManager(config)
        # self.predictor = PestDiseasePredictor(config)
        
        # 加载模型
        # self.predictor.load_models()
        
    def check_environmental_thresholds(self) -> List[Dict]:
        """检查环境参数阈值"""
        warnings = []
        
        try:
            # 获取最新环境数据
            # latest_data = self.predictor.preprocessor.load_data_from_db(
            #     start_date=datetime.now() - timedelta(hours=1)
            # )
            
            # 使用模拟数据
            import pandas as pd
            import numpy as np
            
            latest_data = pd.DataFrame({
                'timestamp': [datetime.now()],
                'temperature': [32.5],
                'humidity': [85.2],
                'soil_moisture': [18.5],
                'light_intensity': [850.0],
                'wind_speed': [12.3],
                'rainfall': [0.0],
                'air_pressure': [1010.2]
            })
            
            if latest_data.empty:
                return warnings
            
            latest_row = latest_data.iloc[-1]
            thresholds = self.config.WARNING_THRESHOLDS
            
            # 检查温度
            if latest_row['temperature']:
                if latest_row['temperature'] > thresholds['temperature_high']:
                    warnings.append({
                        'type': 'temperature_high',
                        'severity': 'high',
                        'message': f"高温预警：当前温度 {latest_row['temperature']:.1f}°C，超过阈值 {thresholds['temperature_high']:.1f}°C",
                        'value': latest_row['temperature'],
                        'threshold': thresholds['temperature_high']
                    })
                elif latest_row['temperature'] < thresholds['temperature_low']:
                    warnings.append({
                        'type': 'temperature_low',
                        'severity': 'medium',
                        'message': f"低温预警：当前温度 {latest_row['temperature']:.1f}°C，低于阈值 {thresholds['temperature_low']:.1f}°C",
                        'value': latest_row['temperature'],
                        'threshold': thresholds['temperature_low']
                    })
            
            # 检查湿度
            if latest_row['humidity']:
                if latest_row['humidity'] > thresholds['humidity_high']:
                    warnings.append({
                        'type': 'humidity_high',
                        'severity': 'medium',
                        'message': f"高湿度预警：当前湿度 {latest_row['humidity']:.1f}%，超过阈值 {thresholds['humidity_high']:.1f}%",
                        'value': latest_row['humidity'],
                        'threshold': thresholds['humidity_high']
                    })
                elif latest_row['humidity'] < thresholds['humidity_low']:
                    warnings.append({
                        'type': 'humidity_low',
                        'severity': 'medium',
                        'message': f"低湿度预警：当前湿度 {latest_row['humidity']:.1f}%，低于阈值 {thresholds['humidity_low']:.1f}%",
                        'value': latest_row['humidity'],
                        'threshold': thresholds['humidity_low']
                    })
            
            # 检查土壤湿度
            if latest_row['soil_moisture']:
                if latest_row['soil_moisture'] < thresholds['soil_moisture_low']:
                    warnings.append({
                        'type': 'soil_moisture_low',
                        'severity': 'high',
                        'message': f"土壤缺水预警：当前土壤湿度 {latest_row['soil_moisture']:.1f}%，低于阈值 {thresholds['soil_moisture_low']:.1f}%",
                        'value': latest_row['soil_moisture'],
                        'threshold': thresholds['soil_moisture_low']
                    })
            
            return warnings
            
        except Exception as e:
            logging.error(f"Error checking environmental thresholds: {e}")
            return warnings
    
    def check_pest_disease_risk(self) -> List[Dict]:
        """检查病虫害风险"""
        warnings = []
        
        try:
            # 使用预测模型获取风险预测
            # prediction = self.predictor.predict_current_risk()
            
            # 使用模拟数据
            prediction = {
                "pest_risk": {
                    "aphids": 0.75,
                    "spider_mites": 0.35,
                    "scale_insects": 0.25
                },
                "disease_risk": {
                    "powdery_mildew": 0.65,
                    "rust": 0.45,
                    "leaf_spot": 0.35
                }
            }
            
            thresholds = self.config.WARNING_THRESHOLDS
            
            # 检查害虫风险
            for pest, risk in prediction.get('pest_risk', {}).items():
                if risk > thresholds.get('pest_risk', 0.7):
                    warnings.append({
                        'type': 'pest_risk',
                        'pest_type': pest,
                        'severity': 'high' if risk > 0.8 else 'medium',
                        'message': f"{pest}风险预警：当前风险指数 {risk:.2f}，超过阈值 {thresholds.get('pest_risk', 0.7):.2f}",
                        'value': risk,
                        'threshold': thresholds.get('pest_risk', 0.7)
                    })
            
            # 检查病害风险
            for disease, risk in prediction.get('disease_risk', {}).items():
                if risk > thresholds.get('disease_risk', 0.6):
                    warnings.append({
                        'type': 'disease_risk',
                        'disease_type': disease,
                        'severity': 'high' if risk > 0.8 else 'medium',
                        'message': f"{disease}风险预警：当前风险指数 {risk:.2f}，超过阈值 {thresholds.get('disease_risk', 0.6):.2f}",
                        'value': risk,
                        'threshold': thresholds.get('disease_risk', 0.6)
                    })
            
            return warnings
            
        except Exception as e:
            logging.error(f"Error checking pest/disease risk: {e}")
            return []
    
    def generate_warning_message(self, warning: Dict) -> Tuple[str, str]:
        """生成预警消息"""
        try:
            warning_type = warning['type']
            severity = warning['severity']
            message = warning['message']
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 生成标题
            severity_map = {
                'low': '低级',
                'medium': '中级',
                'high': '高级'
            }
            
            title = f"【{severity_map[severity]}预警】郎家园枣园监测系统"
            
            # 生成详细消息
            detailed_message = f"""
预警时间：{timestamp}
预警类型：{warning_type}
预警等级：{severity_map[severity]}
预警内容：{message}

建议措施：
"""
            
            # 根据预警类型添加建议措施
            if warning_type == 'temperature_high':
                detailed_message += "- 增加灌溉频率，保持土壤湿润\n- 设置遮阳网，减少直射阳光\n- 加强通风，降低温度"
            elif warning_type == 'temperature_low':
                detailed_message += "- 覆盖保温材料\n- 关闭通风设施\n- 必要时使用加热设备"
            elif warning_type == 'humidity_high':
                detailed_message += "- 加强通风，降低湿度\n- 注意防范真菌病害\n- 减少喷灌频率"
            elif warning_type == 'humidity_low':
                detailed_message += "- 增加喷雾次数\n- 调整灌溉方式\n- 关注植物水分状况"
            elif warning_type == 'soil_moisture_low':
                detailed_message += "- 立即灌溉\n- 检查灌溉系统\n- 调整灌溉计划"
            elif warning_type == 'pest_disease_risk':
                detailed_message += "- 加强田间巡查\n- 准备防治措施\n- 监测病虫害发展\n- 考虑预防性处理"
            
            detailed_message += f"\n\n郎家园枣园智能监测系统\n{timestamp}"
            
            return title, detailed_message
            
        except Exception as e:
            logging.error(f"Error generating warning message: {e}")
            return "预警通知", warning.get('message', '未知预警')
    
    def get_notification_recipients(self) -> List[Dict]:
        """获取通知接收者"""
        try:
            session = self.Session()
            
            # 获取所有活跃用户及其通知设置
            users = session.query(User).filter(User.is_active == True).all()
            recipients = []
            
            for user in users:
                # 获取用户的通知设置
                notification_settings = session.query(NotificationSetting).filter(
                    NotificationSetting.user_id == user.id
                ).all()
                
                # 构建用户通知配置
                user_notifications = {
                    'user_id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'phone': user.phone,
                    'notifications': {}
                }
                
                # 处理通知设置
                for setting in notification_settings:
                    user_notifications['notifications'][setting.notification_type] = {
                        'enabled': setting.is_enabled,
                        'thresholds': setting.threshold_settings or {}
                    }
                
                recipients.append(user_notifications)
            
            session.close()
            return recipients
            
        except Exception as e:
            logging.error(f"Error getting notification recipients: {e}")
            return []
    
    def send_warning_notifications(self, warning: Dict) -> Dict:
        """发送预警通知"""
        try:
            # 生成预警消息
            title, message = self.generate_warning_message(warning)
            
            # 获取接收者
            recipients = self.get_notification_recipients()
            
            sent_notifications = {
                'email': [],
                'sms': [],
                'push': []
            }
            
            # 发送通知
            for recipient in recipients:
                user_notifications = recipient['notifications']
                
                # 发送邮件
                if (user_notifications.get('email', {}).get('enabled', True) and 
                    recipient['email']):
                    
                    # 生成HTML邮件
                    html_message = self.generate_html_email(warning, message)
                    
                    if self.notification_manager.send_email(
                        recipient['email'], title, message, html_message
                    ):
                        sent_notifications['email'].append(recipient['email'])
                
                # 发送短信
                if (user_notifications.get('sms', {}).get('enabled', False) and 
                    recipient['phone']):
                    
                    # 生成简短的短信内容
                    sms_message = f"{title}\n{warning['message']}\n{datetime.now().strftime('%H:%M')}"
                    
                    if self.notification_manager.send_sms(recipient['phone'], sms_message):
                        sent_notifications['sms'].append(recipient['phone'])
                
                # 发送推送通知
                if user_notifications.get('push', {}).get('enabled', False):
                    # 这里需要用户的推送token，实际应用中需要存储
                    # user_token = get_user_push_token(recipient['user_id'])
                    # if user_token:
                    #     if self.notification_manager.send_push_notification(
                    #         user_token, title, warning['message']
                    #     ):
                    #         sent_notifications['push'].append(user_token)
                    pass
            
            return sent_notifications
            
        except Exception as e:
            logging.error(f"Error sending warning notifications: {e}")
            return {}
    
    def generate_html_email(self, warning: Dict, message: str) -> str:
        """生成HTML邮件内容"""
        try:
            severity_colors = {
                'low': '#28a745',
                'medium': '#ffc107',
                'high': '#dc3545'
            }
            
            color = severity_colors.get(warning['severity'], '#007bff')
            
            html = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; }}
                    .container {{ max-width: 600px; margin: 0 auto; }}
                    .header {{ background-color: {color}; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; background-color: #f8f9fa; }}
                    .warning-details {{ background-color: white; padding: 15px; border-radius: 5px; margin: 10px 0; }}
                    .footer {{ padding: 20px; text-align: center; color: #666; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h2>郎家园枣园监测系统预警</h2>
                    </div>
                    <div class="content">
                        <div class="warning-details">
                            <pre>{message}</pre>
                        </div>
                    </div>
                    <div class="footer">
                        <p>这是一条自动生成的预警通知，请不要回复此邮件。</p>
                        <p>如有疑问，请联系系统管理员。</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            return html
            
        except Exception as e:
            logging.error(f"Error generating HTML email: {e}")
            return message
    
    def save_warning_to_db(self, warning: Dict, sent_notifications: Dict):
        """保存预警记录到数据库"""
        try:
            session = self.Session()
            
            warning_record = WarningRecord(
                warning_type=warning['type'],
                severity=warning['severity'],
                message=warning['message'],
                location=warning.get('location', 'Default'),
                sent_notifications=sent_notifications
            )
            
            session.add(warning_record)
            session.commit()
            session.close()
            
            logging.info(f"Warning saved to database: {warning['type']}")
            
        except Exception as e:
            logging.error(f"Error saving warning to database: {e}")
    
    def run_warning_check(self):
        """运行预警检查"""
        try:
            all_warnings = []
            
            # 检查环境阈值
            env_warnings = self.check_environmental_thresholds()
            all_warnings.extend(env_warnings)
            
            # 检查病虫害风险
            pest_warnings = self.check_pest_disease_risk()
            all_warnings.extend(pest_warnings)
            
            # 处理预警
            for warning in all_warnings:
                logging.info(f"Processing warning: {warning['type']}")
                
                # 发送通知
                sent_notifications = self.send_warning_notifications(warning)
                
                # 保存到数据库
                self.save_warning_to_db(warning, sent_notifications)
            
            logging.info(f"Warning check completed. {len(all_warnings)} warnings processed.")
            
        except Exception as e:
            logging.error(f"Error running warning check: {e}")
    
    def start_monitoring(self, interval_minutes: int = 10):
        """启动监控"""
        import schedule
        import time
        
        schedule.every(interval_minutes).minutes.do(self.run_warning_check)
        
        logging.info(f"Started warning monitoring every {interval_minutes} minutes")
        
        while True:
            schedule.run_pending()
            time.sleep(1)

# 使用示例
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    config = Config()
    warning_system = WarningSystem(config)
    
    # 运行一次检查
    warning_system.run_warning_check()
    
    # 启动持续监控
    # warning_system.start_monitoring(interval_minutes=5) 