<template>
  <div class="ai-chat-page">
    <div class="page-header">
      <div class="header-left">
        <el-button text @click="$router.push('/ai-center')" class="back-btn">
          <el-icon><ArrowLeft /></el-icon>
          <span>返回 AI 中心</span>
        </el-button>
        <h1 class="page-title">AI 对话查询</h1>
        <p class="page-subtitle">用自然语言查询候选人信息、岗位状态等</p>
      </div>
      <div class="header-right">
        <el-button @click="showSessionList = true" class="history-btn">
          <el-icon><Clock /></el-icon>
          <span>历史对话</span>
        </el-button>
        <el-button @click="createNewSession" class="new-btn">
          <el-icon><Plus /></el-icon>
          <span>新建对话</span>
        </el-button>
      </div>
    </div>

    <div class="page-content">
      <div class="chat-container glass-card">
        <div class="chat-messages" ref="messagesRef">
          <div v-for="(msg, idx) in messages" :key="idx" 
               :class="['chat-message', msg.role === 'user' ? 'user-message' : 'ai-message']">
            <div class="message-avatar">
              <el-icon :size="18" v-if="msg.role === 'ai'"><ChatDotRound /></el-icon>
              <el-icon :size="18" v-else><User /></el-icon>
            </div>
            <div class="message-content">
              <div class="message-text" v-html="parseMarkdown(msg.content)"></div>
              <div v-if="msg.keywords && msg.keywords.length > 0" class="message-keywords">
                <el-tag v-for="(kw, i) in msg.keywords" :key="i" size="small" class="keyword-tag">{{ kw }}</el-tag>
              </div>
            </div>
          </div>
          <div v-if="loading" class="chat-message ai-message">
            <div class="message-avatar">
              <el-icon :size="18"><ChatDotRound /></el-icon>
            </div>
            <div class="message-content thinking">
              <span class="thinking-dot"></span>
              <span class="thinking-dot"></span>
              <span class="thinking-dot"></span>
            </div>
          </div>
        </div>
        <div class="chat-input-area">
          <el-input
            v-model="input"
            placeholder="输入您的问题，如：有多少候选人有 Java 经验？"
            @keyup.enter="handleSend"
            :disabled="loading"
            class="chat-input"
          />
          <el-button type="primary" @click="handleSend" :loading="loading" class="send-btn">
            <el-icon :size="18"><Promotion /></el-icon>
          </el-button>
        </div>
      </div>
    </div>

    <!-- 历史会话列表 -->
    <el-dialog v-model="showSessionList" title="历史对话" width="600px" class="session-dialog">
      <el-table :data="sessionList" style="width: 100%" @row-click="switchToSession" class="session-table">
        <el-table-column prop="title" label="对话标题" />
        <el-table-column prop="message_count" label="消息数" width="80" />
        <el-table-column prop="updated_at" label="更新时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.updated_at) }}
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { ArrowLeft, ChatDotRound, User, Promotion, Clock, Plus } from '@element-plus/icons-vue'
import { marked } from 'marked'

// 配置marked
marked.setOptions({
  gfm: true,
  breaks: true
})

const messages = ref([
  { role: 'ai', content: '你好！我是 HR 智能助手，可以帮您查询候选人信息、岗位状态等。请问有什么可以帮您的？' }
])
const input = ref('')
const loading = ref(false)
const messagesRef = ref(null)
const sessionId = ref(null)
const showSessionList = ref(false)
const sessionList = ref([])

// Markdown解析
const parseMarkdown = (content) => {
  try {
    // 清理数据库专有字段和处理过程信息
    let cleanContent = content
    
    // 移除类似 "ID: 13" 或 "(ID: 123)" 的格式
    cleanContent = cleanContent.replace(/\(ID:\s*\d+\)/g, '')
    cleanContent = cleanContent.replace(/ID:\s*\d+\s*/g, '')
    
    // 移除数据库字段标识
    cleanContent = cleanContent.replace(/\b(id|user_id|session_id|memory_id)\s*[:：]\s*\w+/gi, '')
    
    // 移除文本分割标记（如"这个岗位 有什么适 配的人吗"这种分割）
    cleanContent = cleanContent.replace(/(\S)\s+(\S)/g, (match, p1, p2) => {
      // 只在两个字符都是中文且中间只有一个空格时合并
      if (/[\u4e00-\u9fa5]/.test(p1) && /[\u4e00-\u9fa5]/.test(p2)) {
        return p1 + p2
      }
      return match
    })
    
    // 移除处理过程日志（如"正在搜索..."、"查询中..."）
    cleanContent = cleanContent.replace(/[【\[](查询|搜索|处理|加载|正在)[^】\]]*[】\]]/g, '')
    
    // 移除代码块标记（如果存在）
    cleanContent = cleanContent.replace(/```[\s\S]*?```/g, '')
    
    // 规范化空格和换行
    cleanContent = cleanContent.replace(/\s+/g, ' ').replace(/\s*(\n)\s*/g, '\n').trim()
    
    // 确保表格格式正确（如果有表格的话）
    cleanContent = formatMarkdownTable(cleanContent)
    
    return marked(cleanContent)
  } catch (e) {
    console.error('Markdown解析失败:', e)
    return content
  }
}

// 格式化Markdown表格
const formatMarkdownTable = (content) => {
  // 匹配表格并确保格式正确
  const tableRegex = /(\|.*\|[\s\S]*?)\n\n/g
  return content.replace(tableRegex, (match) => {
    // 确保表格有正确的分隔行
    const lines = match.trim().split('\n')
    if (lines.length >= 2 && !lines[1].match(/^\|[-:|]+\|$/)) {
      // 添加分隔行
      const header = lines[0]
      const separator = header.replace(/[^|]/g, '-').replace(/\|/g, '|')
      lines.splice(1, 0, separator)
      return lines.join('\n') + '\n\n'
    }
    return match
  })
}

// 生成 UUID
const generateUUID = () => {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0
    const v = c === 'x' ? r : (r & 0x3 | 0x8)
    return v.toString(16)
  })
}

// 初始化会话
const initSession = () => {
  sessionId.value = localStorage.getItem('current_session_id')
  if (!sessionId.value) {
    sessionId.value = generateUUID()
    localStorage.setItem('current_session_id', sessionId.value)
  }
  loadSessionHistory()
}

// 加载当前会话历史
const loadSessionHistory = async () => {
  if (!sessionId.value) return
  
  try {
    const response = await fetch('/hr/api/v1/ai/session/history', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ session_id: sessionId.value })
    })
    
    if (response.ok) {
      const result = await response.json()
      if (result.code === 200 && result.data && result.data.length > 0) {
        messages.value = result.data.map(item => ({
          role: item.role,
          content: item.content,
          keywords: item.keywords || []
        }))
      }
    }
  } catch (error) {
    console.error('加载历史失败:', error)
  }
}

// 获取会话列表
const fetchSessionList = async () => {
  try {
    const response = await fetch('/hr/api/v1/ai/session/list', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({})
    })
    
    if (response.ok) {
      const result = await response.json()
      if (result.code === 200) {
        sessionList.value = result.data || []
      }
    }
  } catch (error) {
    console.error('获取会话列表失败:', error)
  }
}

// 切换到指定会话
const switchToSession = async (row) => {
  try {
    const response = await fetch('/hr/api/v1/ai/session/switch', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        old_session_id: sessionId.value,
        new_session_id: row.session_id
      })
    })
    
    if (response.ok) {
      const result = await response.json()
      if (result.code === 200) {
        sessionId.value = row.session_id
        localStorage.setItem('current_session_id', sessionId.value)
        
        // 加载历史对话
        messages.value = (result.data.history || []).map(item => ({
          role: item.role,
          content: item.content,
          keywords: item.keywords || []
        }))
        
        showSessionList.value = false
        ElMessage.success('已切换到该对话')
      }
    }
  } catch (error) {
    console.error('切换会话失败:', error)
    ElMessage.error('切换会话失败')
  }
}

// 新建对话
const createNewSession = () => {
  sessionId.value = generateUUID()
  localStorage.setItem('current_session_id', sessionId.value)
  messages.value = [
    { role: 'ai', content: '你好！我是 HR 智能助手，可以帮您查询候选人信息、岗位状态等。请问有什么可以帮您的？' }
  ]
  ElMessage.success('已新建对话')
}

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', { 
    year: 'numeric', 
    month: '2-digit', 
    day: '2-digit', 
    hour: '2-digit', 
    minute: '2-digit' 
  })
}

const handleSend = async () => {
  const question = input.value.trim()
  if (!question) return

  messages.value.push({ role: 'user', content: question })
  input.value = ''
  loading.value = true

  // 添加 AI 回复占位（流式输出用）
  messages.value.push({ role: 'ai', content: '' })
  const aiMessageIndex = messages.value.length - 1

  try {
    const response = await fetch('/hr/api/v1/ai/chat-with-memory', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ 
        question,
        context: {
          session_id: sessionId.value
        }
      })
    })

    if (!response.ok) {
      throw new Error('网络请求失败')
    }

    // 获取会话 ID
    const newSessionId = response.headers.get('X-Session-ID')
    if (newSessionId) {
      sessionId.value = newSessionId
      localStorage.setItem('current_session_id', sessionId.value)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder('utf-8')
    let accumulatedText = ''
    let updateTimeout = null

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      accumulatedText += decoder.decode(value, { stream: true })
      
      // 使用防抖，避免显示中间分割状态，只在输入暂停时更新显示
      if (updateTimeout) {
        clearTimeout(updateTimeout)
      }
      updateTimeout = setTimeout(() => {
        messages.value[aiMessageIndex].content = accumulatedText
        nextTick().then(() => {
          if (messagesRef.value) {
            messagesRef.value.scrollTop = messagesRef.value.scrollHeight
          }
        })
      }, 100)
    }

    // 确保最终内容显示
    clearTimeout(updateTimeout)
    messages.value[aiMessageIndex].content = accumulatedText

    // 处理完整响应
    const finalContent = accumulatedText && !accumulatedText.includes('错误') && !accumulatedText.includes('Exception') 
      ? accumulatedText 
      : '抱歉，暂时无法回答您的问题'
    messages.value[aiMessageIndex].content = finalContent
    
    // 刷新会话列表
    fetchSessionList()
  } catch (error) {
    messages.value[aiMessageIndex].content = '抱歉，查询失败，请稍后重试'
    if (import.meta.env.DEV) {
      console.error('流式请求失败:', error)
    }
  } finally {
    loading.value = false
    await nextTick()
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  }
}

onMounted(() => {
  initSession()
  fetchSessionList()
})
</script>

<style scoped lang="scss">
.ai-chat-page {
  min-height: 100%;
}

.page-header {
  background: var(--gradient-primary);
  padding: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;

  .header-left {
    flex: 1;

    .back-btn {
      color: rgba(255, 255, 255, 0.85);
      margin-bottom: 8px;

      &:hover {
        color: #fff;
      }
    }

    .page-title {
      font-size: 24px;
      font-weight: 700;
      color: #fff;
      margin: 0 0 8px 0;
    }

    .page-subtitle {
      font-size: 14px;
      color: rgba(255, 255, 255, 0.85);
      margin: 0;
    }
  }

  .header-right {
    display: flex;
    gap: 12px;

    .history-btn,
    .new-btn {
      color: #fff;
      border-color: rgba(255, 255, 255, 0.6);
      background: rgba(255, 255, 255, 0.15);
      font-weight: 500;
      text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
      
      &:hover {
        color: #fff;
        border-color: #fff;
        background: rgba(255, 255, 255, 0.25);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      }
    }
  }
}

.page-content {
  padding: 24px;
}

.chat-container {
  background: var(--card-bg);
  backdrop-filter: var(--card-blur);
  border: 1px solid var(--card-border);
  border-radius: var(--radius-lg);
  display: flex;
  flex-direction: column;
  height: calc(100vh - 200px);
  min-height: 500px;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  align-items: flex-start;
}

.chat-message {
  display: flex;
  gap: 10px;
  max-width: 80%;

  &.user-message {
    align-self: flex-end;
    flex-direction: row-reverse;

    .message-content {
      background: var(--gradient-primary);
      color: #fff;
      border-radius: 16px 4px 16px 16px;
    }
  }

  &.ai-message {
    align-self: flex-start;

    .message-content {
      background: rgba(255, 255, 255, 0.08);
      border-radius: 4px 16px 16px 16px;
    }
  }

  .message-avatar {
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.1);
  }

  .message-content {
    padding: 12px 16px;
    font-size: 14px;
    line-height: 1.6;
    word-break: break-word;

    .message-keywords {
      margin-top: 8px;
      display: flex;
      gap: 6px;
      flex-wrap: wrap;

      .keyword-tag {
        background: rgba(255, 255, 255, 0.15);
        color: rgba(255, 255, 255, 0.9);
        border: none;
      }
    }
  }
}

.thinking {
  display: flex;
  gap: 4px;
  align-items: center;

  .thinking-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.6);
    animation: thinking 1.4s infinite;

    &:nth-child(2) {
      animation-delay: 0.2s;
    }

    &:nth-child(3) {
      animation-delay: 0.4s;
    }
  }
}

@keyframes thinking {
  0%, 100% {
    opacity: 0.4;
    transform: scale(0.8);
  }
  50% {
    opacity: 1;
    transform: scale(1);
  }
}

.chat-input-area {
  padding: 16px 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  gap: 12px;
  align-items: center;

  .chat-input {
    flex: 1;
  }

  .send-btn {
    flex-shrink: 0;
  }
}

.session-dialog {
  .session-table {
    cursor: pointer;

    :deep(.el-table__row:hover) {
      background: rgba(64, 158, 255, 0.1);
    }
  }
}
</style>
