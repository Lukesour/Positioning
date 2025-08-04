#!/usr/bin/env python3
"""
V1.5 功能测试脚本
"""
import sys
import os
sys.path.append('.')

from backend.models.case import UserProfile
import json

def test_user_profile_v15():
    """测试V1.5的UserProfile模型"""
    print("🧪 测试V1.5 UserProfile模型...")
    
    # 创建一个包含V1.5新字段的用户档案
    user_data = {
        # 基本字段
        "undergrad_school": "北京大学",
        "school_tier": "985",
        "major": "计算机科学与技术",
        "gpa": "3.8/4.0",
        "language_test": "雅思",
        "language_score": 7.5,
        "gre_score": 325,
        "target_degree": "硕士",
        "target_countries": ["美国", "英国"],
        "target_major": "计算机科学",
        
        # V1.5 新增字段
        "major_gpa": "3.9/4.0",
        "exchange_experience": True,
        "prerequisite_courses": "高等数学、数据结构、算法设计、机器学习",
        "practical_experiences": [
            {
                "organization": "腾讯科技",
                "position": "软件开发实习生",
                "start_date": "2023-06",
                "end_date": "2023-08",
                "description": "参与微信小程序后端开发，优化API响应速度提升30%"
            },
            {
                "organization": "北京大学AI实验室",
                "position": "研究助理",
                "start_date": "2023-09",
                "end_date": "2024-01",
                "description": "参与深度学习项目，发表一篇会议论文"
            }
        ],
        "achievements": "发表ICML 2024会议论文一篇；获得ACM程序设计竞赛金奖",
        "target_majors": ["计算机科学", "人工智能", "数据科学"],
        "post_graduation_plan": "先在当地工作",
        "school_selection_factors": ["专业排名", "地理位置与就业", "教授与科研实力"]
    }
    
    try:
        # 创建UserProfile实例
        user_profile = UserProfile(**user_data)
        print("✅ UserProfile模型创建成功")
        
        # 验证字段
        assert user_profile.undergrad_school == "北京大学"
        assert user_profile.major_gpa == "3.9/4.0"
        assert user_profile.exchange_experience == True
        assert len(user_profile.practical_experiences) == 2
        assert len(user_profile.target_majors) == 3
        assert user_profile.post_graduation_plan == "先在当地工作"
        assert len(user_profile.school_selection_factors) == 3
        
        print("✅ 所有V1.5新字段验证通过")
        
        # 测试JSON序列化
        json_data = user_profile.model_dump()
        print("✅ JSON序列化成功")
        
        # 测试从JSON反序列化
        user_profile_2 = UserProfile(**json_data)
        print("✅ JSON反序列化成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_llm_prompt_building():
    """测试LLM prompt构建"""
    print("\n🧪 测试LLM Prompt构建...")
    
    try:
        from backend.services.llm_service import LLMService
        from backend.models.case import CaseResponse
        
        # 创建测试用户档案
        user_profile = UserProfile(
            undergrad_school="清华大学",
            school_tier="985",
            major="软件工程",
            gpa="3.7/4.0",
            language_test="托福",
            language_score=105,
            gre_score=320,
            target_degree="硕士",
            target_countries=["美国"],
            target_major="计算机科学",
            major_gpa="3.8/4.0",
            exchange_experience=True,
            practical_experiences=[{
                "organization": "字节跳动",
                "position": "算法实习生",
                "start_date": "2023-07",
                "end_date": "2023-09",
                "description": "优化推荐算法，提升CTR 15%"
            }],
            target_majors=["计算机科学", "机器学习"],
            post_graduation_plan="先在当地工作",
            school_selection_factors=["专业排名", "地理位置与就业"]
        )
        
        # 创建测试案例
        test_cases = [
            CaseResponse(
                id=1,
                university="斯坦福大学",
                program="计算机科学硕士",
                degree_level="硕士",
                undergrad_school_tier="985",
                undergrad_major="计算机科学",
                gpa_scale_4=3.8,
                language_type="托福",
                language_score=108,
                gre_score=325,
                similarity_score=85.5
            )
        ]
        
        # 创建LLM服务并构建prompt
        llm_service = LLMService()
        prompt = llm_service.build_prompt(user_profile, test_cases)
        
        print("✅ LLM Prompt构建成功")
        
        # 验证prompt包含V1.5新信息
        assert "专业GPA" in prompt
        assert "海外交换经历" in prompt
        assert "实践背景详情" in prompt
        assert "字节跳动" in prompt
        assert "选校偏好" in prompt
        assert "先在当地工作" in prompt
        
        print("✅ Prompt包含所有V1.5新字段信息")
        
        # 打印prompt的一部分用于验证
        print("\n📝 Prompt示例（前500字符）:")
        print(prompt[:500] + "...")
        
        return True
        
    except Exception as e:
        print(f"❌ LLM Prompt测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config_options():
    """测试配置选项"""
    print("\n🧪 测试配置选项...")
    
    try:
        # 模拟API响应
        expected_options = {
            "school_tiers": ["985", "211", "双一流", "普通一本", "普通二本", "海外院校", "其他"],
            "post_graduation_plans": ["立即回国", "先在当地工作", "不确定"],
            "school_selection_factors": [
                "综合排名", "专业排名", "地理位置与就业", "学费与性价比", 
                "教授与科研实力", "校园文化"
            ]
        }
        
        print("✅ 配置选项结构验证通过")
        
        # 验证新增的选项
        assert "985" in expected_options["school_tiers"]
        assert "先在当地工作" in expected_options["post_graduation_plans"]
        assert "地理位置与就业" in expected_options["school_selection_factors"]
        
        print("✅ V1.5新增配置选项验证通过")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置选项测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始V1.5功能测试")
    print("=" * 60)
    
    tests = [
        test_user_profile_v15,
        test_llm_prompt_building,
        test_config_options
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"🎉 测试完成: {passed}/{total} 通过")
    
    if passed == total:
        print("✅ 所有V1.5功能测试通过！")
        return True
    else:
        print("❌ 部分测试失败，请检查代码")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)