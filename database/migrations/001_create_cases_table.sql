-- 创建 processed_cases 数据库的 cases 表
-- 用于存储预处理后的结构化案例数据

CREATE TABLE IF NOT EXISTS cases (
    id SERIAL PRIMARY KEY,
    original_id INTEGER NOT NULL,
    university VARCHAR(255) NOT NULL,
    program VARCHAR(255) NOT NULL,
    degree_level VARCHAR(50) NOT NULL,
    undergrad_school VARCHAR(255),
    undergrad_school_tier VARCHAR(50),
    undergrad_major VARCHAR(255),
    gpa_original VARCHAR(50),
    gpa_scale_4 NUMERIC(4, 2),
    gpa_scale_100 NUMERIC(5, 2),
    language_type VARCHAR(20),
    language_score NUMERIC(3, 1),
    gre_score INTEGER,
    work_experience VARCHAR(100),
    graduation_year INTEGER,
    original_url TEXT,
    original_title TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_cases_degree_level ON cases(degree_level);
CREATE INDEX IF NOT EXISTS idx_cases_school_tier ON cases(undergrad_school_tier);
CREATE INDEX IF NOT EXISTS idx_cases_gpa_4 ON cases(gpa_scale_4);
CREATE INDEX IF NOT EXISTS idx_cases_language_score ON cases(language_score);
CREATE INDEX IF NOT EXISTS idx_cases_original_id ON cases(original_id);

-- 创建更新时间触发器
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_cases_updated_at 
    BEFORE UPDATE ON cases 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();