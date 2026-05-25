<template>
  <div class="ai-chat-page">
    <div class="page-header">
      <el-button text @click="$router.push('/ai-center')" class="back-btn">
        <el-icon><ArrowLeft /></el-icon>
        <span>返回 AI 中心</span>
      </el-button>
      <h1 class="page-title">AI 对话查询</h1>
      <p class="page-subtitle">用自然语言查询候选人信息、岗位状态等</p>
    </div>

    <div class="page-content">
      <div class="chat-container glass-card">
        <div class="chat-messages" ref="messagesRef">
          <div v-for="(msg, idx) in messages" :key="idx" :class="['chat-message', msg.role === 'user' ? 'user-message' : 'ai-message']">
            <div class="message-avatar">
              <el-icon :size="18" v-if="msg.role === 'ai'"><ChatDotRound /></el-icon>
              <el-icon :size="18" v-else><User /></el-icon>
            </div>
            <div class="message-content">{{ msg.content }}</div>
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
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { aiApi } from '@/api'
import { ArrowLeft, ChatDotRound, User, Promotion } from '@element-plus/icons-vue'

const messages = ref([
  { role: 'ai', content: '你好！我是 HR 智能助手，可以帮您查询候选人信息、岗位状态等。请问有什么可以帮您的？' }
])
const input = ref('')
const loading = ref(false)
const messagesRef = ref(null)

const handleSend = async () => {
  const question = input.value.trim()
  if (!question) return

  messages.value.push({ role: 'user', content: question })
  input.value = ''
  loading.value = true

  try {
    const res = await aiApi.chatQuery({ question })
    messages.value.push({ role: 'ai', content: res.data?.answer || '抱歉，暂时无法回答您的问题' })
  } catch (error) {
    messages.value.push({ role: 'ai', content: '抱歉，查询失败，请稍后重试' })
  } finally {
    loading.value = false
    await nextTick()
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  }
}
</script>

<style scoped lang="scss">
.ai-chat-page {
  min-height: 100%;
}

.page-header {
  background: var(--gradient-primary);
  padding: 24px;

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
      background: var(--bg-lighter);
      color: var(--text-primary);
      border-radius: 4px 16px 16px 16px;
    }
  }

  .message-avatar {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--primary-glow);
    color: var(--primary-color);
    flex-shrink: 0;
  }

  .message-content {
    padding: 12px 16px;
    font-size: 14px;
    line-height: 1.6;
  }
}

.thinking {
  display: flex;
  gap: 6px;
  align-items: center;

  .thinking-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--text-tertiary);
    animation: thinking 1.4s ease-in-out infinite;

    &:nth-child(2) { animation-delay: 0.2s; }
    &:nth-child(3) { animation-delay: 0.4s; }
  }
}

@keyframes thinking {
  0%, 60%, 100% { transform: scale(1); opacity: 0.4; }
  30% { transform: scale(1.2); opacity: 1; }
}

.chat-input-area {
  display: flex;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid var(--card-border);

  .chat-input {
    flex: 1;
  }

  .send-btn {
    width: 44px;
    height: 44px;
    border-radius: var(--radius-md);
  }
}
</style>
