"""
应用配置文件
"""
import os
from dotenv import load_dotenv

load_dotenv()

# LLM API 配置
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
LLM_MODEL = os.getenv('LLM_MODEL', 'gpt-3.5-turbo')

# 应用配置
APP_HOST = os.getenv('APP_HOST', '0.0.0.0')
APP_PORT = int(os.getenv('APP_PORT', 8000))
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

# 匹配算法配置
MATCHING_CONFIG = {
    'max_cases': 20,  # 返回的最大案例数
    'weights': {
        'school_tier': 30,  # 院校层次权重
        'gpa': 25,          # GPA权重
        'major': 20,        # 专业权重
        'language': 15,     # 语言成绩权重
        'gre': 10,          # GRE权重
    }
}