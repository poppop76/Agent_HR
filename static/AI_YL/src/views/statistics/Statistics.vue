<template>
  <div class="statistics-page">
    <ParticlesBackground />
    
    <div class="page-header">
      <div class="header-particles"></div>
      <div class="header-content">
        <h1 class="page-title">数据统计分析</h1>
        <p class="page-subtitle">可视化展示招聘全流程数据，洞察人才趋势</p>
      </div>
      <div class="header-actions">
        <el-radio-group v-model="timeRange" @change="fetchStatistics" class="time-range-group">
          <el-radio-button label="day">日</el-radio-button>
          <el-radio-button label="month">月</el-radio-button>
        </el-radio-group>
        <el-button type="primary" size="large" class="action-btn" @click="handleExport">
          <el-icon><Download /></el-icon>
          <span>导出报表</span>
        </el-button>
      </div>
    </div>
    
    <div class="page-content">
      <el-row :gutter="20" class="stats-row">
        <el-col :xs="12" :sm="6">
          <div class="stat-card glass-card stat-card-resumes">
            <div class="stat-icon-wrapper">
              <el-icon :size="28"><Document /></el-icon>
            </div>
            <div class="stat-info">
              <p class="stat-value">{{ stats.totalResumes }}</p>
              <p class="stat-label">简历总数</p>
            </div>
            <div class="stat-card-glow"></div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6">
          <div class="stat-card glass-card stat-card-jobs">
            <div class="stat-icon-wrapper">
              <el-icon :size="28"><Briefcase /></el-icon>
            </div>
            <div class="stat-info">
              <p class="stat-value">{{ stats.totalJobs }}</p>
              <p class="stat-label">岗位总数</p>
            </div>
            <div class="stat-card-glow"></div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6">
          <div class="stat-card glass-card stat-card-matches">
            <div class="stat-icon-wrapper">
              <el-icon :size="28"><Connection /></el-icon>
            </div>
            <div class="stat-info">
              <p class="stat-value">{{ stats.totalMatches }}</p>
              <p class="stat-label">匹配次数</p>
            </div>
            <div class="stat-card-glow"></div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6">
          <div class="stat-card glass-card stat-card-rate">
            <div class="stat-icon-wrapper">
              <el-icon :size="28"><TrendCharts /></el-icon>
            </div>
            <div class="stat-info">
              <p class="stat-value">{{ stats.parseRate }}%</p>
              <p class="stat-label">解析成功率</p>
            </div>
            <div class="stat-card-glow"></div>
          </div>
        </el-col>
      </el-row>
      
      <el-row :gutter="20" class="charts-row">
        <el-col :span="12">
          <div class="chart-card glass-card">
            <div class="chart-header">
              <h3 class="chart-title">简历上传量趋势</h3>
              <div class="chart-badge">本周</div>
            </div>
            <div class="chart-container">
              <div v-if="!chartsLoaded" class="chart-loading">
                <div class="loading-spinner"></div>
                <span>数据加载中...</span>
              </div>
              <div v-else ref="uploadChartRef" class="chart"></div>
            </div>
          </div>
        </el-col>
        <el-col :span="12">
          <div class="chart-card glass-card">
            <div class="chart-header">
              <h3 class="chart-title">解析成功率</h3>
              <div class="chart-badge chart-badge-success">实时</div>
            </div>
            <div class="chart-container">
              <div v-if="!chartsLoaded" class="chart-loading">
                <div class="loading-spinner"></div>
                <span>数据加载中...</span>
              </div>
              <div v-else ref="parseRateChartRef" class="chart"></div>
            </div>
          </div>
        </el-col>
      </el-row>
      
      <el-row :gutter="20" class="charts-row">
        <el-col :span="12">
          <div class="chart-card glass-card">
            <div class="chart-header">
              <h3 class="chart-title">岗位匹配平均分</h3>
              <div class="chart-badge chart-badge-warning">趋势</div>
            </div>
            <div class="chart-container">
              <div v-if="!chartsLoaded" class="chart-loading">
                <div class="loading-spinner"></div>
                <span>数据加载中...</span>
              </div>
              <div v-else ref="matchScoreChartRef" class="chart"></div>
            </div>
          </div>
        </el-col>
        <el-col :span="12">
          <div class="chart-card glass-card">
            <div class="chart-header">
              <h3 class="chart-title">候选人标签分布</h3>
              <div class="chart-badge chart-badge-info">分布</div>
            </div>
            <div class="chart-container">
              <div v-if="!chartsLoaded" class="chart-loading">
                <div class="loading-spinner"></div>
                <span>数据加载中...</span>
              </div>
              <div v-else ref="tagChartRef" class="chart"></div>
            </div>
          </div>
        </el-col>
      </el-row>
      
      <el-row :gutter="20" class="charts-row">
        <el-col :span="24">
          <div class="chart-card glass-card chart-card-wide">
            <div class="chart-header">
              <h3 class="chart-title">人才梯度瀑布流</h3>
              <div class="chart-badge chart-badge-premium">全量</div>
            </div>
            <div class="chart-container chart-container-wide">
              <div v-if="!chartsLoaded" class="chart-loading">
                <div class="loading-spinner"></div>
                <span>数据加载中...</span>
              </div>
              <div v-else ref="waterfallChartRef" class="chart"></div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { statisticsApi, resumeApi, jobApi, matchingApi } from '@/api'
import { ElMessage } from 'element-plus'
import { Download, Document, Briefcase, Connection, TrendCharts } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import ParticlesBackground from '@/components/ParticlesBackground.vue'

const timeRange = ref('month')
const chartsLoaded = ref(false)
const stats = reactive({
  totalResumes: 0,
  totalJobs: 0,
  totalMatches: 0,
  parseRate: 0
})

const uploadChartRef = ref(null)
const parseRateChartRef = ref(null)
const matchScoreChartRef = ref(null)
const tagChartRef = ref(null)
const waterfallChartRef = ref(null)

let uploadChart = null
let parseRateChart = null
let matchScoreChart = null
let tagChart = null
let waterfallChart = null

const fetchStatistics = async () => {
  try {
    const [overviewRes, resumesRes] = await Promise.all([
      statisticsApi.getOverview(),
      resumeApi.getResumeList({ page: 1, pageSize: 100 })
    ])
    const data = overviewRes.data
    stats.totalResumes = data.resumeCount || 0
    stats.totalJobs = data.jobCount || 0
    stats.totalMatches = data.matchingTaskCount || 0
    
    // 计算解析成功率
    const list = resumesRes.data?.list || resumesRes.data?.records || []
    const successCount = list.filter(r => r.parseStatus === 'success').length
    stats.parseRate = list.length > 0 ? Math.round((successCount / list.length) * 100) : 0
    
    chartsLoaded.value = true
    
    // 从统一接口获取图表数据
    if (data.parseRate) {
      initParseRateChart(data.parseRate)
    }
    if (data.uploadTrend) {
      initUploadChart(data.uploadTrend)
    }
    initMatchScoreChart()
    initTagChart()
    initWaterfallChart()
  } catch (error) {
    console.error('获取统计数据失败', error)
    chartsLoaded.value = true
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
    initMatchScoreChart()
    initTagChart()
    initWaterfallChart()
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
  const fail = total - success
  
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
        { value: fail, name: '解析失败', itemStyle: { color: new echarts.graphic.LinearGradient(0, 0, 1, 1, [{ offset: 0, color: '#FF4D4F' }, { offset: 1, color: '#FF7875' }]) } }
      ],
      animationType: 'expansion',
      animationDuration: 1500,
      animationEasing: 'cubicOut'
    }]
  })
}

const initMatchScoreChart = (data) => {
  if (!matchScoreChartRef.value) return
  matchScoreChart = echarts.init(matchScoreChartRef.value)
  
  // 使用模拟数据展示趋势
  const xAxisData = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
  const seriesData = [72, 75, 78, 74, 80, 76, 82]
  
  matchScoreChart.setOption({
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
      max: 100,
      splitLine: { lineStyle: { color: 'rgba(0, 0, 0, 0.04)', type: 'dashed' } },
      axisLabel: { color: '#595959', fontSize: 12 }
    },
    series: [{ 
      data: seriesData, 
      type: 'line', 
      smooth: true,
      symbol: 'circle',
      symbolSize: 10,
      lineStyle: {
        width: 4,
        color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
          { offset: 0, color: '#FA8C16' },
          { offset: 1, color: '#FFA940' }
        ]),
        shadowColor: 'rgba(250, 140, 22, 0.3)',
        shadowBlur: 10
      },
      itemStyle: {
        color: '#FA8C16',
        borderWidth: 3,
        borderColor: '#fff',
        shadowColor: 'rgba(250, 140, 22, 0.4)',
        shadowBlur: 8
      },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(250, 140, 22, 0.2)' },
          { offset: 1, color: 'rgba(250, 140, 22, 0.01)' }
        ])
      },
      animationDuration: 1500,
      animationEasing: 'cubicOut'
    }]
  })
}

const initTagChart = (data) => {
  if (!tagChartRef.value) return
  tagChart = echarts.init(tagChartRef.value)
  
  // 使用模拟数据展示分布
  const tagData = [
    { name: '技术能力强', count: 35 },
    { name: '沟通优秀', count: 25 },
    { name: '经验丰富', count: 20 },
    { name: '学历突出', count: 15 },
    { name: '项目亮眼', count: 10 },
    { name: '潜力新人', count: 8 }
  ]
  const chartData = tagData.map((tag, index) => {
    const colors = [
      [{ offset: 0, color: '#52C41A' }, { offset: 1, color: '#73D13D' }],
      [{ offset: 0, color: '#1890FF' }, { offset: 1, color: '#40A9FF' }],
      [{ offset: 0, color: '#FA8C16' }, { offset: 1, color: '#FFA940' }],
      [{ offset: 0, color: '#FF4D4F' }, { offset: 1, color: '#FF7875' }],
      [{ offset: 0, color: '#722ED1' }, { offset: 1, color: '#9254DE' }],
      [{ offset: 0, color: '#EB2F96' }, { offset: 1, color: '#F759AB' }]
    ]
    return {
      value: tag.count,
      name: tag.name,
      itemStyle: { 
        color: new echarts.graphic.LinearGradient(0, 0, 1, 1, colors[index % colors.length])
      }
    }
  })
  
  tagChart.setOption({
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
      radius: ['35%', '75%'],
      center: ['50%', '50%'],
      roseType: 'area',
      itemStyle: {
        borderRadius: 8,
        borderColor: 'rgba(255, 255, 255, 0.9)',
        borderWidth: 2
      },
      label: {
        color: '#595959',
        fontSize: 12,
        formatter: '{b}\n{d}%'
      },
      labelLine: {
        lineStyle: { color: 'rgba(0, 0, 0, 0.06)' }
      },
      data: chartData,
      animationType: 'expansion',
      animationDuration: 1500,
      animationEasing: 'cubicOut'
    }]
  })
}

const initWaterfallChart = () => {
  if (!waterfallChartRef.value) return
  waterfallChart = echarts.init(waterfallChartRef.value)
  
  waterfallChart.setOption({
    backgroundColor: 'transparent',
    tooltip: { 
      trigger: 'axis',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: 'rgba(82, 196, 26, 0.2)',
      borderWidth: 1,
      textStyle: { color: '#262626' },
      extraCssText: 'backdrop-filter: blur(12px); border-radius: 12px; box-shadow: 0 4px 16px rgba(0,0,0,0.08);',
      axisPointer: {
        type: 'shadow',
        shadowStyle: {
          color: 'rgba(82, 196, 26, 0.05)'
        }
      }
    },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { 
      type: 'category', 
      data: ['优质人才', '普通人才', '待优化人才', '新投递', '面试中', '已录用'],
      axisLine: { lineStyle: { color: 'rgba(0, 0, 0, 0.06)' } },
      axisLabel: { color: '#595959', fontSize: 12 }
    },
    yAxis: { 
      type: 'value',
      splitLine: { lineStyle: { color: 'rgba(0, 0, 0, 0.04)', type: 'dashed' } },
      axisLabel: { color: '#595959', fontSize: 12 }
    },
    series: [{
      type: 'bar',
      stack: 'total',
      barWidth: '50%',
      data: [
        { value: 0, itemStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: '#52C41A' }, { offset: 1, color: '#73D13D' }]) } },
        { value: 0, itemStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: '#1890FF' }, { offset: 1, color: '#40A9FF' }]) } },
        { value: 0, itemStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: '#FA8C16' }, { offset: 1, color: '#FFA940' }]) } },
        { value: 0, itemStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: '#722ED1' }, { offset: 1, color: '#9254DE' }]) } },
        { value: 0, itemStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: '#EB2F96' }, { offset: 1, color: '#F759AB' }]) } },
        { value: 0, itemStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: '#FAAD14' }, { offset: 1, color: '#FFC53D' }]) } }
      ],
      itemStyle: {
        borderRadius: [6, 6, 0, 0]
      },
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

const handleExport = () => {
  ElMessage.info('导出功能暂未实现')
}

const handleResize = () => {
  uploadChart?.resize()
  parseRateChart?.resize()
  matchScoreChart?.resize()
  tagChart?.resize()
  waterfallChart?.resize()
}

onMounted(() => {
  fetchStatistics()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  uploadChart?.dispose()
  parseRateChart?.dispose()
  matchScoreChart?.dispose()
  tagChart?.dispose()
  waterfallChart?.dispose()
})
</script>

<style scoped lang="scss">
.statistics-page {
  min-height: 100%;
  background: transparent;
  position: relative;
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
  align-items: center;
  gap: 16px;
  
  .time-range-group {
    :deep(.el-radio-button__inner) {
      background: rgba(82, 196, 26, 0.1);
      border-color: rgba(255, 255, 255, 0.2);
      color: rgba(255, 255, 255, 0.8);
      border-radius: var(--radius-md);
      padding: 10px 20px;
      font-weight: 500;
      transition: var(--transition-base);
      
      &:hover {
        color: #fff;
      }
    }
    
    :deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
      background: rgba(255, 255, 255, 0.95);
      border-color: rgba(255, 255, 255, 0.95);
      color: var(--primary-color);
      box-shadow: 0 2px 8px rgba(0,0,0,0.15);
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

.stats-row {
  margin-bottom: 20px;
}

.charts-row {
  margin-bottom: 20px;
}

.glass-card {
  background: var(--gradient-card);
  backdrop-filter: blur(12px);
  border-radius: var(--radius-lg);
  box-shadow: var(--card-shadow);
  border: 1px solid var(--card-border);
  padding: 24px;
  margin-bottom: 20px;
  transition: var(--transition-base);
  position: relative;
  overflow: hidden;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent);
    pointer-events: none;
  }
  
  &:hover {
    box-shadow: var(--card-shadow-hover);
    border-color: var(--card-border-glow);
    transform: translateY(-2px);
  }
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 16px;
  margin-bottom: 0;
  position: relative;
  
  .stat-icon-wrapper {
    width: 56px;
    height: 56px;
    border-radius: var(--radius-lg);
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(255, 255, 255, 0.06);
    color: var(--text-secondary);
    transition: var(--transition-base);
  }
  
  .stat-info {
    flex: 1;
    
    .stat-value {
      font-size: 24px;
      font-weight: 700;
      color: var(--text-primary);
      margin: 0 0 4px 0;
    }
    
    .stat-label {
      font-size: 13px;
      color: var(--text-tertiary);
      margin: 0;
    }
  }
  
  .stat-card-glow {
    position: absolute;
    top: -30%;
    right: -10%;
    width: 80px;
    height: 80px;
    border-radius: 50%;
    opacity: 0.12;
    transition: var(--transition-slow);
    pointer-events: none;
  }
  
  &:hover .stat-card-glow {
    opacity: 0.2;
    transform: scale(1.15);
  }
  
  &:hover .stat-icon-wrapper {
    background: rgba(82, 196, 26, 0.1);
    transform: rotate(5deg) scale(1.05);
  }
}

.stat-card-resumes .stat-card-glow { background: var(--primary-color); }
.stat-card-jobs .stat-card-glow { background: var(--warning-color); }
.stat-card-matches .stat-card-glow { background: var(--success-color); }
.stat-card-rate .stat-card-glow { background: var(--secondary-color); }

.stat-card-resumes:hover .stat-icon-wrapper { color: var(--primary-light); }
.stat-card-jobs:hover .stat-icon-wrapper { color: var(--warning-light); }
.stat-card-matches:hover .stat-icon-wrapper { color: var(--success-light); }
.stat-card-rate:hover .stat-icon-wrapper { color: var(--secondary-light); }

.chart-card {
  min-height: 380px;
}

.chart-card-wide {
  min-height: 420px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--card-border);
}

.chart-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.chart-badge {
  padding: 4px 12px;
  border-radius: var(--radius-full);
  font-size: 12px;
  font-weight: 600;
  background: rgba(82, 196, 26, 0.08);
  color: var(--text-tertiary);
  border: 1px solid var(--card-border);
  
  &.chart-badge-success {
    background: rgba(16, 185, 129, 0.15);
    color: var(--success-color);
    border-color: rgba(16, 185, 129, 0.3);
  }
  
  &.chart-badge-warning {
    background: rgba(245, 158, 11, 0.15);
    color: var(--accent-color);
    border-color: rgba(245, 158, 11, 0.3);
  }
  
  &.chart-badge-info {
    background: rgba(124, 58, 237, 0.15);
    color: var(--secondary-light);
    border-color: rgba(124, 58, 237, 0.3);
  }
  
  &.chart-badge-premium {
    background: var(--gradient-accent);
    color: #fff;
    border: none;
    box-shadow: 0 2px 8px rgba(245, 158, 11, 0.3);
  }
}

.chart-container {
  height: 300px;
  position: relative;
}

.chart-container-wide {
  height: 340px;
}

.chart {
  width: 100%;
  height: 100%;
}

.chart-loading {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: var(--text-tertiary);
  font-size: 14px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: var(--radius-md);
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--card-border);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
