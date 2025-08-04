# 智能留学选校规划系统

基于海量成功案例和大型语言模型驱动的智能化留学选校规划工具，为用户提供高度个性化、数据驱动、客观精准的院校定位和申请策略建议。

## 🎯 产品特色

- **海量案例数据库**: 基于真实成功案例进行匹配分析
- **AI智能分析**: 使用大型语言模型生成个性化报告
- **多维度匹配**: 院校层次、GPA、专业、语言成绩等多维度相似度计算
- **三档选校策略**: 冲刺、核心、保底院校科学分层
- **实时数据更新**: ETL模块定期更新案例数据

## 🏗️ 系统架构

```
├── backend/                 # 后端服务
│   ├── app/                # FastAPI应用
│   ├── models/             # 数据模型
│   ├── services/           # 业务服务
│   └── utils/              # 工具函数
├── frontend/               # 前端界面
│   ├── index.html         # 主页面
│   └── js/                # JavaScript文件
├── database/               # 数据库相关
│   └── migrations/        # 数据库迁移脚本
├── scripts/                # 脚本文件
│   └── etl_processor.py   # ETL数据处理
├── config/                 # 配置文件
└── requirements.txt        # Python依赖
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd school-selection-system

# 安装Python依赖
pip install -r requirements.txt
```

### 2. 数据库配置

创建 `.env` 文件并配置数据库连接：

```env
# 源数据库配置（只读）
SOURCE_DB_HOST=localhost
SOURCE_DB_PORT=5432
SOURCE_DB_NAME=compassedu_cases
SOURCE_DB_USER=suan
SOURCE_DB_PASSWORD=your_password

# 目标数据库配置（读写）
TARGET_DB_HOST=localhost
TARGET_DB_PORT=5432
TARGET_DB_NAME=processed_cases
TARGET_DB_USER=suan
TARGET_DB_PASSWORD=your_password

# LLM API配置
OPENAI_API_KEY=your_openai_api_key
OPENAI_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-3.5-turbo
```

### 3. 数据库初始化

```bash
# 创建目标数据库
createdb processed_cases

# 运行数据库迁移
psql -d processed_cases -f database/migrations/001_create_cases_table.sql
```

### 4. 数据预处理

```bash
# 运行ETL处理，将原始数据转换为结构化数据
python run_etl.py
```

### 5. 启动服务

```bash
# 启动后端服务
python run_server.py
```

访问 `http://localhost:8000` 使用系统，或访问 `http://localhost:8000/docs` 查看API文档。

## 📊 核心功能

### 1. 智能案例匹配

- **多维度相似度计算**: 基于院校层次、GPA、专业、语言成绩等维度
- **加权评分算法**: 不同维度采用不同权重进行综合评分
- **动态筛选**: 根据申请学位进行硬性筛选，确保案例相关性

### 2. LLM智能分析

- **个性化报告生成**: 基于用户背景和匹配案例生成详细分析
- **优劣势分析**: 客观评估申请者的竞争力和短板
- **选校策略建议**: 提供冲刺、核心、保底三档选校建议
- **提升建议**: 针对性的背景提升建议

### 3. 数据管理

- **ETL数据处理**: 自动化的数据清洗和标准化流程
- **增量更新**: 支持定期更新案例数据
- **数据质量保证**: 多层次的数据验证和清洗机制

## 🔧 API接口

### 主要接口

- `POST /api/v1/school-planning`: 生成选校规划报告
- `GET /api/v1/cases/count`: 获取案例总数
- `GET /api/v1/cases/sample`: 获取样例案例
- `GET /api/v1/config/options`: 获取配置选项

### 请求示例

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

## 📈 系统配置

### 匹配算法权重配置

在 `config/settings.py` 中可以调整匹配算法的权重：

```python
MATCHING_CONFIG = {
    'max_cases': 20,
    'weights': {
        'school_tier': 30,  # 院校层次权重
        'gpa': 25,          # GPA权重
        'major': 20,        # 专业权重
        'language': 15,     # 语言成绩权重
        'gre': 10,          # GRE权重
    }
}
```

## 🔄 数据更新

### 定期ETL更新

建议设置定时任务定期运行ETL处理：

```bash
# 添加到crontab，每天凌晨2点运行
0 2 * * * /path/to/python /path/to/run_etl.py
```

## 🛠️ 开发指南

### 添加新的匹配维度

1. 在 `backend/models/case.py` 中添加新字段
2. 在 `scripts/etl_processor.py` 中添加数据解析逻辑
3. 在 `backend/services/matching_service.py` 中添加相似度计算方法
4. 更新数据库迁移脚本

### 自定义LLM提示词

在 `backend/services/llm_service.py` 的 `build_prompt` 方法中修改提示词模板。

## 📝 注意事项

1. **数据安全**: 源数据库配置为只读，确保原始数据安全
2. **API限制**: 注意LLM API的调用频率和成本控制
3. **性能优化**: 大量案例时建议添加数据库索引
4. **错误处理**: 系统包含完善的错误处理和降级机制

## 🔮 未来规划

- **V1.1**: 优化专业匹配算法，引入词向量技术
- **V1.2**: 前端输入框增加自动补全功能
- **V2.0**: 用户登录系统，保存历史报告
- **V2.1**: 增加更多筛选维度（学费、课程时长等）

## 📞 技术支持

如有问题或建议，请联系开发团队。