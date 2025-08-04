"""
案例数据模型
"""
from sqlalchemy import Column, Integer, String, Numeric, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

Base = declarative_base()

class Case(Base):
    """案例数据库模型"""
    __tablename__ = 'cases'
    
    id = Column(Integer, primary_key=True, index=True)
    original_id = Column(Integer, nullable=False)
    university = Column(String(255), nullable=False)
    program = Column(String(255), nullable=False)
    degree_level = Column(String(50), nullable=False)
    undergrad_school = Column(String(255))
    undergrad_school_tier = Column(String(50))
    undergrad_major = Column(String(255))
    gpa_original = Column(String(50))
    gpa_scale_4 = Column(Numeric(4, 2))
    gpa_scale_100 = Column(Numeric(5, 2))
    language_type = Column(String(20))
    language_score = Column(Numeric(3, 1))
    gre_score = Column(Integer)
    work_experience = Column(String(100))
    graduation_year = Column(Integer)
    original_url = Column(Text)
    original_title = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class CaseResponse(BaseModel):
    """案例响应模型"""
    id: int
    university: str
    program: str
    degree_level: str
    undergrad_school: Optional[str] = None
    undergrad_school_tier: Optional[str] = None
    undergrad_major: Optional[str] = None
    gpa_original: Optional[str] = None
    gpa_scale_4: Optional[float] = None
    gpa_scale_100: Optional[float] = None
    language_type: Optional[str] = None
    language_score: Optional[float] = None
    gre_score: Optional[int] = None
    work_experience: Optional[str] = None
    graduation_year: Optional[int] = None
    original_url: Optional[str] = None
    original_title: Optional[str] = None
    similarity_score: Optional[float] = None  # 相似度得分
    
    class Config:
        from_attributes = True

class UserProfile(BaseModel):
    """用户输入模型"""
    # --- 现有字段 ---
    undergrad_school: str
    school_tier: str  # 985, 211, 双一流, 普通一本, 普通二本, 海外院校, 其他
    major: str
    gpa: str  # 总GPA，如 "3.5/4.0" 或 "88/100"
    language_test: str  # IELTS, TOEFL, Duolingo, None
    language_score: Optional[float] = None
    gre_score: Optional[int] = None
    target_degree: str  # 硕士, 博士
    target_countries: List[str]  # ["香港", "新加坡", "英国", "美国", "澳大利亚"]
    target_major: str  # 保持向后兼容，但V1.5中会被target_majors替代
    
    # --- V1.5 新增字段 ---
    # 学术背景
    major_gpa: Optional[str] = None  # 专业GPA
    exchange_experience: Optional[bool] = False  # 海外交换/访学经历
    prerequisite_courses: Optional[str] = None  # 核心先修课程
    
    # 实践背景
    practical_experiences: Optional[List[Dict]] = None  # 科研/实习/工作经历
    achievements: Optional[str] = None  # 项目成果（论文/专利等）
    
    # 申请意向与偏好
    target_majors: Optional[List[str]] = None  # 意向申请专业（有序列表）
    post_graduation_plan: Optional[str] = None  # 毕业后去向
    school_selection_factors: Optional[List[str]] = None  # 选校最看重方面（有序列表）

class SchoolRecommendation(BaseModel):
    """学校推荐模型"""
    university: str
    program: str
    reason: str
    evidence_case_id: int

class AnalysisReport(BaseModel):
    """分析报告模型"""
    strengths: str
    weaknesses: str
    recommendations: dict  # {"reach": [...], "target": [...], "safety": [...]}
    suggestions: str

class SchoolPlanningResponse(BaseModel):
    """选校规划响应模型"""
    analysis_report: AnalysisReport
    matched_cases: List[CaseResponse]