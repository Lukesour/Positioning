"""
大型语言模型服务
负责调用LLM API生成智能分析报告
"""
from openai import OpenAI
import json
import logging
from typing import List, Dict
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.models.case import UserProfile, CaseResponse, AnalysisReport
from config.settings import OPENAI_API_KEY, OPENAI_BASE_URL, LLM_MODEL

logger = logging.getLogger(__name__)

class LLMService:
    """LLM服务类"""
    
    def __init__(self):
        # 配置OpenAI客户端 (新版本API)
        self.client = OpenAI(
            api_key=OPENAI_API_KEY,
            base_url=OPENAI_BASE_URL if OPENAI_BASE_URL else None
        )
        self.model = LLM_MODEL
    
    def build_prompt(self, user_profile: UserProfile, matched_cases: List[CaseResponse]) -> str:
        """
        构建发送给LLM的提示词 (V1.5 增强版)
        """
        # 构建案例信息
        cases_info = []
        for i, case in enumerate(matched_cases[:20], 1):
            case_info = {
                "序号": i,
                "录取大学": case.university,
                "录取项目": case.program,
                "学生背景": f"{case.undergrad_school_tier or '未知'} {case.undergrad_major or '未知专业'}",
                "GPA": f"{case.gpa_scale_4 or 'N/A'}/4.0" if case.gpa_scale_4 else "N/A",
                "语言成绩": f"{case.language_type or ''} {case.language_score or 'N/A'}".strip(),
                "GRE": case.gre_score or "N/A",
                "相似度": f"{case.similarity_score:.1f}" if case.similarity_score else "N/A"
            }
            cases_info.append(case_info)
        
        # 构建用户基本信息
        user_info = {
            "申请学位": user_profile.target_degree,
            "本科院校": f"{user_profile.undergrad_school} ({user_profile.school_tier})",
            "本科专业": user_profile.major,
            "总GPA": user_profile.gpa,
            "专业GPA": user_profile.major_gpa or "未提供",
            "专业排名": user_profile.major_ranking or "未提供",  # V1.6.1 新增
            "语言成绩": f"{user_profile.language_test} {user_profile.language_score or 'N/A'}".strip(),
            "GRE成绩": user_profile.gre_score or "N/A",
            "海外交换经历": "有" if user_profile.exchange_experience else "无",
            "意向国家": ", ".join(user_profile.target_countries),
            "意向专业": ", ".join(user_profile.target_majors) if user_profile.target_majors else user_profile.target_major,
            "毕业后规划": user_profile.post_graduation_plan or "未明确",
            "留学预算": user_profile.budget or "未明确"  # V1.6.1 新增
        }
        
        # 构建实践背景信息
        practical_info = ""
        if user_profile.practical_experiences:
            practical_info = "\n## 实践背景详情:\n"
            for i, exp in enumerate(user_profile.practical_experiences, 1):
                practical_info += f"""
{i}. {exp.get('organization', '未知机构')} - {exp.get('position', '未知职位')}
   时间: {exp.get('start_date', '')} 至 {exp.get('end_date', '')}
   职责与成果: {exp.get('description', '无详细描述')}
"""
        
        # 构建学术背景补充信息
        academic_supplement = ""
        if user_profile.prerequisite_courses:
            academic_supplement += f"\n## 核心先修课程:\n{user_profile.prerequisite_courses}\n"
        
        if user_profile.achievements:
            academic_supplement += f"\n## 项目成果与荣誉:\n{user_profile.achievements}\n"
        
        # 构建选校偏好信息
        preferences_info = ""
        if user_profile.school_selection_factors:
            preferences_info = f"\n## 选校偏好 (按重要性排序):\n"
            for i, factor in enumerate(user_profile.school_selection_factors, 1):
                preferences_info += f"{i}. {factor}\n"
        
        prompt = f"""# Role: 你是一名拥有15年经验的资深留学申请顾问，尤其擅长根据学生的背景和过往成功案例，进行精准的院校定位和策略规划。请使用简体中文回答。

# User Profile:
{json.dumps(user_info, ensure_ascii=False, indent=2)}
{academic_supplement}
{practical_info}
{preferences_info}

# Similar Successful Cases:
以下是与该学生背景高度相似的{len(cases_info)}个成功录取案例（按相似度排序）：

{json.dumps(cases_info, ensure_ascii=False, indent=2)}

# Task:
请根据以上用户背景和成功案例，为该学生提供一份详细的留学选校规划报告。报告必须包含以下四个部分：

## 1. 背景综合评估
### 优势 (Strengths)
明确指出该生的核心竞争力在哪里。请特别关注：
- 学术背景优势（院校层次、GPA、专业排名、专业匹配度等）
- 实践经历亮点（科研、实习、项目成果等）
- 海外经历加分项
- 与目标专业的匹配度
请结合具体数据和经历进行分析，特别关注专业排名对申请的积极影响。

### 劣势 (Weaknesses)  
明确指出该生的短板和需要改进的地方。请特别关注：
- 标准化考试成绩不足
- 实践经历的缺失或不足
- 跨专业申请的挑战
- 与成功案例的差距
请与成功案例对比分析，指出具体的改进方向。

## 2. 选校梯度策略
请根据学生的选校偏好（{', '.join(user_profile.school_selection_factors) if user_profile.school_selection_factors else '综合考虑'}）、预算情况（{user_profile.budget or '未明确'}）和成功案例，分为三个梯度：

### 冲刺院校 (Reach) - 推荐2-3所
这些学校的录取要求略高于学生目前水平，但根据案例，有成功的可能性。请说明为什么可以冲刺，并引用具体案例佐证。同时考虑预算因素。

### 核心院校 (Target) - 推荐3-4所  
这些学校的录取要求与学生水平高度匹配，是申请的重点。请说明匹配度高的原因，并引用案例。确保推荐的学校符合预算范围。

### 保底院校 (Safety) - 推荐2-3所
这些学校的录取要求学生已基本达到，录取概率较大，用于确保有学可上。优先考虑性价比高的选择。

## 3. 后续提升建议
针对学生的劣势和毕业后规划（{user_profile.post_graduation_plan or '未明确'}），提出2-3条具体可行的提升建议。例如：
- 标准化考试提升目标和时间安排
- 实践经历补充建议（科研、实习、项目等）
- 申请材料优化建议
- 针对目标专业的背景提升

## 4. 申请时间规划
根据学生的意向国家和专业，提供一个详细的申请时间线建议，包括：
- 标准化考试时间安排
- 申请材料准备时间点
- 申请提交截止日期
- 面试准备时间

请确保分析客观、建议实用，并充分利用提供的成功案例数据和学生的详细背景信息来支撑你的建议。特别要考虑学生的选校偏好和毕业后规划。"""

        return prompt
    
    def generate_analysis_report(self, user_profile: UserProfile, matched_cases: List[CaseResponse]) -> AnalysisReport:
        """
        生成智能分析报告
        """
        try:
            # 构建提示词
            prompt = self.build_prompt(user_profile, matched_cases)
            
            # 调用LLM API (新版本API)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "你是一名专业的留学申请顾问，擅长根据学生背景和成功案例提供精准的选校建议。"
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            # 提取回复内容
            analysis_text = response.choices[0].message.content
            
            # 解析分析报告
            report = self.parse_analysis_report(analysis_text, matched_cases)
            
            logger.info("成功生成LLM分析报告")
            return report
            
        except Exception as e:
            logger.error(f"LLM分析报告生成失败: {e}")
            # 返回默认报告
            return self.generate_fallback_report(user_profile, matched_cases)
    
    def parse_analysis_report(self, analysis_text: str, matched_cases: List[CaseResponse]) -> AnalysisReport:
        """
        解析LLM返回的分析报告文本
        """
        try:
            # 简单的文本解析逻辑
            # 在实际应用中，可能需要更复杂的解析逻辑
            
            sections = analysis_text.split('##')
            
            strengths = ""
            weaknesses = ""
            suggestions = ""
            
            for section in sections:
                if '优势' in section or 'Strengths' in section:
                    strengths = section.strip()
                elif '劣势' in section or 'Weaknesses' in section:
                    weaknesses = section.strip()
                elif '提升建议' in section or '建议' in section:
                    suggestions = section.strip()
            
            # 如果解析失败，使用整个文本
            if not strengths and not weaknesses:
                strengths = "根据您的背景分析，具体优势请参考完整报告。"
                weaknesses = "具体劣势分析请参考完整报告。"
                suggestions = analysis_text
            
            # 生成推荐学校（简化版）
            recommendations = self.extract_recommendations_from_cases(matched_cases)
            
            return AnalysisReport(
                strengths=strengths,
                weaknesses=weaknesses,
                recommendations=recommendations,
                suggestions=suggestions
            )
            
        except Exception as e:
            logger.error(f"解析LLM报告失败: {e}")
            return self.generate_fallback_report(None, matched_cases)
    
    def extract_recommendations_from_cases(self, matched_cases: List[CaseResponse]) -> Dict:
        """
        从匹配案例中提取学校推荐
        """
        if not matched_cases:
            return {"reach": [], "target": [], "safety": []}
        
        # 按相似度分组
        high_score_cases = [case for case in matched_cases if case.similarity_score and case.similarity_score >= 60]
        medium_score_cases = [case for case in matched_cases if case.similarity_score and 40 <= case.similarity_score < 60]
        low_score_cases = [case for case in matched_cases if case.similarity_score and case.similarity_score < 40]
        
        def create_recommendation(case):
            return {
                "university": case.university,
                "program": case.program,
                "reason": f"相似度得分: {case.similarity_score:.1f}",
                "evidence_case_id": case.id
            }
        
        # 去重并选择代表性学校
        def get_unique_universities(cases, limit):
            seen_universities = set()
            recommendations = []
            for case in cases:
                if case.university not in seen_universities and len(recommendations) < limit:
                    recommendations.append(create_recommendation(case))
                    seen_universities.add(case.university)
            return recommendations
        
        return {
            "reach": get_unique_universities(high_score_cases[:3], 3),
            "target": get_unique_universities(medium_score_cases[:4], 4),
            "safety": get_unique_universities(low_score_cases[:3], 3)
        }
    
    def generate_fallback_report(self, user_profile: UserProfile, matched_cases: List[CaseResponse]) -> AnalysisReport:
        """
        生成备用分析报告（当LLM调用失败时使用）
        """
        recommendations = self.extract_recommendations_from_cases(matched_cases)
        
        return AnalysisReport(
            strengths="根据您提供的背景信息，我们为您匹配了相关的成功案例。",
            weaknesses="建议您进一步完善申请材料，提升竞争力。",
            recommendations=recommendations,
            suggestions="建议您根据匹配的案例，制定合适的申请策略。如需更详细的分析，请联系专业顾问。"
        )