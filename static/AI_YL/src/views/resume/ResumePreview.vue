<template>
  <div class="resume-preview-page">
    <ParticlesBackground />
    
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">简历预览</h1>
        <p class="page-subtitle">查看简历原始文件内容</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" class="action-btn" @click="router.push(`/resumes/result/${resumeId}`)">
          <el-icon><DocumentChecked /></el-icon>
          <span>查看解析结果</span>
        </el-button>
        <el-button class="action-btn" @click="downloadFile">
          <el-icon><Download /></el-icon>
          <span>下载原文件</span>
        </el-button>
        <el-button class="action-btn" @click="router.push('/resumes')">
          <el-icon><Back /></el-icon>
          <span>返回列表</span>
        </el-button>
      </div>
    </div>
    
    <div class="page-content">
      <div v-if="loading" class="loading-container glass-card">
        <el-icon class="loading-icon" :size="48"><Loading /></el-icon>
        <p>加载中...</p>
      </div>
      
      <div v-else-if="resumeInfo" class="preview-container glass-card">
        <div class="file-info-bar">
          <div class="file-meta">
            <el-icon :size="24"><Document /></el-icon>
            <span class="file-name">{{ resumeInfo.fileName }}</span>
            <span class="file-type">{{ resumeInfo.fileType.toUpperCase() }}</span>
          </div>
        </div>
        
        <div class="preview-content">
          <iframe v-if="isPdf" :src="fileUrl" class="preview-frame" frameborder="0"></iframe>
          <div v-else-if="isTxt" class="text-preview">
            <pre>{{ txtContent }}</pre>
          </div>
          <div v-else-if="isWord" class="word-preview">
            <el-icon :size="64"><Document /></el-icon>
            <p>Word 文档请下载使用后查看</p>
            <p class="hint">建议下载后使用 Word 或 WPS 打开</p>
            <el-button type="primary" @click="downloadFile" style="margin-top: 16px;">
              <el-icon><Download /></el-icon>
              下载原文件
            </el-button>
          </div>
          <div v-else class="unsupported-preview">
            <el-icon :size="64"><Document /></el-icon>
            <p>该文件格式暂不支持在线预览</p>
            <p class="hint">请下载原文件查看</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { resumeApi } from '@/api'
import { ElMessage } from 'element-plus'
import { Document, DocumentChecked, Back, Loading, Download } from '@element-plus/icons-vue'
import ParticlesBackground from '@/components/ParticlesBackground.vue'

const route = useRoute()
const router = useRouter()
const resumeId = computed(() => route.params.id)

const loading = ref(true)
const resumeInfo = ref(null)
const txtContent = ref('')

const isPdf = computed(() => resumeInfo.value?.fileType?.toLowerCase() === 'pdf')
const isTxt = computed(() => resumeInfo.value?.fileType?.toLowerCase() === 'txt')
const isWord = computed(() => ['doc', 'docx'].includes(resumeInfo.value?.fileType?.toLowerCase()))
const fileUrl = computed(() => {
  if (!resumeInfo.value?.filePath) return ''
  const path = resumeInfo.value.filePath.replace(/\\/g, '/')
  return `${import.meta.env.VITE_API_BASE_URL || ''}/${path}`
})

const fetchResumeInfo = async () => {
  loading.value = true
  try {
    const res = await resumeApi.getResumeDetail(resumeId.value)
    resumeInfo.value = res.data
  } catch (error) {
    ElMessage.error('简历不存在')
    router.push('/resumes')
  } finally {
    loading.value = false
  }
}

const downloadFile = () => {
  if (resumeInfo.value?.filePath) {
    const link = document.createElement('a')
    link.href = `/${resumeInfo.value.filePath.replace(/\\/g, '/')}`
    link.download = resumeInfo.value.fileName
    link.click()
  }
}

onMounted(() => {
  fetchResumeInfo()
})
</script>

<style scoped lang="scss">
.resume-preview-page {
  min-height: 100%;
  position: relative;
}

.page-header {
  position: relative;
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
  padding: 32px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  overflow: hidden;
  
  &::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(245, 158, 11, 0.15) 0%, transparent 70%);
    animation: headerGlow 8s ease-in-out infinite;
  }
}

@keyframes headerGlow {
  0%, 100% { transform: scale(1); opacity: 0.5; }
  50% { transform: scale(1.2); opacity: 0.8; }
}

.header-content {
  position: relative;
  z-index: 1;
  
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

.header-actions {
  position: relative;
  z-index: 1;
  display: flex;
  gap: 12px;
  
  .action-btn {
    height: 44px;
    padding: 0 24px;
    font-size: 15px;
    font-weight: 600;
    border-radius: var(--radius-md);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    transition: var(--transition-base);
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 16px rgba(0, 0, 0, 0.03);
    }
  }
}

.page-content {
  padding: 24px;
  position: relative;
  z-index: 1;
}

.glass-card {
  background: var(--glass-bg);
  backdrop-filter: blur(12px);
  border-radius: var(--radius-lg);
  border: 1px solid var(--glass-border);
  box-shadow: var(--glass-shadow);
}

.loading-container {
  padding: 80px;
  text-align: center;
  
  .loading-icon {
    animation: rotate 1s linear infinite;
    color: var(--primary-color);
  }
  
  p {
    margin-top: 16px;
    color: var(--text-secondary);
  }
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.preview-container {
  overflow: hidden;
}

.file-info-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--glass-border);
}

.file-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--text-primary);
  
  .file-name {
    font-weight: 600;
    font-size: 16px;
  }
  
  .file-type {
    padding: 4px 10px;
    background: var(--primary-color);
    color: #fff;
    border-radius: var(--radius-sm);
    font-size: 12px;
    font-weight: 600;
  }
}

.preview-content {
  height: calc(100vh - 280px);
  min-height: 500px;
}

.preview-frame {
  width: 100%;
  height: 100%;
  border: none;
}

.text-preview {
  padding: 24px;
  height: 100%;
  overflow: auto;
  background: rgba(0, 0, 0, 0.02);
  
  pre {
    white-space: pre-wrap;
    word-wrap: break-word;
    font-family: 'Courier New', monospace;
    font-size: 14px;
    line-height: 1.6;
    color: var(--text-primary);
  }
}

.word-preview,
.unsupported-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--text-secondary);
  
  p {
    margin-top: 16px;
    font-size: 16px;
  }
  
  .hint {
    font-size: 14px;
    color: var(--text-tertiary);
  }
}
</style>
