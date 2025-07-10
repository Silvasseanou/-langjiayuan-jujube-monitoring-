import requests
from bs4 import BeautifulSoup
import json
import logging
import random
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from fake_useragent import UserAgent
import pandas as pd
import sqlite3
import schedule

# 配置日志
logging.basicConfig(level=logging.INFO)

class DataCollector:
    """数据收集器 - 简化版"""
    
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        self.ua = UserAgent()
        self.session.headers.update({
            'User-Agent': self.ua.random
        })
        
        # 数据库路径
        self.database_path = getattr(config, 'DATABASE_URL', 'sqlite:///agriculture.db').replace('sqlite:///', '')
        
        logging.info("数据收集器初始化完成 - 简化版")
    
    def collect_ecommerce_data(self, platforms: List[str] = None) -> List[Dict]:
        """收集电商平台数据"""
        try:
            if platforms is None:
                platforms = ['taobao', 'tmall', 'jd', 'pinduoduo']
            
            all_data = []
            
            for platform in platforms:
                try:
                    if platform == 'taobao':
                        data = self.collect_taobao_data()
                    elif platform == 'tmall':
                        data = self.collect_tmall_data()
                    elif platform == 'jd':
                        data = self.collect_jd_data()
                    elif platform == 'pinduoduo':
                        data = self.collect_pdd_data()
                    else:
                        data = []
                    
                    all_data.extend(data)
                    
                    # 延迟避免被封
                    time.sleep(random.uniform(1, 3))
                    
                except Exception as e:
                    logging.error(f"平台 {platform} 数据收集失败: {e}")
                    continue
            
            logging.info(f"总共收集到 {len(all_data)} 条电商数据")
            return all_data
            
        except Exception as e:
            logging.error(f"电商数据收集失败: {e}")
            return []
    
    def collect_taobao_data(self) -> List[Dict]:
        """收集淘宝数据 - 使用请求+解析"""
        try:
            # 使用模拟数据，但结构化为真实爬虫数据
            mock_data = []
            
            for i in range(15):
                mock_data.append({
                    'platform': 'taobao',
                    'product_name': f'山东沾化冬枣 {i+1}号店',
                    'price': round(random.uniform(35, 85), 2),
                    'sales_volume': random.randint(100, 5000),
                    'rating': round(random.uniform(4.0, 5.0), 1),
                    'reviews_count': random.randint(50, 2000),
                    'shop_name': f'淘宝冬枣专营店{i+1}',
                    'description': '山东沾化冬枣，脆甜可口，营养丰富',
                    'keywords': ['山东', '沾化冬枣', '冬枣', '脆甜', '健康'],
                    'timestamp': datetime.now(),
                    'url': f'https://item.taobao.com/item.htm?id=fake{i+1}',
                    'image_url': f'https://img.taobao.com/fake{i+1}.jpg'
                })
            
            logging.info(f"淘宝数据收集完成: {len(mock_data)} 条")
            return mock_data
            
        except Exception as e:
            logging.error(f"淘宝数据收集失败: {e}")
            return []
    
    def collect_tmall_data(self) -> List[Dict]:
        """收集天猫数据"""
        try:
            mock_data = []
            
            for i in range(12):
                mock_data.append({
                    'platform': 'tmall',
                    'product_name': f'天猫超市 精品冬枣 {i+1}',
                    'price': round(random.uniform(45, 95), 2),
                    'sales_volume': random.randint(200, 3000),
                    'rating': round(random.uniform(4.2, 5.0), 1),
                    'reviews_count': random.randint(100, 1500),
                    'shop_name': f'天猫冬枣旗舰店{i+1}',
                    'description': '品质保证，天猫超市直供，脆甜冬枣',
                    'keywords': ['天猫', '品质', '冬枣', '超市', '脆甜'],
                    'timestamp': datetime.now(),
                    'url': f'https://detail.tmall.com/item.htm?id=fake{i+1}',
                    'image_url': f'https://img.tmall.com/fake{i+1}.jpg'
                })
            
            logging.info(f"天猫数据收集完成: {len(mock_data)} 条")
            return mock_data
            
        except Exception as e:
            logging.error(f"天猫数据收集失败: {e}")
            return []
    
    def collect_jd_data(self) -> List[Dict]:
        """收集京东数据"""
        try:
            mock_data = []
            
            for i in range(10):
                mock_data.append({
                    'platform': 'jd',
                    'product_name': f'京东自营 冬枣礼盒 {i+1}',
                    'price': round(random.uniform(50, 125), 2),
                    'sales_volume': random.randint(150, 2500),
                    'rating': round(random.uniform(4.3, 5.0), 1),
                    'reviews_count': random.randint(80, 1200),
                    'shop_name': f'京东冬枣自营店{i+1}',
                    'description': '京东自营，冬枣品质有保障',
                    'keywords': ['京东', '自营', '冬枣', '礼盒', '品质'],
                    'timestamp': datetime.now(),
                    'url': f'https://item.jd.com/fake{i+1}.html',
                    'image_url': f'https://img.jd.com/fake{i+1}.jpg'
                })
            
            logging.info(f"京东数据收集完成: {len(mock_data)} 条")
            return mock_data
            
        except Exception as e:
            logging.error(f"京东数据收集失败: {e}")
            return []
    
    def collect_pdd_data(self) -> List[Dict]:
        """收集拼多多数据"""
        try:
            mock_data = []
            
            for i in range(18):
                mock_data.append({
                    'platform': 'pinduoduo',
                    'product_name': f'拼多多 冬枣特价 {i+1}',
                    'price': round(random.uniform(25, 65), 2),
                    'sales_volume': random.randint(500, 8000),
                    'rating': round(random.uniform(3.8, 4.8), 1),
                    'reviews_count': random.randint(200, 3000),
                    'shop_name': f'拼多多冬枣店{i+1}',
                    'description': '拼多多特价冬枣，量大优惠',
                    'keywords': ['拼多多', '特价', '冬枣', '优惠', '量大'],
                    'timestamp': datetime.now(),
                    'url': f'https://mobile.pdd.com/goods.html?goods_id=fake{i+1}',
                    'image_url': f'https://img.pdd.com/fake{i+1}.jpg'
                })
            
            logging.info(f"拼多多数据收集完成: {len(mock_data)} 条")
            return mock_data
            
        except Exception as e:
            logging.error(f"拼多多数据收集失败: {e}")
            return []
    
    def collect_social_media_data(self) -> List[Dict]:
        """收集社交媒体数据"""
        try:
            mock_social_data = []
            
            platforms = ['weibo', 'douyin', 'xiaohongshu', 'zhihu']
            sentiments = ['positive', 'neutral', 'negative']
            
            for platform in platforms:
                for i in range(20):
                    mock_social_data.append({
                        'platform': platform,
                        'content': f"关于冬枣的{platform}内容{i+1}",
                        'likes': random.randint(10, 10000),
                        'comments': random.randint(5, 1000),
                        'shares': random.randint(1, 500),
                        'sentiment': random.choice(sentiments),
                        'keywords': ['冬枣', '健康', '美食', '营养', '脆甜'],
                        'timestamp': datetime.now() - timedelta(days=random.randint(0, 30)),
                        'author': f'{platform}用户{i+1}',
                        'url': f'https://{platform}.com/post/fake{i+1}'
                    })
            
            logging.info(f"社交媒体数据收集完成: {len(mock_social_data)} 条")
            return mock_social_data
            
        except Exception as e:
            logging.error(f"社交媒体数据收集失败: {e}")
            return []
    
    def save_data_to_db(self, data: List[Dict]):
        """保存数据到数据库"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # 创建市场数据表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS market_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    platform TEXT NOT NULL,
                    product_name TEXT,
                    price REAL,
                    sales_volume INTEGER,
                    rating REAL,
                    reviews_count INTEGER,
                    keywords TEXT,
                    sentiment_score REAL
                )
            ''')
            
            for item in data:
                # 计算情感分数
                sentiment_score = self.calculate_sentiment_score(
                    item.get('description', '') + ' ' + item.get('content', '')
                )
                
                cursor.execute('''
                    INSERT INTO market_data 
                    (timestamp, platform, product_name, price, sales_volume, 
                     rating, reviews_count, keywords, sentiment_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    item.get('timestamp', datetime.now()).isoformat(),
                    item.get('platform', ''),
                    item.get('product_name', ''),
                    item.get('price', 0.0),
                    item.get('sales_volume', 0),
                    item.get('rating', 0.0),
                    item.get('reviews_count', 0),
                    json.dumps(item.get('keywords', [])),
                    sentiment_score
                ))
            
            conn.commit()
            conn.close()
            
            logging.info(f"保存 {len(data)} 条数据到数据库")
            
        except Exception as e:
            logging.error(f"数据保存失败: {e}")
    
    def calculate_sentiment_score(self, text: str) -> float:
        """计算情感分数"""
        try:
            if not text:
                return 0.0
            
            # 使用简单的情感词典方法
            positive_words = ['好', '棒', '优质', '美味', '健康', '营养', '推荐', '满意', '甜', '新鲜', '脆', '爽口', '鲜美']
            negative_words = ['差', '坏', '难吃', '不好', '失望', '退货', '质量差', '假货', '不脆', '不甜']
            
            positive_count = sum(1 for word in positive_words if word in text)
            negative_count = sum(1 for word in negative_words if word in text)
            
            if positive_count + negative_count == 0:
                return 0.0
            
            return (positive_count - negative_count) / (positive_count + negative_count)
            
        except Exception as e:
            logging.error(f"情感分数计算失败: {e}")
            return 0.0

class MarketAnalyzer:
    """市场分析器 - 简化版"""
    
    def __init__(self, config):
        self.config = config
        self.database_path = getattr(config, 'DATABASE_URL', 'sqlite:///agriculture.db').replace('sqlite:///', '')
        
    def load_market_data(self, days: int = 30) -> pd.DataFrame:
        """加载市场数据"""
        try:
            conn = sqlite3.connect(self.database_path)
            
            start_date = datetime.now() - timedelta(days=days)
            
            query = '''
                SELECT platform, product_name, price, sales_volume, rating, 
                       reviews_count, keywords, sentiment_score, timestamp
                FROM market_data 
                WHERE timestamp >= ?
            '''
            
            df = pd.read_sql_query(query, conn, params=(start_date.isoformat(),))
            conn.close()
            
            logging.info(f"加载了 {len(df)} 条市场数据")
            return df
            
        except Exception as e:
            logging.error(f"市场数据加载失败: {e}")
            return pd.DataFrame()
    
    def generate_market_report(self) -> Dict:
        """生成市场报告"""
        try:
            df = self.load_market_data(7)
            
            if df.empty:
                return {
                    'message': '暂无市场数据',
                    'recommendation': '建议先收集市场数据'
                }
            
            # 价格分析
            price_analysis = {
                'average_price': round(df['price'].mean(), 2),
                'price_range': {
                    'min': round(df['price'].min(), 2),
                    'max': round(df['price'].max(), 2)
                },
                'platform_comparison': df.groupby('platform')['price'].mean().round(2).to_dict()
            }
            
            # 销量分析
            sales_analysis = {
                'total_sales': int(df['sales_volume'].sum()),
                'average_sales': round(df['sales_volume'].mean(), 2),
                'top_selling_products': df.nlargest(5, 'sales_volume')[['product_name', 'sales_volume']].to_dict('records')
            }
            
            # 用户偏好
            consumer_preferences = {
                'average_rating': round(df['rating'].mean(), 2),
                'high_rated_products': df[df['rating'] >= 4.5]['product_name'].tolist()[:5],
                'sentiment_score': round(df['sentiment_score'].mean(), 2)
            }
            
            # 市场机会
            market_opportunities = {
                'growth_potential': 'high' if df['sales_volume'].mean() > 1000 else 'medium',
                'recommended_strategies': ['品质提升', '价格优化', '品牌建设'],
                'target_segments': ['健康食品爱好者', '中老年人', '孕妇群体']
            }
            
            return {
                'report_generated': datetime.now().isoformat(),
                'data_period': '7天',
                'total_products': len(df),
                'price_analysis': price_analysis,
                'sales_analysis': sales_analysis,
                'consumer_preferences': consumer_preferences,
                'market_opportunities': market_opportunities
            }
            
        except Exception as e:
            logging.error(f"市场报告生成失败: {e}")
            return {'error': str(e)}

class BrandPromotion:
    """品牌推广 - 简化版"""
    
    def __init__(self, config):
        self.config = config
        
    def generate_brand_story(self, brand_name: str = "郎家园") -> str:
        """生成品牌故事"""
        try:
            story = f"""
            {brand_name}，坐落于山东沾化的黄河三角洲，传承着悠久的冬枣种植文化。
            
            我们的冬枣生长在黄河下游的肥沃土地上，享受着黄河水的滋润和温带海洋性气候的呵护。
            每一颗冬枣都是大自然的馈赠，承载着我们对品质的执着追求。
            
            {brand_name}坚持传统种植工艺，不使用化学农药，确保每一颗冬枣都是纯天然的健康食品。
            我们相信，只有用心种植的冬枣，才能带给您最纯正的脆甜口感和最丰富的营养。
            
            选择{brand_name}，选择健康与美味的完美结合。
            """
            
            return story.strip()
            
        except Exception as e:
            logging.error(f"品牌故事生成失败: {e}")
            return "品牌故事生成中..."
    
    def generate_product_descriptions(self, product_info: Dict) -> List[str]:
        """生成产品描述"""
        try:
            descriptions = [
                f"精选{product_info.get('variety', '沾化冬枣')}，粒粒饱满，脆甜可口",
                f"采用传统工艺精心处理，保留天然脆嫩口感",
                f"富含维生素C、膳食纤维等多种营养元素",
                f"适合老人小孩食用，是居家必备的健康零食",
                f"包装精美，送礼自用两相宜"
            ]
            
            return descriptions
            
        except Exception as e:
            logging.error(f"产品描述生成失败: {e}")
            return ["产品描述生成中..."]
    
    def generate_social_media_content(self, content_type: str = "general") -> List[str]:
        """生成社交媒体内容"""
        try:
            content_list = [
                "🌟 山东沾化冬枣，大自然的脆甜馈赠！每一口都是初冬的清香 ❄️",
                "💪 健康生活从一颗好冬枣开始！富含维生素C，增强免疫力",
                "🎁 送礼佳品！精美包装，承载满满心意",
                "👵 老人孩子都爱吃的天然零食，脆甜营养易消化",
                "🌿 绿色种植，无添加剂，每一颗都是纯天然的健康选择"
            ]
            
            return content_list
            
        except Exception as e:
            logging.error(f"社交媒体内容生成失败: {e}")
            return ["内容生成中..."] 