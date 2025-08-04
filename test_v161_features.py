#!/usr/bin/env python3
"""
智能留学选校规划系统 V1.6.1 功能测试
测试新增的专业排名和预算字段功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import json
import asyncio
from backend.models.case import UserProfile, AnalysisReport
from backend.services.llm_service import LLMService

def test_user_profile_v161():
    """测试V1.6.1新增字段的UserProfile模型"""
    print("🧪 测试 UserProfile V1.6.1 新增字段...")
    
    # 测试包含新字段的用户档案
    user_data = {
        # 基本字段
        "undergrad_school": "北京大学",
        "school_tier": "985",
        "major": "计算机科学与技术",
        "gpa": "3.8/4.0",
        "language_test": "TOEFL",
        "language_score": 105.0,
        "gre_score": 325,
        "target_degree": "硕士",
        "target_countries": ["美国", "英国"],
        "target_major": "计算机科学",
        
        # V1.5字段
        "major_gpa": "3.9/4.0",
        "exchange_experience": True,
        "prerequisite_courses": "高等数学、线性代数、数据结构、算法设计",
        "practical_experiences": [
            {
                "organization": "字节跳动",
                "position": "算法实习生",
                "start_date": "2023-06",
                "end_date": "2023-09",
                "description": "负责推荐算法优化，提升CTR 15%"
            }
        ],
        "achievements": "发表SCI论文1篇，获得国家奖学金",
        "target_majors": ["计算机科学", "人工智能", "数据科学"],
        "post_graduation_plan": "先在当地工作",
        "school_selection_factors": ["专业排名", "地理位置与就业", "教授与科研实力"],
        
        # V1.6.1 新增字段
        "major_ranking": "Top 5%",
        "budget": "50-70万人民币"
    }
    
    try:
        # 创建UserProfile实例
        user_profile = UserProfile(**user_data)
        
        # 验证新字段
        assert user_profile.major_ranking == "Top 5%", "专业排名字段测试失败"
        assert user_profile.budget == "50-70万人民币", "预算字段测试失败"
        
        # 验证JSON序列化
        json_data = user_profile.model_dump()
        assert "major_ranking" in json_data, "JSON序列化缺少专业排名字段"
        assert "budget" in json_data, "JSON序列化缺少预算字段"
        
        print("✅ UserProfile V1.6.1 新增字段测试通过")
        return user_profile
        
    except Exception as e:
        print(f"❌ UserProfile V1.6.1 测试失败: {e}")
        return None

def test_llm_prompt_v161():
    """测试LLM Prompt是否包含V1.6.1新增字段"""
    print("\n🧪 测试 LLM Prompt V1.6.1 增强...")
    
    # 创建测试用户档案
    user_profile = test_user_profile_v161()
    if not user_profile:
        print("❌ 无法创建用户档案，跳过LLM测试")
        return False
    
    try:
        # 创建LLM服务实例
        llm_service = LLMService()
        
        # 创建模拟案例数据
        from backend.models.case import CaseResponse
        mock_cases = [
            CaseResponse(
                id=1,
                university="斯坦福大学",
                program="计算机科学硕士",
                degree_level="硕士",
                undergrad_school="清华大学",
                undergrad_school_tier="985",
                undergrad_major="计算机科学",
                gpa_scale_4=3.9,
                language_type="TOEFL",
                language_score=108.0,
                gre_score=330,
                similarity_score=85.5
            )
        ]
        
        # 构建Prompt
        prompt = llm_service.build_prompt(user_profile, mock_cases)
        
        # 验证新字段是否包含在Prompt中
        assert "专业排名" in prompt, "Prompt中缺少专业排名信息"
        assert "Top 5%" in prompt, "Prompt中缺少具体专业排名值"
        assert "留学预算" in prompt, "Prompt中缺少预算信息"
        assert "50-70万人民币" in prompt, "Prompt中缺少具体预算值"
        assert "预算情况" in prompt, "Prompt中缺少预算分析指导"
        
        print("✅ LLM Prompt V1.6.1 增强测试通过")
        print(f"📝 Prompt长度: {len(prompt)} 字符")
        
        # 可选：打印Prompt片段用于验证
        print("\n📋 Prompt关键片段:")
        lines = prompt.split('\n')
        for line in lines:
            if any(keyword in line for keyword in ["专业排名", "留学预算", "预算情况"]):
                print(f"  {line.strip()}")
        
        return True
        
    except Exception as e:
        print(f"❌ LLM Prompt V1.6.1 测试失败: {e}")
        return False

def test_backward_compatibility():
    """测试向后兼容性"""
    print("\n🧪 测试向后兼容性...")
    
    # 测试不包含新字段的旧版本数据
    old_user_data = {
        "undergrad_school": "复旦大学",
        "school_tier": "985",
        "major": "金融学",
        "gpa": "3.7/4.0",
        "language_test": "IELTS",
        "language_score": 7.5,
        "target_degree": "硕士",
        "target_countries": ["英国", "香港"],
        "target_major": "金融工程"
    }
    
    try:
        # 创建UserProfile实例（不包含新字段）
        user_profile = UserProfile(**old_user_data)
        
        # 验证新字段的默认值
        assert user_profile.major_ranking is None, "专业排名字段默认值应为None"
        assert user_profile.budget is None, "预算字段默认值应为None"
        
        # 验证LLM服务仍能正常工作
        llm_service = LLMService()
        prompt = llm_service.build_prompt(user_profile, [])
        
        # 验证Prompt中包含"未提供"或"未明确"等默认值
        assert "未提供" in prompt or "未明确" in prompt, "Prompt应包含默认值处理"
        
        print("✅ 向后兼容性测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 向后兼容性测试失败: {e}")
        return False

def test_optional_fields():
    """测试可选字段的处理"""
    print("\n🧪 测试可选字段处理...")
    
    test_cases = [
        # 只有专业排名，没有预算
        {
            "undergrad_school": "上海交通大学",
            "school_tier": "985",
            "major": "机械工程",
            "gpa": "3.6/4.0",
            "language_test": "TOEFL",
            "target_degree": "硕士",
            "target_countries": ["德国"],
            "target_major": "机械工程",
            "major_ranking": "10/150"
        },
        # 只有预算，没有专业排名
        {
            "undergrad_school": "浙江大学",
            "school_tier": "985",
            "major": "电子工程",
            "gpa": "3.8/4.0",
            "language_test": "IELTS",
            "target_degree": "硕士",
            "target_countries": ["美国"],
            "target_major": "电子工程",
            "budget": "预算充足"
        },
        # 两个字段都有
        {
            "undergrad_school": "中山大学",
            "school_tier": "985",
            "major": "生物医学工程",
            "gpa": "3.7/4.0",
            "language_test": "TOEFL",
            "target_degree": "硕士",
            "target_countries": ["加拿大"],
            "target_major": "生物工程",
            "major_ranking": "Top 10%",
            "budget": "30-50万人民币"
        }
    ]
    
    try:
        llm_service = LLMService()
        
        for i, test_data in enumerate(test_cases, 1):
            print(f"  测试用例 {i}...")
            
            user_profile = UserProfile(**test_data)
            prompt = llm_service.build_prompt(user_profile, [])
            
            # 验证字段处理
            if "major_ranking" in test_data:
                assert test_data["major_ranking"] in prompt, f"用例{i}: 专业排名未包含在Prompt中"
            else:
                assert "未提供" in prompt, f"用例{i}: 缺少默认值处理"
                
            if "budget" in test_data:
                assert test_data["budget"] in prompt, f"用例{i}: 预算未包含在Prompt中"
            else:
                assert "未明确" in prompt, f"用例{i}: 缺少默认值处理"
        
        print("✅ 可选字段处理测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 可选字段处理测试失败: {e}")
        return False

def main():
    """运行所有V1.6.1功能测试"""
    print("🚀 开始 V1.6.1 功能测试")
    print("=" * 50)
    
    test_results = []
    
    # 运行各项测试
    test_results.append(("UserProfile V1.6.1 新增字段", test_user_profile_v161() is not None))
    test_results.append(("LLM Prompt V1.6.1 增强", test_llm_prompt_v161()))
    test_results.append(("向后兼容性", test_backward_compatibility()))
    test_results.append(("可选字段处理", test_optional_fields()))
    
    # 汇总测试结果
    print("\n" + "=" * 50)
    print("📊 测试结果汇总:")
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 总体结果: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 所有 V1.6.1 功能测试通过！")
        return True
    else:
        print("⚠️  部分测试失败，请检查相关功能")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)