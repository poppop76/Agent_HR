# Agent 记忆机制实现说明

## 概述

本次实现为 HR Agent 系统添加了完整的记忆机制，包括短期记忆和长期记忆，支持上下文压缩、关键词提取和会话管理功能。

## 功能特性

### 1. 短期记忆（Redis）
- **存储位置**：Redis
- **存储内容**：最近 5 条完整对话上下文
- **关键词索引**：每条对话提取 5 个关键词
- **过期时间**：1 小时
- **搜索功能**：支持关键词匹配搜索

### 2. 长期记忆（数据库）
- **存储位置**：MySQL 数据库
- **存储表**：
  - `conversation_memory`：对话记录表
  - `conversation_session`：会话元信息表
- **异步保存**：对话完成后异步保存到数据库
- **持久化**：永久保存，支持历史查询

### 3. 关键词提取
- **自动提取**：每段对话自动提取 5 个关键词
- **智能过滤**：过滤停用词
- **词频统计**：基于词频和重要性排序

### 4. 上下文压缩
- **自动检测**：当上下文超过 4000 字符时触发压缩
- **压缩策略**：
  - 保留最重要的 70% 对话
  - 基于关键词丰富度评分
  - 截断过长内容（>500 字符）

### 5. 记忆切换
- **优先级**：优先使用短期记忆，不足时从长期记忆补充
- **智能搜索**：根据关键词搜索相关记忆
- **会话管理**：支持多会话切换

### 6. 前端功能
- **历史对话展示**：显示所有历史会话列表
- **会话切换**：点击即可回到之前的对话
- **新建对话**：支持创建新的对话会话
- **关键词展示**：在对话消息下方显示提取的关键词

## 文件结构

```
HR_Agent/
├── agent/memory/
│   ├── __init__.py              # 模块初始化
│   └── memory_manager.py        # 记忆管理核心类
├── api/
│   └── memory_api.py            # 记忆管理 API 路由
├── schemas/
│   └── ai_schema.py             # 添加记忆相关 Schema
├── main.py                      # 注册记忆管理路由
├── scripts/
│   └── create_memory_tables.py  # 数据库表创建脚本
├── static/AI_YL/src/views/ai/
│   └── AIChat.vue               # 前端对话界面（带记忆功能）
└── test_memory.py               # 记忆功能测试脚本
```

## 数据库表结构

### conversation_memory（对话记忆表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键 |
| session_id | VARCHAR(64) | 会话 ID（索引） |
| user_id | INT | 用户 ID |
| role | VARCHAR(20) | 角色（user/assistant） |
| content | TEXT | 对话内容 |
| keywords | JSON | 关键词列表 |
| summary | TEXT | 对话摘要 |
| created_at | DATETIME | 创建时间 |
| compressed | INT | 是否被压缩 |
| parent_id | INT | 父对话 ID |

### conversation_session（会话表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键 |
| session_id | VARCHAR(64) | 会话 ID（唯一索引） |
| user_id | INT | 用户 ID |
| title | VARCHAR(255) | 会话标题 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |
| message_count | INT | 消息数量 |
| is_active | INT | 是否活跃 |

## API 接口

### 1. 带记忆的对话接口
```
POST /hr/api/v1/ai/chat-with-memory
```

**请求参数：**
```json
{
  "question": "问题内容",
  "context": {
    "session_id": "会话 ID",
    "user_id": 1
  }
}
```

**响应：** 流式输出，响应头包含 `X-Session-ID`

### 2. 获取会话列表
```
POST /hr/api/v1/ai/session/list
```

**响应：**
```json
{
  "code": 200,
  "msg": "获取成功",
  "data": [
    {
      "session_id": "xxx",
      "title": "对话标题",
      "message_count": 10,
      "created_at": "2024-01-01T10:00:00",
      "updated_at": "2024-01-01T12:00:00"
    }
  ]
}
```

### 3. 切换会话
```
POST /hr/api/v1/ai/session/switch
```

**请求参数：**
```json
{
  "old_session_id": "旧会话 ID",
  "new_session_id": "新会话 ID",
  "user_id": 1
}
```

### 4. 获取会话历史
```
POST /hr/api/v1/ai/session/history
```

**请求参数：**
```json
{
  "session_id": "会话 ID"
}
```

## 使用流程

### 1. 创建数据库表
```bash
python scripts/create_memory_tables.py
```

### 2. 启动服务
```bash
python main.py
```

### 3. 访问前端
打开浏览器访问前端页面，进入 AI 对话界面。

### 4. 功能使用
- **新建对话**：点击右上角"新建对话"按钮
- **查看历史**：点击右上角"历史对话"按钮
- **切换会话**：点击历史会话列表中的任意一行
- **关键词展示**：每段对话下方会自动显示提取的关键词

## 记忆工作流程

### 对话流程
1. 用户发送问题
2. 从短期记忆（Redis）获取最近 5 条上下文
3. 如果需要，从长期记忆（数据库）补充上下文
4. 搜索与问题相关的历史记忆
5. 将相关记忆添加到系统提示词
6. 调用 LLM 生成回复
7. 流式输出回复给用户
8. 异步保存对话到短期记忆和长期记忆

### 记忆搜索流程
1. 提取用户问题的关键词（5 个）
2. 在短期记忆中搜索匹配的对话
3. 在长期记忆中搜索匹配的对话
4. 合并结果，按匹配度排序
5. 返回最相关的 3 条记忆给 LLM

### 上下文压缩流程
1. 检查上下文总长度是否超过阈值（4000 字符）
2. 如果超过，计算每条对话的重要性（基于关键词数量）
3. 保留最重要的 70% 对话
4. 截断过长的对话内容（>500 字符）
5. 更新压缩标记

## 配置参数

在 `agent/memory/memory_manager.py` 中可以调整以下参数：

```python
# 短期记忆配置
ShortTermMemory(redis_client, max_contexts=5)  # 存储 5 条上下文
context_ttl = 3600  # 1 小时过期

# 上下文压缩配置
ContextCompressor(max_length=4000)  # 最大 4000 字符
compression_ratio = 0.7  # 保留 70%

# 关键词提取
KeywordExtractor.extract(text, top_k=5)  # 提取 5 个关键词
```

## 测试

运行测试脚本验证记忆功能：
```bash
python test_memory.py
```

测试内容包括：
- 关键词提取
- 短期记忆存储和搜索
- 长期记忆存储和搜索
- 上下文压缩
- 完整记忆管理器

## 注意事项

1. **Redis 服务**：确保 Redis 服务正常运行
2. **数据库连接**：确保 MySQL 数据库连接正常
3. **异步保存**：长期记忆使用异步保存，可能有 1-2 秒延迟
4. **会话 ID**：前端使用 localStorage 保存当前会话 ID
5. **关键词质量**：关键词提取使用简化算法，可优化为使用 LLM

## 优化建议

1. **关键词提取优化**：使用 LLM 或更智能的分词算法
2. **全文搜索**：使用 Elasticsearch 等工具提升搜索性能
3. **记忆摘要**：使用 LLM 为长对话生成摘要
4. **记忆权重**：根据时间衰减调整记忆权重
5. **多模态记忆**：支持存储图片、文件等多模态信息

## 技术栈

- **后端**：Python, FastAPI, SQLAlchemy
- **短期记忆**：Redis
- **长期记忆**：MySQL
- **前端**：Vue 3, Element Plus
- **关键词提取**：正则分词 + 词频统计
- **异步处理**：ThreadPoolExecutor

## 开发者

实现日期：2026-06-08
版本：v1.0
