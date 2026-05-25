# HR智能简历解析与人岗匹配Agent系统 - 接口文档

## 一、基础信息

**统一基础URL**: `/hr/api/v1`

**认证方式**: `Bearer Token (JWT)`

**请求头**: `Authorization: Bearer {token}`

---

## 二、统一返回格式

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

**统一分页返回格式**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [],
    "total": 0,
    "page": 1,
    "pageSize": 10
  }
}
```

---

## 三、错误码

```json
{
  "200": "操作成功",
  "400": "参数错误",
  "401": "未登录/Token过期/Token无效",
  "403": "无操作权限",
  "404": "资源不存在",
  "500": "服务端异常",
  "1001": "简历解析中",
  "1002": "简历解析失败"
}
```

---

## 四、接口详情

### 1. 认证模块（Auth）

#### 1.1 用户登录

**功能**: 用户登录获取Token

**URL**: `/auth/login`

**方式**: POST

**传递参数**:
```json
{
  "username": "string, 必填, 账号",
  "password": "string, 必填, 密码"
}
```

**返回参数**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "token": "string, 登录凭证",
    "user": {
      "id": "number",
      "username": "string",
      "name": "string, 姓名",
      "role": "string, admin/hr"
    }
  }
}
```

---

### 2. 用户管理模块（User，仅管理员）

#### 2.1 获取用户列表

**功能**: 获取所有系统用户列表（仅管理员）

**URL**: `/user/list`

**方式**: GET

**传递参数**: 无

**返回参数**:
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": "number",
      "username": "string",
      "name": "string, 姓名",
      "role": "string, admin/hr",
      "status": "number, 1=启用/0=禁用",
      "createdAt": "string"
    }
  ]
}
```

---

#### 2.2 添加用户

**功能**: 添加新用户（仅管理员）

**URL**: `/user/add`

**方式**: POST

**传递参数**:
```json
{
  "username": "string, 必填, 用户名",
  "name": "string, 必填, 姓名",
  "password": "string, 必填, 密码",
  "role": "string, 必填, admin/hr"
}
```

**返回参数**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": "number, 新增用户ID"
  }
}
```

---

#### 2.3 更新用户

**功能**: 更新用户信息（仅管理员）

**URL**: `/user/update/{id}`

**方式**: PUT

**传递参数**: 路径参数 `id`（必填）

```json
{
  "name": "string, 可选, 姓名",
  "role": "string, 可选, admin/hr",
  "status": "number, 可选, 1=启用/0=禁用"
}
```

**返回参数**:
```json
{
  "code": 200,
  "message": "success",
  "data": null
}
```

---

#### 2.4 删除用户

**功能**: 删除用户（仅管理员）

**URL**: `/user/delete/{id}`

**方式**: DELETE

**传递参数**: 路径参数 `id`（必填）

**返回参数**:
```json
{
  "code": 200,
  "message": "success",
  "data": null
}
```

---

### 3. 岗位管理模块（Job）

#### 3.1 获取岗位列表

**功能**: 获取岗位列表（分页）

**URL**: `/job/list`

**方式**: GET

**传递参数**:
```json
{
  "page": "number, 默认1",
  "pageSize": "number, 默认10",
  "keyword": "string, 可选, 岗位名称关键词",
  "department": "string, 可选, 部门",
  "status": "string, 可选, published/unpublished",
  "jobType": "string, 可选, 岗位类别"
}
```

**返回参数**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [
      {
        "id": "number",
        "name": "string, 岗位名称",
        "jobType": "string, 岗位类别",
        "department": "string",
        "salary": "string",
        "location": "string",
        "requirements": "string, 任职要求",
        "responsibilities": "string, 岗位职责",
        "status": "string",
        "createdAt": "string"
      }
    ],
    "total": "number",
    "page": "number",
    "pageSize": "number"
  }
}
```

---

#### 3.2 新增岗位

**功能**: 新增岗位

**URL**: `/job/add`

**方式**: POST

**传递参数**:
```json
{
  "name": "string, 必填, 岗位名称",
  "jobType": "string, 必填, 岗位类别",
  "department": "string, 可选, 部门",
  "salary": "string, 可选, 薪资范围",
  "location": "string, 可选, 工作地点",
  "requirements": "string, 必填, 任职要求",
  "responsibilities": "string, 必填, 岗位职责",
  "status": "string, 可选, 默认unpublished"
}
```

**返回参数**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": "number, 新增岗位ID"
  }
}
```

---

#### 3.3 编辑岗位

**功能**: 编辑岗位（包含上架/下架，通过status字段控制）

**URL**: `/job/update/{id}`

**方式**: PUT

**传递参数**: 路径参数 `id`（必填）

```json
{
  "name": "string, 可选",
  "jobType": "string, 可选",
  "department": "string, 可选",
  "salary": "string, 可选",
  "location": "string, 可选",
  "requirements": "string, 可选",
  "responsibilities": "string, 可选",
  "status": "string, 可选, published/unpublished"
}
```

**返回参数**:
```json
{
  "code": 200,
  "message": "success",
  "data": null
}
```

---

#### 3.4 删除岗位

**功能**: 删除岗位

**URL**: `/job/delete/{id}`

**方式**: DELETE

**传递参数**: 路径参数 `id`（必填）

**返回参数**:
```json
{
  "code": 200,
  "message": "success",
  "data": null
}
```

---

### 4. 简历管理模块（Resume）

#### 4.1 上传简历

**功能**: 上传简历文件（上传后自动触发解析）

**URL**: `/resume/upload`

**方式**: POST

**传递参数**: `multipart/form-data`

```json
{
  "file": "File, 必填, 支持PDF/Word/TXT, 单个≤20MB"
}
```

**返回参数**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": "number, 简历ID",
    "fileName": "string",
    "filePath": "string",
    "parseStatus": "string, pending/processing/success/fail"
  }
}
```

---

#### 4.2 获取简历列表

**功能**: 获取简历列表（分页）

**URL**: `/resume/list`

**方式**: GET

**传递参数**:
```json
{
  "page": "number, 默认1",
  "pageSize": "number, 默认10",
  "keyword": "string, 可选, 文件名/候选人姓名",
  "parseStatus": "string, 可选, pending/processing/success/fail",
  "name": "string, 可选, 候选人姓名",
  "status": "string, 可选, 同parseStatus"
}
```

**返回参数**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [
      {
        "id": "number",
        "fileName": "string",
        "fileType": "string",
        "parseStatus": "string",
        "name": "string, 候选人姓名",
        "phone": "string",
        "email": "string",
        "education": "string, 学历",
        "workYears": "number, 工作年限",
        "uploadedAt": "string"
      }
    ],
    "total": "number",
    "page": "number",
    "pageSize": "number"
  }
}
```

---

#### 4.3 删除简历

**功能**: 删除简历

**URL**: `/resume/delete/{id}`

**方式**: DELETE

**传递参数**: 路径参数 `id`（必填）

**返回参数**:
```json
{
  "code": 200,
  "message": "success",
  "data": null
}
```

---

### 5. 人岗匹配模块（Matching）

#### 5.1 执行人岗匹配

**功能**: 执行人岗匹配任务

**URL**: `/matching/run`

**方式**: POST

**传递参数**:
```json
{
  "jobId": "number, 必填, 岗位ID",
  "resumeIds": "number[], 必填, 简历ID列表, 单次≤100个"
}
```

**返回参数**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "taskId": "number, 匹配任务ID"
  }
}
```

---

#### 5.2 获取匹配结果列表

**功能**: 获取匹配结果列表

**URL**: `/matching/resultList`

**方式**: GET

**传递参数**:
```json
{
  "jobId": "number, 必填",
  "page": "number, 默认1",
  "pageSize": "number, 默认10"
}
```

**返回参数**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [
      {
        "id": "number",
        "candidateId": "number",
        "candidateName": "string",
        "totalScore": "number",
        "skillScore": "number",
        "experienceScore": "number",
        "educationScore": "number",
        "projectScore": "number",
        "highlights": "string[]",
        "shortcomings": "string[]"
      }
    ],
    "total": "number",
    "page": "number",
    "pageSize": "number"
  }
}
```

---

#### 5.3 获取匹配报告

**功能**: 获取匹配详情报告

**URL**: `/matching/report/{id}`

**方式**: GET

**传递参数**: 路径参数 `id`（必填，匹配结果ID）

**返回参数**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": "number",
    "jobInfo": {},
    "candidateInfo": {},
    "totalScore": "number",
    "dimensionScores": {},
    "highlights": "string[]",
    "shortcomings": "string[]",
    "suggestions": "string[]"
  }
}
```

---

### 6. AI智能模块（AI）

#### 6.1 简历智能解析

**功能**: AI解析简历内容

**URL**: `/ai/parse-resume`

**方式**: POST

**传递参数**:
```json
{
  "resumeId": "number, 必填, 简历ID"
}
```

**返回参数**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "name": "string",
    "phone": "string",
    "email": "string",
    "gender": "string",
    "education": "string",
    "workYears": "number",
    "skills": "string[]",
    "workExperience": [],
    "educationHistory": [],
    "projects": []
  }
}
```

---

#### 6.2 生成面试问题

**功能**: 根据岗位和候选人信息生成面试问题

**URL**: `/ai/interview-questions`

**方式**: POST

**传递参数**:
```json
{
  "jobId": "number, 必填, 岗位ID",
  "candidateId": "number, 必填, 候选人ID",
  "questionCount": "number, 可选, 问题数量，默认10",
  "questionTypes": "string[], 可选, 问题类型（technical/behavioral/experience/cultural）"
}
```

**返回参数**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "questions": [
      {
        "id": "number",
        "type": "string, 问题类型",
        "question": "string, 问题内容",
        "evaluationPoints": "string[], 评估要点",
        "difficulty": "string, 难度（easy/medium/hard）"
      }
    ],
    "suggestions": "string[], 面试建议"
  }
}
```

---

#### 6.3 简历智能摘要

**功能**: 生成候选人核心优势摘要

**URL**: `/ai/resume-summary`

**方式**: POST

**传递参数**:
```json
{
  "candidateId": "number, 必填, 候选人ID",
  "summaryLength": "string, 可选, 摘要长度（short/medium/long）"
}
```

**返回参数**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "summary": "string, 候选人摘要",
    "coreStrengths": "string[], 核心优势",
    "keySkills": "string[], 关键技能",
    "experienceHighlights": "string[], 经验亮点",
    "potentialRisks": "string[], 潜在风险"
  }
}
```

---

#### 6.4 薪资建议

**功能**: 基于市场数据给出薪资建议

**URL**: `/ai/salary-suggestion`

**方式**: POST

**传递参数**:
```json
{
  "jobId": "number, 必填, 岗位ID",
  "candidateId": "number, 必填, 候选人ID"
}
```

**返回参数**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "suggestedMin": "number, 建议最低薪资",
    "suggestedMax": "number, 建议最高薪资",
    "marketAverage": "number, 市场平均薪资",
    "factors": [
      {
        "factor": "string, 影响因素",
        "impact": "string, 影响程度（positive/negative/neutral）",
        "description": "string, 说明"
      }
    ],
    "confidence": "number, 建议置信度（0-100）"
  }
}
```

---

#### 6.5 对话式查询

**功能**: 自然语言查询候选人和岗位信息

**URL**: `/ai/chat-query`

**方式**: POST

**传递参数**:
```json
{
  "question": "string, 必填, 自然语言查询内容"
}
```

**返回参数**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "answer": "string, AI回答内容"
  }
}
```

---

#### 6.6 智能报告生成

**功能**: AI自动生成招聘分析报告

**URL**: `/ai/report-generate`

**方式**: POST

**传递参数**:
```json
{
  "reportType": "string, 必填, 报告类型（weekly/monthly/jobAnalysis/candidateAnalysis）",
  "dateRange": "string[], 可选, 时间范围 [startDate, endDate]"
}
```

**返回参数**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "title": "string, 报告标题",
    "period": "string, 报告周期",
    "content": "string, HTML格式报告内容",
    "newResumes": "number, 新增简历数",
    "matchCount": "number, 匹配次数",
    "avgScore": "number, 平均匹配分"
  }
}
```

---

#### 6.7 获取报告列表

**功能**: 获取历史报告列表（分页）

**URL**: `/ai/report-list`

**方式**: GET

**传递参数**:
```json
{
  "page": "number, 默认1",
  "pageSize": "number, 默认10",
  "reportType": "string, 可选, 报告类型"
}
```

**返回参数**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [
      {
        "id": "number",
        "reportType": "string, 报告类型",
        "title": "string, 报告标题",
        "period": "string, 报告周期",
        "newResumes": "number, 新增简历数",
        "matchCount": "number, 匹配次数",
        "avgScore": "number, 平均匹配分",
        "status": "number, 1=已完成/0=生成中/-1=失败",
        "createdAt": "string"
      }
    ],
    "total": "number",
    "page": "number",
    "pageSize": "number"
  }
}
```

---

#### 6.8 获取报告详情

**功能**: 获取报告详细内容

**URL**: `/ai/report-detail/{id}`

**方式**: GET

**传递参数**: 路径参数 `id`（必填）

**返回参数**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": "number",
    "reportType": "string",
    "title": "string",
    "period": "string",
    "content": "string, HTML格式报告内容",
    "newResumes": "number",
    "matchCount": "number",
    "avgScore": "number",
    "status": "number",
    "createdAt": "string"
  }
}
```

---

#### 6.9 删除报告

**功能**: 删除历史报告

**URL**: `/ai/report-delete/{id}`

**方式**: DELETE

**传递参数**: 路径参数 `id`（必填）

**返回参数**:
```json
{
  "code": 200,
  "message": "success",
  "data": null
}
```

---

#### 6.10 简历智能对比

**功能**: 多候选人多维度对比分析

**URL**: `/ai/candidate-compare`

**方式**: POST

**传递参数**:
```json
{
  "jobId": "number, 必填, 岗位ID",
  "candidateIds": "number[], 必填, 候选人ID列表"
}
```

**返回参数**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "rankings": [
      {
        "candidateId": "number",
        "candidateName": "string",
        "overallScore": "number",
        "dimensionScores": {},
        "strengths": "string[]",
        "weaknesses": "string[]"
      }
    ],
    "recommendation": "string, 推荐建议",
    "analysis": "string, 详细分析"
  }
}
```

---

#### 6.11 人才预测

**功能**: 预测候选人入职意愿和稳定性

**URL**: `/ai/talent-predict`

**方式**: POST

**传递参数**:
```json
{
  "candidateId": "number, 必填, 候选人ID",
  "jobId": "number, 必填, 岗位ID"
}
```

**返回参数**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "joinWillingness": "number, 入职意愿（0-100）",
    "stabilityScore": "number, 稳定性评分（0-100）",
    "expectedTenure": "string, 预期在职时长",
    "riskFactors": "string[], 风险因素",
    "positiveFactors": "string[], 积极因素",
    "recommendations": "string[], 建议措施"
  }
}
```

---

### 7. 数据统计模块（Statistics）

#### 7.1 获取概览统计

**功能**: 获取系统概览统计数据（包含趋势和解析率）

**URL**: `/statistics/overview`

**方式**: GET

**传递参数**:
```json
{
  "period": "string, 可选, day/week/month"
}
```

**返回参数**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "resumeCount": "number, 简历总数",
    "jobCount": "number, 岗位总数",
    "matchingTaskCount": "number, 匹配任务数",
    "parseRate": {
      "rate": "number, 解析成功率百分比",
      "successCount": "number",
      "failCount": "number",
      "processingCount": "number"
    },
    "uploadTrend": [
      {
        "date": "string",
        "count": "number"
      }
    ]
  }
}
```

---

### 8. 系统配置模块（System，仅管理员）

#### 8.1 获取权重配置列表

**功能**: 获取所有岗位类别的匹配权重配置（仅管理员）

**URL**: `/weight/list`

**方式**: GET

**传递参数**: 无

**返回参数**:
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": "number",
      "jobType": "string, 岗位类别",
      "jobTypeDesc": "string, 类别描述",
      "skillWeight": "number, 技能权重（0-1）",
      "experienceWeight": "number, 经验权重（0-1）",
      "educationWeight": "number, 学历权重（0-1）",
      "projectWeight": "number, 项目权重（0-1）"
    }
  ]
}
```

---

#### 8.2 更新权重配置

**功能**: 更新指定岗位类别的匹配权重（仅管理员）

**URL**: `/weight/update/{id}`

**方式**: PUT

**传递参数**: 路径参数 `id`（必填）

```json
{
  "jobTypeDesc": "string, 可选, 类别描述",
  "skillWeight": "number, 必填, 技能权重（0-1）",
  "experienceWeight": "number, 必填, 经验权重（0-1）",
  "educationWeight": "number, 必填, 学历权重（0-1）",
  "projectWeight": "number, 必填, 项目权重（0-1）"
}
```

**返回参数**:
```json
{
  "code": 200,
  "message": "success",
  "data": null
}
```

---

## 五、接口汇总

| 模块 | 接口数量 | 说明 |
|------|---------|------|
| 认证模块 | 1 | 登录 |
| 用户管理 | 4 | 用户CRUD（仅管理员） |
| 岗位管理 | 4 | 岗位CRUD（列表含详情、编辑含上下架） |
| 简历管理 | 3 | 上传（自动解析）、列表、删除 |
| 人岗匹配 | 3 | 执行匹配、结果列表、报告 |
| AI智能模块 | 11 | 解析、面试问题、摘要、薪资、对话、报告生成、报告列表、报告详情、报告删除、对比、预测 |
| 数据统计 | 1 | 概览（含趋势和解析率） |
| 系统配置 | 2 | 权重配置列表、更新（仅管理员） |
| **合计** | **29** | |
