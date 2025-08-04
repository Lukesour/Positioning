"""
ETL数据预处理模块
从 compassedu_cases 数据库读取原始数据，清洗后存入 processed_cases 数据库
"""
import psycopg2
import re
import logging
from typing import Dict, Optional, Tuple
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import SOURCE_DB_CONFIG, TARGET_DB_CONFIG

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ETLProcessor:
    """ETL数据处理器"""
    
    def __init__(self):
        self.source_conn = None
        self.target_conn = None
        
        # 院校层次映射
        self.school_tier_keywords = {
            '985院校': ['985', 'C9', '清华', '北大', '复旦', '上交', '浙大', '中科大', '南大', '哈工大'],
            '211院校': ['211', '中南', '华中', '西北', '东北', '华东', '西南', '中央'],
            '双非院校': ['学院', '大学'],
            '海外院校': ['University', 'College', 'Institute']
        }
        
        # 学位层次映射
        self.degree_mapping = {
            '硕士': ['硕士', 'Master', 'MSc', 'MA', 'MS', 'MEng', 'MBA', 'MFA'],
            '博士': ['博士', 'PhD', 'DPhil', 'Doctor']
        }
        
    def connect_databases(self):
        """连接源数据库和目标数据库"""
        try:
            # 连接源数据库（只读）
            self.source_conn = psycopg2.connect(**SOURCE_DB_CONFIG)
            logger.info("成功连接源数据库")
            
            # 连接目标数据库（读写）
            self.target_conn = psycopg2.connect(**TARGET_DB_CONFIG)
            logger.info("成功连接目标数据库")
            
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            raise
    
    def close_connections(self):
        """关闭数据库连接"""
        if self.source_conn:
            self.source_conn.close()
        if self.target_conn:
            self.target_conn.close()
    
    def parse_gpa(self, gpa_str: str) -> Tuple[Optional[float], Optional[float]]:
        """
        解析GPA字符串，返回4.0制和100分制的GPA
        """
        if not gpa_str:
            return None, None
            
        # 清理字符串
        gpa_str = str(gpa_str).strip()
        
        # 匹配模式：数字/数字 或 纯数字
        patterns = [
            r'(\d+\.?\d*)/(\d+\.?\d*)',  # 3.5/4.0 或 85/100
            r'(\d+\.?\d*)',              # 3.5 或 85
        ]
        
        for pattern in patterns:
            match = re.search(pattern, gpa_str)
            if match:
                if len(match.groups()) == 2:  # 有分母
                    numerator = float(match.group(1))
                    denominator = float(match.group(2))
                    
                    if denominator == 4.0 or denominator == 4:
                        # 4.0制
                        gpa_4 = numerator
                        gpa_100 = numerator * 25
                    elif denominator == 100:
                        # 100分制
                        gpa_100 = numerator
                        gpa_4 = numerator / 25
                    else:
                        # 其他制式，尝试推断
                        if numerator <= 4:
                            gpa_4 = numerator
                            gpa_100 = numerator * 25
                        else:
                            gpa_100 = numerator
                            gpa_4 = numerator / 25
                else:  # 只有数字
                    value = float(match.group(1))
                    if value <= 4:
                        # 推断为4.0制
                        gpa_4 = value
                        gpa_100 = value * 25
                    else:
                        # 推断为100分制
                        gpa_100 = value
                        gpa_4 = value / 25
                
                # 确保数值在合理范围内
                gpa_4 = max(0, min(4.0, gpa_4)) if gpa_4 else None
                gpa_100 = max(0, min(100, gpa_100)) if gpa_100 else None
                
                return gpa_4, gpa_100
        
        return None, None
    
    def parse_language_score(self, language_str: str) -> Tuple[Optional[str], Optional[float]]:
        """
        解析语言成绩字符串
        """
        if not language_str:
            return None, None
            
        language_str = str(language_str).strip()
        
        # 语言类型映射
        language_types = {
            '雅思': ['雅思', 'IELTS', 'ielts'],
            '托福': ['托福', 'TOEFL', 'toefl'],
            '多邻国': ['多邻国', 'Duolingo', 'duolingo']
        }
        
        language_type = None
        for lang, keywords in language_types.items():
            if any(keyword in language_str for keyword in keywords):
                language_type = lang
                break
        
        # 提取分数
        score_match = re.search(r'(\d+\.?\d*)', language_str)
        language_score = float(score_match.group(1)) if score_match else None
        
        return language_type, language_score
    
    def determine_school_tier(self, school_name: str) -> str:
        """
        判断院校层次
        """
        if not school_name:
            return '其他'
            
        school_name = str(school_name).strip()
        
        for tier, keywords in self.school_tier_keywords.items():
            if any(keyword in school_name for keyword in keywords):
                return tier
        
        return '双非院校'  # 默认为双非院校
    
    def determine_degree_level(self, title: str, program: str = '') -> str:
        """
        判断学位层次
        """
        text = f"{title} {program}".lower()
        
        for degree, keywords in self.degree_mapping.items():
            if any(keyword.lower() in text for keyword in keywords):
                return degree
        
        return '硕士'  # 默认为硕士
    
    def extract_university_program(self, title: str) -> Tuple[str, str]:
        """
        从标题中提取大学名称和项目名称
        """
        if not title:
            return '', ''
        
        # 常见的分隔符模式
        patterns = [
            r'(.+?)大学(.+?)(?:硕士|博士|Master|PhD)',
            r'(.+?)(?:University|College)(.+?)(?:Master|PhD)',
            r'(.+?)大学(.+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, title)
            if match:
                university = match.group(1).strip() + ('大学' if '大学' in match.group(1) else '')
                program = match.group(2).strip()
                return university, program
        
        # 如果没有匹配到，尝试简单分割
        parts = title.split(' ')
        if len(parts) >= 2:
            return parts[0], ' '.join(parts[1:])
        
        return title, ''
    
    def process_case(self, raw_case: dict) -> dict:
        """
        处理单个案例数据
        """
        processed = {
            'original_id': raw_case.get('id'),
            'original_title': raw_case.get('title', ''),
            'original_url': raw_case.get('url', ''),
        }
        
        # 使用数据库中已有的大学和项目信息，如果没有则从标题提取
        university = raw_case.get('university', '')
        program = raw_case.get('program', '')
        
        if not university or not program:
            title = raw_case.get('title', '')
            extracted_university, extracted_program = self.extract_university_program(title)
            university = university or extracted_university
            program = program or extracted_program
            
        processed['university'] = university
        processed['program'] = program
        
        # 判断学位层次
        processed['degree_level'] = self.determine_degree_level(title, program)
        
        # 解析学生背景信息
        background = raw_case.get('student_background', '')
        
        # 这里需要根据实际的数据格式来解析
        # 假设背景信息包含院校、专业等信息
        processed['undergrad_school'] = self.extract_undergrad_school(background)
        processed['undergrad_school_tier'] = self.determine_school_tier(processed['undergrad_school'])
        processed['undergrad_major'] = self.extract_major(background)
        
        # 解析GPA
        gpa_str = raw_case.get('gpa', '')
        processed['gpa_original'] = gpa_str
        gpa_4, gpa_100 = self.parse_gpa(gpa_str)
        processed['gpa_scale_4'] = gpa_4
        processed['gpa_scale_100'] = gpa_100
        
        # 解析语言成绩
        language_str = raw_case.get('language_score', '')
        language_type, language_score = self.parse_language_score(language_str)
        processed['language_type'] = language_type
        processed['language_score'] = language_score
        
        # 解析GRE成绩（从背景信息中提取）
        gre_match = re.search(r'GRE[:\s]*(\d+)', background)
        processed['gre_score'] = int(gre_match.group(1)) if gre_match else None
        
        # 其他字段
        processed['work_experience'] = self.extract_work_experience(background)
        
        # 毕业年份优先使用数据库字段，否则从背景信息提取
        graduation_year = raw_case.get('graduation_year', '')
        if graduation_year and graduation_year.isdigit():
            processed['graduation_year'] = int(graduation_year)
        else:
            processed['graduation_year'] = self.extract_graduation_year(background)
        
        return processed
    
    def extract_undergrad_school(self, background: str) -> str:
        """从背景信息中提取本科院校"""
        if not background:
            return ''
        
        # 查找大学名称的模式，优化匹配规则
        patterns = [
            r'([^，,。.\s]*大学)',
            r'([^，,。.\s]*学院)',
            r'([^，,。.\s]*University)',
            r'([^，,。.\s]*College)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, background)
            if matches:
                # 返回第一个匹配的学校名称
                school = matches[0].strip()
                if len(school) > 2:  # 过滤太短的匹配
                    return school
        
        return ''
    
    def extract_major(self, background: str) -> str:
        """从背景信息中提取专业"""
        if not background:
            return ''
        
        # 根据实际数据格式，专业通常在学校名称之后
        # 例如："北京邮电大学 物联网工程"
        parts = background.split()
        
        # 查找专业模式
        major_patterns = [
            r'([^，,。\s]*工程)',
            r'([^，,。\s]*科学)',
            r'([^，,。\s]*技术)',
            r'([^，,。\s]*管理)',
            r'([^，,。\s]*经济)',
            r'([^，,。\s]*文学)',
            r'([^，,。\s]*理学)',
            r'([^，,。\s]*学)',
        ]
        
        for pattern in major_patterns:
            matches = re.findall(pattern, background)
            if matches:
                major = matches[0].strip()
                if len(major) > 2 and '大学' not in major and '学院' not in major:
                    return major
        
        # 如果没有匹配到，尝试从分词中提取
        if len(parts) >= 2:
            for part in parts[1:]:  # 跳过第一个（通常是学校）
                if any(keyword in part for keyword in ['工程', '科学', '技术', '管理', '经济']):
                    return part.strip()
        
        return ''
    
    def extract_work_experience(self, background: str) -> str:
        """提取工作经验"""
        if '应届' in background:
            return '应届生'
        elif '工作' in background:
            return '有工作经验'
        else:
            return '应届生'
    
    def extract_graduation_year(self, background: str) -> Optional[int]:
        """提取毕业年份"""
        year_match = re.search(r'20(\d{2})', background)
        if year_match:
            return int(f"20{year_match.group(1)}")
        return None
    
    def run_etl(self):
        """运行ETL流程"""
        try:
            self.connect_databases()
            
            # 读取源数据
            source_cursor = self.source_conn.cursor()
            source_cursor.execute("""
                SELECT id, title, url, university, program, student_background, gpa, language_score, graduation_year
                FROM compassedu_cases
                ORDER BY id
            """)
            
            raw_cases = source_cursor.fetchall()
            logger.info(f"从源数据库读取到 {len(raw_cases)} 条记录")
            
            # 处理数据并插入目标数据库
            target_cursor = self.target_conn.cursor()
            
            # 清空目标表
            target_cursor.execute("TRUNCATE TABLE cases RESTART IDENTITY")
            
            processed_count = 0
            for raw_case in raw_cases:
                try:
                    # 将元组转换为字典
                    case_dict = {
                        'id': raw_case[0],
                        'title': raw_case[1],
                        'url': raw_case[2],
                        'university': raw_case[3],
                        'program': raw_case[4],
                        'student_background': raw_case[5],
                        'gpa': raw_case[6],
                        'language_score': raw_case[7],
                        'graduation_year': raw_case[8],
                    }
                    
                    processed_case = self.process_case(case_dict)
                    
                    # 插入到目标数据库
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
                    
                    target_cursor.execute(insert_sql, processed_case)
                    processed_count += 1
                    
                    if processed_count % 100 == 0:
                        logger.info(f"已处理 {processed_count} 条记录")
                        
                except Exception as e:
                    logger.error(f"处理案例 {raw_case[0]} 时出错: {e}")
                    continue
            
            # 提交事务
            self.target_conn.commit()
            logger.info(f"ETL处理完成，共处理 {processed_count} 条记录")
            
        except Exception as e:
            logger.error(f"ETL处理失败: {e}")
            if self.target_conn:
                self.target_conn.rollback()
            raise
        finally:
            self.close_connections()

if __name__ == "__main__":
    processor = ETLProcessor()
    processor.run_etl()