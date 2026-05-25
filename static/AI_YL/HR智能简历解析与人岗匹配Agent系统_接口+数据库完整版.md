# HR智能简历解析与人岗匹配Agent系统\_接口\+数据库完整版

# 一、项目概述

本项目为企业级HR招聘智能辅助系统，采用 **Java \+ Python 微服务架构**，实现简历上传、AI解析、人岗智能匹配、候选人管理等全流程功能，适配企业HR招聘场景，支持管理员与HR双角色权限管控，可直接用于毕业设计、前后端开发、答辩展示。

- Java端：负责业务逻辑、权限管理、数据库操作、流程控制、文件存储

- Python端：负责AI简历解析、人岗匹配算法、大模型推理、结构化信息抽取

- 前端：后台管理系统（深色高级商务风、粒子特效、玻璃拟态，贴合HR岗位属性）

# 二、API接口文档（最终完整版）

## 2\.1 基础信息

- 基础URL：`/hr/api/v1`

- 认证方式：`Bearer Token \(JWT\)`（登录后获取，所有需权限接口必带）

- 请求格式：`application/json`（普通接口）/ `multipart/form\-data`（文件上传接口）

- 响应格式：统一JSON格式（所有接口均遵循）

- 分页统一参数：`page`（页码，默认1）、`pageSize`（每页条数，默认10）

## 2\.2 通用响应格式

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

## 2\.3 错误码规范

- 200：操作成功

- 400：参数错误（请求参数缺失、格式错误）

- 401：未登录/Token过期/Token无效

- 403：无操作权限（如HR操作管理员功能）

- 404：资源不存在（如查询不存在的岗位、简历）

- 500：服务端异常（后端程序、数据库、Python AI服务异常）

- 1001：简历解析中（异步解析未完成）

- 1002：简历解析失败（文件损坏、格式不支持、AI解析异常）

## 2\.4 接口模块详情

### 2\.4\.1 认证模块（Auth）

- **登录接口**

    - 请求方式：POST

    - 接口路径：`/auth/login`

    - 请求参数：`username`（字符串，必填，账号）、`password`（字符串，必填，密码）

    - 响应数据：`token`（字符串，登录凭证）、`userInfo`（对象，用户基本信息：id、username、realName、role、phone）

- **获取当前用户信息**

    - 请求方式：GET

    - 接口路径：`/auth/userInfo`

    - 请求头：`Authorization: Bearer \{token\}`

    - 响应数据：用户基本信息（id、username、realName、role、phone、email、status）

- **修改密码**

    - 请求方式：POST

    - 接口路径：`/auth/changePassword`

    - 请求头：`Authorization: Bearer \{token\}`

    - 请求参数：`oldPassword`（字符串，必填，原密码）、`newPassword`（字符串，必填，新密码）

    - 响应数据：无额外业务数据，返回通用成功响应

### 2\.4\.2 岗位管理模块（Job）

- **岗位列表查询**

    - 请求方式：GET

    - 接口路径：`/job/list`

    - 请求头：`Authorization: Bearer \{token\}`

    - 请求参数：`page`、`pageSize`、`keyword`（可选，岗位名称关键词）、`department`（可选，部门）、`status`（可选，状态：published/unpublished）、`jobType`（可选，岗位类别）

    - 响应数据：分页列表（list：岗位信息列表，total：总条数，page：当前页码，pageSize：每页条数，每条包含jobType岗位类别、jobTypeDesc类别描述）

- **岗位详情查询**

    - 请求方式：GET

    - 接口路径：`/job/detail/\{id\}`

    - 请求头：`Authorization: Bearer \{token\}`

    - 路径参数：`id`（必填，岗位ID）

    - 响应数据：岗位完整信息（id、name、department、salary、location、requirements、responsibilities、status、jobType、jobTypeDesc、createdBy、createdAt等）

- **新增岗位**

    - 请求方式：POST

    - 接口路径：`/job/add`

    - 请求头：`Authorization: Bearer \{token\}`

    - 请求参数：`name`（必填，岗位名称）、`jobType`（必填，岗位类别）、`department`（可选，部门）、`salary`（可选，薪资范围）、`location`（可选，工作地点）、`requirements`（必填，任职要求）、`responsibilities`（必填，岗位职责）

    - 响应数据：新增岗位ID

- **编辑岗位**

    - 请求方式：PUT

    - 接口路径：`/job/update/\{id\}`

    - 请求头：`Authorization: Bearer \{token\}`

    - 路径参数：`id`（必填，岗位ID）

    - 请求参数：同新增岗位（可部分修改，包含jobType）

    - 响应数据：无额外业务数据，返回通用成功响应

- **删除岗位**

    - 请求方式：DELETE

    - 接口路径：`/job/delete/\{id\}`

    - 请求头：`Authorization: Bearer \{token\}`

    - 路径参数：`id`（必填，岗位ID）

    - 响应数据：无额外业务数据，返回通用成功响应

- **岗位上下架**

    - 请求方式：PUT

    - 接口路径：`/job/changeStatus`

    - 请求头：`Authorization: Bearer \{token\}`

    - 请求参数：`id`（必填，岗位ID）、`status`（必填，状态：published=上架，unpublished=下架）

    - 响应数据：无额外业务数据，返回通用成功响应

### 2\.4\.3 简历管理模块（Resume）

- **单文件上传**

    - 请求方式：POST

    - 接口路径：`/resume/upload`

    - 请求头：`Authorization: Bearer \{token\}`

    - 请求格式：multipart/form\-data

    - 请求参数：`file`（必填，文件，支持PDF/Word/TXT，单个文件≤20MB）

    - 响应数据：简历ID、文件名、文件路径、解析状态（默认pending）

- **批量上传**

    - 请求方式：POST

    - 接口路径：`/resume/batchUpload`

    - 请求头：`Authorization: Bearer \{token\}`

    - 请求格式：multipart/form\-data

    - 请求参数：`files`（必填，多文件，支持PDF/Word/TXT，单次≤100个，单个文件≤20MB）

    - 响应数据：上传成功的简历列表（包含简历ID、文件名、解析状态）

- **简历列表查询**

    - 请求方式：GET

    - 接口路径：`/resume/list`

    - 请求头：`Authorization: Bearer \{token\}`

    - 请求参数：`page`、`pageSize`、`keyword`（可选，文件名/候选人姓名）、`parseStatus`（可选，解析状态：pending/processing/success/fail）

    - 响应数据：分页列表（list：简历信息列表，total：总条数，page：当前页码，pageSize：每页条数）

- **简历详情查询**

    - 请求方式：GET

    - 接口路径：`/resume/detail/\{id\}`

    - 请求头：`Authorization: Bearer \{token\}`

    - 路径参数：`id`（必填，简历ID）

    - 响应数据：简历完整信息（id、fileName、filePath、fileType、parseStatus、parseProgress、uploadedBy、uploadedAt等）

- **获取解析状态**

    - 请求方式：GET

    - 接口路径：`/resume/parseStatus/\{id\}`

    - 请求头：`Authorization: Bearer \{token\}`

    - 路径参数：`id`（必填，简历ID）

    - 响应数据：`parseStatus`（解析状态）、`parseProgress`（解析进度，0\-100）、`parseResultId`（解析结果ID，解析成功时返回）

- **重新解析简历**

    - 请求方式：POST

    - 接口路径：`/resume/reparse/\{id\}`

    - 请求头：`Authorization: Bearer \{token\}`

    - 路径参数：`id`（必填，简历ID，仅解析失败的简历可重新解析）

    - 响应数据：无额外业务数据，返回通用成功响应（解析状态重置为processing）

- **删除简历**

    - 请求方式：DELETE

    - 接口路径：`/resume/delete/\{id\}`

    - 请求头：`Authorization: Bearer \{token\}`

    - 路径参数：`id`（必填，简历ID）

    - 响应数据：无额外业务数据，返回通用成功响应（同时删除关联的解析结果、候选人信息）

### 2\.4\.4 候选人管理模块（Candidate）

- **候选人列表查询**

    - 请求方式：GET

    - 接口路径：`/candidate/list`

    - 请求头：`Authorization: Bearer \{token\}`

    - 请求参数：`page`、`pageSize`、`name`（可选，候选人姓名）、`skill`（可选，技能关键词）、`education`（可选，学历）、`workYears`（可选，工作年限）

    - 响应数据：分页列表（list：候选人信息列表，total：总条数，page：当前页码，pageSize：每页条数）

- **候选人详情查询**

    - 请求方式：GET

    - 接口路径：`/candidate/detail/\{id\}`

    - 请求头：`Authorization: Bearer \{token\}`

    - 路径参数：`id`（必填，候选人ID）

    - 响应数据：候选人完整信息（基础信息、教育背景、工作经历、技能、项目经历、关联简历ID、标签等）

- **添加候选人标签**

    - 请求方式：POST

    - 接口路径：`/candidate/addTag`

    - 请求头：`Authorization: Bearer \{token\}`

    - 请求参数：`candidateId`（必填，候选人ID）、`tag`（必填，标签内容，如“Java开发”“应届生”）

    - 响应数据：无额外业务数据，返回通用成功响应

- **批量导出候选人**

    - 请求方式：POST

    - 接口路径：`/candidate/export`

    - 请求头：`Authorization: Bearer \{token\}`

    - 请求参数：`candidateIds`（可选，数组，指定候选人ID；不填则导出当前筛选条件下所有候选人）

    - 响应数据：blob文件（Excel格式，包含候选人所有结构化信息）

### 2\.4\.5 岗位类别及权重管理模块（Weight，仅管理员）

- **获取所有岗位类别及权重**

    - 请求方式：GET

    - 接口路径：`/matching/weight/list`

    - 请求头：`Authorization: Bearer \{token\}`（仅管理员可调用）

    - 响应数据：岗位类别及权重列表（id、jobType、jobTypeDesc、skillWeight、experienceWeight、educationWeight、projectWeight）

- **根据岗位类别查询权重**

    - 请求方式：GET

    - 接口路径：`/matching/weight/getByJobType`

    - 请求头：`Authorization: Bearer \{token\}`

    - 请求参数：`jobType`（必填，岗位类别）

    - 响应数据：该岗位类别的权重配置

- **新增岗位类别及权重**

    - 请求方式：POST

    - 接口路径：`/matching/weight/add`

    - 请求头：`Authorization: Bearer \{token\}`（仅管理员可调用）

    - 请求参数：`jobType`（必填，岗位类别，不可重复）、`jobTypeDesc`（可选，类别描述）、`skillWeight`（必填，0\-1）、`experienceWeight`（必填，0\-1）、`educationWeight`（必填，0\-1）、`projectWeight`（必填，0\-1），四个权重之和为1

    - 响应数据：新增岗位类别及权重ID

- **编辑岗位类别及权重**

    - 请求方式：PUT

    - 接口路径：`/matching/weight/update/\{id\}`

    - 请求头：`Authorization: Bearer \{token\}`（仅管理员可调用）

    - 路径参数：`id`（必填，权重配置ID）

    - 请求参数：同新增接口（可部分修改，权重仍需校验和为1）

    - 响应数据：无额外业务数据，返回通用成功响应

- **删除岗位类别及权重**

    - 请求方式：DELETE

    - 接口路径：`/matching/weight/delete/\{id\}`

    - 请求头：`Authorization: Bearer \{token\}`（仅管理员可调用）

    - 路径参数：`id`（必填，权重配置ID）

    - 响应数据：无额外业务数据，返回通用成功响应

    - 校验规则：若该岗位类别已被岗位关联，禁止删除，返回400错误提示"该类别已关联岗位，无法删除"

### 2\.4\.6 人岗匹配模块（Matching）

- **执行人人岗匹配**

    - 请求方式：POST

    - 接口路径：`/matching/run`

    - 请求头：`Authorization: Bearer \{token\}`

    - 请求参数：`jobId`（必填，岗位ID）、`resumeIds`（必填，数组，简历ID列表，单次≤100个）

    - 响应数据：匹配任务ID（用于查询匹配进度和结果）

    - 说明：接口内部根据jobId查询该岗位的jobType，再根据jobType调取对应权重计算匹配分数，无需前端传入权重

- **匹配结果列表**

    - 请求方式：GET

    - 接口路径：`/matching/resultList`

    - 请求头：`Authorization: Bearer \{token\}`

    - 请求参数：`jobId`（必填，岗位ID）、`page`、`pageSize`

    - 响应数据：分页列表（包含候选人信息、匹配总分、各维度得分、匹配亮点/短板）

- **匹配详情报告**

    - 请求方式：GET

    - 接口路径：`/matching/report/\{id\}`

    - 请求头：`Authorization: Bearer \{token\}`

    - 路径参数：`id`（必填，匹配结果ID）

    - 响应数据：完整匹配报告（岗位需求、候选人信息、各维度匹配详情、得分计算逻辑、匹配建议、weightInfo：包含岗位类别、各维度权重）

- **导出匹配报告**

    - 请求方式：GET

    - 接口路径：`/matching/export/\{id\}`

    - 请求头：`Authorization: Bearer \{token\}`

    - 路径参数：`id`（必填，匹配任务ID）

    - 响应数据：blob文件（Excel格式，包含该岗位下所有候选人的匹配详情、得分、亮点/短板）

### 2\.4\.7 数据统计模块（Statistics）

- **概览统计**

    - 请求方式：GET

    - 接口路径：`/statistics/overview`

    - 请求头：`Authorization: Bearer \{token\}`

    - 请求参数：`period`（必填，统计周期：day=今日，week=本周，month=本月）

    - 响应数据：核心统计数据（简历上传数、解析成功数、匹配任务数、优质候选人数、岗位数）

- **简历上传趋势**

    - 请求方式：GET

    - 接口路径：`/statistics/resumeUpload`

    - 请求头：`Authorization: Bearer \{token\}`

    - 响应数据：近7天简历上传数量趋势（x轴：日期，y轴：上传数量）

- **解析成功率**

    - 请求方式：GET

    - 接口路径：`/statistics/parseRate`

    - 请求头：`Authorization: Bearer \{token\}`

    - 响应数据：解析成功率、解析成功数、解析失败数、解析中数

- **匹配分数分布**

    - 请求方式：GET

    - 接口路径：`/statistics/matchScore`

    - 请求头：`Authorization: Bearer \{token\}`

    - 响应数据：匹配分数分布统计（如80\-100分、60\-80分、60分以下的候选人数量）

### 2\.4\.7 管理员模块（Admin）

- **HR账号列表**

    - 请求方式：GET

    - 接口路径：`/admin/userList`

    - 请求头：`Authorization: Bearer \{token\}`（仅管理员可调用）

    - 请求参数：`page`、`pageSize`、`keyword`（可选，账号/姓名关键词）

    - 响应数据：分页列表（HR账号信息，包含id、username、realName、phone、status等）

- **新增HR账号**

    - 请求方式：POST

    - 接口路径：`/admin/addUser`

    - 请求头：`Authorization: Bearer \{token\}`（仅管理员可调用）

    - 请求参数：`username`（必填，账号）、`password`（必填，初始密码）、`realName`（可选，真实姓名）、`phone`（可选，手机号）、`email`（可选，邮箱）

    - 响应数据：新增HR账号ID

- **启用/禁用HR账号**

    - 请求方式：PUT

    - 接口路径：`/admin/changeStatus`

    - 请求头：`Authorization: Bearer \{token\}`（仅管理员可调用）

    - 请求参数：`id`（必填，HR账号ID）、`status`（必填，状态：1=启用，0=禁用）

    - 响应数据：无额外业务数据，返回通用成功响应

- **系统监控**

    - 请求方式：GET

    - 接口路径：`/admin/monitor`

    - 请求头：`Authorization: Bearer \{token\}`（仅管理员可调用）

    - 响应数据：系统运行状态（Java服务、Python AI服务状态）、CPU使用率、内存使用率、接口平均耗时、最近接口调用记录

# 三、数据库设计文档（最终完整版）

## 3\.1 数据库基础配置

- 数据库类型：MySQL 8\.0\+

- 存储引擎：InnoDB（支持事务、外键，适配业务场景）

- 字符集：utf8mb4（支持中文、特殊字符，避免乱码）

- 排序规则：utf8mb4\_unicode\_ci（统一排序，适配多语言）

- 设计原则：遵循第三范式（3NF），避免字段冗余；高频查询场景适度反范式，提升查询效率；所有表均支持软删除，便于数据回溯。

## 3\.2 核心数据表设计（含SQL建表语句）

### 3\.2\.1 sys\_user（用户表：存储HR、管理员账号信息）

```sql
CREATE TABLE sys_user (
  id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '用户ID（自增主键）',
  username VARCHAR(50) NOT NULL UNIQUE COMMENT '登录账号',
  password VARCHAR(255) NOT NULL COMMENT '加密密码（BCrypt加密）',
  real_name VARCHAR(50) COMMENT '真实姓名',
  phone VARCHAR(20) COMMENT '手机号',
  email VARCHAR(100) COMMENT '邮箱',
  role VARCHAR(20) NOT NULL DEFAULT 'hr' COMMENT '角色（admin=管理员，hr=普通HR）',
  status TINYINT DEFAULT 1 COMMENT '状态（1=启用，0=禁用）',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  deleted_at DATETIME NULL COMMENT '删除时间（软删除，NULL=未删除）',
  INDEX idx_role (role) COMMENT '角色索引，提升查询效率',
  INDEX idx_status (status) COMMENT '状态索引，提升查询效率'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表（HR/管理员）';
```

### 3\.2\.2 job（岗位表：存储岗位基本信息）

```sql
CREATE TABLE job (
  id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '岗位ID（自增主键）',
  name VARCHAR(100) NOT NULL COMMENT '岗位名称',
  job_type VARCHAR(50) COMMENT '岗位类别（关联matching_weight表的job_type）',
  department VARCHAR(50) COMMENT '所属部门',
  salary VARCHAR(50) COMMENT '薪资范围（如5k-10k）',
  location VARCHAR(100) COMMENT '工作地点',
  requirements TEXT COMMENT '任职要求（富文本）',
  responsibilities TEXT COMMENT '岗位职责（富文本）',
  status VARCHAR(20) DEFAULT 'unpublished' COMMENT '状态（published=上架，unpublished=下架）',
  created_by BIGINT COMMENT '创建人ID（关联sys_user表id）',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  deleted_at DATETIME NULL COMMENT '删除时间（软删除）',
  INDEX idx_job_type (job_type) COMMENT '岗位类别索引，提升关联查询效率',
  INDEX idx_dept (department) COMMENT '部门索引，提升查询效率',
  INDEX idx_status (status) COMMENT '状态索引，提升查询效率'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='岗位表';
```

### 3\.2\.3 resume（简历主表：存储简历上传基础信息）

```sql
CREATE TABLE resume (
  id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '简历ID（自增主键）',
  file_name VARCHAR(255) NOT NULL COMMENT '简历文件名',
  file_path VARCHAR(512) NOT NULL COMMENT '简历文件存储路径（MinIO存储）',
  file_type VARCHAR(20) COMMENT '文件类型（pdf/word/txt）',
  file_size BIGINT COMMENT '文件大小（字节）',
  parse_status VARCHAR(20) DEFAULT 'pending' COMMENT '解析状态（pending=未解析，processing=解析中，success=成功，fail=失败）',
  parse_progress INT DEFAULT 0 COMMENT '解析进度（0-100）',
  uploaded_by BIGINT COMMENT '上传人ID（关联sys_user表id）',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '上传时间',
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  deleted_at DATETIME NULL COMMENT '删除时间（软删除）',
  INDEX idx_parse (parse_status) COMMENT '解析状态索引，提升查询效率',
  INDEX idx_upload (uploaded_by) COMMENT '上传人索引，提升查询效率'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='简历主表';
```

### 3\.2\.4 resume\_parse\_result（简历解析结果表：存储简历结构化信息）

```sql
CREATE TABLE resume_parse_result (
  id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '解析结果ID（自增主键）',
  resume_id BIGINT NOT NULL UNIQUE COMMENT '关联简历ID（关联resume表id）',
  name VARCHAR(50) COMMENT '候选人姓名',
  phone VARCHAR(20) COMMENT '候选人手机号',
  email VARCHAR(100) COMMENT '候选人邮箱',
  gender VARCHAR(10) COMMENT '性别（男/女/未知）',
  age INT COMMENT '年龄',
  education VARCHAR(50) COMMENT '学历（本科/硕士/博士等）',
  university VARCHAR(100) COMMENT '毕业院校',
  major VARCHAR(100) COMMENT '所学专业',
  work_years VARCHAR(20) COMMENT '工作年限（如1-3年、3-5年）',
  skills JSON COMMENT '技能列表（JSON格式，如["Java","MySQL"]）',
  work_experience JSON COMMENT '工作经历（JSON格式，包含公司、岗位、工作时间、核心职责）',
  education_history JSON COMMENT '教育经历（JSON格式，包含院校、专业、毕业时间）',
  projects JSON COMMENT '项目经历（JSON格式，包含项目名称、职责、成果）',
  parsed_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '解析完成时间',
  INDEX idx_resume (resume_id) COMMENT '关联简历ID索引，提升查询效率'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='简历解析结果表';
```

### 3\.2\.5 candidate（候选人表：存储解析后的候选人核心信息）

```sql
CREATE TABLE candidate (
  id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '候选人ID（自增主键）',
  resume_id BIGINT NOT NULL UNIQUE COMMENT '关联简历ID（关联resume表id）',
  name VARCHAR(50) COMMENT '候选人姓名',
  phone VARCHAR(20) COMMENT '候选人手机号',
  education VARCHAR(50) COMMENT '学历',
  work_years VARCHAR(20) COMMENT '工作年限',
  skills JSON COMMENT '技能列表（JSON格式）',
  status VARCHAR(30) DEFAULT 'new' COMMENT '候选人状态（new=新入库，interview=待面试，reject=已拒绝，offer=已发offer）',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '入库时间',
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  INDEX idx_edu (education) COMMENT '学历索引，提升查询效率',
  INDEX idx_status (status) COMMENT '状态索引，提升查询效率'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='候选人表';
```

### 3\.2\.6 candidate\_tag（候选人标签表：存储候选人标签信息）

```sql
CREATE TABLE candidate_tag (
  id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '标签ID（自增主键）',
  candidate_id BIGINT NOT NULL COMMENT '关联候选人ID（关联candidate表id）',
  tag VARCHAR(50) NOT NULL COMMENT '标签内容（如“Java开发”“应届生”“大厂经验”）',
  created_by BIGINT COMMENT '创建人ID（关联sys_user表id）',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  INDEX idx_candidate (candidate_id) COMMENT '关联候选人ID索引，提升查询效率',
  INDEX idx_tag (tag) COMMENT '标签索引，提升查询效率'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='候选人标签表';
```

### 3\.2\.7 matching\_task（匹配任务表：存储人岗匹配任务信息）

```sql
CREATE TABLE matching_task (
  id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '匹配任务ID（自增主键）',
  job_id BIGINT NOT NULL COMMENT '关联岗位ID（关联job表id）',
  status VARCHAR(30) DEFAULT 'pending' COMMENT '任务状态（pending=待执行，processing=执行中，completed=已完成，fail=执行失败）',
  total INT DEFAULT 0 COMMENT '待匹配简历总数',
  processed INT DEFAULT 0 COMMENT '已匹配简历数',
  progress INT DEFAULT 0 COMMENT '匹配进度（0-100）',
  created_by BIGINT COMMENT '创建人ID（关联sys_user表id）',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  completed_at DATETIME NULL COMMENT '完成时间',
  INDEX idx_job (job_id) COMMENT '关联岗位ID索引，提升查询效率',
  INDEX idx_status (status) COMMENT '任务状态索引，提升查询效率'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='匹配任务表';
```

### 3\.2\.8 matching\_result（匹配结果表：存储人岗匹配详细结果）

```sql
CREATE TABLE matching_result (
  id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '匹配结果ID（自增主键）',
  task_id BIGINT COMMENT '关联匹配任务ID（关联matching_task表id）',
  job_id BIGINT COMMENT '关联岗位ID（关联job表id）',
  candidate_id BIGINT COMMENT '关联候选人ID（关联candidate表id）',
  total_score DECIMAL(5,2) COMMENT '匹配总分（0-100分）',
  skill_score DECIMAL(5,2) COMMENT '技能匹配分（0-100分）',
  experience_score DECIMAL(5,2) COMMENT '经验匹配分（0-100分）',
  education_score DECIMAL(5,2) COMMENT '学历匹配分（0-100分）',
  project_score DECIMAL(5,2) COMMENT '项目匹配分（0-100分）',
  highlights JSON COMMENT '匹配亮点（JSON格式，如["技能完全匹配","有相关项目经验"]）',
  weaknesses JSON COMMENT '匹配短板（JSON格式，如["工作年限不足","学历未达标"]）',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '匹配时间',
  INDEX idx_task (task_id) COMMENT '关联任务ID索引，提升查询效率',
  INDEX idx_job (job_id) COMMENT '关联岗位ID索引，提升查询效率',
  INDEX idx_candidate (candidate_id) COMMENT '关联候选人ID索引，提升查询效率',
  INDEX idx_score (total_score) COMMENT '匹配总分索引，便于按分数排序查询'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='匹配结果表';
```

### 3\.2\.9 matching\_weight（匹配权重表：按岗位类别区分权重配置）

```sql
CREATE TABLE matching_weight (
  id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '权重ID（自增主键）',
  job_type VARCHAR(50) NOT NULL UNIQUE COMMENT '岗位类别（如"technical"技术岗、"management"管理岗）',
  job_type_desc VARCHAR(200) COMMENT '岗位类别描述（说明该类岗位权重侧重）',
  skill_weight DECIMAL(3,2) NOT NULL COMMENT '技能权重（0-1，保留2位小数）',
  experience_weight DECIMAL(3,2) NOT NULL COMMENT '经验权重（0-1，保留2位小数）',
  education_weight DECIMAL(3,2) NOT NULL COMMENT '学历权重（0-1，保留2位小数）',
  project_weight DECIMAL(3,2) NOT NULL COMMENT '项目权重（0-1，保留2位小数）',
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  INDEX idx_job_type (job_type) COMMENT '岗位类别索引，提升查询效率'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='匹配权重表（按岗位类别区分）';
```

### 3\.2\.10 operation\_log（操作日志表：存储用户操作记录，用于审计）

```sql
CREATE TABLE operation_log (
  id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '日志ID（自增主键）',
  user_id BIGINT COMMENT '操作用户ID（关联sys_user表id）',
  module VARCHAR(50) COMMENT '操作模块（如auth、job、resume）',
  action VARCHAR(100) COMMENT '操作动作（如login、addJob、uploadResume）',
  ip VARCHAR(50) COMMENT '操作IP地址',
  result TINYINT DEFAULT 1 COMMENT '操作结果（1=成功，0=失败）',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
  INDEX idx_user (user_id) COMMENT '操作用户索引，提升查询效率',
  INDEX idx_module (module) COMMENT '操作模块索引，提升查询效率'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='操作日志表';
```

## 3\.3 初始化SQL（直接运行，快速搭建基础数据）

```sql
-- 初始化管理员账号：账号admin，密码admin123（BCrypt加密）
INSERT INTO sys_user (username, password, real_name, role, status)
VALUES ('admin','$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy','系统管理员','admin',1);

-- 初始化岗位类别及对应权重（适配通用HR招聘场景）
INSERT INTO matching_weight (job_type, job_type_desc, skill_weight, experience_weight, education_weight, project_weight)
VALUES 
('technical', '技术岗：侧重技能和项目经验，学历要求适中', 0.50, 0.30, 0.10, 0.10),
('management', '管理岗：侧重工作经验和综合能力，技能要求适中', 0.20, 0.40, 0.20, 0.20),
('operation', '运营岗：侧重项目运营经验和执行能力，技能要求灵活', 0.30, 0.20, 0.10, 0.40),
('administrative', '行政岗：侧重基础能力和稳定性，学历和经验均衡', 0.10, 0.20, 0.30, 0.40);
```

## 3\.4 数据库优化建议

- **关联约束**：可给job表的job_type字段添加外键约束（关联matching_weight表的job_type），确保岗位类别必须是权重表中已存在的类别，避免无效数据。
  ```sql
  ALTER TABLE job ADD CONSTRAINT fk_job_job_type FOREIGN KEY (job_type) REFERENCES matching_weight (job_type);
  ```

- **数据兼容**：若已有岗位数据，新增job_type字段后，可默认给所有现有岗位分配"technical（技术岗）"类别，后续由HR手动修改，避免数据异常。
  ```sql
  UPDATE job SET job_type = 'technical' WHERE job_type IS NULL;
  ```

- **索引优化**：确保job表的job_type、matching_weight表的job_type均有索引，提升"岗位-权重"关联查询效率（人岗匹配时高频调用）。

# 四、文档使用说明

- 文档用途：适用于毕业设计、课程设计、求职项目展示、前后端开发联调、答辩材料提交，内容完整闭环，可直接使用。

- 保存方法：全选文档内容 → 新建文本文件 → 粘贴内容 → 修改文件后缀为“\.md”（如“HR智能简历解析Agent系统\_接口\+数据库完整版\.md”），即可保存为可下载、可编辑的MD文档。

- 使用建议：
        

    - 后端开发：直接参考API接口文档开发接口，使用提供的SQL语句建表，初始化基础数据后即可联调。

    - 前端开发：参考API接口文档的请求/响应格式，对接后端接口，实现页面交互。

    - 答辩/论文：可直接截取文档中的接口清单、数据库表结构，用于项目介绍、技术方案章节。

- 注意事项：
        

    - 所有接口均需携带Token（登录后获取），管理员接口仅管理员角色可调用，HR角色无权限操作。

    - 简历上传支持PDF、Word、TXT格式，单次批量上传不超过100个文件，单个文件不超过20MB。

    - 数据库表中所有软删除字段（deleted\_at），删除时仅更新该字段，不物理删除数据，便于数据恢复和审计。

    - 匹配权重修改后，新的匹配任务将采用新权重计算，历史匹配结果不受影响。

> （注：文档部分内容可能由 AI 生成）
