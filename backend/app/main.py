"""
FastAPI 主应用程序
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import logging
from typing import List

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.models.case import UserProfile, SchoolPlanningResponse, AnalysisReport
from backend.services.matching_service import MatchingService
from backend.services.llm_service import LLMService
from backend.utils.database import get_db, create_tables
from config.settings import DEBUG

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="智能留学选校规划系统",
    description="基于海量成功案例和LLM的智能化留学选校规划工具",
    version="1.0.0",
    debug=DEBUG
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# 创建数据库表
create_tables()

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """返回主页"""
    try:
        with open("frontend/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="""
        <html>
            <head><title>智能留学选校规划系统</title></head>
            <body>
                <h1>智能留学选校规划系统</h1>
                <p>前端页面正在开发中...</p>
                <p>请访问 <a href="/docs">/docs</a> 查看API文档</p>
            </body>
        </html>
        """)

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "message": "智能留学选校规划系统运行正常"}

@app.post("/api/v1/school-planning", response_model=SchoolPlanningResponse)
async def school_planning(
    user_profile: UserProfile,
    db: Session = Depends(get_db)
):
    """
    智能选校规划主接口
    """
    try:
        logger.info(f"收到选校规划请求: {user_profile.undergrad_school}")
        
        # 1. 初始化服务
        matching_service = MatchingService(db)
        llm_service = LLMService()
        
        # 2. 查找相似案例
        matched_cases = matching_service.find_similar_cases(user_profile)
        
        if not matched_cases:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="未找到匹配的案例，请检查输入信息或联系管理员"
            )
        
        logger.info(f"找到 {len(matched_cases)} 个匹配案例")
        
        # 3. 生成LLM分析报告
        analysis_report = llm_service.generate_analysis_report(user_profile, matched_cases)
        
        # 4. 构建响应
        response = SchoolPlanningResponse(
            analysis_report=analysis_report,
            matched_cases=matched_cases
        )
        
        logger.info("选校规划请求处理完成")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"选校规划处理失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"服务器内部错误: {str(e)}"
        )

@app.get("/api/v1/cases/count")
async def get_cases_count(db: Session = Depends(get_db)):
    """获取案例总数"""
    try:
        from backend.models.case import Case
        count = db.query(Case).count()
        return {"total_cases": count}
    except Exception as e:
        logger.error(f"获取案例数量失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取案例数量失败"
        )

@app.get("/api/v1/cases/sample")
async def get_sample_cases(limit: int = 10, db: Session = Depends(get_db)):
    """获取样例案例"""
    try:
        from backend.models.case import Case, CaseResponse
        cases = db.query(Case).limit(limit).all()
        return [CaseResponse.from_orm(case) for case in cases]
    except Exception as e:
        logger.error(f"获取样例案例失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取样例案例失败"
        )

@app.get("/api/v1/config/options")
async def get_config_options():
    """获取配置选项（用于前端下拉框）"""
    return {
        "school_tiers": ["985", "211", "双一流", "普通一本", "普通二本", "海外院校", "其他"],
        "language_tests": ["雅思", "托福", "多邻国", "暂无"],
        "degree_levels": ["硕士", "博士"],
        "countries": ["英国", "香港", "新加坡", "美国", "澳大利亚", "加拿大", "德国", "法国", "荷兰"],
        "popular_majors": [
            "计算机科学", "软件工程", "数据科学", "人工智能", "机器学习",
            "金融", "会计", "市场营销", "管理学", "工商管理",
            "机械工程", "电子工程", "土木工程", "材料科学",
            "经济学", "国际关系", "教育学", "心理学", "传媒学"
        ],
        "popular_universities": [
            "北京大学", "清华大学", "复旦大学", "上海交通大学", "浙江大学",
            "中国科学技术大学", "南京大学", "华中科技大学", "中山大学", "西安交通大学",
            "哈尔滨工业大学", "北京理工大学", "东南大学", "同济大学", "天津大学"
        ],
        "post_graduation_plans": ["立即回国", "先在当地工作", "不确定"],
        "school_selection_factors": [
            "综合排名", "专业排名", "地理位置与就业", "学费与性价比", 
            "教授与科研实力", "校园文化"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    from config.settings import APP_HOST, APP_PORT
    
    uvicorn.run(
        "backend.app.main:app",
        host=APP_HOST,
        port=APP_PORT,
        reload=DEBUG
    )