# 快速启动指南

## 🚀 5分钟快速体验

### 前置条件
- Python 3.8+
- PostgreSQL 12+

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置环境
创建 `.env` 文件：
```env
# 数据库配置
SOURCE_DB_HOST=localhost
SOURCE_DB_PORT=5432
SOURCE_DB_NAME=compassedu_cases
SOURCE_DB_USER=suan
SOURCE_DB_PASSWORD=your_password

TARGET_DB_HOST=localhost
TARGET_DB_PORT=5432
TARGET_DB_NAME=processed_cases
TARGET_DB_USER=suan
TARGET_DB_PASSWORD=your_password

# LLM API配置（可选，用于AI分析）
OPENAI_API_KEY=your_openai_api_key
OPENAI_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-3.5-turbo

# 应用配置
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=True
```

### 3. 数据库初始化
```bash
# 创建数据库
createdb processed_cases

# 运行迁移
psql -d processed_cases -f database/migrations/001_create_cases_table.sql
```

### 4. 数据预处理（可选）
如果有源数据：
```bash
python run_etl.py
```

### 5. 启动服务
```bash
python run_server.py
```

### 6. 访问系统
- 主页: http://localhost:8000
- API文档: http://localhost:8000/docs

## 🧪 测试系统
```bash
python test_system.py
```

## 📝 示例数据

如果没有真实数据，可以使用以下示例进行测试：

### 用户输入示例
```json
{
  "undergrad_school": "中山大学",
  "school_tier": "985院校",
  "major": "软件工程",
  "gpa": "85/100",
  "language_test": "雅思",
  "language_score": 6.5,
  "gre_score": 320,
  "target_degree": "硕士",
  "target_countries": ["香港", "新加坡"],
  "target_major": "计算机科学"
}
```

### API测试
```bash
curl -X POST "http://localhost:8000/api/v1/school-planning" \
     -H "Content-Type: application/json" \
     -d '{
       "undergrad_school": "中山大学",
       "school_tier": "985院校",
       "major": "软件工程",
       "gpa": "85/100",
       "language_test": "雅思",
       "language_score": 6.5,
       "target_degree": "硕士",
       "target_countries": ["香港"],
       "target_major": "计算机科学"
     }'
```

## 🔧 常见问题

### Q: 数据库连接失败
A: 检查PostgreSQL服务是否启动，确认用户名密码正确

### Q: LLM API调用失败
A: 检查OPENAI_API_KEY是否配置正确，系统会使用备用报告

### Q: 没有匹配案例
A: 确保已运行ETL处理，或者调整匹配条件

### Q: 前端页面无法访问
A: 确认服务器已启动，检查端口是否被占用

## 📚 更多信息

- [完整文档](README.md)
- [部署指南](DEPLOYMENT.md)
- [项目总结](PROJECT_SUMMARY.md)