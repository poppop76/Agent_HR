<template>
  <div class="matching-page">
    <div class="page-header">
      <div class="header-particles"></div>
      <div class="header-content">
        <h1 class="page-title">人岗匹配分析</h1>
        <p class="page-subtitle">AI驱动的智能匹配，精准评估候选人与岗位匹配度</p>
      </div>
      <div class="header-actions">
        <el-tooltip placement="bottom" effect="light">
          <template #content>
            <div class="weight-tooltip">
              <h4>匹配权重说明</h4>
              <p>系统采用固定权重配置：技能40%、经验30%、学历20%、项目10%</p>
            </div>
          </template>
          <el-button size="large" class="info-btn">
            <el-icon><InfoFilled /></el-icon>
            <span>权重说明</span>
          </el-button>
        </el-tooltip>
      </div>
    </div>
    
    <div class="page-content">
      <div class="matching-card glass-card">
        <el-form :model="matchingForm" label-width="120px" class="matching-form">
          <el-form-item label="目标岗位">
            <el-select v-model="matchingForm.jobId" placeholder="请选择目标岗位" class="custom-select">
              <el-option v-for="job in jobs" :key="job.id" :label="job.name" :value="job.id" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="候选人">
            <el-select v-model="matchingForm.candidateIds" multiple placeholder="请选择候选人" class="custom-select">
              <el-option v-for="candidate in candidates" :key="candidate.id" :label="candidate.name" :value="candidate.id" />
            </el-select>
          </el-form-item>
          
          <el-form-item>
            <el-button type="primary" size="large" :loading="loading" class="matching-btn" @click="handleMatching">
              <el-icon><Connection /></el-icon>
              <span v-if="!loading">开始智能匹配</span>
              <span v-else>AI匹配中...</span>
            </el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <div v-if="matchingResults.length > 0" class="results-card glass-card">
        <div class="results-header">
          <h3 class="subsection-title">匹配结果</h3>
          <span class="result-count">{{ matchingResults.length }} 位候选人</span>
        </div>
        <el-table :data="matchingResults" style="width: 100%" class="glass-table">
          <el-table-column prop="candidateName" label="候选人" />
          <el-table-column prop="totalScore" label="总分" width="120">
            <template #default="{ row }">
              <div class="score-display">
                <span :class="getScoreClass(row.totalScore)">{{ row.totalScore }}</span>
                <span class="score-label">分</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="skillScore" label="技能匹配" width="140">
            <template #default="{ row }">
              <div class="progress-wrapper">
                <div class="progress-bar">
                  <div class="progress-fill" :style="{ width: row.skillScore + '%', background: getProgressGradient(row.skillScore) }"></div>
                </div>
                <span class="progress-text">{{ row.skillScore }}%</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="experienceScore" label="经验匹配" width="140">
            <template #default="{ row }">
              <div class="progress-wrapper">
                <div class="progress-bar">
                  <div class="progress-fill" :style="{ width: row.experienceScore + '%', background: getProgressGradient(row.experienceScore) }"></div>
                </div>
                <span class="progress-text">{{ row.experienceScore }}%</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="educationScore" label="学历匹配" width="140">
            <template #default="{ row }">
              <div class="progress-wrapper">
                <div class="progress-bar">
                  <div class="progress-fill" :style="{ width: row.educationScore + '%', background: getProgressGradient(row.educationScore) }"></div>
                </div>
                <span class="progress-text">{{ row.educationScore }}%</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="projectScore" label="项目匹配" width="140">
            <template #default="{ row }">
              <div class="progress-wrapper">
                <div class="progress-bar">
                  <div class="progress-fill" :style="{ width: row.projectScore + '%', background: getProgressGradient(row.projectScore) }"></div>
                </div>
                <span class="progress-text">{{ row.projectScore }}%</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="180">
            <template #default="{ row }">
              <el-button size="small" type="primary" class="action-btn-small" @click="router.push(`/matching/report/${row.id}`)">
                查看报告
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { matchingApi, jobApi, resumeApi } from '@/api'
import { ElMessage } from 'element-plus'
import { Connection, InfoFilled } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()

const jobs = ref([])
const candidates = ref([])
const matchingResults = ref([])
const loading = ref(false)

const matchingForm = reactive({
  jobId: '',
  candidateIds: []
})

const getScoreClass = (score) => {
  if (score >= 80) return 'score-excellent'
  if (score >= 60) return 'score-good'
  if (score >= 40) return 'score-average'
  return 'score-poor'
}

const getProgressGradient = (score) => {
  if (score >= 80) return 'linear-gradient(90deg, #10B981, #34D399)'
  if (score >= 60) return 'linear-gradient(90deg, #2563EB, #3B82F6)'
  if (score >= 40) return 'linear-gradient(90deg, #F59E0B, #FBBF24)'
  return 'linear-gradient(90deg, #E11D48, #FB7185)'
}

const fetchJobs = async () => {
  try {
    const res = await jobApi.getJobList({ pageSize: 100 })
    jobs.value = res.data.list
  } catch (error) {
    console.error('获取岗位列表失败')
  }
}

// 获取候选人列表（从简历列表获取）
const fetchCandidates = async () => {
  try {
    const res = await resumeApi.getResumeList({ pageSize: 100 })
    candidates.value = res.data.list || []
  } catch (error) {
    console.error('获取候选人列表失败')
  }
}

const handleMatching = async () => {
  if (!matchingForm.jobId) {
    ElMessage.warning('请选择目标岗位')
    return
  }
  if (matchingForm.candidateIds.length === 0) {
    ElMessage.warning('请选择候选人')
    return
  }
  
  loading.value = true
  try {
    const res = await matchingApi.performMatching({
      jobId: matchingForm.jobId,
      candidateIds: matchingForm.candidateIds
    })
    matchingResults.value = res.data
    ElMessage.success('匹配完成')
  } catch (error) {
    ElMessage.error('匹配失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchJobs()
  fetchCandidates()
  
  if (route.query.jobId) {
    matchingForm.jobId = route.query.jobId
  }
  if (route.query.resumeId) {
    matchingForm.candidateIds = [route.query.resumeId]
  }
})
</script>

<style scoped lang="scss">
.matching-page {
  min-height: 100%;
  background: transparent;
}

.page-header {
  background: var(--gradient-primary);
  padding: 32px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
  overflow: hidden;
  margin-bottom: 24px;
  
  &::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -10%;
    width: 120%;
    height: 200%;
    background: radial-gradient(ellipse at 30% 50%, rgba(255,255,255,0.1) 0%, transparent 60%);
    pointer-events: none;
  }
  
  &::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
  }
}

.header-particles {
  position: absolute;
  inset: 0;
  background-image: 
    radial-gradient(circle at 20% 30%, rgba(255,255,255,0.08) 1px, transparent 1px),
    radial-gradient(circle at 80% 70%, rgba(255,255,255,0.06) 1px, transparent 1px);
  background-size: 80px 80px, 120px 120px;
  animation: particlesFloat 15s linear infinite;
  pointer-events: none;
}

@keyframes particlesFloat {
  0% { transform: translateY(0); }
  100% { transform: translateY(-50px); }
}

.header-content {
  position: relative;
  z-index: 1;
  
  .page-title {
    font-size: 24px;
    font-weight: 700;
    color: #fff;
    margin: 0 0 8px 0;
    text-shadow: 0 2px 8px rgba(0,0,0,0.2);
  }
  
  .page-subtitle {
    font-size: 14px;
    color: rgba(255, 255, 255, 0.9);
    margin: 0;
  }
}

.header-actions {
  position: relative;
  z-index: 1;
  display: flex;
  gap: 12px;
  
  .info-btn {
    height: 44px;
    padding: 0 24px;
    font-size: 14px;
    font-weight: 600;
    border-radius: var(--radius-md);
    background: rgba(255, 255, 255, 0.15);
    color: #fff;
    border: 1px solid rgba(255, 255, 255, 0.3);
    backdrop-filter: blur(8px);
    transition: var(--transition-base);
    display: flex;
    align-items: center;
    gap: 8px;
    
    &:hover {
      background: rgba(255, 255, 255, 0.25);
      transform: translateY(-2px);
    }
  }
  
  .action-btn {
    height: 44px;
    padding: 0 24px;
    font-size: 14px;
    font-weight: 600;
    border-radius: var(--radius-md);
    background: rgba(255, 255, 255, 0.95);
    color: var(--primary-color);
    border: none;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    transition: var(--transition-base);
    display: flex;
    align-items: center;
    gap: 8px;
    
    &:hover {
      background: #fff;
      transform: translateY(-2px);
      box-shadow: 0 6px 16px rgba(0,0,0,0.2);
    }
    
    &:active {
      transform: translateY(0) scale(0.98);
    }
  }
}

.page-content {
  padding: 0 24px 24px;
}

.glass-card {
  background: var(--gradient-card);
  backdrop-filter: blur(12px);
  border-radius: var(--radius-lg);
  box-shadow: var(--card-shadow);
  border: 1px solid var(--card-border);
  padding: 24px;
  margin-bottom: 24px;
  transition: var(--transition-base);
  
  &:hover {
    box-shadow: var(--card-shadow-hover);
    border-color: var(--card-border-glow);
  }
}

.matching-form {
  max-width: 800px;
  
  :deep(.el-form-item__label) {
    font-size: 14px;
    font-weight: 500;
    color: var(--text-secondary);
  }
}

.custom-select {
  width: 100%;
  
  :deep(.el-select__wrapper) {
    background: rgba(255, 255, 255, 0.06);
    backdrop-filter: blur(8px);
    border-radius: var(--radius-md);
    box-shadow: none;
    border: 1px solid var(--card-border);
    transition: var(--transition-base);
    
    &:hover {
      border-color: var(--card-border-glow);
      background: rgba(82, 196, 26, 0.08);
    }
    
    &.is-focus {
      border-color: var(--primary-color);
      box-shadow: 0 0 0 2px var(--primary-glow);
      background: rgba(82, 196, 26, 0.1);
    }
    
    .el-select__input {
      color: var(--text-primary);
      font-size: 14px;
    }
  }
}

.matching-btn {
  height: 48px;
  padding: 0 40px;
  font-size: 15px;
  font-weight: 600;
  border-radius: var(--radius-md);
  background: var(--gradient-primary);
  border: none;
  box-shadow: 0 4px 12px var(--primary-glow);
  transition: var(--transition-base);
  display: flex;
  align-items: center;
  gap: 8px;
  
  &:hover {
    box-shadow: 0 6px 16px var(--primary-glow);
    transform: translateY(-2px);
  }
  
  &:active {
    transform: translateY(0) scale(0.98);
  }
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.subsection-title {
  font-size: 18px;
  color: var(--text-primary);
  margin: 0;
  font-weight: 600;
}

.result-count {
  padding: 6px 16px;
  background: rgba(16, 185, 129, 0.15);
  color: var(--success-color);
  border-radius: var(--radius-full);
  font-size: 13px;
  font-weight: 600;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.glass-table {
  :deep(.el-table__header) {
    th {
      background: rgba(255, 255, 255, 0.04);
      color: var(--text-secondary);
      font-weight: 600;
      font-size: 14px;
      border: none;
      border-bottom: 1px solid var(--card-border);
    }
  }
  
  :deep(.el-table__body) {
    tr {
      transition: var(--transition-base);
      
      &:hover {
        background: rgba(255, 255, 255, 0.06) !important;
        
        td {
          border-bottom-color: var(--card-border-glow);
        }
      }
    }
    
    td {
      font-size: 14px;
      color: var(--text-secondary);
      border: none;
      border-bottom: 1px solid var(--card-border);
      padding: 14px 0;
    }
  }
  
  :deep(.el-table__inner-wrapper) {
    border-collapse: separate;
  }
}

.score-display {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.score-label {
  font-size: 12px;
  color: var(--text-tertiary);
}

.score-excellent {
  font-size: 20px;
  font-weight: 700;
  color: var(--success-color);
}

.score-good {
  font-size: 20px;
  font-weight: 700;
  color: var(--primary-light);
}

.score-average {
  font-size: 20px;
  font-weight: 700;
  color: var(--accent-color);
}

.score-poor {
  font-size: 20px;
  font-weight: 700;
  color: var(--danger-color);
}

.progress-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background: rgba(82, 196, 26, 0.08);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: var(--radius-full);
  transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.progress-text {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  min-width: 40px;
  text-align: right;
}

.action-btn-small {
  border-radius: var(--radius-md);
  padding: 8px 16px;
  font-size: 13px;
  font-weight: 600;
  transition: var(--transition-base);
  height: 32px;
  
  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  }
  
  &:active {
    transform: translateY(0) scale(0.98);
  }
}

.weight-tooltip {
  padding: 8px 0;
  min-width: 240px;
  
  h4 {
    margin: 0 0 8px;
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary);
  }
  
  p {
    margin: 0;
    font-size: 13px;
    color: var(--text-secondary);
    line-height: 1.6;
  }
}
</style>
