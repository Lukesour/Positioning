#!/usr/bin/env python3
"""
优化的ETL数据预处理模块
基于真实数据格式进行优化
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

class OptimizedETLProcessor:
    """优化的ETL数据处理器"""
    
    def __init__(self):
        self.source_conn = None
        self.target_conn = None
        self.processed_count = 0
        self.error_count = 0
        
        # 院校层次映射
        self.school_tier_mapping = {
            '985院校': '985院校',
            '211院校': '211院校', 
            '普通本科': '双非院校',
            '海外院校': '海外院校'
        }
        
        # 985院校列表
        self.tier_985_schools = [
            '清华大学', '北京大学', '复旦大学', '上海交通大学', '浙江大学', '中国科学技术大学',
            '南京大学', '哈尔滨工业大学', '西安交通大学', '中山大学', '华南理工大学', '山东大学',
            '华中科技大学', '大连理工大学', '北京理工大学', '天津大学', '东南大学', '华东师范大学',
            '中南大学', '西北工业大学', '同济大学', '厦门大学', '北京航空航天大学', '重庆大学',
            '四川大学', '电子科技大学', '西北大学', '兰州大学', '东北大学', '湖南大学',
            '华东理工大学', '中国农业大学', '中国海洋大学', '北京师范大学', '中央民族大学',
            '国防科技大学', '西北农林科技大学', '新疆大学', '云南大学'
        ]
        
        # 211院校关键词
        self.tier_211_keywords = [
            '北京邮电', '上海财经', '中央财经', '对外经济贸易', '华东理工', '东华大学',
            '上海大学', '苏州大学', '南京理工', '南京航空航天', '河海大学', '江南大学',
            '南京师范', '华中师范', '华南师范', '暨南大学', '华南农业', '广西大学',
            '海南大学', '西南交通', '西南财经', '云南大学', '西北大学', '陕西师范',
            '长安大学', '兰州大学', '宁夏大学', '新疆大学', '石河子大学', '青海大学',
            '内蒙古大学', '延边大学', '东北师范', '哈尔滨工程', '东北农业', '东北林业',
            '辽宁大学', '大连海事', '太原理工', '中北大学', '河北工业', '华北电力',
            '北京交通', '北京科技', '北京化工', '北京林业', '中国传媒', '中央音乐',
            '中国政法', '中国矿业', '中国石油', '中国地质', '北京中医药', '北京外国语',
            '首都师范', '首都医科', '首都经济贸易', '中国人民公安', '外交学院', '国际关系学院',
            '北京体育', '中央美术', '中央戏剧', '中国音乐', '北京电影', '中国戏曲',
            '天津医科', '河北大学', '山西大学', '内蒙古科技', '沈阳工业', '沈阳农业',
            '大连大学', '渤海大学', '吉林大学', '延边科技', '长春理工', '东北电力',
            '吉林农业', '长春中医药', '哈尔滨医科', '哈尔滨师范', '黑龙江大学', '哈尔滨商业',
            '上海理工', '上海海事', '东华大学', '上海电力', '上海应用技术', '上海海洋',
            '上海中医药', '华东政法', '上海师范', '上海外国语', '上海对外经贸', '上海体育',
            '上海音乐', '上海戏剧', '南京工业', '常州大学', '南京邮电', '南京林业',
            '江苏大学', '南京信息工程', '南通大学', '南京农业', '南京医科', '徐州医科',
            '南京中医药', '中国药科', '南京师范', '江苏师范', '淮阴师范', '盐城师范',
            '南京财经', '江苏科技', '常熟理工', '淮阴工学院', '常州工学院', '扬州大学',
            '三江学院', '南京大学金陵学院', '东南大学成贤学院', '南京理工大学紫金学院',
            '南京航空航天大学金城学院', '中国传媒大学南广学院', '南京工业大学浦江学院',
            '南京师范大学泰州学院', '南京理工大学泰州科技学院', '南京师范大学中北学院',
            '南京医科大学康达学院', '南京中医药大学翰林学院', '南京信息工程大学滨江学院',
            '苏州大学文正学院', '苏州大学应用技术学院', '苏州科技大学天平学院',
            '江苏大学京江学院', '扬州大学广陵学院', '江苏师范大学科文学院',
            '南京邮电大学通达学院', '南京财经大学红山学院', '江苏科技大学苏州理工学院',
            '常州大学怀德学院', '南通大学杏林学院', '南京审计大学金审学院'
        ]
    
    def connect_databases(self):
        """连接源数据库和目标数据库"""
        try:
            self.source_conn = psycopg2.connect(**SOURCE_DB_CONFIG)
            logger.info("成功连接源数据库")
            
            self.target_conn = psycopg2.connect(**TARGET_DB_CONFIG)
            self.target_conn.autocommit = False
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
    
    def parse_title_info(self, title: str) -> Dict:
        """从标题中解析信息"""
        info = {
            'university': '',
            'program': '',
            'undergrad_school': '',
            'undergrad_major': '',
            'gpa': '',
            'language_info': '',
            'work_experience': '应届生'
        }
        
        if not title:
            return info
        
        # 提取录取大学和项目
        # 模式：大学名+项目名+研究生offer
        university_match = re.search(r'^([^，,。]*(?:大学|学院|University|College|Institute))[^，,。]*?([^，,。]*(?:硕士|博士|Master|PhD))', title)
        if university_match:
            info['university'] = university_match.group(1).strip()
            info['program'] = university_match.group(2).strip()
        
        # 提取本科院校信息
        # 模式：本科院校名 专业名 其他信息
        lines = title.split('\n')
        for line in lines:
            line = line.strip()
            
            # 查找包含大学名称的行
            if any(keyword in line for keyword in ['大学', '学院', 'University', 'College']):
                # 提取学校名
                school_match = re.search(r'([^，,。\s]*(?:大学|学院|University|College))', line)
                if school_match:
                    school_name = school_match.group(1).strip()
                    # 确保这不是录取大学
                    if school_name != info['university']:
                        info['undergrad_school'] = school_name
                
                # 提取专业
                major_patterns = [
                    r'([^，,。\s]*(?:工程|科学|技术|管理|经济|学|设计))',
                    r'([^，,。\s]*(?:计算机|软件|电子|机械|土木|化学|物理|数学|金融|会计|市场营销))'
                ]
                for pattern in major_patterns:
                    major_match = re.search(pattern, line)
                    if major_match:
                        major = major_match.group(1).strip()
                        if len(major) > 2 and '大学' not in major and '学院' not in major:
                            info['undergrad_major'] = major
                            break
                
                # 提取GPA
                gpa_match = re.search(r'GPA[：:\s]*(\d+\.?\d*(?:/\d+\.?\d*)?)', line)
                if gpa_match:
                    info['gpa'] = gpa_match.group(1)
                
                # 提取语言成绩
                language_patterns = [
                    r'(雅思[：:\s]*\d+\.?\d*)',
                    r'(托福[：:\s]*\d+\.?\d*)',
                    r'(IELTS[：:\s]*\d+\.?\d*)',
                    r'(TOEFL[：:\s]*\d+\.?\d*)'
                ]
                for pattern in language_patterns:
                    lang_match = re.search(pattern, line)
                    if lang_match:
                        info['language_info'] = lang_match.group(1)
                        break
                
                # 提取工作经验
                if '应届' in line:
                    info['work_experience'] = '应届生'
                elif '已毕业' in line:
                    info['work_experience'] = '已毕业'
                elif '经验' in line:
                    info['work_experience'] = '有工作经验'
        
        return info
    
    def determine_school_tier_from_background(self, background: str) -> str:
        """从背景信息确定院校层次"""
        if not background:
            return '其他'
        
        background = background.strip()
        
        # 直接映射
        for key, value in self.school_tier_mapping.items():
            if key in background:
                return value
        
        return '其他'
    
    def determine_school_tier_from_name(self, school_name: str) -> str:
        """从学校名称确定院校层次"""
        if not school_name:
            return '其他'
        
        # 985院校
        for school in self.tier_985_schools:
            if school in school_name:
                return '985院校'
        
        # 211院校
        for keyword in self.tier_211_keywords:
            if keyword in school_name:
                return '211院校'
        
        # 海外院校
        if any(keyword in school_name for keyword in ['University', 'College', 'Institute']):
            return '海外院校'
        
        return '双非院校'
    
    def safe_parse_gpa(self, gpa_str: str) -> Tuple[Optional[float], Optional[float]]:
        """安全解析GPA字符串"""
        if not gpa_str or gpa_str.strip() == '':
            return None, None
            
        try:
            gpa_str = str(gpa_str).strip()
            
            # 匹配模式
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
                            # 推断
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
    
    def process_single_case(self, raw_case: tuple) -> Optional[Dict]:
        """处理单个案例"""
        try:
            case_id, title, url, university, program, background, gpa, language_score, graduation_year = raw_case
            
            # 解析标题信息
            title_info = self.parse_title_info(title or '')
            
            # 基本信息
            processed = {
                'original_id': case_id,
                'original_title': title or '',
                'original_url': url or '',
            }
            
            # 大学和项目信息
            processed['university'] = university or title_info['university']
            processed['program'] = program or title_info['program']
            
            # 本科信息
            processed['undergrad_school'] = title_info['undergrad_school']
            
            # 院校层次：优先使用背景信息，然后根据学校名称判断
            tier_from_background = self.determine_school_tier_from_background(background or '')
            if tier_from_background != '其他':
                processed['undergrad_school_tier'] = tier_from_background
            else:
                processed['undergrad_school_tier'] = self.determine_school_tier_from_name(processed['undergrad_school'])
            
            processed['undergrad_major'] = title_info['undergrad_major']
            
            # 学位层次
            degree_text = f"{title} {program}".lower()
            if any(keyword in degree_text for keyword in ['博士', 'phd', 'doctor']):
                processed['degree_level'] = '博士'
            else:
                processed['degree_level'] = '硕士'
            
            # GPA信息
            gpa_source = gpa or title_info['gpa']
            processed['gpa_original'] = gpa_source
            gpa_4, gpa_100 = self.safe_parse_gpa(gpa_source)
            processed['gpa_scale_4'] = gpa_4
            processed['gpa_scale_100'] = gpa_100
            
            # 语言成绩
            language_source = language_score or title_info['language_info']
            language_type, language_score_val = self.safe_parse_language_score(language_source)
            processed['language_type'] = language_type
            processed['language_score'] = language_score_val
            
            # GRE成绩
            gre_match = re.search(r'GRE[：:\s]*(\d+)', title or '')
            processed['gre_score'] = int(gre_match.group(1)) if gre_match else None
            
            # 工作经验
            processed['work_experience'] = title_info['work_experience']
            
            # 毕业年份
            if graduation_year and str(graduation_year).isdigit():
                processed['graduation_year'] = int(graduation_year)
            else:
                year_match = re.search(r'20(\d{2})', title or '')
                if year_match:
                    year = int(f"20{year_match.group(1)}")
                    if 2020 <= year <= 2030:
                        processed['graduation_year'] = year
                    else:
                        processed['graduation_year'] = None
                else:
                    processed['graduation_year'] = None
            
            # 验证必要字段
            if not processed['university'] or not processed['degree_level']:
                logger.warning(f"案例 {case_id} 缺少必要信息，跳过")
                return None
            
            return processed
            
        except Exception as e:
            logger.error(f"处理案例时出错: {e}")
            return None
    
    def run_etl(self, batch_size: int = 100):
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
    processor = OptimizedETLProcessor()
    processor.run_etl()