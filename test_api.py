#!/usr/bin/env python3
"""
API功能测试脚本
"""
import requests
import json
import time

def test_api():
    """测试API功能"""
    base_url = "http://localhost:8000"
    
    print("🚀 开始测试智能留学选校规划系统API")
    print("=" * 60)
    
    # 1. 测试健康检查
    print("1. 测试健康检查...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ 健康检查通过")
            print(f"   响应: {response.json()}")
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 健康检查异常: {e}")
    
    print()
    
    # 2. 测试案例数量
    print("2. 测试案例数量...")
    try:
        response = requests.get(f"{base_url}/api/v1/cases/count")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 案例数量获取成功: {data['total_cases']} 条")
        else:
            print(f"❌ 案例数量获取失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 案例数量获取异常: {e}")
    
    print()
    
    # 3. 测试配置选项
    print("3. 测试配置选项...")
    try:
        response = requests.get(f"{base_url}/api/v1/config/options")
        if response.status_code == 200:
            data = response.json()
            print("✅ 配置选项获取成功")
            print(f"   院校层次: {data['school_tiers']}")
            print(f"   语言考试: {data['language_tests']}")
            print(f"   目标国家: {data['countries']}")
        else:
            print(f"❌ 配置选项获取失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 配置选项获取异常: {e}")
    
    print()
    
    # 4. 测试选校规划（主要功能）
    print("4. 测试选校规划（主要功能）...")
    
    test_cases = [
        {
            "name": "985院校软件工程学生",
            "data": {
                "undergrad_school": "中山大学",
                "school_tier": "985院校",
                "major": "软件工程",
                "gpa": "85/100",
                "language_test": "雅思",
                "language_score": 6.5,
                "target_degree": "硕士",
                "target_countries": ["香港", "新加坡"],
                "target_major": "计算机科学"
            }
        },
        {
            "name": "211院校计算机学生",
            "data": {
                "undergrad_school": "北京邮电大学",
                "school_tier": "211院校",
                "major": "计算机科学与技术",
                "gpa": "3.2/4.0",
                "language_test": "雅思",
                "language_score": 6.0,
                "target_degree": "硕士",
                "target_countries": ["香港"],
                "target_major": "信息工程"
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"   测试案例 {i}: {test_case['name']}")
        try:
            response = requests.post(
                f"{base_url}/api/v1/school-planning",
                json=test_case['data'],
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ 选校规划成功")
                print(f"      匹配案例数: {len(data['matched_cases'])}")
                
                # 显示推荐结果
                recommendations = data['analysis_report']['recommendations']
                print(f"      冲刺院校: {len(recommendations['reach'])} 所")
                print(f"      核心院校: {len(recommendations['target'])} 所")
                print(f"      保底院校: {len(recommendations['safety'])} 所")
                
                # 显示前3个匹配案例
                print("      前3个匹配案例:")
                for j, case in enumerate(data['matched_cases'][:3], 1):
                    print(f"        {j}. {case['university']} - {case['program']} (相似度: {case.get('similarity_score', 'N/A')})")
                
            else:
                print(f"   ❌ 选校规划失败: {response.status_code}")
                print(f"      错误信息: {response.text}")
                
        except Exception as e:
            print(f"   ❌ 选校规划异常: {e}")
        
        print()
    
    print("=" * 60)
    print("🎉 API测试完成")
    print()
    print("💡 系统使用说明:")
    print(f"   - 前端界面: {base_url}")
    print(f"   - API文档: {base_url}/docs")
    print(f"   - 健康检查: {base_url}/health")

if __name__ == "__main__":
    test_api()