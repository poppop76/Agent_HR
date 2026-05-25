<template>
  <div class="ai-predict-page">
    <div class="page-header">
      <el-button text @click="$router.push('/ai-center')" class="back-btn">
        <el-icon><ArrowLeft /></el-icon>
        <span>返回 AI 中心</span>
      </el-button>
      <h1 class="page-title">人才预测</h1>
      <p class="page-subtitle">预测候选人入职意愿和稳定性</p>
    </div>

    <div class="page-content">
      <el-row :gutter="20">
        <el-col :xs="24" :md="8">
          <div class="form-card glass-card">
            <h3 class="card-title">预测配置</h3>
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
              <el-button type="primary" class="generate-btn" @click="handlePredict" :loading="loading">
                <el-icon><MagicStick /></el-icon>
                <span>开始预测</span>
              </el-button>
            </el-form>
          </div>
        </el-col>

        <el-col :xs="24" :md="16">
          <div class="result-card glass-card" v-if="result">
            <div class="predict-overview">
              <div class="predict-item">
                <span class="label">入职意愿</span>
                <el-progress :percentage="result.joinWillingness" :color="getPredictColor(result.joinWillingness)" />
              </div>
              <div class="predict-item">
                <span class="label">稳定性评分</span>
                <el-progress :percentage="result.stabilityScore" :color="getPredictColor(result.stabilityScore)" />
              </div>
              <div class="predict-item">
                <span class="label">预期在职时长</span>
                <span class="value">{{ result.expectedTenure }}</span>
              </div>
            </div>
            <el-row :gutter="16" style="margin-top: 20px">
              <el-col :span="12">
                <div class="info-section">
                  <h4>积极因素</h4>
                  <el-tag v-for="(f, idx) in result.positiveFactors" :key="idx" type="success" class="info-tag">{{ f }}</el-tag>
                </div>
              </el-col>
              <el-col :span="12">
                <div class="info-section">
                  <h4>风险因素</h4>
                  <el-tag v-for="(f, idx) in result.riskFactors" :key="idx" type="danger" class="info-tag">{{ f }}</el-tag>
                </div>
              </el-col>
            </el-row>
          </div>
          <div class="empty-card glass-card" v-else>
            <el-empty description="配置参数后点击预测" />
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

const handlePredict = async () => {
  if (!form.jobId || !form.candidateId) {
    ElMessage.warning('请选择岗位和候选人')
    return
  }
  loading.value = true
  try {
    const res = await aiApi.predictTalent(form)
    result.value = res.data
    ElMessage.success('人才预测完成')
  } catch (error) {
    ElMessage.error('人才预测失败')
  } finally {
    loading.value = false
  }
}

const getPredictColor = (score) => {
  if (score >= 70) return '#10B981'
  if (score >= 50) return '#F59E0B'
  return '#EF4444'
}

onMounted(() => {
  fetchJobs()
  fetchCandidates()
})
</script>

<style scoped lang="scss">
.ai-predict-page {
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
  .predict-overview {
    padding: 16px;
    background: var(--primary-glow);
    border-radius: var(--radius-md);

    .predict-item {
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

  .info-section {
    h4 {
      margin: 0 0 12px;
      color: var(--text-primary);
      font-size: 14px;
    }

    .info-tag {
      margin: 4px;
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
