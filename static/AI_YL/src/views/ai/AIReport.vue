<template>
  <div class="ai-report-page">
    <div class="page-header">
      <el-button text @click="$router.push('/ai-center')" class="back-btn">
        <el-icon><ArrowLeft /></el-icon>
        <span>返回 AI 中心</span>
      </el-button>
      <h1 class="page-title">智能报告</h1>
      <p class="page-subtitle">一键生成招聘数据分析报告</p>
    </div>

    <div class="page-content">
      <el-row :gutter="20">
        <el-col :xs="24" :md="8">
          <div class="form-card glass-card">
            <h3 class="card-title">报告配置</h3>
            <el-form :model="form" label-position="top">
              <el-form-item label="报告类型">
                <el-select v-model="form.reportType" placeholder="请选择报告类型" style="width: 100%">
                  <el-option label="招聘周报" value="weekly" />
                  <el-option label="招聘月报" value="monthly" />
                  <el-option label="岗位分析报告" value="jobAnalysis" />
                  <el-option label="候选人分析报告" value="candidateAnalysis" />
                </el-select>
              </el-form-item>
              <el-form-item label="时间范围">
                <el-date-picker
                  v-model="form.dateRange"
                  type="daterange"
                  range-separator="至"
                  start-placeholder="开始日期"
                  end-placeholder="结束日期"
                  style="width: 100%"
                />
              </el-form-item>
              <el-button type="primary" class="generate-btn" @click="handleGenerate" :loading="loading">
                <el-icon><MagicStick /></el-icon>
                <span>生成报告</span>
              </el-button>
            </el-form>
          </div>
        </el-col>

        <el-col :xs="24" :md="16">
          <div class="result-card glass-card" v-if="result">
            <div class="result-header">
              <h3 class="card-title">{{ result.title }}</h3>
              <span class="report-period">报告周期: {{ result.period }}</span>
            </div>
            <div class="report-stats">
              <div class="stat-item">
                <span class="stat-label">新增简历</span>
                <span class="stat-value">{{ result.newResumes }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">匹配次数</span>
                <span class="stat-value">{{ result.matchCount }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">平均匹配分</span>
                <span class="stat-value">{{ result.avgScore }}</span>
              </div>
            </div>
            <div class="report-content" v-html="result.content"></div>
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
import { ref, reactive } from 'vue'
import { aiApi } from '@/api'
import { ElMessage } from 'element-plus'
import { ArrowLeft, MagicStick } from '@element-plus/icons-vue'

const loading = ref(false)
const result = ref(null)

const form = reactive({
  reportType: 'weekly',
  dateRange: null
})

const handleGenerate = async () => {
  if (!form.reportType) {
    ElMessage.warning('请选择报告类型')
    return
  }
  loading.value = true
  try {
    const res = await aiApi.generateReport(form)
    result.value = res.data
    ElMessage.success('报告生成成功')
  } catch (error) {
    ElMessage.error('报告生成失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped lang="scss">
.ai-report-page {
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
  .result-header {
    margin-bottom: 20px;

    .card-title {
      font-size: 18px;
      font-weight: 600;
      color: var(--text-primary);
      margin: 0 0 8px 0;
    }

    .report-period {
      font-size: 13px;
      color: var(--text-secondary);
    }
  }

  .report-stats {
    display: flex;
    gap: 16px;
    margin-bottom: 24px;

    .stat-item {
      flex: 1;
      padding: 16px;
      background: var(--primary-glow);
      border-radius: var(--radius-md);
      text-align: center;

      .stat-label {
        display: block;
        font-size: 13px;
        color: var(--text-secondary);
        margin-bottom: 8px;
      }

      .stat-value {
        display: block;
        font-size: 24px;
        font-weight: 700;
        color: var(--primary-color);
      }
    }
  }

  .report-content {
    font-size: 14px;
    line-height: 1.8;
    color: var(--text-primary);
  }
}

.empty-card {
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
