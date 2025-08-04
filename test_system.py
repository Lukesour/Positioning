#!/usr/bin/env python3
"""
系统测试脚本
"""
import sys
import os
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """测试模块导入"""
    print("测试模块导入...")
    
    try:
        from config.database import SOURCE_DB_CONFIG, TARGET_DB_CONFIG
        print("✓ 数据库配置导入成功")
    except Exception as e:
        print(f"✗ 数据库配置导入失败: {e}")
    
    try:
        from config.settings import MATCHING_CONFIG
        print("✓ 应用配置导入成功")
    except Exception as e:
        print(f"✗ 应用配置导入失败: {e}")
    
    try:
        from backend.models.case import UserProfile, CaseResponse
        print("✓ 数据模型导入成功")
    except Exception as e:
        print(f"✗ 数据模型导入失败: {e}")
    
    try:
        from backend.services.matching_service import MatchingService
        print("✓ 匹配服务导入成功")
    except Exception as e:
        print(f"✗ 匹配服务导入失败: {e}")
    
    try:
        from backend.services.llm_service import LLMService
        print("✓ LLM服务导入成功")
    except Exception as e:
        print(f"✗ LLM服务导入失败: {e}")

def test_user_profile():
    """测试用户配置文件模型"""
    print("\n测试用户配置文件模型...")
    
    try:
        from backend.models.case import UserProfile
        
        # 创建测试用户配置
        user_profile = UserProfile(
            undergrad_school="中山大学",
            school_tier="985院校",
            major="软件工程",
            gpa="85/100",
            language_test="雅思",
            language_score=6.5,
            gre_score=320,
            target_degree="硕士",
            target_countries=["香港", "新加坡"],
            target_major="计算机科学"
        )
        
        print("✓ 用户配置文件创建成功")
        print(f"  - 院校: {user_profile.undergrad_school}")
        print(f"  - 层次: {user_profile.school_tier}")
        print(f"  - 专业: {user_profile.major}")
        print(f"  - GPA: {user_profile.gpa}")
        print(f"  - 目标国家: {user_profile.target_countries}")
        
    except Exception as e:
        print(f"✗ 用户配置文件测试失败: {e}")

def test_matching_algorithm():
    """测试匹配算法"""
    print("\n测试匹配算法...")
    
    try:
        from backend.services.matching_service import MatchingService
        from backend.models.case import UserProfile
        
        # 创建模拟的数据库会话（这里只是测试算法逻辑）
        class MockDB:
            def query(self, model):
                return self
            
            def filter(self, *args):
                return self
            
            def all(self):
                return []  # 返回空列表进行测试
        
        db = MockDB()
        service = MatchingService(db)
        
        # 测试GPA解析
        gpa_4, gpa_100 = service.parse_user_gpa("3.5/4.0")
        assert gpa_4 == 3.5
        assert gpa_100 == 87.5
        print("✓ GPA解析测试通过")
        
        gpa_4, gpa_100 = service.parse_user_gpa("85/100")
        assert gpa_4 == 3.4
        assert gpa_100 == 85.0
        print("✓ GPA解析测试通过")
        
        # 测试院校层次评分
        score = service.calculate_school_tier_score("985院校", "985院校")
        assert score == 30  # 完全匹配
        print("✓ 院校层次评分测试通过")
        
        score = service.calculate_school_tier_score("985院校", "211院校")
        assert score == 15  # 相邻匹配
        print("✓ 院校层次评分测试通过")
        
    except Exception as e:
        print(f"✗ 匹配算法测试失败: {e}")

def test_project_structure():
    """测试项目结构"""
    print("\n测试项目结构...")
    
    required_files = [
        "requirements.txt",
        "README.md",
        "run_server.py",
        "run_etl.py",
        "backend/app/main.py",
        "backend/models/case.py",
        "backend/services/matching_service.py",
        "backend/services/llm_service.py",
        "backend/utils/database.py",
        "config/database.py",
        "config/settings.py",
        "scripts/etl_processor.py",
        "database/migrations/001_create_cases_table.sql",
        "frontend/index.html",
        "frontend/js/main.js"
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} 缺失")

def main():
    """主测试函数"""
    print("=" * 60)
    print("智能留学选校规划系统 - 系统测试")
    print("=" * 60)
    
    test_project_structure()
    test_imports()
    test_user_profile()
    test_matching_algorithm()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
    print("\n下一步:")
    print("1. 配置 .env 文件中的数据库连接信息")
    print("2. 创建 processed_cases 数据库")
    print("3. 运行数据库迁移: psql -d processed_cases -f database/migrations/001_create_cases_table.sql")
    print("4. 运行ETL处理: python run_etl.py")
    print("5. 启动服务器: python run_server.py")

if __name__ == "__main__":
    main()