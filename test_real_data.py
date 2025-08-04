#!/usr/bin/env python3
"""
真实数据测试脚本
展示系统使用真实数据的完整功能
"""
import requests
import json
import time

def test_real_data_system():
    """测试真实数据系统功能"""
    base_url = "http://localhost:8000"
    
    print("🎓 智能留学选校规划系统 - 真实数据测试")
    print("=" * 60)
    
    # 1. 检查数据量
    print("1. 检查系统数据...")
    try:
        response = requests.get(f"{base_url}/api/v1/cases/count")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 系统已加载 {data['total_cases']} 条真实案例数据")
        else:
            print(f"❌ 获取数据量失败: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return
    
    print()
    
    # 2. 测试不同背景的学生
    test_cases = [
        {
            "name": "211院校计算机学生 - 申请香港新加坡",
            "profile": {
                "undergrad_school": "北京邮电大学",
                "school_tier": "211院校",
                "major": "计算机科学与技术",
                "gpa": "3.2/4.0",
                "language_test": "雅思",
                "language_score": 6.5,
                "target_degree": "硕士",
                "target_countries": ["香港", "新加坡"],
                "target_major": "计算机科学"
            }
        },
        {
            "name": "985院校工程学生 - 申请英国澳洲",
            "profile": {
                "undergrad_school": "山东大学",
                "school_tier": "985院校",
                "major": "电子信息工程",
                "gpa": "85/100",
                "language_test": "雅思",
                "language_score": 7.0,
                "target_degree": "硕士",
                "target_countries": ["英国", "澳大利亚"],
                "target_major": "电子工程"
            }
        },
        {
            "name": "双非院校商科学生 - 申请香港",
            "profile": {
                "undergrad_school": "深圳大学",
                "school_tier": "双非院校",
                "major": "国际经济与贸易",
                "gpa": "3.5/4.0",
                "language_test": "雅思",
                "language_score": 6.5,
                "target_degree": "硕士",
                "target_countries": ["香港"],
                "target_major": "金融"
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"{i}. 测试案例: {test_case['name']}")
        print("-" * 50)
        
        try:
            response = requests.post(
                f"{base_url}/api/v1/school-planning",
                json=test_case['profile'],
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # 显示匹配结果
                matched_cases = data['matched_cases']
                print(f"   📊 匹配到 {len(matched_cases)} 个相似案例")
                
                # 显示前5个最相似的案例
                print("   🎯 最相似的5个案例:")
                for j, case in enumerate(matched_cases[:5], 1):
                    similarity = case.get('similarity_score', 0)
                    university = case.get('university', 'N/A')
                    program = case.get('program', 'N/A')
                    undergrad_school = case.get('undergrad_school', 'N/A')
                    undergrad_tier = case.get('undergrad_school_tier', 'N/A')
                    gpa = case.get('gpa_scale_4', 'N/A')
                    
                    # 清理大学名称（去掉多余信息）
                    if '\n' in university:
                        university = university.split('\n')[0]
                    
                    print(f"      {j}. {university} - {program}")
                    print(f"         学生背景: {undergrad_school} ({undergrad_tier}) GPA:{gpa}")
                    print(f"         相似度: {similarity:.1f}分")
                    print()
                
                # 显示推荐结果
                recommendations = data['analysis_report']['recommendations']
                print("   🏆 选校建议:")
                print(f"      冲刺院校: {len(recommendations['reach'])} 所")
                for school in recommendations['reach']:
                    print(f"        - {school['university']} ({school['program']})")
                
                print(f"      核心院校: {len(recommendations['target'])} 所")
                for school in recommendations['target'][:3]:  # 只显示前3个
                    print(f"        - {school['university']} ({school['program']})")
                
                print(f"      保底院校: {len(recommendations['safety'])} 所")
                for school in recommendations['safety']:
                    print(f"        - {school['university']} ({school['program']})")
                
            else:
                print(f"   ❌ 请求失败: {response.status_code}")
                print(f"      错误信息: {response.text}")
                
        except Exception as e:
            print(f"   ❌ 测试异常: {e}")
        
        print()
        print()
    
    print("=" * 60)
    print("🎉 真实数据测试完成！")
    print()
    print("💡 系统特点:")
    print("   ✅ 使用3480条真实留学案例数据")
    print("   ✅ 智能匹配算法，多维度相似度计算")
    print("   ✅ 科学的三档选校策略")
    print("   ✅ 覆盖985/211/双非各层次院校")
    print("   ✅ 支持香港、新加坡、英国、澳洲等热门地区")
    print()
    print("🌐 访问系统:")
    print(f"   前端界面: {base_url}")
    print(f"   API文档: {base_url}/docs")

if __name__ == "__main__":
    test_real_data_system()