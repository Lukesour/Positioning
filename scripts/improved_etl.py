#!/usr/bin/env python3
"""
改进的ETL数据预处理模块
更好地处理真实数据中的异常情况
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

class ImprovedETLProcessor:
    """改进的ETL数据处理器"""
    
    def __init__(self):
        self.source_conn = None
        self.target_conn = None
        self.processed_count = 0
        self.error_count = 0
        
    def connect_databases(self):
        """连接源数据库和目标数据库"""
        try:
            # 连接源数据库（只读）
            self.source_conn = psycopg2.connect(**SOURCE_DB_CONFIG)
            logger.info("成功连接源数据库")
            
            # 连接目标数据库（读写）
            self.target_conn = psycopg2.connect(**TARGET_DB_CONFIG)
            self.target_conn.autocommit = False  # 手动控制事务
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
    
    def safe_parse_gpa(self, gpa_str: str) -> Tuple[Optional[float], Optional[float]]:
        """安全解析GPA字符串"""
        if not gpa_str or gpa_str.strip() == '':
            return None, None
            
        try:
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
                            gpa_4 = min(4.0, max(0, numerator))
                            gpa_100 = min(100.0, max(0, numerator * 25))
                        elif denominator == 100:
                            gpa_100 = min(100.0, max(0, numerator))
                            gpa_4 = min(4.0, max(0, numerator / 25))
                        else:
                            # 其他制式，尝试推断
                            if numerator <= 4:
                                gpa_4 = min(4.0, max(0, numerator))
                                gpa_100 = min(100.0, max(0, numerator * 25))
                            else:
                                gpa_100 = min(100.0, max(0, numerator))
                                gpa_4 = min(4.0, max(0, numerator / 25))
                    else:  # 只有数字
                        value = float(match.group(1))
                        if value <= 4:
                            gpa_4 = min(4.0, max(0, value))
                            gpa_100 = min(100.0, max(0, value * 25))
                        else:
                            gpa_100 = min(100.0, max(0, value))
                            gpa_4 = min(4.0, max(0, value / 25))
                    
                    return gpa_4, gpa_100
            
        except (ValueError, TypeError) as e:
            logger.warning(f"GPA解析失败: {gpa_str}, 错误: {e}")
        
        return None, None
    
    def safe_parse_language_score(self, language_str: str) -> Tuple[Optional[str], Optional[float]]:
        """安全解析语言成绩字符串"""
        if not language_str or language_str.strip() == '':
            return None, None
            
        try:
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
            if score_match:
                score = float(score_match.group(1))
                # 合理性检查
                if language_type == '雅思' and score > 9:
                    score = None
                elif language_type == '托福' and score > 120:
                    score = None
                elif language_type == '多邻国' and score > 160:
                    score = None
                
                return language_type, score
            
        except (ValueError, TypeError) as e:
            logger.warning(f"语言成绩解析失败: {language_str}, 错误: {e}")
        
        return None, None
    
    def determine_school_tier(self, school_name: str) -> str:
        """判断院校层次"""
        if not school_name:
            return '其他'
            
        school_name = str(school_name).strip()
        
        # 985院校关键词
        if any(keyword in school_name for keyword in ['清华', '北大', '复旦', '上交', '浙大', '中科大', '南大', '哈工大', '西交', '中山', '华南理工', '山东大学', '华中科技', '大连理工']):
            return '985院校'
        
        # 211院校关键词
        if any(keyword in school_name for keyword in ['211', '北京邮电', '上海财经', '华东师范', '中南', '华中', '西北', '东北', '西南']):
            return '211院校'
        
        # 海外院校
        if any(keyword in school_name for keyword in ['University', 'College', 'Institute']):
            return '海外院校'
        
        return '双非院校'
    
    def extract_basic_info(self, title: str, background: str) -> Dict:
        """提取基本信息"""
        info = {
            'university': '',
            'program': '',
            'undergrad_school': '',
            'undergrad_major': '',
            'work_experience': '应届生',
            'graduation_year': None
        }
        
        # 从标题提取大学和项目
        if title:
            # 常见模式：大学名+项目名
            university_patterns = [
                r'([^，,。]*大学)',
                r'([^，,。]*理工学院)',
                r'([^，,。]*University)',
                r'([^，,。]*College)',
            ]
            
            for pattern in university_patterns:
                match = re.search(pattern, title)
                if match:
                    info['university'] = match.group(1).strip()
                    break
            
            # 提取项目名称
            if '硕士' in title:
                program_match = re.search(r'([^，,。]*硕士)', title)
                if program_match:
                    info['program'] = program_match.group(1).strip()
        
        # 从背景信息提取本科院校和专业
        if background:
            # 提取本科院校
            school_patterns = [
                r'([^，,。\s]*大学)',
                r'([^，,。\s]*学院)',
            ]
            
            for pattern in school_patterns:
                matches = re.findall(pattern, background)
                if matches:
                    info['undergrad_school'] = matches[0].strip()
                    break
            
            # 提取专业
            major_patterns = [
                r'([^，,。\s]*工程)',
                r'([^，,。\s]*科学)',
                r'([^，,。\s]*技术)',
                r'([^，,。\s]*管理)',
                r'([^，,。\s]*经济)',
            ]
            
            for pattern in major_patterns:
                matches = re.findall(pattern, background)
                if matches:
                    major = matches[0].strip()
                    if len(major) > 2 and '大学' not in major:
                        info['undergrad_major'] = major
                        break
            
            # 提取工作经验
            if '应届' in background:
                info['work_experience'] = '应届生'
            elif '经验' in background:
                info['work_experience'] = '有工作经验'
            
            # 提取毕业年份
            year_match = re.search(r'20(\d{2})', background)
            if year_match:
                year = int(f"20{year_match.group(1)}")
                if 2020 <= year <= 2030:  # 合理性检查
                    info['graduation_year'] = year
        
        return info
    
    def process_single_case(self, raw_case: tuple) -> Optional[Dict]:
        """处理单个案例，返回处理后的数据或None（如果处理失败）"""
        try:
            # 解包数据
            case_id, title, url, university, program, background, gpa, language_score, graduation_year = raw_case
            
            # 基本信息
            processed = {
                'original_id': case_id,
                'original_title': title or '',
                'original_url': url or '',
            }
            
            # 提取基本信息
            basic_info = self.extract_basic_info(title or '', background or '')
            
            # 使用数据库字段或提取的信息
            processed['university'] = university or basic_info['university']
            processed['program'] = program or basic_info['program']
            processed['undergrad_school'] = basic_info['undergrad_school']
            processed['undergrad_school_tier'] = self.determine_school_tier(processed['undergrad_school'])
            processed['undergrad_major'] = basic_info['undergrad_major']
            
            # 判断学位层次
            degree_text = f"{title} {program}".lower()
            if any(keyword in degree_text for keyword in ['博士', 'phd', 'doctor']):
                processed['degree_level'] = '博士'
            else:
                processed['degree_level'] = '硕士'
            
            # 解析GPA
            processed['gpa_original'] = gpa or ''
            gpa_4, gpa_100 = self.safe_parse_gpa(gpa)
            processed['gpa_scale_4'] = gpa_4
            processed['gpa_scale_100'] = gpa_100
            
            # 解析语言成绩
            language_type, language_score_val = self.safe_parse_language_score(language_score or '')
            processed['language_type'] = language_type
            processed['language_score'] = language_score_val
            
            # 解析GRE成绩
            gre_match = re.search(r'GRE[:\s]*(\d+)', background or '')
            processed['gre_score'] = int(gre_match.group(1)) if gre_match else None
            
            # 其他字段
            processed['work_experience'] = basic_info['work_experience']
            
            # 毕业年份
            if graduation_year and str(graduation_year).isdigit():
                processed['graduation_year'] = int(graduation_year)
            else:
                processed['graduation_year'] = basic_info['graduation_year']
            
            # 验证必要字段
            if not processed['university'] or not processed['degree_level']:
                logger.warning(f"案例 {case_id} 缺少必要信息，跳过")
                return None
            
            return processed
            
        except Exception as e:
            logger.error(f"处理案例时出错: {e}")
            return None
    
    def run_etl(self, batch_size: int = 100):
        """运行ETL流程，使用批处理提高效率"""
        try:
            self.connect_databases()
            
            # 读取源数据
            source_cursor = self.source_conn.cursor()
            source_cursor.execute("""
                SELECT id, title, url, university, program, student_background, gpa, language_score, graduation_year
                FROM compassedu_cases
                ORDER BY id
            """)
            
            # 清空目标表
            target_cursor = self.target_conn.cursor()
            target_cursor.execute("TRUNCATE TABLE cases RESTART IDENTITY")
            
            logger.info("开始处理数据...")
            
            # 批量处理
            while True:
                raw_cases = source_cursor.fetchmany(batch_size)
                if not raw_cases:
                    break
                
                batch_data = []
                for raw_case in raw_cases:
                    processed_case = self.process_single_case(raw_case)
                    if processed_case:
                        batch_data.append(processed_case)
                    else:
                        self.error_count += 1
                
                # 批量插入
                if batch_data:
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
                    
                    try:
                        target_cursor.executemany(insert_sql, batch_data)
                        self.target_conn.commit()
                        self.processed_count += len(batch_data)
                        logger.info(f"已处理 {self.processed_count} 条记录")
                    except Exception as e:
                        logger.error(f"批量插入失败: {e}")
                        self.target_conn.rollback()
                        # 尝试逐条插入
                        for case_data in batch_data:
                            try:
                                target_cursor.execute(insert_sql, case_data)
                                self.target_conn.commit()
                                self.processed_count += 1
                            except Exception as e2:
                                logger.error(f"插入案例 {case_data.get('original_id')} 失败: {e2}")
                                self.target_conn.rollback()
                                self.error_count += 1
            
            logger.info(f"ETL处理完成！")
            logger.info(f"成功处理: {self.processed_count} 条记录")
            logger.info(f"失败记录: {self.error_count} 条")
            
        except Exception as e:
            logger.error(f"ETL处理失败: {e}")
            if self.target_conn:
                self.target_conn.rollback()
            raise
        finally:
            self.close_connections()

if __name__ == "__main__":
    processor = ImprovedETLProcessor()
    processor.run_etl()