<template>
  <div class="ai-center-page">
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">AI 智能中心</h1>
        <p class="page-subtitle">基于大语言模型的智能招聘助手</p>
      </div>
    </div>

    <div class="page-content">
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :md="8" v-for="feature in features" :key="feature.path">
          <div class="feature-card glass-card" @click="$router.push(feature.path)">
            <div class="card-icon" :style="{ background: feature.gradient }">
              <el-icon :size="28"><component :is="feature.icon" /></el-icon>
            </div>
            <h3 class="card-title">{{ feature.title }}</h3>
            <p class="card-desc">{{ feature.desc }}</p>
            <div class="card-arrow">
              <el-icon :size="16"><ArrowRight /></el-icon>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ChatDotRound, ChatLineRound, Notebook, Document, Money, TrendCharts, Sort, ArrowRight } from '@element-plus/icons-vue'

const features = [
  {
    title: 'AI 面试助手',
    desc: '根据岗位和候选人智能生成面试问题',
    icon: ChatDotRound,
    path: '/ai-center/interview',
    gradient: 'linear-gradient(135deg, #10B981, #059669)'
  },
  {
    title: 'AI 对话查询',
    desc: '用自然语言查询候选人和岗位信息',
    icon: ChatLineRound,
    path: '/ai-center/chat',
    gradient: 'linear-gradient(135deg, #6366F1, #4F46E5)'
  },
  {
    title: '智能报告',
    desc: '一键生成招聘数据分析报告',
    icon: Notebook,
    path: '/ai-center/report',
    gradient: 'linear-gradient(135deg, #F59E0B, #D97706)'
  },
  {
    title: '简历摘要',
    desc: '自动生成候选人核心优势摘要',
    icon: Document,
    path: '/ai-center/summary',
    gradient: 'linear-gradient(135deg, #EC4899, #DB2777)'
  },
  {
    title: '薪资建议',
    desc: '基于市场数据给出薪资参考',
    icon: Money,
    path: '/ai-center/salary',
    gradient: 'linear-gradient(135deg, #3B82F6, #2563EB)'
  },
  {
    title: '人才预测',
    desc: '预测候选人入职意愿和稳定性',
    icon: TrendCharts,
    path: '/ai-center/predict',
    gradient: 'linear-gradient(135deg, #8B5CF6, #7C3AED)'
  }
]
</script>

<style scoped lang="scss">
.ai-center-page {
  min-height: 100%;
}

.page-header {
  background: var(--gradient-primary);
  padding: 32px 24px;
  
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

.feature-card {
  background: var(--card-bg);
  backdrop-filter: var(--card-blur);
  border: 1px solid var(--card-border);
  border-radius: var(--radius-lg);
  padding: 24px;
  cursor: pointer;
  transition: var(--transition-base);
  position: relative;
  margin-bottom: 20px;
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: var(--card-shadow-hover);
    border-color: var(--card-border-glow);
    
    .card-arrow {
      opacity: 1;
      transform: translateX(0);
    }
  }
  
  .card-icon {
    width: 52px;
    height: 52px;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    margin-bottom: 16px;
  }
  
  .card-title {
    font-size: 16px;
    font-weight: 600;
    color: var(--text-primary);
    margin: 0 0 8px 0;
  }
  
  .card-desc {
    font-size: 13px;
    color: var(--text-secondary);
    margin: 0;
    line-height: 1.5;
  }
  
  .card-arrow {
    position: absolute;
    right: 20px;
    top: 50%;
    transform: translateY(-50%) translateX(8px);
    color: var(--primary-color);
    opacity: 0;
    transition: var(--transition-base);
  }
}
</style>
