"""
智能案例匹配服务
实现多维度相似度计算和案例推荐算法
"""
import math
from typing import List, Dict, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import logging

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.models.case import Case, UserProfile, CaseResponse
from config.settings import MATCHING_CONFIG

logger = logging.getLogger(__name__)

class MatchingService:
    """案例匹配服务"""
    
    def __init__(self, db: Session):
        self.db = db
        self.weights = MATCHING_CONFIG['weights']
        self.max_cases = MATCHING_CONFIG['max_cases']
    
    def parse_user_gpa(self, gpa_str: str) -> Tuple[float, float]:
        """
        解析用户输入的GPA
        返回 (gpa_4, gpa_100)
        """
        import re
        
        if not gpa_str:
            return 0.0, 0.0
        
        # 匹配 x.x/4.0 或 xx/100 格式
        pattern = r'(\d+\.?\d*)/(\d+\.?\d*)'
        match = re.search(pattern, gpa_str)
        
        if match:
            numerator = float(match.group(1))
            denominator = float(match.group(2))
            
            if denominator == 4.0 or denominator == 4:
                return numerator, numerator * 25
            elif denominator == 100:
                return numerator / 25, numerator
        
        # 如果没有分母，尝试推断
        value_match = re.search(r'(\d+\.?\d*)', gpa_str)
        if value_match:
            value = float(value_match.group(1))
            if value <= 4:
                return value, value * 25
            else:
                return value / 25, value
        
        return 0.0, 0.0
    
    def calculate_school_tier_score(self, user_tier: str, case_tier: str) -> float:
        """
        计算院校层次相似度得分
        """
        if not case_tier:
            return 0.0
        
        # 院校层次等级映射
        tier_levels = {
            '985院校': 4,
            '211院校': 3,
            '双非院校': 2,
            '海外院校': 3,  # 海外院校等同于211
            '其他': 1
        }
        
        user_level = tier_levels.get(user_tier, 1)
        case_level = tier_levels.get(case_tier, 1)
        
        if user_level == case_level:
            return self.weights['school_tier']  # 完全匹配
        elif abs(user_level - case_level) == 1:
            return self.weights['school_tier'] * 0.5  # 相邻等级
        else:
            return 0.0
    
    def calculate_gpa_score(self, user_gpa_4: float, case_gpa_4: float) -> float:
        """
        计算GPA相似度得分
        """
        if not case_gpa_4 or case_gpa_4 <= 0:
            return 0.0
        
        diff = abs(user_gpa_4 - case_gpa_4)
        
        if diff <= 0.1:
            return self.weights['gpa']
        elif diff <= 0.2:
            return self.weights['gpa'] * 0.8
        elif diff <= 0.3:
            return self.weights['gpa'] * 0.6
        elif diff <= 0.5:
            return self.weights['gpa'] * 0.4
        else:
            return self.weights['gpa'] * 0.2
    
    def calculate_major_score(self, user_major: str, case_major: str) -> float:
        """
        计算专业相似度得分
        """
        if not case_major:
            return 0.0
        
        user_major = user_major.lower()
        case_major = case_major.lower()
        
        # 完全匹配
        if user_major == case_major:
            return self.weights['major']
        
        # 关键词匹配
        user_keywords = set(user_major.split())
        case_keywords = set(case_major.split())
        
        if user_keywords & case_keywords:  # 有交集
            overlap_ratio = len(user_keywords & case_keywords) / len(user_keywords | case_keywords)
            return self.weights['major'] * overlap_ratio
        
        # 专业领域相似度（简化版）
        major_groups = {
            'computer': ['计算机', '软件', '信息', 'computer', 'software', 'information'],
            'business': ['商业', '管理', '金融', '经济', 'business', 'management', 'finance', 'economics'],
            'engineering': ['工程', '机械', '电子', 'engineering', 'mechanical', 'electrical'],
            'science': ['科学', '数学', '物理', '化学', 'science', 'mathematics', 'physics', 'chemistry']
        }
        
        user_group = None
        case_group = None
        
        for group, keywords in major_groups.items():
            if any(keyword in user_major for keyword in keywords):
                user_group = group
            if any(keyword in case_major for keyword in keywords):
                case_group = group
        
        if user_group and user_group == case_group:
            return self.weights['major'] * 0.3
        
        return 0.0
    
    def calculate_language_score(self, user_score: float, case_score: float) -> float:
        """
        计算语言成绩相似度得分
        """
        if not case_score or case_score <= 0:
            return 0.0
        
        diff = abs(user_score - case_score)
        
        if diff <= 0.5:
            return self.weights['language']
        elif diff <= 1.0:
            return self.weights['language'] * 0.7
        elif diff <= 1.5:
            return self.weights['language'] * 0.4
        else:
            return self.weights['language'] * 0.1
    
    def calculate_gre_score(self, user_gre: int, case_gre: int) -> float:
        """
        计算GRE成绩相似度得分
        """
        if not case_gre or case_gre <= 0:
            return 0.0
        
        if not user_gre or user_gre <= 0:
            return 0.0
        
        diff = abs(user_gre - case_gre)
        
        if diff <= 10:
            return self.weights['gre']
        elif diff <= 20:
            return self.weights['gre'] * 0.7
        elif diff <= 30:
            return self.weights['gre'] * 0.4
        else:
            return self.weights['gre'] * 0.1
    
    def calculate_similarity_score(self, user_profile: UserProfile, case: Case) -> float:
        """
        计算用户与案例的总体相似度得分
        """
        total_score = 0.0
        
        # 解析用户GPA
        user_gpa_4, user_gpa_100 = self.parse_user_gpa(user_profile.gpa)
        
        # 院校层次得分
        school_score = self.calculate_school_tier_score(
            user_profile.school_tier, 
            case.undergrad_school_tier
        )
        total_score += school_score
        
        # GPA得分
        if case.gpa_scale_4:
            gpa_score = self.calculate_gpa_score(user_gpa_4, float(case.gpa_scale_4))
            total_score += gpa_score
        
        # 专业得分
        major_score = self.calculate_major_score(
            user_profile.major, 
            case.undergrad_major or ''
        )
        total_score += major_score
        
        # 语言成绩得分
        if user_profile.language_score and case.language_score:
            language_score = self.calculate_language_score(
                user_profile.language_score, 
                float(case.language_score)
            )
            total_score += language_score
        
        # GRE得分
        if user_profile.gre_score and case.gre_score:
            gre_score = self.calculate_gre_score(
                user_profile.gre_score, 
                case.gre_score
            )
            total_score += gre_score
        
        return total_score
    
    def find_similar_cases(self, user_profile: UserProfile) -> List[CaseResponse]:
        """
        查找相似案例
        """
        try:
            # Step 1: 硬性筛选 - 相同学位层次
            base_query = self.db.query(Case).filter(
                Case.degree_level == user_profile.target_degree
            )
            
            # 获取所有候选案例
            candidate_cases = base_query.all()
            logger.info(f"找到 {len(candidate_cases)} 个候选案例")
            
            # Step 2: 计算相似度得分
            scored_cases = []
            for case in candidate_cases:
                similarity_score = self.calculate_similarity_score(user_profile, case)
                if similarity_score > 0:  # 只保留有得分的案例
                    case_response = CaseResponse.from_orm(case)
                    case_response.similarity_score = similarity_score
                    scored_cases.append(case_response)
            
            # Step 3: 按得分排序并返回Top N
            scored_cases.sort(key=lambda x: x.similarity_score, reverse=True)
            top_cases = scored_cases[:self.max_cases]
            
            logger.info(f"返回 {len(top_cases)} 个匹配案例")
            return top_cases
            
        except Exception as e:
            logger.error(f"查找相似案例时出错: {e}")
            return []
    
    def categorize_recommendations(self, cases: List[CaseResponse], user_profile: UserProfile) -> Dict[str, List[Dict]]:
        """
        将案例分类为冲刺、核心、保底三个梯度
        """
        if not cases:
            return {"reach": [], "target": [], "safety": []}
        
        # 按相似度得分分组
        high_score_threshold = 60  # 高分阈值
        medium_score_threshold = 40  # 中等分数阈值
        
        reach_schools = []
        target_schools = []
        safety_schools = []
        
        # 统计不同大学的案例
        university_cases = {}
        for case in cases:
            if case.university not in university_cases:
                university_cases[case.university] = []
            university_cases[case.university].append(case)
        
        # 为每个大学选择最佳案例作为推荐
        for university, uni_cases in university_cases.items():
            best_case = max(uni_cases, key=lambda x: x.similarity_score)
            
            recommendation = {
                "university": best_case.university,
                "program": best_case.program,
                "reason": f"相似度得分: {best_case.similarity_score:.1f}",
                "evidence_case_id": best_case.id
            }
            
            if best_case.similarity_score >= high_score_threshold:
                target_schools.append(recommendation)
            elif best_case.similarity_score >= medium_score_threshold:
                if len(target_schools) < 3:
                    target_schools.append(recommendation)
                else:
                    safety_schools.append(recommendation)
            else:
                safety_schools.append(recommendation)
        
        # 如果target_schools太少，从safety中提升一些
        while len(target_schools) < 3 and safety_schools:
            target_schools.append(safety_schools.pop(0))
        
        # 选择一些高排名学校作为冲刺目标
        # 这里可以根据实际需求调整逻辑
        prestigious_universities = [
            "牛津大学", "剑桥大学", "帝国理工学院", "伦敦政治经济学院",
            "香港大学", "香港科技大学", "香港中文大学",
            "新加坡国立大学", "南洋理工大学"
        ]
        
        for case in cases[:5]:  # 从前5个案例中选择冲刺目标
            if any(uni in case.university for uni in prestigious_universities):
                reach_recommendation = {
                    "university": case.university,
                    "program": case.program,
                    "reason": f"顶尖院校，值得冲刺 (相似度: {case.similarity_score:.1f})",
                    "evidence_case_id": case.id
                }
                reach_schools.append(reach_recommendation)
                if len(reach_schools) >= 3:
                    break
        
        return {
            "reach": reach_schools[:3],
            "target": target_schools[:4],
            "safety": safety_schools[:3]
        }