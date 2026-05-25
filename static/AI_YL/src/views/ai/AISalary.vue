<template>
  <div class="ai-salary-page">
    <div class="page-header">
      <el-button text @click="$router.push('/ai-center')" class="back-btn">
        <el-icon><ArrowLeft /></el-icon>
        <span>返回 AI 中心</span>
      </el-button>
      <h1 class="page-title">薪资建议</h1>
      <p class="page-subtitle">基于市场数据给出薪资参考</p>
    </div>

    <div class="page-content">
      <el-row :gutter="20">
        <el-col :xs="24" :md="8">
          <div class="form-card glass-card">
            <h3 class="card-title">查询配置</h3>
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
              <el-button type="primary" class="generate-btn" @click="handleGenerate" :loading="loading">
                <el-icon><MagicStick /></el-icon>
                <span>获取薪资建议</span>
              </el-button>
            </el-form>
          </div>
        </el-col>

        <el-col :xs="24" :md="16">
          <div class="result-card glass-card" v-if="result">
            <div class="salary-overview">
              <div class="salary-item">
                <span class="label">建议薪资范围</span>
                <span class="value">{{ result.suggestedMin }} - {{ result.suggestedMax }} 元/月</span>
              </div>
              <div class="salary-item">
                <span class="label">市场平均薪资</span>
                <span class="value">{{ result.marketAverage }} 元/月</span>
              </div>
              <div class="salary-item">
                <span class="label">置信度</span>
                <el-progress :percentage="result.confidence" :color="getConfidenceColor(result.confidence)" />
              </div>
            </div>
            <div class="factors-section">
              <h4>影响因素</h4>
              <div v-for="(f, idx) in result.factors" :key="idx" class="factor-item">
                <el-tag :type="getImpactType(f.impact)" size="small">{{ f.factor }}</el-tag>
                <span class="factor-desc">{{ f.description }}</span>
              </div>
            </div>
          </div>
          <div class="empty-card glass-card" v-else>
            <el-empty description="配置参数后点击查询" />
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
  candidateId: null
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
    const res = await aiApi.getSalarySuggestion(form)
    result.value = res.data
    ElMessage.success('薪资建议获取成功')
  } catch (error) {
    ElMessage.error('获取薪资建议失败')
  } finally {
    loading.value = false
  }
}

const getConfidenceColor = (confidence) => {
  if (confidence >= 80) return '#10B981'
  if (confidence >= 60) return '#F59E0B'
  return '#EF4444'
}

const getImpactType = (impact) => {
  const map = { positive: 'success', negative: 'danger', neutral: 'info' }
  return map[impact] || 'info'
}

onMounted(() => {
  fetchJobs()
  fetchCandidates()
})
</script>

<style scoped lang="scss">
.ai-salary-page {
  min-height: 100%;
}

.page-header {
  background: var(--gradient-primary);
  padding: 24px;

  .back-btn {
    color: rgba(255, 255, 255, 0.85);
    margin-bottom: 8px;
    &:hover { color: #fff; }
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

.form-card {
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
  .salary-overview {
    padding: 16px;
    background: var(--primary-glow);
    border-radius: var(--radius-md);

    .salary-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 0;
      border-bottom: 1px solid var(--card-border);

      &:last-child {
        border-bottom: none;
      }

      .label {
        font-size: 14px;
        color: var(--text-secondary);
      }

      .value {
        font-size: 15px;
        color: var(--text-primary);
        font-weight: 600;
      }
    }
  }

  .factors-section {
    margin-top: 20px;

    h4 {
      margin: 0 0 12px;
      color: var(--text-primary);
      font-size: 14px;
    }

    .factor-item {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 8px 0;

      .factor-desc {
        font-size: 14px;
        color: var(--text-secondary);
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
