<template>
  <div class="metrics-dashboard">
    <div class="page-header">
      <div class="header-left">
        <el-button text @click="$router.push('/ai-center')" class="back-btn">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <div class="title-group">
          <h1 class="page-title">AI 系统监控</h1>
          <p class="page-subtitle">实时监控 AI 系统性能和质量指标</p>
        </div>
      </div>
    </div>

    <!-- 质量指标卡片 -->
    <div class="metrics-cards">
      <div class="metric-card recall-card">
        <div class="card-icon">
          <el-icon><Search /></el-icon>
        </div>
        <div class="card-content">
          <div class="card-label">召回率</div>
          <div class="card-value">{{ formatPercent(qualityMetrics.avg_recall_rate) }}</div>
          <div class="card-trend">
            <el-icon v-if="recallTrend >= 0" class="trend-up"><CaretTop /></el-icon>
            <el-icon v-else class="trend-down"><CaretBottom /></el-icon>
            {{ Math.abs(recallTrend).toFixed(1) }}%
          </div>
        </div>
      </div>

      <div class="metric-card hallucination-card">
        <div class="card-icon">
          <el-icon><Warning /></el-icon>
        </div>
        <div class="card-content">
          <div class="card-label">幻觉率</div>
          <div class="card-value">{{ formatPercent(qualityMetrics.avg_hallucination_rate) }}</div>
          <div class="card-trend">
            <el-icon v-if="hallucinationTrend <= 0" class="trend-up"><CaretTop /></el-icon>
            <el-icon v-else class="trend-down"><CaretBottom /></el-icon>
            {{ Math.abs(hallucinationTrend).toFixed(1) }}%
          </div>
        </div>
      </div>

      <div class="metric-card accuracy-card">
        <div class="card-icon">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="card-content">
          <div class="card-label">准确率</div>
          <div class="card-value">{{ formatPercent(qualityMetrics.avg_accuracy) }}</div>
          <div class="card-trend">
            <el-icon v-if="accuracyTrend >= 0" class="trend-up"><CaretTop /></el-icon>
            <el-icon v-else class="trend-down"><CaretBottom /></el-icon>
            {{ Math.abs(accuracyTrend).toFixed(1) }}%
          </div>
        </div>
      </div>

      <div class="metric-card rating-card">
        <div class="card-icon">
          <el-icon><Star /></el-icon>
        </div>
        <div class="card-content">
          <div class="card-label">用户评分</div>
          <div class="card-value">{{ qualityMetrics.avg_user_rating.toFixed(1) }}</div>
          <div class="card-trend">
            <el-icon v-if="ratingTrend >= 0" class="trend-up"><CaretTop /></el-icon>
            <el-icon v-else class="trend-down"><CaretBottom /></el-icon>
            {{ Math.abs(ratingTrend).toFixed(1) }}
          </div>
        </div>
      </div>
    </div>

    <!-- Token使用统计 -->
    <div class="token-section">
      <div class="section-header">
        <h3>Token 使用统计</h3>
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          @change="loadTokenUsage"
          class="date-picker"
        />
      </div>

      <div class="token-cards">
        <div class="token-card">
          <div class="token-label">总输入 Token</div>
          <div class="token-value">{{ formatNumber(tokenMetrics.total_input_tokens) }}</div>
        </div>
        <div class="token-card">
          <div class="token-label">总输出 Token</div>
          <div class="token-value">{{ formatNumber(tokenMetrics.total_output_tokens) }}</div>
        </div>
        <div class="token-card">
          <div class="token-label">缓存命中 Token</div>
          <div class="token-value">{{ formatNumber(tokenMetrics.total_cached_tokens) }}</div>
        </div>
        <div class="token-card">
          <div class="token-label">总 Token 数</div>
          <div class="token-value">{{ formatNumber(tokenMetrics.total_tokens) }}</div>
        </div>
        <div class="token-card">
          <div class="token-label">Token 命中率</div>
          <div class="token-value">{{ formatPercent(tokenMetrics.avg_token_hit_rate) }}</div>
        </div>
        <div class="token-card">
          <div class="token-label">估算成本</div>
          <div class="token-value">${{ tokenMetrics.estimated_cost.toFixed(2) }}</div>
        </div>
      </div>
    </div>

    <!-- 趋势图表 -->
    <div class="charts-section">
      <div class="chart-card">
        <h3>指标趋势（最近7天）</h3>
        <div ref="trendChartRef" class="chart-container"></div>
      </div>

      <div class="chart-card">
        <h3>Token 使用趋势</h3>
        <div ref="tokenChartRef" class="chart-container"></div>
      </div>
    </div>

    <!-- 使用统计 -->
    <div class="usage-section">
      <div class="usage-card">
        <h3>使用统计</h3>
        <div class="usage-stats">
          <div class="usage-item">
            <span class="usage-label">总对话数</span>
            <span class="usage-value">{{ usageMetrics.total_conversations }}</span>
          </div>
          <div class="usage-item">
            <span class="usage-label">日期范围</span>
            <span class="usage-value">{{ usageMetrics.date_range?.start }} 至 {{ usageMetrics.date_range?.end }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Warning, CircleCheck, Star, CaretTop, CaretBottom, ArrowLeft } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import axios from 'axios'

// 数据
const qualityMetrics = ref({
  avg_recall_rate: 0,
  avg_hallucination_rate: 0,
  avg_accuracy: 0,
  avg_user_rating: 0
})

const tokenMetrics = ref({
  total_input_tokens: 0,
  total_output_tokens: 0,
  total_cached_tokens: 0,
  total_tokens: 0,
  avg_token_hit_rate: 0,
  estimated_cost: 0
})

const usageMetrics = ref({
  total_conversations: 0,
  date_range: { start: '', end: '' }
})

const trends = ref([])
const recallTrend = ref(0)
const hallucinationTrend = ref(0)
const accuracyTrend = ref(0)
const ratingTrend = ref(0)

const dateRange = ref([])
const trendChartRef = ref(null)
const tokenChartRef = ref(null)

// 格式化函数
const formatPercent = (value) => {
  return (value * 100).toFixed(1) + '%'
}

const formatNumber = (value) => {
  if (value >= 1000000) {
    return (value / 1000000).toFixed(1) + 'M'
  } else if (value >= 1000) {
    return (value / 1000).toFixed(1) + 'K'
  }
  return value.toString()
}

// 加载指标汇总
const loadMetricsSummary = async () => {
  try {
    const response = await axios.get('/hr/api/v1/monitoring/summary')
    if (response.data.code === 200) {
      const data = response.data.data
      qualityMetrics.value = data.quality_metrics
      tokenMetrics.value = data.token_metrics
      usageMetrics.value = data.usage_metrics
    }
  } catch (error) {
    console.error('加载指标汇总失败:', error)
    ElMessage.error('加载指标汇总失败')
  }
}

// 加载指标趋势
const loadMetricsTrend = async () => {
  try {
    const response = await axios.get('/hr/api/v1/monitoring/trend', {
      params: { days: 7, metric_type: 'all' }
    })
    if (response.data.code === 200) {
      trends.value = response.data.data
      
      // 计算趋势
      if (trends.value.length >= 2) {
        const latest = trends.value[trends.value.length - 1]
        const previous = trends.value[trends.value.length - 2]
        
        recallTrend.value = (latest.recall_rate - previous.recall_rate) * 100
        hallucinationTrend.value = (latest.hallucination_rate - previous.hallucination_rate) * 100
        accuracyTrend.value = (latest.accuracy - previous.accuracy) * 100
        ratingTrend.value = (latest.accuracy - previous.accuracy) * 100
      }
      
      // 更新图表
      updateTrendChart()
      updateTokenChart()
    }
  } catch (error) {
    console.error('加载指标趋势失败:', error)
    ElMessage.error('加载指标趋势失败')
  }
}

// 加载Token使用统计
const loadTokenUsage = async () => {
  try {
    const params = {}
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0].toISOString().split('T')[0]
      params.end_date = dateRange.value[1].toISOString().split('T')[0]
    }
    
    const response = await axios.get('/hr/api/v1/monitoring/token-usage', { params })
    if (response.data.code === 200) {
      const data = response.data.data
      // 合并token数据，保留已有的avg_token_hit_rate
      tokenMetrics.value = {
        ...tokenMetrics.value,
        total_input_tokens: data.summary.total_input_tokens || 0,
        total_output_tokens: data.summary.total_output_tokens || 0,
        total_cached_tokens: data.summary.total_cached_tokens || 0,
        total_tokens: data.summary.total_tokens || 0,
        estimated_cost: data.summary.estimated_cost || 0
      }
    }
  } catch (error) {
    console.error('加载Token使用统计失败:', error)
  }
}

// 更新趋势图表
const updateTrendChart = () => {
  if (!trendChartRef.value) return
  
  const chart = echarts.init(trendChartRef.value)
  const dates = trends.value.map(t => t.date)
  
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['召回率', '幻觉率', '准确率']
    },
    xAxis: {
      type: 'category',
      data: dates
    },
    yAxis: {
      type: 'value',
      max: 1,
      axisLabel: {
        formatter: (value) => (value * 100).toFixed(0) + '%'
      }
    },
    series: [
      {
        name: '召回率',
        type: 'line',
        data: trends.value.map(t => (t.recall_rate || 0)),
        smooth: true,
        itemStyle: { color: '#667eea' }
      },
      {
        name: '幻觉率',
        type: 'line',
        data: trends.value.map(t => (t.hallucination_rate || 0)),
        smooth: true,
        itemStyle: { color: '#f5576c' }
      },
      {
        name: '准确率',
        type: 'line',
        data: trends.value.map(t => (t.accuracy || 0)),
        smooth: true,
        itemStyle: { color: '#4facfe' }
      }
    ]
  }
  
  chart.setOption(option)
}

// 更新Token图表
const updateTokenChart = () => {
  if (!tokenChartRef.value) return
  
  const chart = echarts.init(tokenChartRef.value)
  const dates = trends.value.map(t => t.date)
  
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['总Token数']
    },
    xAxis: {
      type: 'category',
      data: dates
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: (value) => formatNumber(value)
      }
    },
    series: [
      {
        name: '总Token数',
        type: 'bar',
        data: trends.value.map(t => t.total_tokens),
        itemStyle: {
          color: '#409EFF'
        }
      }
    ]
  }
  
  chart.setOption(option)
}

// 初始化
onMounted(() => {
  loadMetricsSummary()
  loadMetricsTrend()
  loadTokenUsage()
  
  // 设置默认日期范围（本月）
  const now = new Date()
  const firstDay = new Date(now.getFullYear(), now.getMonth(), 1)
  dateRange.value = [firstDay, now]
})
</script>

<style scoped lang="scss">
.metrics-dashboard {
  padding: 24px;
  background: var(--bg-color);
  min-height: 100vh;
}

.page-header {
  margin-bottom: 32px;

  .header-left {
    display: flex;
    align-items: center;
    gap: 16px;

    .back-btn {
      flex-shrink: 0;
      font-size: 14px;
      color: var(--text-secondary);
      padding: 8px 12px;
      border-radius: 8px;
      transition: all 0.2s;

      &:hover {
        color: var(--primary-color);
        background: rgba(99, 102, 241, 0.1);
      }

      .el-icon {
        margin-right: 4px;
      }
    }

    .title-group {
      flex: 1;
    }
  }

  .page-title {
    font-size: 28px;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0 0 8px 0;
  }

  .page-subtitle {
    font-size: 14px;
    color: var(--text-secondary);
    margin: 0;
  }
}

.metrics-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 32px;

  .metric-card {
    background: var(--card-bg);
    border-radius: 12px;
    padding: 24px;
    display: flex;
    align-items: center;
    gap: 16px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);

    .card-icon {
      width: 48px;
      height: 48px;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 24px;
    }

    .recall-card .card-icon {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
    }

    .hallucination-card .card-icon {
      background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
      color: white;
    }

    .accuracy-card .card-icon {
      background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
      color: white;
    }

    .rating-card .card-icon {
      background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
      color: white;
    }

    .card-content {
      flex: 1;

      .card-label {
        font-size: 14px;
        color: var(--text-secondary);
        margin-bottom: 8px;
      }

      .card-value {
        font-size: 28px;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 4px;
      }

      .card-trend {
        font-size: 12px;
        display: flex;
        align-items: center;
        gap: 4px;

        .trend-up {
          color: #67c23a;
        }

        .trend-down {
          color: #f56c6c;
        }
      }
    }
  }
}

.token-section {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 32px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);

  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;

    h3 {
      font-size: 18px;
      font-weight: 600;
      color: var(--text-primary);
      margin: 0;
    }

    .date-picker {
      width: 280px;
    }
  }

  .token-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;

    .token-card {
      background: var(--bg-color);
      border-radius: 8px;
      padding: 16px;
      text-align: center;

      .token-label {
        font-size: 14px;
        color: var(--text-secondary);
        margin-bottom: 8px;
      }

      .token-value {
        font-size: 24px;
        font-weight: 700;
        color: var(--text-primary);
      }
    }
  }
}

.charts-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 24px;
  margin-bottom: 32px;

  .chart-card {
    background: var(--card-bg);
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);

    h3 {
      font-size: 18px;
      font-weight: 600;
      color: var(--text-primary);
      margin: 0 0 16px 0;
    }

    .chart-container {
      height: 300px;
    }
  }
}

.usage-section {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);

  .usage-card {
    h3 {
      font-size: 18px;
      font-weight: 600;
      color: var(--text-primary);
      margin: 0 0 16px 0;
    }

    .usage-stats {
      display: flex;
      gap: 32px;

      .usage-item {
        display: flex;
        flex-direction: column;
        gap: 8px;

        .usage-label {
          font-size: 14px;
          color: var(--text-secondary);
        }

        .usage-value {
          font-size: 20px;
          font-weight: 600;
          color: var(--text-primary);
        }
      }
    }
  }
}
</style>