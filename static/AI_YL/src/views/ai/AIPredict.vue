<template>
  <div class="ai-predict-page">
    <div class="page-header">
      <el-button text @click="$router.push('/ai-center')" class="back-btn">
        <el-icon><ArrowLeft /></el-icon>
        <span>返回 AI 中心</span>
      </el-button>
      <h1 class="page-title">人才预测</h1>
      <p class="page-subtitle">根据岗位需求推荐最合适的候选人</p>
    </div>

    <div class="page-content">
      <el-row :gutter="20">
        <el-col :xs="24" :md="6">
          <div class="form-card glass-card">
            <h3 class="card-title">预测配置</h3>
            <el-form :model="form" label-position="top">
              <el-form-item label="选择岗位">
                <el-select v-model="form.jobId" placeholder="请选择岗位" style="width: 100%">
                  <el-option v-for="job in jobs" :key="job.id" :label="job.name" :value="job.id" />
                </el-select>
              </el-form-item>
              <el-form-item label="推荐数量">
                <el-select v-model="form.topN" placeholder="请选择数量" style="width: 100%">
                  <el-option :key="3" :label="3" :value="3" />
                  <el-option :key="5" :label="5" :value="5" />
                  <el-option :key="10" :label="10" :value="10" />
                </el-select>
              </el-form-item>
              <el-button type="primary" class="generate-btn" @click="handlePredict" :loading="loading">
                <el-icon><MagicStick /></el-icon>
                <span>开始预测</span>
              </el-button>
            </el-form>
          </div>
        </el-col>

        <el-col :xs="24" :md="18">
          <div class="result-card glass-card" v-if="result && result.length > 0">
            <h3 class="result-title">推荐候选人列表</h3>
            <el-table :data="result" border :highlight-current-row="true">
              <el-table-column label="排名" width="80">
                <template #default="scope">
                  <span class="rank-badge" :class="getRankClass(scope.$index)">{{ scope.$index + 1 }}</span>
                </template>
              </el-table-column>
              <el-table-column label="候选人" width="150">
                <template #default="scope">
                  <div class="candidate-info">
                    <span class="candidate-name">{{ scope.row.name }}</span>
                    <span class="candidate-position">{{ scope.row.targetPosition }}</span>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="匹配度">
                <template #default="scope">
                  <el-progress :percentage="scope.row.matchScore" :color="getMatchColor(scope.row.matchScore)" :show-text="false" />
                </template>
              </el-table-column>
              <el-table-column label="入职意愿">
                <template #default="scope">
                  <el-progress :percentage="scope.row.joinWillingness" :color="getPredictColor(scope.row.joinWillingness)" :show-text="false" />
                </template>
              </el-table-column>
              <el-table-column label="稳定性" width="120">
                <template #default="scope">
                  <el-tag :type="getStabilityType(scope.row.stabilityScore)">{{ scope.row.stabilityScore }}%</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="预期在职时长" width="150">
                <template #default="scope">
                  <span class="tenure">{{ scope.row.expectedTenure }}</span>
                </template>
              </el-table-column>
              <el-table-column label="优势" width="200">
                <template #default="scope">
                  <el-tag v-for="(f, idx) in scope.row.positiveFactors.slice(0, 2)" :key="idx" type="success" size="small">{{ f }}</el-tag>
                </template>
              </el-table-column>
            </el-table>
          </div>
          <div class="empty-card glass-card" v-else>
            <el-empty description="选择岗位后点击预测获取推荐" />
          </div>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { aiApi, jobApi } from '@/api'
import { ElMessage } from 'element-plus'
import { ArrowLeft, MagicStick } from '@element-plus/icons-vue'

const jobs = ref([])
const loading = ref(false)
const result = ref(null)

const form = reactive({
  jobId: null,
  topN: 5
})

const fetchJobs = async () => {
  try {
    const res = await jobApi.getJobList({ page: 1, pageSize: 100 })
    jobs.value = res.data.list || []
  } catch (error) {
    console.error('获取岗位列表失败')
  }
}

const handlePredict = async () => {
  if (!form.jobId) {
    ElMessage.warning('请选择岗位')
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

const getMatchColor = (score) => {
  if (score >= 80) return '#10B981'
  if (score >= 60) return '#3B82F6'
  if (score >= 40) return '#F59E0B'
  return '#EF4444'
}

const getRankClass = (index) => {
  if (index === 0) return 'rank-gold'
  if (index === 1) return 'rank-silver'
  if (index === 2) return 'rank-bronze'
  return 'rank-normal'
}

const getStabilityType = (score) => {
  if (score >= 80) return 'success'
  if (score >= 60) return 'warning'
  return 'danger'
}

onMounted(() => {
  fetchJobs()
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
  .result-title {
    font-size: 16px;
    font-weight: 600;
    color: var(--text-primary);
    margin: 0 0 16px 0;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--card-border);
  }

  .rank-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    font-size: 12px;
    font-weight: 600;
    
    &.rank-gold {
      background: linear-gradient(135deg, #FFD700, #FFA500);
      color: #fff;
    }
    
    &.rank-silver {
      background: linear-gradient(135deg, #C0C0C0, #A8A8A8);
      color: #fff;
    }
    
    &.rank-bronze {
      background: linear-gradient(135deg, #CD7F32, #B87333);
      color: #fff;
    }
    
    &.rank-normal {
      background: var(--primary-glow);
      color: var(--text-secondary);
    }
  }

  .candidate-info {
    display: flex;
    flex-direction: column;
    
    .candidate-name {
      font-size: 14px;
      font-weight: 600;
      color: var(--text-primary);
    }
    
    .candidate-position {
      font-size: 12px;
      color: var(--text-secondary);
    }
  }

  .tenure {
    font-size: 13px;
    color: var(--primary-color);
    font-weight: 500;
  }
}

.empty-card {
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
