<template>
  <div class="dashboard-page">
    <div class="dashboard-hero">
      <div class="hero-particles"></div>
      <div class="hero-content">
        <h1 class="hero-title">HR智能简历解析与人岗匹配Agent系统</h1>
        <p class="hero-subtitle">新一代智能招聘解决方案，让人才匹配更高效</p>
        <div class="hero-actions">
          <el-button type="primary" size="large" @click="router.push('/resumes/upload')">
            <el-icon :size="16"><Upload /></el-icon>
            <span>快速上传简历</span>
          </el-button>
          <el-button size="large" @click="router.push('/matching')">
            <el-icon :size="16"><Connection /></el-icon>
            <span>开始人岗匹配</span>
          </el-button>
        </div>
      </div>
    </div>

    <div class="dashboard-content">
      <el-row :gutter="16" class="stats-row">
        <el-col :xs="12" :sm="12" :md="6">
          <div class="stat-card stat-card-resumes">
            <div class="stat-icon-wrapper">
              <el-icon :size="24"><Document /></el-icon>
            </div>
            <div class="stat-info">
              <p class="stat-value">{{ stats.totalResumes }}</p>
              <p class="stat-label">简历总数</p>
            </div>
            <div class="stat-card-glow"></div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="12" :md="6">
          <div class="stat-card stat-card-jobs">
            <div class="stat-icon-wrapper stat-icon-briefcase">
              <el-icon :size="24"><Briefcase /></el-icon>
            </div>
            <div class="stat-info">
              <p class="stat-value">{{ stats.totalJobs }}</p>
              <p class="stat-label">岗位总数</p>
            </div>
            <div class="stat-card-glow"></div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="12" :md="6">
          <div class="stat-card stat-card-matches">
            <div class="stat-icon-wrapper stat-icon-connection">
              <el-icon :size="24"><Connection /></el-icon>
            </div>
            <div class="stat-info">
              <p class="stat-value">{{ stats.totalMatches }}</p>
              <p class="stat-label">匹配次数</p>
            </div>
            <div class="stat-card-glow"></div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="12" :md="6">
          <div class="stat-card stat-card-candidates">
            <div class="stat-icon-wrapper stat-icon-avatar">
              <el-icon :size="24"><Avatar /></el-icon>
            </div>
            <div class="stat-info">
              <p class="stat-value">{{ stats.totalResumes }}</p>
              <p class="stat-label">简历总数</p>
            </div>
            <div class="stat-card-glow"></div>
          </div>
        </el-col>
      </el-row>

      <!-- Agent 能力概览 -->
      <el-row :gutter="16" class="agent-capabilities-row">
        <el-col :span="24">
          <div class="card-container agent-capabilities-card">
            <div class="card-header">
              <h3><el-icon :size="18"><Lightning /></el-icon> Agent 核心能力</h3>
              <el-link type="primary" @click="router.push('/ai-center')">进入 AI 中心</el-link>
            </div>
            <el-row :gutter="12">
              <el-col :xs="12" :sm="8" :md="4">
                <div class="capability-item" @click="router.push('/resumes/upload')">
                  <div class="capability-icon capability-icon-1">
                    <el-icon :size="28"><Upload /></el-icon>
                  </div>
                  <h4>简历解析</h4>
                  <p>AI自动提取关键信息</p>
                </div>
              </el-col>
              <el-col :xs="12" :sm="8" :md="4">
                <div class="capability-item" @click="router.push('/matching')">
                  <div class="capability-icon capability-icon-2">
                    <el-icon :size="28"><Connection /></el-icon>
                  </div>
                  <h4>人岗匹配</h4>
                  <p>多维度智能评分</p>
                </div>
              </el-col>
              <el-col :xs="12" :sm="8" :md="4">
                <div class="capability-item" @click="router.push('/ai-center')">
                  <div class="capability-icon capability-icon-3">
                    <el-icon :size="28"><ChatLineRound /></el-icon>
                  </div>
                  <h4>AI对话</h4>
                  <p>自然语言数据查询</p>
                </div>
              </el-col>
              <el-col :xs="12" :sm="8" :md="4">
                <div class="capability-item" @click="router.push('/ai-center')">
                  <div class="capability-icon capability-icon-4">
                    <el-icon :size="28"><Notebook /></el-icon>
                  </div>
                  <h4>智能报告</h4>
                  <p>一键生成分析报告</p>
                </div>
              </el-col>
              <el-col :xs="12" :sm="8" :md="4">
                <div class="capability-item" @click="router.push('/ai-center')">
                  <div class="capability-icon capability-icon-5">
                    <el-icon :size="28"><Sort /></el-icon>
                  </div>
                  <h4>候选人对比</h4>
                  <p>多维度差异分析</p>
                </div>
              </el-col>
              <el-col :xs="12" :sm="8" :md="4">
                <div class="capability-item" @click="router.push('/ai-center')">
                  <div class="capability-icon capability-icon-6">
                    <el-icon :size="28"><TrendCharts /></el-icon>
                  </div>
                  <h4>人才预测</h4>
                  <p>AI预测匹配度</p>
                </div>
              </el-col>
            </el-row>
          </div>
        </el-col>
      </el-row>

      <el-row :gutter="16">
        <el-col :xs="24" :md="14">
          <div class="card-container chart-card">
            <div class="card-header">
              <h3>简历上传趋势</h3>
              <el-radio-group v-model="chartPeriod" size="small" @change="updateUploadChart">
                <el-radio-button label="week">本周</el-radio-button>
                <el-radio-button label="month">本月</el-radio-button>
              </el-radio-group>
            </div>
            <div class="chart-wrapper" ref="uploadChartRef"></div>
          </div>
        </el-col>
        <el-col :xs="24" :md="10">
          <div class="card-container chart-card">
            <div class="card-header">
              <h3>解析成功率</h3>
            </div>
            <div class="chart-wrapper" ref="parseRateChartRef"></div>
          </div>
        </el-col>
      </el-row>

      <el-row :gutter="16">
        <el-col :xs="24" :md="14">
          <div class="card-container">
            <div class="card-header">
              <h3>快捷操作</h3>
            </div>
            <div class="quick-actions">
              <div class="quick-action-item" @click="router.push('/resumes/upload')">
                <div class="quick-action-icon quick-action-icon-1">
                  <el-icon :size="20"><Upload /></el-icon>
                </div>
                <div class="quick-action-info">
                  <h4>上传简历</h4>
                  <p>支持PDF/Word/TXT格式</p>
                </div>
                <el-icon class="quick-action-arrow" :size="16"><ArrowRight /></el-icon>
              </div>
              <div class="quick-action-item" @click="router.push('/jobs/add')">
                <div class="quick-action-icon quick-action-icon-2">
                  <el-icon :size="20"><Plus /></el-icon>
                </div>
                <div class="quick-action-info">
                  <h4>新增岗位</h4>
                  <p>创建新的招聘职位</p>
                </div>
                <el-icon class="quick-action-arrow" :size="16"><ArrowRight /></el-icon>
              </div>
              <div class="quick-action-item" @click="router.push('/matching')">
                <div class="quick-action-icon quick-action-icon-3">
                  <el-icon :size="20"><Connection /></el-icon>
                </div>
                <div class="quick-action-info">
                  <h4>人岗匹配</h4>
                  <p>AI智能匹配分析</p>
                </div>
                <el-icon class="quick-action-arrow" :size="16"><ArrowRight /></el-icon>
              </div>
              <div class="quick-action-item" @click="router.push('/ai-center')">
                <div class="quick-action-icon quick-action-icon-4">
                  <el-icon :size="20"><Lightning /></el-icon>
                </div>
                <div class="quick-action-info">
                  <h4>AI智能中心</h4>
                  <p>智能解析与对话</p>
                </div>
                <el-icon class="quick-action-arrow" :size="16"><ArrowRight /></el-icon>
              </div>
            </div>
          </div>
        </el-col>
        <el-col :xs="24" :md="10">
          <div class="card-container">
            <div class="card-header">
              <h3>最近解析简历</h3>
              <el-link type="primary" @click="router.push('/resumes')">查看全部</el-link>
            </div>
            <div class="recent-list">
              <div v-for="(item, index) in recentResumes" :key="index" class="recent-item">
                <div class="recent-item-avatar">
                  <el-avatar :size="36">{{ item.fileName?.charAt(0) || 'R' }}</el-avatar>
                </div>
                <div class="recent-item-info">
                  <h4>{{ item.fileName || '未知文件' }}</h4>
                  <p>{{ item.fileType || '未知类型' }}</p>
                </div>
                <div class="recent-item-status">
                  <el-tag :type="item.parseStatus === 'success' ? 'success' : 'warning'" size="small">
                    {{ item.parseStatus === 'success' ? '解析成功' : item.parseStatus === 'processing' ? '解析中' : '待解析' }}
                  </el-tag>
                  <span class="recent-item-time">{{ item.createdAt || '' }}</span>
                </div>
              </div>
              <div v-if="!recentResumes.length" class="empty-state">
                <el-icon :size="40" color="#94A3B8"><Document /></el-icon>
                <p>暂无解析记录</p>
              </div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { statisticsApi, resumeApi } from '@/api'
import * as echarts from 'echarts'
import { 
  Document, Briefcase, Connection, Avatar, Upload, Plus, DataAnalysis,
  TopRight, TrendCharts, PieChart, Lightning, Clock, ArrowRight,
  DataLine, ChatLineRound, Notebook, Sort
} from '@element-plus/icons-vue'

const router = useRouter()

const stats = ref({
  totalResumes: 0,
  totalJobs: 0,
  totalMatches: 0,
  totalCandidates: 0
})
const recentResumes = ref([])
const chartPeriod = ref('month')
const uploadChartRef = ref(null)
const parseRateChartRef = ref(null)

let uploadChart = null
let parseRateChart = null

const fetchStats = async () => {
  try {
    const [statsRes, resumesRes] = await Promise.all([
      statisticsApi.getOverview({ period: 'month' }),
      resumeApi.getResumeList({ page: 1, pageSize: 5 })
    ])
    const overviewData = statsRes.data
    stats.value = {
      totalResumes: overviewData.resumeCount || 0,
      totalJobs: overviewData.jobCount || 0,
      totalMatches: overviewData.matchingTaskCount || 0,
      totalCandidates: overviewData.resumeCount || 0
    }
    recentResumes.value = resumesRes.data?.list || resumesRes.data?.records || []
    
    // 从统一接口获取图表数据
    if (overviewData.parseRate) {
      initParseRateChart(overviewData.parseRate)
    }
    if (overviewData.uploadTrend) {
      initUploadChart(overviewData.uploadTrend)
    }
  } catch (error) {
    console.error('获取统计数据失败', error)
  }
}

const fetchChartsData = async () => {
  try {
    const res = await statisticsApi.getOverview()
    if (res.data.parseRate) {
      initParseRateChart(res.data.parseRate)
    }
    if (res.data.uploadTrend) {
      initUploadChart(res.data.uploadTrend)
    }
  } catch (error) {
    console.error('获取图表数据失败')
  }
}

const initUploadChart = (data) => {
  if (!uploadChartRef.value) return
  uploadChart = echarts.init(uploadChartRef.value)
  
  const xAxisData = data?.map(item => item.date) || []
  const seriesData = data?.map(item => item.count) || []
  
  uploadChart.setOption({
    backgroundColor: 'transparent',
    tooltip: { 
      trigger: 'axis',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: 'rgba(82, 196, 26, 0.2)',
      borderWidth: 1,
      textStyle: { color: '#262626' },
      extraCssText: 'backdrop-filter: blur(12px); border-radius: 12px; box-shadow: 0 4px 16px rgba(0,0,0,0.08);'
    },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { 
      type: 'category', 
      data: xAxisData,
      axisLine: { lineStyle: { color: 'rgba(0, 0, 0, 0.06)' } },
      axisLabel: { color: '#595959', fontSize: 12 }
    },
    yAxis: { 
      type: 'value',
      splitLine: { lineStyle: { color: 'rgba(0, 0, 0, 0.04)', type: 'dashed' } },
      axisLabel: { color: '#595959', fontSize: 12 }
    },
    series: [{ 
      data: seriesData, 
      type: 'bar',
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#52C41A' },
          { offset: 0.5, color: '#73D13D' },
          { offset: 1, color: '#1890FF' }
        ]),
        borderRadius: [6, 6, 0, 0]
      },
      barWidth: '45%',
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowColor: 'rgba(82, 196, 26, 0.3)'
        }
      },
      animationDuration: 1500,
      animationEasing: 'cubicOut'
    }]
  })
}

const initParseRateChart = (data) => {
  if (!parseRateChartRef.value) return
  parseRateChart = echarts.init(parseRateChartRef.value)
  
  const total = data?.total || 0
  const success = data?.success || 0
  const fail = data?.fail || 0
  const processing = data?.processing || 0
  
  parseRateChart.setOption({
    backgroundColor: 'transparent',
    tooltip: { 
      trigger: 'item',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: 'rgba(82, 196, 26, 0.2)',
      borderWidth: 1,
      textStyle: { color: '#262626' },
      extraCssText: 'backdrop-filter: blur(12px); border-radius: 12px; box-shadow: 0 4px 16px rgba(0,0,0,0.08);'
    },
    series: [{
      type: 'pie',
      radius: ['50%', '75%'],
      center: ['50%', '50%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 10,
        borderColor: 'rgba(255, 255, 255, 0.9)',
        borderWidth: 3
      },
      label: {
        show: true,
        color: '#595959',
        fontSize: 13,
        formatter: '{b}\n{d}%'
      },
      labelLine: {
        lineStyle: { color: 'rgba(0, 0, 0, 0.06)' }
      },
      emphasis: {
        label: {
          show: true,
          fontSize: 16,
          fontWeight: 'bold'
        },
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.1)'
        }
      },
      data: [
        { value: success, name: '解析成功', itemStyle: { color: new echarts.graphic.LinearGradient(0, 0, 1, 1, [{ offset: 0, color: '#52C41A' }, { offset: 1, color: '#73D13D' }]) } },
        { value: fail, name: '解析失败', itemStyle: { color: new echarts.graphic.LinearGradient(0, 0, 1, 1, [{ offset: 0, color: '#FF4D4F' }, { offset: 1, color: '#FF7875' }]) } },
        { value: processing, name: '解析中', itemStyle: { color: new echarts.graphic.LinearGradient(0, 0, 1, 1, [{ offset: 0, color: '#1890FF' }, { offset: 1, color: '#40A9FF' }]) } }
      ],
      animationType: 'expansion',
      animationDuration: 1500,
      animationEasing: 'cubicOut'
    }]
  })
}

const updateUploadChart = async () => {
  try {
    const res = await statisticsApi.getOverview()
    if (res.data.uploadTrend) {
      initUploadChart(res.data.uploadTrend)
    }
  } catch (error) {
    console.error('获取上传数据失败')
  }
}

const handleResize = () => {
  uploadChart?.resize()
  parseRateChart?.resize()
}

onMounted(() => {
  fetchStats()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  uploadChart?.dispose()
  parseRateChart?.dispose()
})
</script>

<style scoped lang="scss">
.dashboard-page {
  min-height: calc(100vh - 60px);
  overflow-y: auto;
  background: transparent;
}

.dashboard-hero {
  background: var(--gradient-primary);
  padding: 40px 16px 48px;
  position: relative;
  overflow: hidden;
  
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

.hero-particles {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: 
    radial-gradient(circle at 20% 30%, rgba(255,255,255,0.15) 1px, transparent 1px),
    radial-gradient(circle at 80% 70%, rgba(255,255,255,0.12) 1px, transparent 1px),
    radial-gradient(circle at 50% 50%, rgba(255,255,255,0.1) 2px, transparent 2px);
  background-size: 100px 100px, 150px 150px, 200px 200px;
  animation: particlesFloat 20s linear infinite;
}

@keyframes particlesFloat {
  from { transform: translateY(0); }
  to { transform: translateY(-200px); }
}

.hero-content {
  max-width: 800px;
  margin: 0 auto;
  text-align: center;
  position: relative;
  z-index: 1;
}

.hero-title {
  font-size: 28px;
  font-weight: 700;
  color: #fff;
  line-height: 1.4;
  margin-bottom: 12px;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
}

.hero-subtitle {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.85);
  margin-bottom: 28px;
}

.hero-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  flex-wrap: wrap;
  
  .el-button {
    height: 44px;
    padding: 0 28px;
    border-radius: var(--radius-md);
    font-size: 14px;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 8px;
    transition: var(--transition-base);
    
    &:first-child {
      background: #fff;
      color: var(--primary-color);
      border: none;
      
      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.03);
      }
    }
    
    &:last-child {
      background: rgba(82, 196, 26, 0.15);
      border: 1px solid rgba(255, 255, 255, 0.3);
      color: #fff;
      backdrop-filter: blur(8px);
      
      &:hover {
        background: rgba(255, 255, 255, 0.25);
        transform: translateY(-2px);
      }
    }
  }
}

.dashboard-content {
  padding: 24px 16px;
}

.stats-row {
  margin-bottom: 16px;
}

.stat-card {
  background: var(--gradient-card);
  backdrop-filter: blur(12px);
  border-radius: var(--radius-lg);
  box-shadow: var(--card-shadow);
  padding: 20px 16px;
  display: flex;
  align-items: center;
  gap: 16px;
  transition: var(--transition-base);
  border: 1px solid var(--card-border);
  margin-bottom: 16px;
  position: relative;
  overflow: hidden;
  
  &:hover {
    box-shadow: var(--card-shadow-hover);
    transform: translateY(-4px);
    border-color: var(--card-border-glow);
  }
}

.stat-card-glow {
  position: absolute;
  top: -50%;
  right: -20%;
  width: 100px;
  height: 100px;
  border-radius: 50%;
  opacity: 0.15;
  transition: var(--transition-slow);
}

.stat-card-resumes .stat-card-glow { background: var(--primary-color); }
.stat-card-jobs .stat-card-glow { background: var(--warning-color); }
.stat-card-matches .stat-card-glow { background: var(--success-color); }
.stat-card-candidates .stat-card-glow { background: var(--danger-color); }

.stat-card:hover .stat-card-glow {
  opacity: 0.25;
  transform: scale(1.2);
}

.stat-icon-wrapper {
  width: 52px;
  height: 52px;
  border-radius: var(--radius-md);
  background: var(--gradient-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
  box-shadow: 0 2px 8px var(--primary-glow);
  
  &.stat-icon-briefcase {
    background: var(--gradient-accent);
    box-shadow: 0 2px 8px rgba(245, 158, 11, 0.3);
  }
  
  &.stat-icon-connection {
    background: linear-gradient(135deg, #10B981 0%, #34D399 100%);
    box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
  }
  
  &.stat-icon-avatar {
    background: linear-gradient(135deg, #E11D48 0%, #FB7185 100%);
    box-shadow: 0 2px 8px rgba(225, 29, 72, 0.3);
  }
}

.stat-info {
  flex: 1;
  position: relative;
  z-index: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
}

.stat-label {
  color: var(--text-secondary);
  font-size: 12px;
  margin-top: 4px;
}

.card-container {
  margin-bottom: 16px;
  background: var(--gradient-card);
  backdrop-filter: blur(12px);
  border: 1px solid var(--card-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--card-shadow);
  position: relative;
  overflow: hidden;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(82,196,26,0.15), transparent);
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  
  h3 {
    font-size: 16px;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0;
  }
}

.chart-wrapper {
  height: 240px;
}

.chart-placeholder {
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.03);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px dashed var(--card-border);
}

.chart-placeholder-content {
  text-align: center;
  color: var(--text-tertiary);
  
  p {
    margin-top: 8px;
    font-size: 12px;
  }
}

.placeholder-hint {
  display: inline-block;
  margin-top: 6px;
  padding: 2px 10px;
  background: rgba(82, 196, 26, 0.1);
  color: var(--primary-color);
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.quick-actions {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.quick-action-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px;
  background: rgba(0, 0, 0, 0.02);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: var(--transition-base);
  border: 1px solid transparent;
  
  &:hover {
    background: rgba(82, 196, 26, 0.05);
    border-color: var(--card-border-glow);
    transform: translateX(4px);
  }
}

.quick-action-icon {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
  
  &.quick-action-icon-1 { 
    background: var(--gradient-primary);
    box-shadow: 0 2px 8px var(--primary-glow);
  }
  &.quick-action-icon-2 { 
    background: linear-gradient(135deg, #10B981 0%, #34D399 100%);
    box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
  }
  &.quick-action-icon-3 { 
    background: var(--gradient-accent);
    box-shadow: 0 2px 8px rgba(245, 158, 11, 0.3);
  }
  &.quick-action-icon-4 { 
    background: linear-gradient(135deg, #E11D48 0%, #FB7185 100%);
    box-shadow: 0 2px 8px rgba(225, 29, 72, 0.3);
  }
}

.quick-action-info {
  flex: 1;
  
  h4 {
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 4px;
  }
  
  p {
    font-size: 12px;
    color: var(--text-tertiary);
  }
}

.quick-action-arrow {
  color: var(--text-tertiary);
  transition: var(--transition-base);
}

.quick-action-item:hover .quick-action-arrow {
  color: var(--primary-light);
  transform: translateX(4px);
}

.recent-list {
  max-height: 280px;
  overflow-y: auto;
  
  &::-webkit-scrollbar {
    width: 4px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: var(--card-border);
    border-radius: 2px;
  }
}

.recent-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid var(--card-border);
  transition: var(--transition-base);
  
  &:last-child {
    border-bottom: none;
  }
  
  &:hover {
    background: rgba(255, 255, 255, 0.03);
    margin: 0 -16px;
    padding-left: 16px;
    padding-right: 16px;
  }
}

.recent-item-avatar {
  flex-shrink: 0;
  
  :deep(.el-avatar) {
    background: var(--gradient-primary);
    color: #fff;
  }
}

.recent-item-info {
  flex: 1;
  
  h4 {
    font-size: 14px;
    font-weight: 500;
    color: var(--text-primary);
    margin-bottom: 4px;
  }
  
  p {
    font-size: 12px;
    color: var(--text-tertiary);
  }
}

.recent-item-status {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.recent-item-time {
  font-size: 12px;
  color: var(--text-tertiary);
}

.empty-state {
  text-align: center;
  padding: 40px 0;
  color: var(--text-tertiary);
  
  p {
    margin-top: 8px;
    font-size: 12px;
  }
}

// Agent 能力概览样式
.agent-capabilities-row {
  margin-top: 16px;
}

.agent-capabilities-card {
  .card-header {
    h3 {
      display: flex;
      align-items: center;
      gap: 8px;
    }
  }
}

.capability-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 20px 12px;
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: var(--transition-base);
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid transparent;
  margin-bottom: 12px;
  
  &:hover {
    background: rgba(255, 255, 255, 0.06);
    border-color: var(--card-border-glow);
    transform: translateY(-4px);
    
    .capability-icon {
      transform: scale(1.1);
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
    }
  }
  
  .capability-icon {
    width: 56px;
    height: 56px;
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    margin-bottom: 12px;
    transition: var(--transition-base);
    
    &.capability-icon-1 {
      background: linear-gradient(135deg, #10b981, #059669);
    }
    
    &.capability-icon-2 {
      background: linear-gradient(135deg, #3b82f6, #2563eb);
    }
    
    &.capability-icon-3 {
      background: linear-gradient(135deg, #8b5cf6, #7c3aed);
    }
    
    &.capability-icon-4 {
      background: linear-gradient(135deg, #ec4899, #db2777);
    }
    
    &.capability-icon-5 {
      background: linear-gradient(135deg, #f59e0b, #d97706);
    }
    
    &.capability-icon-6 {
      background: linear-gradient(135deg, #ef4444, #dc2626);
    }
  }
  
  h4 {
    margin: 0 0 4px;
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary);
  }
  
  p {
    margin: 0;
    font-size: 12px;
    color: var(--text-secondary);
  }
}
</style>
