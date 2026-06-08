-- =============================================
-- HR_Agent 数据库初始化脚本
-- 使用方法: mysql -u root -p < init.sql
-- 或在 MySQL 客户端中执行: source init.sql
-- =============================================

-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS hr_agent DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE hr_agent;

-- =============================================
-- 1. 用户表
-- =============================================
CREATE TABLE IF NOT EXISTS sys_user (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '用户ID',
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    password VARCHAR(255) NOT NULL COMMENT '加密密码',
    name VARCHAR(50) COMMENT '姓名',
    role VARCHAR(20) DEFAULT 'hr' COMMENT '角色 admin/hr',
    status VARCHAR(20) DEFAULT '1' COMMENT '状态',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- =============================================
-- 2. 部门表
-- =============================================
CREATE TABLE IF NOT EXISTS department (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '部门ID',
    name VARCHAR(100) NOT NULL UNIQUE COMMENT '部门名称',
    description VARCHAR(500) COMMENT '部门描述',
    status SMALLINT DEFAULT 1 COMMENT '状态（1=启用，0=禁用）',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='部门表';

-- =============================================
-- 3. 岗位类别表
-- =============================================
CREATE TABLE IF NOT EXISTS job_category (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '类别ID',
    code VARCHAR(50) NOT NULL UNIQUE COMMENT '类别编码',
    name VARCHAR(100) NOT NULL COMMENT '类别名称',
    description VARCHAR(500) COMMENT '类别描述',
    status INT DEFAULT 1 COMMENT '状态',
    sort_order INT DEFAULT 0 COMMENT '排序',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='岗位类别表';

-- =============================================
-- 4. 岗位表
-- =============================================
CREATE TABLE IF NOT EXISTS job (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '岗位ID',
    name VARCHAR(100) NOT NULL COMMENT '岗位名称',
    job_type VARCHAR(50) COMMENT '岗位类别',
    department VARCHAR(50) COMMENT '部门',
    salary VARCHAR(50) COMMENT '薪资',
    location VARCHAR(100) COMMENT '地点',
    requirements TEXT COMMENT '任职要求',
    responsibilities TEXT COMMENT '岗位职责',
    status VARCHAR(20) DEFAULT 'unpublished' COMMENT '状态',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='岗位表';

-- =============================================
-- 5. 简历表
-- =============================================
CREATE TABLE IF NOT EXISTS resume (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '简历ID',
    file_name VARCHAR(255) NOT NULL COMMENT '文件名',
    file_path VARCHAR(512) NOT NULL COMMENT '路径',
    file_type VARCHAR(20) COMMENT '类型 pdf/doc',
    file_size BIGINT COMMENT '大小',
    parse_status VARCHAR(20) DEFAULT 'pending' COMMENT '解析状态',
    parse_progress BIGINT DEFAULT 0 COMMENT '进度',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='简历表';

-- =============================================
-- 6. 候选人表
-- =============================================
CREATE TABLE IF NOT EXISTS candidate (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '候选人ID',
    resume_id BIGINT NOT NULL COMMENT '简历ID',
    name VARCHAR(50) NOT NULL COMMENT '姓名',
    phone VARCHAR(20) COMMENT '手机号',
    email VARCHAR(100) COMMENT '邮箱',
    gender VARCHAR(10) COMMENT '性别',
    age INT COMMENT '年龄',
    education VARCHAR(50) COMMENT '最高学历',
    candidate_type VARCHAR(20) COMMENT '候选人类型(在校生/应届生/有工作经验)',
    work_years INT COMMENT '工作年限',
    skills JSON COMMENT '技能列表',
    target_position VARCHAR(100) COMMENT '求职意向/目标岗位',
    skill_description TEXT COMMENT '专业技能原始描述',
    professional_skills JSON COMMENT '专业技能详情(languages/frameworks/tools/certificates)',
    self_evaluation TEXT COMMENT '自我评价',
    work_experience JSON COMMENT '工作经历',
    internship_experience JSON COMMENT '实习经历',
    education_history JSON COMMENT '教育经历',
    project_experience JSON COMMENT '项目经历',
    status VARCHAR(20) DEFAULT 'active' COMMENT '状态',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='候选人表';

-- =============================================
-- 7. 人岗匹配任务表
-- =============================================
CREATE TABLE IF NOT EXISTS matching_task (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '任务ID',
    job_id BIGINT NOT NULL COMMENT '岗位ID',
    resume_ids JSON NOT NULL COMMENT '简历ID列表',
    status VARCHAR(20) DEFAULT 'pending' COMMENT '状态',
    progress INT DEFAULT 0 COMMENT '进度',
    total_count INT COMMENT '总数',
    completed_count INT COMMENT '完成数',
    error_message TEXT COMMENT '错误信息',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    completed_at DATETIME COMMENT '完成时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='人岗匹配任务表';

-- =============================================
-- 8. 人岗匹配结果表
-- =============================================
CREATE TABLE IF NOT EXISTS matching_result (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '结果ID',
    task_id BIGINT NOT NULL COMMENT '任务ID',
    job_id BIGINT NOT NULL COMMENT '岗位ID',
    candidate_id BIGINT NOT NULL COMMENT '候选人ID',
    resume_id BIGINT NOT NULL COMMENT '简历ID',
    total_score DECIMAL(5,2) COMMENT '总分',
    skill_score DECIMAL(5,2) COMMENT '技能分',
    experience_score DECIMAL(5,2) COMMENT '经验分',
    education_score DECIMAL(5,2) COMMENT '学历分',
    project_score DECIMAL(5,2) COMMENT '项目分',
    highlights JSON COMMENT '亮点',
    shortcomings JSON COMMENT '短板',
    suggestions JSON COMMENT '建议',
    weight_info JSON COMMENT '权重信息',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='人岗匹配结果表';

-- =============================================
-- 9. 匹配权重配置表
-- =============================================
CREATE TABLE IF NOT EXISTS matching_weight (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '权重ID',
    category_id BIGINT NOT NULL COMMENT '关联类别ID',
    skill_weight DECIMAL(3,2) NOT NULL COMMENT '技能权重',
    experience_weight DECIMAL(3,2) NOT NULL COMMENT '经验权重',
    education_weight DECIMAL(3,2) NOT NULL COMMENT '学历权重',
    project_weight DECIMAL(3,2) NOT NULL COMMENT '项目权重',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (category_id) REFERENCES job_category(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='匹配权重配置表';

-- =============================================
-- 10. AI报告记录表
-- =============================================
CREATE TABLE IF NOT EXISTS ai_report_record (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '报告ID',
    report_type VARCHAR(50) NOT NULL COMMENT '报告类型',
    period VARCHAR(20) COMMENT '周期',
    title VARCHAR(200) NOT NULL COMMENT '标题',
    content TEXT COMMENT '内容',
    new_resumes INT DEFAULT 0 COMMENT '新简历数',
    match_count INT DEFAULT 0 COMMENT '匹配数',
    avg_score DECIMAL(5,2) COMMENT '平均分',
    status INT DEFAULT 1 COMMENT '状态',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='AI报告记录表';

-- =============================================
-- 11. 对话记忆表（长期记忆）
-- =============================================
CREATE TABLE IF NOT EXISTS conversation_memory (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '记忆ID',
    session_id VARCHAR(64) NOT NULL COMMENT '会话ID',
    memory_id VARCHAR(64) NOT NULL UNIQUE COMMENT '唯一标识，用于关联Milvus',
    user_id INT COMMENT '用户ID',
    role VARCHAR(20) NOT NULL COMMENT '角色(user/assistant)',
    content TEXT NOT NULL COMMENT '对话内容',
    keywords JSON COMMENT '关键词列表',
    summary TEXT COMMENT '对话摘要',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    compressed INT DEFAULT 0 COMMENT '是否被压缩（0:否，1:是）',
    parent_id INT COMMENT '父对话ID',
    INDEX idx_session_id (session_id),
    INDEX idx_memory_id (memory_id),
    INDEX idx_created_at (created_at),
    INDEX idx_session_created (session_id, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='对话记忆表';

-- =============================================
-- 12. 会话元信息表
-- =============================================
CREATE TABLE IF NOT EXISTS conversation_session (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '会话ID',
    session_id VARCHAR(64) NOT NULL UNIQUE COMMENT '会话标识',
    user_id INT COMMENT '用户ID',
    title VARCHAR(255) COMMENT '会话标题',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    message_count INT DEFAULT 0 COMMENT '消息数量',
    is_active INT DEFAULT 1 COMMENT '是否活跃',
    INDEX idx_session_id (session_id),
    INDEX idx_user_active (user_id, is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='会话元信息表';

-- =============================================
-- 13. 对话指标表（监控）
-- =============================================
CREATE TABLE IF NOT EXISTS conversation_metrics (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '指标ID',
    session_id VARCHAR(64) NOT NULL COMMENT '会话ID',
    conversation_id VARCHAR(64) NOT NULL UNIQUE COMMENT '对话ID',
    
    -- 检索指标
    recall_rate FLOAT COMMENT '召回率',
    retrieved_count INT DEFAULT 0 COMMENT '检索到的文档数',
    relevant_count INT DEFAULT 0 COMMENT '相关文档数',
    
    -- 回答质量指标
    hallucination_rate FLOAT COMMENT '幻觉率',
    accuracy FLOAT COMMENT '准确率',
    user_rating INT COMMENT '用户评分（1-5）',
    
    -- Token使用指标
    input_tokens INT DEFAULT 0 COMMENT '输入Token数',
    output_tokens INT DEFAULT 0 COMMENT '输出Token数',
    cached_tokens INT DEFAULT 0 COMMENT '缓存命中的Token数',
    total_tokens INT DEFAULT 0 COMMENT '总Token数',
    token_hit_rate FLOAT COMMENT 'Token命中率',
    
    -- 元数据
    query_text TEXT COMMENT '用户查询文本',
    response_text TEXT COMMENT 'AI回答文本',
    model_name VARCHAR(100) COMMENT '使用的模型名称',
    retrieval_method VARCHAR(50) COMMENT '检索方法（关键词/语义/混合）',
    
    -- 详细数据
    retrieval_details JSON COMMENT '检索详情',
    response_details JSON COMMENT '回答详情',
    token_details JSON COMMENT 'Token详情',
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_session_id (session_id),
    INDEX idx_conversation_id (conversation_id),
    INDEX idx_created_at (created_at),
    INDEX idx_session_created (session_id, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='对话指标表';

-- =============================================
-- 14. Token使用汇总表
-- =============================================
CREATE TABLE IF NOT EXISTS token_usage_summary (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '汇总ID',
    date VARCHAR(10) NOT NULL COMMENT '日期（YYYY-MM-DD）',
    
    -- Token统计
    total_input_tokens INT DEFAULT 0 COMMENT '总输入Token',
    total_output_tokens INT DEFAULT 0 COMMENT '总输出Token',
    total_cached_tokens INT DEFAULT 0 COMMENT '总缓存Token',
    total_tokens INT DEFAULT 0 COMMENT '总Token数',
    
    -- 对话统计
    total_conversations INT DEFAULT 0 COMMENT '总对话数',
    total_sessions INT DEFAULT 0 COMMENT '总会话数',
    
    -- 成本估算
    estimated_cost FLOAT COMMENT '估算成本',
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_date (date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Token使用汇总表';

-- =============================================
-- 15. 系统指标表
-- =============================================
CREATE TABLE IF NOT EXISTS system_metrics (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '指标ID',
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '时间戳',
    
    -- 性能指标
    avg_response_time FLOAT COMMENT '平均响应时间（秒）',
    p95_response_time FLOAT COMMENT 'P95响应时间',
    p99_response_time FLOAT COMMENT 'P99响应时间',
    
    -- 质量指标
    avg_recall_rate FLOAT COMMENT '平均召回率',
    avg_hallucination_rate FLOAT COMMENT '平均幻觉率',
    avg_accuracy FLOAT COMMENT '平均准确率',
    avg_token_hit_rate FLOAT COMMENT '平均Token命中率',
    
    -- 使用量指标
    total_tokens INT DEFAULT 0 COMMENT '总Token数',
    total_conversations INT DEFAULT 0 COMMENT '总对话数',
    
    -- 错误指标
    error_count INT DEFAULT 0 COMMENT '错误数',
    error_rate FLOAT COMMENT '错误率',
    
    -- 元数据
    time_window VARCHAR(20) COMMENT '时间窗口（hourly/daily/weekly）',
    
    INDEX idx_timestamp (timestamp),
    INDEX idx_timestamp_window (timestamp, time_window)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统指标表';

-- =============================================
-- 16. 用户反馈表
-- =============================================
CREATE TABLE IF NOT EXISTS user_feedback (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '反馈ID',
    conversation_id VARCHAR(64) NOT NULL COMMENT '对话ID',
    session_id VARCHAR(64) NOT NULL COMMENT '会话ID',
    
    -- 反馈内容
    rating INT NOT NULL COMMENT '评分（1-5）',
    feedback_text TEXT COMMENT '反馈文本',
    feedback_type VARCHAR(50) COMMENT '反馈类型（helpful/not_helpful/needs_improvement）',
    
    -- 元数据
    user_id INT COMMENT '用户ID',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    INDEX idx_conversation_id (conversation_id),
    INDEX idx_session_id (session_id),
    INDEX idx_conversation_rating (conversation_id, rating)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户反馈表';

-- =============================================
-- 初始化数据
-- =============================================

-- 默认管理员用户
INSERT INTO sys_user (username, password, name, role, status) VALUES 
('admin', 'e10adc3949ba59abbe56e057f20f883e', '管理员', 'admin', '1')
ON DUPLICATE KEY UPDATE username = username;

-- 默认部门
INSERT INTO department (name, description, status) VALUES 
('开发部', '软件开发部门', 1),
('产品部', '产品设计部门', 1),
('运营部', '运营管理部门', 1)
ON DUPLICATE KEY UPDATE name = name;

-- =============================================
-- 完成
-- =============================================
SELECT '数据库初始化完成！' AS message;
SHOW TABLES;