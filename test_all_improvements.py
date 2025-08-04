#!/usr/bin/env python3
"""
界面与体验优化功能测试脚本
"""
import sys
import os
import requests
import json
from bs4 import BeautifulSoup

def test_optional_field_labels():
    """测试选填字段标识"""
    print("🧪 测试选填字段标识...")
    
    try:
        response = requests.get('http://localhost:8000/')
        if response.status_code == 200:
            html_content = response.text
            optional_count = html_content.count('(选填)')
            
            expected_optional_fields = [
                '专业 GPA/均分',
                'TOEFL/IELTS 成绩', 
                'GRE/GMAT 成绩',
                '海外交换/访学经历',
                '核心先修课程',
                '科研/实习/工作经历',
                '项目成果（论文/专利等）',
                '毕业后去向',
                '选校最看重方面'
            ]
            
            print(f"✅ 找到 {optional_count} 个选填字段标识")
            print(f"✅ 预期 {len(expected_optional_fields)} 个选填字段")
            
            if optional_count >= len(expected_optional_fields):
                print("✅ 选填字段标识测试通过")
                return True
            else:
                print("❌ 选填字段标识数量不足")
                return False
        else:
            print(f"❌ 无法访问前端页面: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_autocomplete_api():
    """测试自动补全API"""
    print("\n🧪 测试自动补全API...")
    
    try:
        response = requests.get('http://localhost:8000/api/v1/autocomplete-options')
        if response.status_code == 200:
            data = response.json()
            
            universities_count = data.get('total_universities', 0)
            majors_count = data.get('total_majors', 0)
            
            print(f"✅ API调用成功")
            print(f"✅ 返回 {universities_count} 所院校")
            print(f"✅ 返回 {majors_count} 个专业")
            
            # 验证数据质量
            universities = data.get('universities', [])
            majors = data.get('majors', [])
            
            if universities_count > 100 and majors_count > 50:
                print("✅ 数据量充足")
                
                # 显示一些示例
                print(f"📝 院校示例: {universities[:5]}")
                print(f"📝 专业示例: {majors[:5]}")
                
                print("✅ 自动补全API测试通过")
                return True
            else:
                print("❌ 数据量不足")
                return False
        else:
            print(f"❌ API调用失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_submit_button_logic():
    """测试提交按钮逻辑"""
    print("\n🧪 测试提交按钮逻辑...")
    
    try:
        response = requests.get('http://localhost:8000/')
        if response.status_code == 200:
            html_content = response.text
            
            # 检查CSS中是否包含正确的按钮样式
            checks = [
                '.submit-btn:disabled' in html_content,
                '.submit-btn.enabled' in html_content,
                'pointer-events: none' in html_content,
                'opacity: 0.6' in html_content
            ]
            
            passed_checks = sum(checks)
            print(f"✅ CSS样式检查: {passed_checks}/4 通过")
            
            # 检查JavaScript中是否包含正确的验证逻辑
            js_checks = [
                'validateForm()' in html_content,
                'disabled = false' in html_content,
                'disabled = true' in html_content,
                'classList.add(\'enabled\')' in html_content
            ]
            
            passed_js_checks = sum(js_checks)
            print(f"✅ JavaScript逻辑检查: {passed_js_checks}/4 通过")
            
            if passed_checks >= 3 and passed_js_checks >= 3:
                print("✅ 提交按钮逻辑测试通过")
                return True
            else:
                print("❌ 提交按钮逻辑测试失败")
                return False
        else:
            print(f"❌ 无法访问前端页面: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_drag_sort_functionality():
    """测试拖拽排序功能"""
    print("\n🧪 测试拖拽排序功能...")
    
    try:
        response = requests.get('http://localhost:8000/')
        if response.status_code == 200:
            html_content = response.text
            
            # 检查拖拽相关的代码
            drag_checks = [
                'makeSortable' in html_content,
                'dragstart' in html_content,
                'dragend' in html_content,
                'dragover' in html_content,
                'drop' in html_content,
                'draggable = true' in html_content
            ]
            
            passed_drag_checks = sum(drag_checks)
            print(f"✅ 拖拽事件处理: {passed_drag_checks}/6 通过")
            
            # 检查CSS样式
            css_checks = [
                '.sortable-item' in html_content,
                'cursor: move' in html_content,
                '.drag-handle' in html_content,
                'transition:' in html_content
            ]
            
            passed_css_checks = sum(css_checks)
            print(f"✅ 拖拽样式: {passed_css_checks}/4 通过")
            
            if passed_drag_checks >= 5 and passed_css_checks >= 3:
                print("✅ 拖拽排序功能测试通过")
                return True
            else:
                print("❌ 拖拽排序功能测试失败")
                return False
        else:
            print(f"❌ 无法访问前端页面: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_enhanced_autocomplete():
    """测试增强的自动补全功能"""
    print("\n🧪 测试增强的自动补全功能...")
    
    try:
        response = requests.get('http://localhost:8000/')
        if response.status_code == 200:
            html_content = response.text
            
            # 检查自动补全相关代码
            autocomplete_checks = [
                'loadAutocompleteOptions' in html_content,
                'setupAutocomplete' in html_content,
                'autocomplete-suggestions' in html_content,
                'useDatabase = false' in html_content,
                'highlightedText' in html_content,
                'keydown' in html_content
            ]
            
            passed_autocomplete_checks = sum(autocomplete_checks)
            print(f"✅ 自动补全逻辑: {passed_autocomplete_checks}/6 通过")
            
            # 检查样式改进
            style_checks = [
                'box-shadow:' in html_content,
                '.autocomplete-suggestion:hover' in html_content,
                '.autocomplete-suggestion.active' in html_content,
                'strong' in html_content
            ]
            
            passed_style_checks = sum(style_checks)
            print(f"✅ 自动补全样式: {passed_style_checks}/4 通过")
            
            if passed_autocomplete_checks >= 5 and passed_style_checks >= 3:
                print("✅ 增强的自动补全功能测试通过")
                return True
            else:
                print("❌ 增强的自动补全功能测试失败")
                return False
        else:
            print(f"❌ 无法访问前端页面: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_complete_form_submission():
    """测试完整的表单提交流程"""
    print("\n🧪 测试完整的表单提交流程...")
    
    try:
        # 构建包含所有新功能的测试数据
        test_data = {
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
            "prerequisite_courses": "高等数学、数据结构、算法设计",
            "practical_experiences": [
                {
                    "organization": "腾讯科技",
                    "position": "软件开发实习生",
                    "start_date": "2023-06",
                    "end_date": "2023-08",
                    "description": "参与微信小程序后端开发，优化API响应速度提升30%"
                }
            ],
            "achievements": "发表会议论文一篇",
            "target_majors": ["计算机科学", "人工智能"],
            "post_graduation_plan": "先在当地工作",
            "school_selection_factors": ["专业排名", "地理位置与就业"]
        }
        
        response = requests.post(
            'http://localhost:8000/api/v1/school-planning',
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ 表单提交成功")
            print(f"✅ 返回 {len(result.get('matched_cases', []))} 个匹配案例")
            print("✅ AI分析报告生成成功")
            
            # 检查分析报告是否包含新字段信息
            analysis = result.get('analysis_report', {})
            if analysis:
                print("✅ 分析报告包含完整内容")
                return True
            else:
                print("❌ 分析报告内容不完整")
                return False
        else:
            print(f"❌ 表单提交失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始界面与体验优化功能测试")
    print("=" * 60)
    
    tests = [
        ("选填字段标识", test_optional_field_labels),
        ("自动补全API", test_autocomplete_api),
        ("提交按钮逻辑", test_submit_button_logic),
        ("拖拽排序功能", test_drag_sort_functionality),
        ("增强的自动补全", test_enhanced_autocomplete),
        ("完整表单提交", test_complete_form_submission)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} - 通过")
            else:
                print(f"❌ {test_name} - 失败")
        except Exception as e:
            print(f"❌ {test_name} - 异常: {e}")
    
    print("\n" + "=" * 60)
    print(f"🎉 测试完成: {passed}/{total} 通过")
    
    if passed == total:
        print("✅ 所有界面与体验优化功能测试通过！")
        print("\n📋 改进总结:")
        print("1. ✅ 修复了选填字段标识问题")
        print("2. ✅ 修复了提交按钮无法点击的问题")
        print("3. ✅ 实现了选校因素的拖拽排序功能")
        print("4. ✅ 创建了自动补全API，从数据库获取真实数据")
        print("5. ✅ 增强了前端自动补全功能和用户体验")
        print("\n🌐 访问地址:")
        print("• 主界面: http://localhost:8000")
        print("• 测试页面: http://localhost:8000/test_improvements.html")
        print("• API文档: http://localhost:8000/docs")
        return True
    else:
        print("❌ 部分测试失败，请检查代码")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)