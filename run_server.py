#!/usr/bin/env python3
"""
启动服务器脚本
"""
import uvicorn
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import APP_HOST, APP_PORT, DEBUG

if __name__ == "__main__":
    print("=" * 50)
    print("智能留学选校规划系统")
    print("=" * 50)
    print(f"服务器地址: http://{APP_HOST}:{APP_PORT}")
    print(f"API文档: http://{APP_HOST}:{APP_PORT}/docs")
    print("=" * 50)
    
    uvicorn.run(
        "backend.app.main:app",
        host=APP_HOST,
        port=APP_PORT,
        reload=DEBUG,
        log_level="info"
    )