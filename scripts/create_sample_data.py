#!/usr/bin/env python3
"""
创建示例数据脚本
用于演示系统功能
"""
import psycopg2
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import TARGET_DB_CONFIG

def create_sample_data():
    """创建示例数据"""
    
    # 示例案例数据
    sample_cases = [
        {
            'original_id': 1,
            'university': '香港科技大学',
            'program': '计算机科学理学硕士',
            'degree_level': '硕士',
            'undergrad_school': '中山大学',
            'undergrad_school_tier': '985院校',
            'undergrad_major': '软件工程',
            'gpa_original': '85/100',
            'gpa_scale_4': 3.4,
            'gpa_scale_100': 85.0,
            'language_type': '雅思',
            'language_score': 6.5,
            'gre_score': 320,
            'work_experience': '应届生',
            'graduation_year': 2024,
            'original_url': 'https://example.com/case1',
            'original_title': '香港科技大学计算机科学理学硕士录取案例'
        },
        {
            'original_id': 2,
            'university': '新加坡国立大学',
            'program': '计算机科学硕士',
            'degree_level': '硕士',
            'undergrad_school': '华南理工大学',
            'undergrad_school_tier': '985院校',
            'undergrad_major': '计算机科学与技术',
            'gpa_original': '3.6/4.0',
            'gpa_scale_4': 3.6,
            'gpa_scale_100': 90.0,
            'language_type': '托福',
            'language_score': 105.0,
            'gre_score': 325,
            'work_experience': '应届生',
            'graduation_year': 2024,
            'original_url': 'https://example.com/case2',
            'original_title': '新加坡国立大学计算机科学硕士录取案例'
        },
        {
            'original_id': 3,
            'university': '香港中文大学',
            'program': '信息工程理学硕士',
            'degree_level': '硕士',
            'undergrad_school': '北京邮电大学',
            'undergrad_school_tier': '211院校',
            'undergrad_major': '物联网工程',
            'gpa_original': '76/100',
            'gpa_scale_4': 3.04,
            'gpa_scale_100': 76.0,
            'language_type': '雅思',
            'language_score': 6.0,
            'gre_score': None,
            'work_experience': '应届生',
            'graduation_year': 2025,
            'original_url': 'https://example.com/case3',
            'original_title': '香港中文大学信息工程理学硕士录取案例'
        },
        {
            'original_id': 4,
            'university': '南洋理工大学',
            'program': '人工智能硕士',
            'degree_level': '硕士',
            'undergrad_school': '山东大学',
            'undergrad_school_tier': '985院校',
            'undergrad_major': '计算机科学与技术',
            'gpa_original': '79/100',
            'gpa_scale_4': 3.16,
            'gpa_scale_100': 79.0,
            'language_type': '雅思',
            'language_score': 6.0,
            'gre_score': None,
            'work_experience': '四年以上经验',
            'graduation_year': 2020,
            'original_url': 'https://example.com/case4',
            'original_title': '南洋理工大学人工智能硕士录取案例'
        },
        {
            'original_id': 5,
            'university': '香港城市大学',
            'program': '电子资讯工程学理学硕士',
            'degree_level': '硕士',
            'undergrad_school': '深圳大学',
            'undergrad_school_tier': '双非院校',
            'undergrad_major': '自动化',
            'gpa_original': '75.3/100',
            'gpa_scale_4': 3.01,
            'gpa_scale_100': 75.3,
            'language_type': '雅思',
            'language_score': 6.5,
            'gre_score': None,
            'work_experience': '应届生',
            'graduation_year': 2025,
            'original_url': 'https://example.com/case5',
            'original_title': '香港城市大学电子资讯工程学理学硕士录取案例'
        },
        {
            'original_id': 6,
            'university': '帝国理工学院',
            'program': '计算机科学硕士',
            'degree_level': '硕士',
            'undergrad_school': '清华大学',
            'undergrad_school_tier': '985院校',
            'undergrad_major': '计算机科学与技术',
            'gpa_original': '3.8/4.0',
            'gpa_scale_4': 3.8,
            'gpa_scale_100': 95.0,
            'language_type': '雅思',
            'language_score': 7.5,
            'gre_score': 330,
            'work_experience': '应届生',
            'graduation_year': 2024,
            'original_url': 'https://example.com/case6',
            'original_title': '帝国理工学院计算机科学硕士录取案例'
        },
        {
            'original_id': 7,
            'university': '香港大学',
            'program': '计算机科学理学硕士',
            'degree_level': '硕士',
            'undergrad_school': '复旦大学',
            'undergrad_school_tier': '985院校',
            'undergrad_major': '软件工程',
            'gpa_original': '3.7/4.0',
            'gpa_scale_4': 3.7,
            'gpa_scale_100': 92.5,
            'language_type': '雅思',
            'language_score': 7.0,
            'gre_score': 325,
            'work_experience': '应届生',
            'graduation_year': 2024,
            'original_url': 'https://example.com/case7',
            'original_title': '香港大学计算机科学理学硕士录取案例'
        },
        {
            'original_id': 8,
            'university': '新加坡南洋理工大学',
            'program': '数据科学硕士',
            'degree_level': '硕士',
            'undergrad_school': '华中科技大学',
            'undergrad_school_tier': '985院校',
            'undergrad_major': '数据科学与大数据技术',
            'gpa_original': '88/100',
            'gpa_scale_4': 3.52,
            'gpa_scale_100': 88.0,
            'language_type': '托福',
            'language_score': 100.0,
            'gre_score': 315,
            'work_experience': '应届生',
            'graduation_year': 2024,
            'original_url': 'https://example.com/case8',
            'original_title': '新加坡南洋理工大学数据科学硕士录取案例'
        },
        {
            'original_id': 9,
            'university': '伦敦大学学院',
            'program': '金融科技硕士',
            'degree_level': '硕士',
            'undergrad_school': '上海财经大学',
            'undergrad_school_tier': '211院校',
            'undergrad_major': '金融学',
            'gpa_original': '3.5/4.0',
            'gpa_scale_4': 3.5,
            'gpa_scale_100': 87.5,
            'language_type': '雅思',
            'language_score': 7.0,
            'gre_score': 320,
            'work_experience': '一年经验',
            'graduation_year': 2023,
            'original_url': 'https://example.com/case9',
            'original_title': '伦敦大学学院金融科技硕士录取案例'
        },
        {
            'original_id': 10,
            'university': '香港理工大学',
            'program': '软件技术理学硕士',
            'degree_level': '硕士',
            'undergrad_school': '大连理工大学',
            'undergrad_school_tier': '985院校',
            'undergrad_major': '软件工程',
            'gpa_original': '82/100',
            'gpa_scale_4': 3.28,
            'gpa_scale_100': 82.0,
            'language_type': '雅思',
            'language_score': 6.5,
            'gre_score': None,
            'work_experience': '应届生',
            'graduation_year': 2024,
            'original_url': 'https://example.com/case10',
            'original_title': '香港理工大学软件技术理学硕士录取案例'
        }
    ]
    
    try:
        # 连接数据库
        conn = psycopg2.connect(**TARGET_DB_CONFIG)
        cursor = conn.cursor()
        
        # 清空现有数据
        cursor.execute("TRUNCATE TABLE cases RESTART IDENTITY")
        
        # 插入示例数据
        insert_sql = """
            INSERT INTO cases (
                original_id, university, program, degree_level,
                undergrad_school, undergrad_school_tier, undergrad_major,
                gpa_original, gpa_scale_4, gpa_scale_100,
                language_type, language_score, gre_score,
                work_experience, graduation_year,
                original_url, original_title
            ) VALUES (
                %(original_id)s, %(university)s, %(program)s, %(degree_level)s,
                %(undergrad_school)s, %(undergrad_school_tier)s, %(undergrad_major)s,
                %(gpa_original)s, %(gpa_scale_4)s, %(gpa_scale_100)s,
                %(language_type)s, %(language_score)s, %(gre_score)s,
                %(work_experience)s, %(graduation_year)s,
                %(original_url)s, %(original_title)s
            )
        """
        
        for case in sample_cases:
            cursor.execute(insert_sql, case)
        
        # 提交事务
        conn.commit()
        
        print(f"✅ 成功创建 {len(sample_cases)} 条示例数据")
        
        # 验证数据
        cursor.execute("SELECT COUNT(*) FROM cases")
        count = cursor.fetchone()[0]
        print(f"✅ 数据库中共有 {count} 条记录")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ 创建示例数据失败: {e}")
        if conn:
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    print("=" * 50)
    print("创建示例数据")
    print("=" * 50)
    create_sample_data()
    print("=" * 50)