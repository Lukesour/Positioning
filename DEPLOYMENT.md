# 部署指南

## 环境要求

- Python 3.8+
- PostgreSQL 12+
- 至少 2GB RAM
- 10GB 磁盘空间

## 部署步骤

### 1. 系统准备

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装PostgreSQL
sudo apt install postgresql postgresql-contrib

# 安装Python和pip
sudo apt install python3 python3-pip python3-venv
```

### 2. 数据库设置

```bash
# 切换到postgres用户
sudo -u postgres psql

# 创建用户和数据库
CREATE USER suan WITH PASSWORD 'your_secure_password';
CREATE DATABASE compassedu_cases OWNER suan;
CREATE DATABASE processed_cases OWNER suan;
GRANT ALL PRIVILEGES ON DATABASE compassedu_cases TO suan;
GRANT ALL PRIVILEGES ON DATABASE processed_cases TO suan;
\q
```

### 3. 项目部署

```bash
# 克隆项目
git clone <repository-url>
cd school-selection-system

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入正确的配置信息
```

### 4. 数据库初始化

```bash
# 运行数据库迁移
psql -h localhost -U suan -d processed_cases -f database/migrations/001_create_cases_table.sql

# 运行ETL处理（需要先有源数据）
python run_etl.py
```

### 5. 启动服务

```bash
# 开发环境
python run_server.py

# 生产环境（使用gunicorn）
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend.app.main:app --bind 0.0.0.0:8000
```

### 6. 配置反向代理（可选）

使用Nginx作为反向代理：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/your/project/frontend/;
    }
}
```

### 7. 设置定时任务

```bash
# 编辑crontab
crontab -e

# 添加ETL定时任务（每天凌晨2点运行）
0 2 * * * /path/to/venv/bin/python /path/to/project/run_etl.py >> /var/log/etl.log 2>&1
```

## 监控和维护

### 日志管理

```bash
# 查看应用日志
tail -f /var/log/school-selection.log

# 查看ETL日志
tail -f /var/log/etl.log
```

### 性能监控

- 监控数据库连接数
- 监控API响应时间
- 监控LLM API调用次数和成本
- 监控磁盘空间使用

### 备份策略

```bash
# 数据库备份脚本
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -h localhost -U suan processed_cases > /backup/processed_cases_$DATE.sql
pg_dump -h localhost -U suan compassedu_cases > /backup/compassedu_cases_$DATE.sql

# 保留最近30天的备份
find /backup -name "*.sql" -mtime +30 -delete
```

## 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查PostgreSQL服务状态
   - 验证数据库配置信息
   - 检查防火墙设置

2. **LLM API调用失败**
   - 验证API密钥
   - 检查网络连接
   - 确认API配额

3. **ETL处理失败**
   - 检查源数据库连接
   - 验证数据格式
   - 查看详细错误日志

### 性能优化

1. **数据库优化**
   ```sql
   -- 创建额外索引
   CREATE INDEX idx_cases_composite ON cases(degree_level, undergrad_school_tier, gpa_scale_4);
   
   -- 分析表统计信息
   ANALYZE cases;
   ```

2. **应用优化**
   - 启用数据库连接池
   - 实现结果缓存
   - 优化LLM提示词长度

## 安全考虑

1. **数据库安全**
   - 使用强密码
   - 限制数据库访问IP
   - 定期更新PostgreSQL

2. **API安全**
   - 实现请求频率限制
   - 添加输入验证
   - 使用HTTPS

3. **系统安全**
   - 定期更新系统包
   - 配置防火墙
   - 监控异常访问