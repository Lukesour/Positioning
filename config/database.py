"""
数据库配置文件
"""
import os
from dotenv import load_dotenv

load_dotenv()

# 源数据库配置 (只读)
SOURCE_DB_CONFIG = {
    'host': os.getenv('SOURCE_DB_HOST', 'localhost'),
    'port': int(os.getenv('SOURCE_DB_PORT', 5432)),
    'database': os.getenv('SOURCE_DB_NAME', 'compassedu_cases'),
    'user': os.getenv('SOURCE_DB_USER', 'suan'),
    'password': os.getenv('SOURCE_DB_PASSWORD', ''),
}

# 目标数据库配置 (读写)
TARGET_DB_CONFIG = {
    'host': os.getenv('TARGET_DB_HOST', 'localhost'),
    'port': int(os.getenv('TARGET_DB_PORT', 5432)),
    'database': os.getenv('TARGET_DB_NAME', 'processed_cases'),
    'user': os.getenv('TARGET_DB_USER', 'suan'),
    'password': os.getenv('TARGET_DB_PASSWORD', ''),
}

# SQLAlchemy 连接字符串
SOURCE_DATABASE_URL = f"postgresql://{SOURCE_DB_CONFIG['user']}:{SOURCE_DB_CONFIG['password']}@{SOURCE_DB_CONFIG['host']}:{SOURCE_DB_CONFIG['port']}/{SOURCE_DB_CONFIG['database']}"

TARGET_DATABASE_URL = f"postgresql://{TARGET_DB_CONFIG['user']}:{TARGET_DB_CONFIG['password']}@{TARGET_DB_CONFIG['host']}:{TARGET_DB_CONFIG['port']}/{TARGET_DB_CONFIG['database']}"