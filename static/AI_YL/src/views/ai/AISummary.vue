<template>
  <div class="ai-summary-page">
    <div class="page-header">
      <el-button text @click="$router.push('/ai-center')" class="back-btn">
        <el-icon><ArrowLeft /></el-icon>
        <span>返回 AI 中心</span>
      </el-button>
      <h1 class="page-title">简历智能摘要</h1>
      <p class="page-subtitle">自动生成候选人核心优势和关键信息</p>
    </div>

    <div class="page-content">
      <el-row :gutter="20">
        <el-col :xs="24" :md="8">
          <div class="form-card glass-card">
            <h3 class="card-title">生成配置</h3>
            <el-form :model="form" label-position="top">
              <el-form-item label="选择候选人">
                <el-select v-model="form.candidateId" placeholder="请选择候选人" style="width: 100%">
                  <el-option v-for="c in candidates" :key="c.id" :label="c.name" :value="c.id" />
                </el-select>
              </el-form-item>
              <el-form-item label="摘要长度">
                <el-radio-group v-model="form.summaryLength">
                  <el-radio-button label="short">简短</el-radio-button>
                  <el-radio-button label="medium">适中</el-radio-button>
                  <el-radio-button label="long">详细</el-radio-button>
                </el-radio-group>
              </el-form-item>
              <el-button type="primary" class="generate-btn" @click="handleGenerate" :loading="loading">
                <el-icon><MagicStick /></el-icon>
                <span>生成简历摘要</span>
              </el-button>
            </el-form>
          </div>
        </el-col>

        <el-col :xs="24" :md="16">
          <div class="result-card glass-card" v-if="result">
            <div class="summary-text">{{ result.summary }}</div>
            <el-row :gutter="16" style="margin-top: 20px">
              <el-col :span="12">
                <div class="info-section">
                  <h4>核心优势</h4>
                  <el-tag v-for="(s, idx) in result.coreStrengths" :key="idx" type="success" class="info-tag">{{ s }}</el-tag>
                </div>
              </el-col>
              <el-col :span="12">
                <div class="info-section">
                  <h4>关键技能</h4>
                  <el-tag v-for="(s, idx) in result.keySkills" :key="idx" type="primary" class="info-tag">{{ s }}</el-tag>
                </div>
              </el-col>
            </el-row>
            <el-row :gutter="16" style="margin-top: 16px">
              <el-col :span="12">
                <div class="info-section">
                  <h4>经验亮点</h4>
                  <el-tag v-for="(s, idx) in result.experienceHighlights" :key="idx" type="warning" class="info-tag">{{ s }}</el-tag>
                </div>
              </el-col>
              <el-col :span="12">
                <div class="info-section">
                  <h4>潜在风险</h4>
                  <el-tag v-for="(s, idx) in result.potentialRisks" :key="idx" type="danger" class="info-tag">{{ s }}</el-tag>
                </div>
              </el-col>
            </el-row>
          </div>
          <div class="empty-card glass-card" v-else>
            <el-empty description="选择候选人后点击生成" />
          </div>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { aiApi, resumeApi } from '@/api'
import { ElMessage } from 'element-plus'
import { ArrowLeft, MagicStick } from '@element-plus/icons-vue'

const candidates = ref([])
const loading = ref(false)
const result = ref(null)

const form = reactive({
  candidateId: null,
  summaryLength: 'medium'
})

const fetchCandidates = async () => {
  try {
    const res = await resumeApi.getResumeList({ page: 1, pageSize: 100 })
    candidates.value = res.data.list || []
  } catch (error) {
    console.error('获取候选人列表失败')
  }
}

const handleGenerate = async () => {
  if (!form.candidateId) {
    ElMessage.warning('请选择候选人')
    return
  }
  loading.value = true
  try {
    const res = await aiApi.generateResumeSummary(form)
    result.value = res.data
    ElMessage.success('简历摘要生成成功')
  } catch (error) {
    ElMessage.error('生成简历摘要失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchCandidates()
})
</script>

<style scoped lang="scss">
.ai-summary-page {
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
  .summary-text {
    font-size: 15px;
    line-height: 1.8;
    color: var(--text-primary);
    padding: 16px;
    background: var(--primary-glow);
    border-radius: var(--radius-md);
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
