<template>
  <div class="ai-interview-page">
    <div class="page-header">
      <el-button text @click="$router.push('/ai-center')" class="back-btn">
        <el-icon><ArrowLeft /></el-icon>
        <span>返回 AI 中心</span>
      </el-button>
      <h1 class="page-title">AI 面试助手</h1>
      <p class="page-subtitle">根据岗位和候选人智能生成面试问题</p>
    </div>

    <div class="page-content">
      <el-row :gutter="20">
        <el-col :xs="24" :md="10">
          <div class="form-card glass-card">
            <h3 class="card-title">生成配置</h3>
            <el-form :model="form" label-position="top">
              <el-form-item label="选择岗位">
                <el-select v-model="form.jobId" placeholder="请选择岗位" style="width: 100%">
                  <el-option v-for="job in jobs" :key="job.id" :label="job.name" :value="job.id" />
                </el-select>
              </el-form-item>
              <el-form-item label="选择候选人">
                <el-select v-model="form.candidateId" placeholder="请选择候选人" style="width: 100%">
                  <el-option v-for="c in candidates" :key="c.id" :label="c.name" :value="c.id" />
                </el-select>
              </el-form-item>
              <el-form-item label="问题数量">
                <el-slider v-model="form.questionCount" :min="5" :max="20" :step="5" show-stops />
              </el-form-item>
              <el-form-item label="问题类型">
                <el-checkbox-group v-model="form.questionTypes">
                  <el-checkbox label="technical">技术能力</el-checkbox>
                  <el-checkbox label="behavioral">行为面试</el-checkbox>
                  <el-checkbox label="experience">项目经验</el-checkbox>
                  <el-checkbox label="cultural">文化匹配</el-checkbox>
                </el-checkbox-group>
              </el-form-item>
              <el-button type="primary" class="generate-btn" @click="handleGenerate" :loading="loading">
                <el-icon><MagicStick /></el-icon>
                <span>生成面试问题</span>
              </el-button>
            </el-form>
          </div>
        </el-col>

        <el-col :xs="24" :md="14">
          <div class="result-card glass-card" v-if="result">
            <h3 class="card-title">面试问题</h3>
            <div v-for="(q, index) in result.questions" :key="index" class="question-item">
              <div class="question-header">
                <el-tag :type="getDifficultyType(q.difficulty)" size="small">{{ getDifficultyText(q.difficulty) }}</el-tag>
                <el-tag type="info" size="small">{{ getQuestionTypeText(q.type) }}</el-tag>
                <span class="question-text">问题 {{ index + 1 }}: {{ q.question }}</span>
              </div>
              <div class="evaluation-points">
                <span class="label">评估要点:</span>
                <el-tag v-for="(point, idx) in q.evaluationPoints" :key="idx" size="small" effect="plain">{{ point }}</el-tag>
              </div>
            </div>
            <div class="suggestions" v-if="result.suggestions">
              <h4>面试建议</h4>
              <ul>
                <li v-for="(s, idx) in result.suggestions" :key="idx">{{ s }}</li>
              </ul>
            </div>
          </div>
          <div class="empty-card glass-card" v-else>
            <el-empty description="配置参数后点击生成" />
          </div>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { aiApi, jobApi, resumeApi } from '@/api'
import { ElMessage } from 'element-plus'
import { ArrowLeft, MagicStick } from '@element-plus/icons-vue'

const jobs = ref([])
const candidates = ref([])
const loading = ref(false)
const result = ref(null)

const form = reactive({
  jobId: null,
  candidateId: null,
  questionCount: 10,
  questionTypes: ['technical', 'behavioral', 'experience']
})

const fetchJobs = async () => {
  try {
    const res = await jobApi.getJobList({ page: 1, pageSize: 100 })
    jobs.value = res.data.list || []
  } catch (error) {
    console.error('获取岗位列表失败')
  }
}

const fetchCandidates = async () => {
  try {
    const res = await resumeApi.getResumeList({ page: 1, pageSize: 100 })
    candidates.value = res.data.list || []
  } catch (error) {
    console.error('获取候选人列表失败')
  }
}

const handleGenerate = async () => {
  if (!form.jobId || !form.candidateId) {
    ElMessage.warning('请选择岗位和候选人')
    return
  }
  loading.value = true
  try {
    const res = await aiApi.generateInterviewQuestions(form)
    result.value = res.data
    ElMessage.success('面试问题生成成功')
  } catch (error) {
    ElMessage.error('生成面试问题失败')
  } finally {
    loading.value = false
  }
}

const getDifficultyType = (difficulty) => {
  const map = { easy: 'success', medium: 'warning', hard: 'danger' }
  return map[difficulty] || 'info'
}

const getDifficultyText = (difficulty) => {
  const map = { easy: '简单', medium: '中等', hard: '困难' }
  return map[difficulty] || difficulty
}

const getQuestionTypeText = (type) => {
  const map = { technical: '技术能力', behavioral: '行为面试', experience: '项目经验', cultural: '文化匹配' }
  return map[type] || type
}

onMounted(() => {
  fetchJobs()
  fetchCandidates()
})
</script>

<style scoped lang="scss">
.ai-interview-page {
  min-height: 100%;
}

.page-header {
  background: var(--gradient-primary);
  padding: 24px;
  position: relative;
  
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

.glass-card {
  background: var(--card-bg);
  backdrop-filter: var(--card-blur);
  border: 1px solid var(--card-border);
  border-radius: var(--radius-lg);
  padding: 24px;
}

.form-card, .result-card {
  .card-title {
    font-size: 16px;
    font-weight: 600;
    color: var(--text-primary);
    margin: 0 0 20px 0;
  }
  
  .generate-btn {
    width: 100%;
    height: 44px;
    font-size: 15px;
    font-weight: 600;
    border-radius: var(--radius-md);
    margin-top: 8px;
  }
}

.result-card {
  .question-item {
    padding: 16px;
    background: var(--primary-glow);
    border-radius: var(--radius-md);
    margin-bottom: 12px;
    
    .question-header {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 12px;
      
      .question-text {
        font-size: 14px;
        color: var(--text-primary);
        font-weight: 500;
      }
    }
    
    .evaluation-points {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
      
      .label {
        font-size: 13px;
        color: var(--text-secondary);
      }
    }
  }
  
  .suggestions {
    margin-top: 20px;
    padding: 16px;
    background: var(--primary-glow);
    border-radius: var(--radius-md);
    
    h4 {
      margin: 0 0 12px;
      color: var(--text-primary);
    }
    
    ul {
      margin: 0;
      padding-left: 20px;
      
      li {
        color: var(--text-secondary);
        margin-bottom: 8px;
      }
    }
  }
}

.empty-card {
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
