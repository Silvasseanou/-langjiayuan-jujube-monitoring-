#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬虫功能测试脚本
测试所有爬虫功能是否正常运行
"""

import sys
import os
import json
import logging
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('crawler_test.log')
    ]
)

def test_market_analysis_import():
    """测试市场分析模块导入"""
    try:
        from modules.market_analysis import DataCollector, MarketAnalyzer, BrandPromotion
        from config import Config
        
        config = Config()
        
        logging.info("✅ 市场分析模块导入成功")
        
        # 测试DataCollector
        collector = DataCollector(config)
        logging.info("✅ DataCollector 创建成功")
        
        # 测试MarketAnalyzer
        analyzer = MarketAnalyzer(config)
        logging.info("✅ MarketAnalyzer 创建成功")
        
        # 测试BrandPromotion
        brand = BrandPromotion(config)
        logging.info("✅ BrandPromotion 创建成功")
        
        return True
        
    except Exception as e:
        logging.error(f"❌ 市场分析模块导入失败: {e}")
        return False

def test_crawler_methods():
    """测试爬虫方法"""
    try:
        from modules.market_analysis import DataCollector
        from config import Config
        
        config = Config()
        collector = DataCollector(config)
        
        # 测试各个爬虫方法是否存在
        methods = [
            'collect_ecommerce_data',
            'collect_taobao_data',
            'collect_tmall_data',
            'collect_jd_data',
            'collect_pdd_data',
            'collect_social_media_data',
            'save_data_to_db',
            'calculate_sentiment_score'
        ]
        
        for method in methods:
            if hasattr(collector, method):
                logging.info(f"✅ 方法 {method} 存在")
            else:
                logging.error(f"❌ 方法 {method} 不存在")
                return False
        
        return True
        
    except Exception as e:
        logging.error(f"❌ 爬虫方法测试失败: {e}")
        return False

def test_crawler_execution():
    """测试爬虫执行"""
    try:
        from modules.market_analysis import DataCollector
        from config import Config
        
        config = Config()
        collector = DataCollector(config)
        
        logging.info("🕷️ 开始测试爬虫执行...")
        
        # 测试淘宝爬虫
        logging.info("📱 测试淘宝爬虫...")
        taobao_data = collector.collect_taobao_data()
        logging.info(f"✅ 淘宝爬虫完成，收集到 {len(taobao_data)} 条数据")
        
        # 测试天猫爬虫
        logging.info("🛒 测试天猫爬虫...")
        tmall_data = collector.collect_tmall_data()
        logging.info(f"✅ 天猫爬虫完成，收集到 {len(tmall_data)} 条数据")
        
        # 测试京东爬虫
        logging.info("🏪 测试京东爬虫...")
        jd_data = collector.collect_jd_data()
        logging.info(f"✅ 京东爬虫完成，收集到 {len(jd_data)} 条数据")
        
        # 测试拼多多爬虫
        logging.info("🛍️ 测试拼多多爬虫...")
        pdd_data = collector.collect_pdd_data()
        logging.info(f"✅ 拼多多爬虫完成，收集到 {len(pdd_data)} 条数据")
        
        # 测试社交媒体爬虫
        logging.info("📱 测试社交媒体爬虫...")
        social_data = collector.collect_social_media_data()
        logging.info(f"✅ 社交媒体爬虫完成，收集到 {len(social_data)} 条数据")
        
        # 测试综合爬虫
        logging.info("🔄 测试综合爬虫...")
        all_data = collector.collect_ecommerce_data()
        logging.info(f"✅ 综合爬虫完成，收集到 {len(all_data)} 条数据")
        
        # 测试数据保存
        logging.info("💾 测试数据保存...")
        collector.save_data_to_db(all_data)
        logging.info("✅ 数据保存成功")
        
        # 输出数据样本
        if all_data:
            logging.info("📋 数据样本:")
            for i, item in enumerate(all_data[:3]):
                logging.info(f"  样本 {i+1}: {json.dumps(item, ensure_ascii=False, indent=2)}")
        
        return True
        
    except Exception as e:
        logging.error(f"❌ 爬虫执行测试失败: {e}")
        return False

def test_market_analysis():
    """测试市场分析功能"""
    try:
        from modules.market_analysis import MarketAnalyzer
        from config import Config
        
        config = Config()
        analyzer = MarketAnalyzer(config)
        
        logging.info("📊 测试市场分析功能...")
        
        # 测试生成市场报告
        report = analyzer.generate_market_report()
        logging.info(f"✅ 市场报告生成成功，包含 {len(report)} 个分析维度")
        
        # 输出报告样本
        logging.info("📈 市场报告样本:")
        for key, value in report.items():
            logging.info(f"  {key}: {str(value)[:100]}...")
        
        return True
        
    except Exception as e:
        logging.error(f"❌ 市场分析测试失败: {e}")
        return False

def test_brand_promotion():
    """测试品牌推广功能"""
    try:
        from modules.market_analysis import BrandPromotion
        from config import Config
        
        config = Config()
        brand = BrandPromotion(config)
        
        logging.info("🎯 测试品牌推广功能...")
        
        # 测试品牌故事生成
        story = brand.generate_brand_story()
        logging.info(f"✅ 品牌故事生成成功，长度: {len(story)} 字符")
        
        # 测试产品描述生成
        descriptions = brand.generate_product_descriptions({
            'name': '郎家园优质红枣',
            'variety': '和田枣',
            'size': '特大',
            'sweetness': '高'
        })
        logging.info(f"✅ 产品描述生成成功，生成 {len(descriptions)} 条描述")
        
        # 测试社交媒体内容生成
        social_content = brand.generate_social_media_content()
        logging.info(f"✅ 社交媒体内容生成成功，生成 {len(social_content)} 条内容")
        
        return True
        
    except Exception as e:
        logging.error(f"❌ 品牌推广测试失败: {e}")
        return False

def main():
    """主测试函数"""
    logging.info("🚀 开始爬虫功能测试")
    logging.info("=" * 60)
    
    tests = [
        ("模块导入", test_market_analysis_import),
        ("爬虫方法", test_crawler_methods),
        ("爬虫执行", test_crawler_execution),
        ("市场分析", test_market_analysis),
        ("品牌推广", test_brand_promotion)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        logging.info(f"\n🧪 运行测试: {test_name}")
        logging.info("-" * 40)
        
        try:
            if test_func():
                logging.info(f"✅ {test_name} 测试通过")
                passed += 1
            else:
                logging.error(f"❌ {test_name} 测试失败")
                failed += 1
        except Exception as e:
            logging.error(f"❌ {test_name} 测试异常: {e}")
            failed += 1
    
    # 输出测试结果
    logging.info("\n" + "=" * 60)
    logging.info("📊 测试结果汇总:")
    logging.info(f"✅ 通过: {passed}")
    logging.info(f"❌ 失败: {failed}")
    logging.info(f"📈 成功率: {passed/(passed+failed)*100:.1f}%")
    
    if failed == 0:
        logging.info("🎉 所有测试通过！爬虫功能正常")
        return True
    else:
        logging.error("⚠️ 部分测试失败，请检查相关功能")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 