-- ============================================
-- HR智能简历解析与人岗匹配Agent系统 - 数据库建表脚本
-- 数据库类型: MySQL 8.0+
-- 存储引擎: InnoDB
-- 字符集: utf8mb4
-- 对应接口版本: 29个接口
-- ============================================

CREATE DATABASE IF NOT EXISTS hr_matching_system DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE hr_matching_system;

-- ============================================
-- 1. 用户表（对应接口: 登录 + 用户管理4个接口）
-- ============================================
CREATE TABLE `sys_user` (
  `id` BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '用户ID',
  `username` VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名（登录账号）',
  `password` VARCHAR(255) NOT NULL COMMENT '加密密码（BCrypt）',
  `name` VARCHAR(50) COMMENT '姓名（显示名称）',
  `role` VARCHAR(20) NOT NULL DEFAULT 'hr' COMMENT '角色（admin/hr）',
  `status` TINYINT DEFAULT 1 COMMENT '状态（1=启用，0=禁用）',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  INDEX `idx_role` (`role`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- ============================================
-- 2. 岗位表（对应接口: 岗位管理4个接口）
-- ============================================
CREATE TABLE `job` (
  `id` BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '岗位ID',
  `name` VARCHAR(100) NOT NULL COMMENT '岗位名称',
  `job_type` VARCHAR(50) COMMENT '岗位类别',
  `department` VARCHAR(50) COMMENT '所属部门',
  `salary` VARCHAR(50) COMMENT '薪资范围',
  `location` VARCHAR(100) COMMENT '工作地点',
  `requirements` TEXT COMMENT '任职要求',
  `responsibilities` TEXT COMMENT '岗位职责',
  `status` VARCHAR(20) DEFAULT 'unpublished' COMMENT '状态（published/unpublished）',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  INDEX `idx_job_type` (`job_type`),
  INDEX `idx_dept` (`department`),
  INDEX `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='岗位表';

-- ============================================
-- 3. 岗位类别权重配置表（对应接口: 系统配置2个接口）
-- ============================================
CREATE TABLE `matching_weight` (
  `id` BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '权重配置ID',
  `job_type` VARCHAR(50) NOT NULL UNIQUE COMMENT '岗位类别',
  `job_type_desc` VARCHAR(100) COMMENT '类别描述',
  `skill_weight` DECIMAL(3,2) NOT NULL COMMENT '技能权重（0-1）',
  `experience_weight` DECIMAL(3,2) NOT NULL COMMENT '经验权重（0-1）',
  `education_weight` DECIMAL(3,2) NOT NULL COMMENT '学历权重（0-1）',
  `project_weight` DECIMAL(3,2) NOT NULL COMMENT '项目权重（0-1）',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  INDEX `idx_job_type` (`job_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='岗位类别权重配置表';

-- ============================================
-- 4. 简历主表（对应接口: 简历管理3个接口）
-- ============================================
CREATE TABLE `resume` (
  `id` BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '简历ID',
  `file_name` VARCHAR(255) NOT NULL COMMENT '文件名',
  `file_path` VARCHAR(512) NOT NULL COMMENT '文件存储路径',
  `file_type` VARCHAR(20) COMMENT '文件类型（pdf/doc/docx/txt）',
  `file_size` BIGINT COMMENT '文件大小（字节）',
  `parse_status` VARCHAR(20) DEFAULT 'pending' COMMENT '解析状态（pending/processing/success/fail）',
  `parse_progress` INT DEFAULT 0 COMMENT '解析进度（0-100）',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '上传时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  INDEX `idx_parse` (`parse_status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='简历主表';

-- ============================================
-- 5. 候选人表（简历解析后生成，AI模块和匹配模块共用）
-- ============================================
CREATE TABLE `candidate` (
  `id` BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '候选人ID',
  `resume_id` BIGINT NOT NULL COMMENT '关联简历ID',
  `name` VARCHAR(50) NOT NULL COMMENT '候选人姓名',
  `phone` VARCHAR(20) COMMENT '手机号',
  `email` VARCHAR(100) COMMENT '邮箱',
  `gender` VARCHAR(10) COMMENT '性别',
  `age` INT COMMENT '年龄',
  `education` VARCHAR(50) COMMENT '最高学历',
  `work_years` INT COMMENT '工作年限',
  `skills` JSON COMMENT '技能列表',
  `self_evaluation` TEXT COMMENT '自我评价',
  `work_experience` JSON COMMENT '工作经历',
  `education_history` JSON COMMENT '教育经历',
  `project_experience` JSON COMMENT '项目经历',
  `status` VARCHAR(20) DEFAULT 'active' COMMENT '状态（active/archived）',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  INDEX `idx_resume` (`resume_id`),
  INDEX `idx_name` (`name`),
  INDEX `idx_education` (`education`),
  INDEX `idx_work_years` (`work_years`),
  INDEX `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='候选人表';

-- ============================================
-- 6. 人岗匹配任务表（对应接口: POST /matching/run）
-- ============================================
CREATE TABLE `matching_task` (
  `id` BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '任务ID',
  `job_id` BIGINT NOT NULL COMMENT '岗位ID',
  `resume_ids` JSON NOT NULL COMMENT '简历ID列表',
  `status` VARCHAR(20) DEFAULT 'pending' COMMENT '状态（pending/processing/completed/failed）',
  `progress` INT DEFAULT 0 COMMENT '进度（0-100）',
  `total_count` INT COMMENT '总匹配数',
  `completed_count` INT COMMENT '已完成数',
  `error_message` TEXT COMMENT '错误信息',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `completed_at` DATETIME COMMENT '完成时间',
  INDEX `idx_job` (`job_id`),
  INDEX `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='人岗匹配任务表';

-- ============================================
-- 7. 人岗匹配结果表（对应接口: GET /matching/resultList, /matching/report/{id}）
-- ============================================
CREATE TABLE `matching_result` (
  `id` BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '结果ID',
  `task_id` BIGINT NOT NULL COMMENT '任务ID',
  `job_id` BIGINT NOT NULL COMMENT '岗位ID',
  `candidate_id` BIGINT NOT NULL COMMENT '候选人ID',
  `resume_id` BIGINT NOT NULL COMMENT '简历ID',
  `total_score` DECIMAL(5,2) COMMENT '总分（0-100）',
  `skill_score` DECIMAL(5,2) COMMENT '技能得分',
  `experience_score` DECIMAL(5,2) COMMENT '经验得分',
  `education_score` DECIMAL(5,2) COMMENT '学历得分',
  `project_score` DECIMAL(5,2) COMMENT '项目得分',
  `highlights` JSON COMMENT '匹配亮点',
  `shortcomings` JSON COMMENT '匹配短板',
  `suggestions` JSON COMMENT '匹配建议',
  `weight_info` JSON COMMENT '权重信息',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  INDEX `idx_task` (`task_id`),
  INDEX `idx_job` (`job_id`),
  INDEX `idx_candidate` (`candidate_id`),
  INDEX `idx_resume` (`resume_id`),
  INDEX `idx_total_score` (`total_score`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='人岗匹配结果表';

-- ============================================
-- 8. AI报告记录表（对应接口: POST /ai/report-generate）
-- ============================================
CREATE TABLE `ai_report_record` (
  `id` BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '报告ID',
  `report_type` VARCHAR(50) NOT NULL COMMENT '报告类型（weekly/monthly/jobAnalysis/candidateAnalysis）',
  `period` VARCHAR(20) COMMENT '报告周期',
  `title` VARCHAR(200) NOT NULL COMMENT '报告标题',
  `content` TEXT COMMENT '报告内容（HTML）',
  `new_resumes` INT DEFAULT 0 COMMENT '新增简历数',
  `match_count` INT DEFAULT 0 COMMENT '匹配次数',
  `avg_score` DECIMAL(5,2) COMMENT '平均匹配分',
  `status` TINYINT DEFAULT 1 COMMENT '状态（1=已完成，0=生成中，-1=失败）',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  INDEX `idx_report_type` (`report_type`),
  INDEX `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='AI报告记录表';

-- ============================================
-- 初始化数据
-- ============================================

-- 默认管理员账号（密码: admin123，BCrypt加密）
INSERT INTO `sys_user` (`username`, `password`, `name`, `role`, `status`)
VALUES ('admin', '$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iAt6Z5EH', '系统管理员', 'admin', 1);

-- 默认岗位类别权重
INSERT INTO `matching_weight` (`job_type`, `job_type_desc`, `skill_weight`, `experience_weight`, `education_weight`, `project_weight`) VALUES
('技术研发', '技术研发类岗位', 0.40, 0.30, 0.15, 0.15),
('产品设计', '产品设计类岗位', 0.30, 0.30, 0.20, 0.20),
('市场营销', '市场营销类岗位', 0.25, 0.35, 0.20, 0.20),
('人力资源', '人力资源类岗位', 0.20, 0.40, 0.25, 0.15),
('财务管理', '财务管理类岗位', 0.30, 0.30, 0.25, 0.15),
('行政管理', '行政管理类岗位', 0.20, 0.35, 0.30, 0.15);
