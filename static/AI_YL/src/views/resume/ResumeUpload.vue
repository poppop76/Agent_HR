<template>
  <div class="resume-upload-page">
    <ParticlesBackground />
    
    <div class="page-header">
      <div class="header-particles"></div>
      <div class="header-content">
        <h1 class="page-title">智能简历解析</h1>
        <p class="page-subtitle">支持批量上传，AI自动解析简历内容</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" size="large" class="action-btn" @click="triggerFolderInput">
          <el-icon><FolderOpened /></el-icon>
          <span>文件夹上传</span>
        </el-button>
      </div>
    </div>
    
    <div class="page-content">
      <div class="upload-card glass-card">
        <div class="card-header">
          <h3 class="card-title">上传简历</h3>
          <div class="card-badge">AI 解析</div>
        </div>
        
        <div 
          class="upload-area"
          :class="{ 'is-dragover': isDragover }"
          @dragover.prevent="isDragover = true"
          @dragleave.prevent="isDragover = false"
          @drop.prevent="handleDrop"
          @click="triggerFileInput"
        >
          <div class="upload-glow"></div>
          <div class="upload-icon-wrapper">
            <el-icon :size="56"><UploadFilled /></el-icon>
          </div>
          <p class="upload-text">拖拽文件到此处，或点击上传</p>
          <p class="upload-hint">支持 PDF/Word/TXT 格式，单个文件不超过 10MB</p>
          <input 
            ref="fileInputRef"
            type="file" 
            multiple 
            accept=".pdf,.doc,.docx,.txt"
            style="display: none"
            @change="handleFileSelect"
          />
        </div>
        
        <div class="upload-actions">
          <el-button type="primary" size="large" class="upload-btn" @click="triggerFileInput">
            <el-icon><Upload /></el-icon>
            <span>选择文件</span>
          </el-button>
          <input 
            ref="folderInputRef"
            type="file" 
            multiple 
            accept=".pdf,.doc,.docx,.txt"
            webkitdirectory
            style="display: none"
            @change="handleFileSelect"
          />
        </div>
      </div>
      
      <div v-if="uploadList.length > 0" class="upload-list-card glass-card">
        <div class="card-header">
          <h3 class="card-title">上传列表</h3>
          <div class="card-badge card-badge-info">{{ uploadList.length }} 个文件</div>
        </div>
        
        <div class="upload-list">
          <div v-for="(file, index) in uploadList" :key="file.id" class="upload-item" :style="{ animationDelay: `${index * 0.05}s` }">
            <div class="file-info">
              <div class="file-icon" :class="getFileIconClass(file.name)">
                <el-icon :size="22"><component :is="getFileIcon(file.name)" /></el-icon>
              </div>
              <div class="file-details">
                <span class="file-name">{{ file.name }}</span>
                <span class="file-size">{{ formatFileSize(file.size) }}</span>
              </div>
            </div>
            
            <div class="file-progress-wrapper">
              <el-progress 
                :percentage="file.progress" 
                :status="file.status === 'success' ? 'success' : file.status === 'error' ? 'exception' : undefined"
                :stroke-width="8"
                class="file-progress"
              />
            </div>
            
            <div class="file-status">
              <span v-if="file.status === 'uploading'" class="status-uploading">
                <el-icon class="rotating"><Loading /></el-icon>
                上传中...
              </span>
              <span v-else-if="file.status === 'success'" class="status-success">
                <el-icon><CircleCheckFilled /></el-icon>
                上传成功
              </span>
              <span v-else-if="file.status === 'error'" class="status-error">
                <el-icon><CircleCloseFilled /></el-icon>
                上传失败
              </span>
            </div>
            
            <div class="item-glow"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { resumeApi } from '@/api'
import { ElMessage } from 'element-plus'
import { 
  UploadFilled, Upload, FolderOpened, 
  Document, CircleCheckFilled, CircleCloseFilled, Loading
} from '@element-plus/icons-vue'
import ParticlesBackground from '@/components/ParticlesBackground.vue'

const router = useRouter()
const fileInputRef = ref(null)
const folderInputRef = ref(null)
const isDragover = ref(false)
const uploadList = ref([])

const MAX_FILE_SIZE = 10 * 1024 * 1024
const ALLOWED_TYPES = [
  'application/pdf',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'text/plain'
]

const triggerFileInput = () => {
  fileInputRef.value?.click()
}

const triggerFolderInput = () => {
  folderInputRef.value?.click()
}

const handleDrop = (e) => {
  isDragover.value = false
  const files = Array.from(e.dataTransfer.files)
  handleFiles(files)
}

const handleFileSelect = (e) => {
  const files = Array.from(e.target.files)
  handleFiles(files)
  e.target.value = ''
}

const handleFiles = (files) => {
  const validFiles = files.filter(file => {
    if (!ALLOWED_TYPES.includes(file.type)) {
      ElMessage.warning(`${file.name} 格式不支持`)
      return false
    }
    if (file.size > MAX_FILE_SIZE) {
      ElMessage.warning(`${file.name} 文件大小超过限制`)
      return false
    }
    return true
  })
  
  validFiles.forEach(file => {
    uploadFile(file)
  })
}

const uploadFile = async (file) => {
  const uploadItem = {
    id: Date.now() + Math.random(),
    name: file.name,
    size: file.size,
    progress: 0,
    status: 'uploading'
  }
  uploadList.value.push(uploadItem)
  
  const formData = new FormData()
  formData.append('file', file)
  
  try {
    await resumeApi.uploadResume(formData, {
      onUploadProgress: (e) => {
        uploadItem.progress = Math.round((e.loaded * 100) / e.total)
      }
    })
    uploadItem.status = 'success'
    uploadItem.progress = 100
    ElMessage.success(`${file.name} 上传成功`)
  } catch (error) {
    uploadItem.status = 'error'
    ElMessage.error(`${file.name} 上传失败`)
  }
}

const formatFileSize = (bytes) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
}

const getFileIcon = (fileName) => {
  const ext = fileName.split('.').pop().toLowerCase()
  if (ext === 'pdf') return 'Document'
  if (['doc', 'docx'].includes(ext)) return 'Document'
  return 'Document'
}

const getFileIconClass = (fileName) => {
  const ext = fileName.split('.').pop().toLowerCase()
  if (ext === 'pdf') return 'icon-pdf'
  if (['doc', 'docx'].includes(ext)) return 'icon-word'
  return 'icon-txt'
}
</script>

<style scoped lang="scss">
.resume-upload-page {
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
  
  &::after {
    content: '';
    position: absolute;
    bottom: -30%;
    left: -5%;
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, rgba(124, 58, 237, 0.2) 0%, transparent 70%);
    animation: headerGlow 10s ease-in-out infinite reverse;
  }
}

.header-particles {
  position: absolute;
  inset: 0;
  background-image: 
    radial-gradient(circle at 20% 50%, rgba(82, 196, 26, 0.08) 1px, transparent 1px),
    radial-gradient(circle at 80% 30%, rgba(255, 255, 255, 0.06) 1px, transparent 1px);
  background-size: 100px 100px, 150px 150px;
  animation: particleFloat 20s linear infinite;
  pointer-events: none;
}

@keyframes headerGlow {
  0%, 100% { transform: scale(1); opacity: 0.5; }
  50% { transform: scale(1.2); opacity: 0.8; }
}

@keyframes particleFloat {
  0% { transform: translateY(0) translateX(0); }
  50% { transform: translateY(-20px) translateX(10px); }
  100% { transform: translateY(0) translateX(0); }
}

.header-content {
  position: relative;
  z-index: 1;
  
  .page-title {
    font-size: 24px;
    font-weight: 700;
    color: #fff;
    margin: 0 0 8px 0;
    text-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
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
  
  .action-btn {
    height: 44px;
    padding: 0 24px;
    font-size: 15px;
    font-weight: 600;
    border-radius: var(--radius-md);
    background: rgba(255, 255, 255, 0.95);
    color: var(--primary-color);
    border: none;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    transition: var(--transition-base);
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 16px rgba(0, 0, 0, 0.03);
      background: #fff;
    }
    
    &:active {
      transform: translateY(0);
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
  transition: var(--transition-base);
  
  &:hover {
    border-color: rgba(255, 255, 255, 0.18);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25);
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--glass-border);
  
  .card-title {
    font-size: 18px;
    font-weight: 600;
    color: var(--text-primary);
    margin: 0;
  }
}

.card-badge {
  padding: 6px 14px;
  border-radius: var(--radius-sm);
  font-size: 12px;
  font-weight: 600;
  background: linear-gradient(135deg, var(--accent-color) 0%, #f97316 100%);
  color: #fff;
  box-shadow: 0 2px 8px rgba(245, 158, 11, 0.3);
  
  &.card-badge-info {
    background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
    box-shadow: 0 2px 8px rgba(30, 58, 138, 0.3);
  }
}

.upload-card {
  padding: 24px;
  margin-bottom: 24px;
  position: relative;
  overflow: hidden;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--primary-color), var(--secondary-color), var(--accent-color));
    background-size: 200% 100%;
    animation: borderFlow 3s linear infinite;
  }
}

@keyframes borderFlow {
  0% { background-position: 0% 0%; }
  100% { background-position: 200% 0%; }
}

.upload-area {
  position: relative;
  border: 2px dashed var(--glass-border);
  border-radius: var(--radius-md);
  padding: 60px 30px;
  text-align: center;
  cursor: pointer;
  transition: var(--transition-base);
  background: rgba(99, 102, 241, 0.04);
  overflow: hidden;
  
  &:hover,
  &.is-dragover {
    border-color: var(--primary-color);
    background: rgba(30, 58, 138, 0.08);
    
    .upload-icon-wrapper {
      transform: scale(1.05);
      box-shadow: 0 8px 24px rgba(30, 58, 138, 0.4);
    }
    
    .upload-glow {
      opacity: 1;
    }
  }
}

.upload-glow {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at center, rgba(30, 58, 138, 0.15) 0%, transparent 70%);
  opacity: 0;
  transition: var(--transition-slow);
  pointer-events: none;
}

.upload-icon-wrapper {
  position: relative;
  width: 96px;
  height: 96px;
  margin: 0 auto 20px;
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  transition: var(--transition-base);
  box-shadow: 0 4px 16px rgba(30, 58, 138, 0.3);
  
  &::before {
    content: '';
    position: absolute;
    inset: -4px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    opacity: 0.3;
    filter: blur(8px);
    animation: iconPulse 3s ease-in-out infinite;
  }
}

@keyframes iconPulse {
  0%, 100% { transform: scale(1); opacity: 0.3; }
  50% { transform: scale(1.1); opacity: 0.5; }
}

.upload-text {
  font-size: 16px;
  color: var(--text-primary);
  margin: 16px 0 10px;
  font-weight: 600;
}

.upload-hint {
  font-size: 13px;
  color: var(--text-tertiary);
}

.upload-actions {
  display: flex;
  gap: 16px;
  margin-top: 24px;
  justify-content: center;
}

.upload-btn {
  height: 48px;
  padding: 0 32px;
  font-size: 15px;
  font-weight: 600;
  border-radius: var(--radius-md);
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
  border: none;
  box-shadow: 0 4px 12px rgba(30, 58, 138, 0.3);
  transition: var(--transition-base);
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(30, 58, 138, 0.4);
  }
  
  &:active {
    transform: translateY(0);
  }
}

.upload-list-card {
  padding: 24px;
  position: relative;
  overflow: hidden;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--secondary-color), var(--accent-color), var(--primary-color));
    background-size: 200% 100%;
    animation: borderFlow 3s linear infinite reverse;
  }
}

.upload-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.upload-item {
  position: relative;
  padding: 20px;
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-md);
  background: rgba(99, 102, 241, 0.03);
  transition: var(--transition-base);
  animation: slideIn 0.4s ease-out backwards;
  overflow: hidden;
  
  &::after {
    content: '';
    position: absolute;
    top: 0;
    right: 0;
    width: 3px;
    height: 0;
    background: linear-gradient(180deg, var(--primary-color), var(--secondary-color));
    transition: height 0.3s ease;
  }
  
  &:hover {
    border-color: rgba(82, 196, 26, 0.15);
    background: rgba(30, 58, 138, 0.08);
    transform: translateX(4px);
    
    &::after {
      height: 100%;
    }
    
    .item-glow {
      opacity: 1;
    }
  }
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.item-glow {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at left center, rgba(30, 58, 138, 0.1) 0%, transparent 60%);
  opacity: 0;
  transition: var(--transition-slow);
  pointer-events: none;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.file-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-weight: 600;
  
  &.icon-pdf {
    background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
    box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
  }
  
  &.icon-word {
    background: linear-gradient(135deg, var(--primary-color) 0%, #2563eb 100%);
    box-shadow: 0 4px 12px rgba(30, 58, 138, 0.3);
  }
  
  &.icon-txt {
    background: linear-gradient(135deg, var(--text-secondary) 0%, var(--text-tertiary) 100%);
    box-shadow: 0 4px 12px rgba(148, 163, 184, 0.3);
  }
}

.file-details {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.file-name {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 15px;
}

.file-size {
  color: var(--text-tertiary);
  font-size: 13px;
}

.file-progress-wrapper {
  margin-bottom: 12px;
}

.file-progress {
  :deep(.el-progress-bar__outer) {
    background: rgba(99, 102, 241, 0.06);
    border-radius: var(--radius-sm);
  }
  
  :deep(.el-progress-bar__inner) {
    background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
    border-radius: var(--radius-sm);
    transition: width 0.3s ease;
  }
  
  :deep(.el-progress__text) {
    color: var(--text-secondary);
    font-size: 12px;
  }
}

.file-status {
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
}

.status-uploading {
  color: var(--primary-color);
  display: flex;
  align-items: center;
  gap: 6px;
  
  .rotating {
    animation: rotate 1s linear infinite;
  }
}

.status-success {
  color: var(--success-color);
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-error {
  color: var(--danger-color);
  display: flex;
  align-items: center;
  gap: 6px;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes successPulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.status-success {
  animation: successPulse 0.5s ease;
}
</style>
