#!/usr/bin/env python3
"""
运行ETL数据处理脚本
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripts.etl_processor import ETLProcessor

if __name__ == "__main__":
    print("=" * 50)
    print("ETL数据预处理开始")
    print("=" * 50)
    
    try:
        processor = ETLProcessor()
        processor.run_etl()
        print("=" * 50)
        print("ETL数据预处理完成")
        print("=" * 50)
    except Exception as e:
        print(f"ETL处理失败: {e}")
        sys.exit(1)