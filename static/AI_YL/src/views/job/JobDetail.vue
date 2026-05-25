<template>
  <div class="job-detail-page">
    <ParticlesBackground />
    
    <div class="page-header">
      <div class="header-particles"></div>
      <div class="header-content">
        <h1 class="page-title">岗位详情</h1>
        <p class="page-subtitle">查看和管理岗位详细信息</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" size="large" class="action-btn" @click="router.push(`/jobs/edit/${job.id}`)">
          <el-icon><Edit /></el-icon>
          <span>编辑岗位</span>
        </el-button>
        <el-button size="large" class="back-btn" @click="router.back()">
          <el-icon><ArrowLeft /></el-icon>
          <span>返回列表</span>
        </el-button>
      </div>
    </div>
    
    <div class="page-content">
      <el-row :gutter="20">
        <el-col :span="16">
          <div class="detail-card glass-card">
            <div class="card-header">
              <h3 class="card-title">基本信息</h3>
              <div class="card-badge">详情</div>
            </div>
            
            <div class="info-grid">
              <div class="info-item">
                <span class="info-label">岗位名称</span>
                <span class="info-value">{{ job.name || '未知岗位' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">岗位类别</span>
                <span class="info-value">
                  <el-tag v-if="job.jobType" :type="getJobTypeTagType(job.jobType)" effect="dark" size="small">{{ job.jobTypeDesc || job.jobType }}</el-tag>
                  <span v-else class="info-value-text">未设置</span>
                </span>
              </div>
              <div class="info-item">
                <span class="info-label">所属部门</span>
                <span class="info-value">{{ job.department || '未设置' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">薪资范围</span>
                <span class="info-value info-value-accent">{{ job.salary || '面议' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">工作地点</span>
                <span class="info-value">{{ job.location || '未设置' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">状态</span>
                <span :class="['status-badge', job.status === 'published' ? 'status-published' : 'status-unpublished']">
                  {{ job.status === 'published' ? '已上架' : '已下架' }}
                </span>
              </div>
            </div>
          </div>
          
          <div class="detail-card glass-card">
            <div class="card-header">
              <h3 class="card-title">岗位职责</h3>
            </div>
            <div class="content-text">{{ job.responsibilities || '暂无岗位职责描述' }}</div>
          </div>
          
          <div class="detail-card glass-card">
            <div class="card-header">
              <h3 class="card-title">任职要求</h3>
            </div>
            <div class="content-text">{{ job.requirements || '暂无任职要求描述' }}</div>
          </div>
        </el-col>
        
        <el-col :span="8">
          <div class="related-card glass-card">
            <div class="card-header">
              <h3 class="card-title">关联简历</h3>
              <div class="card-badge card-badge-info">{{ relatedResumes.length }} 个</div>
            </div>
            
            <el-button type="primary" class="match-btn" @click="router.push(`/matching?jobId=${job.id}`)">
              <el-icon><Connection /></el-icon>
              <span>查看人岗匹配</span>
            </el-button>
            
            <div class="related-list">
              <div v-for="resume in relatedResumes" :key="resume.id" class="related-item">
                <div class="resume-avatar">
                  <el-icon :size="20"><User /></el-icon>
                </div>
                <div class="resume-info">
                  <p class="resume-name">{{ resume.name }}</p>
                  <p class="resume-meta">
                    <span class="match-score" :class="getScoreClass(resume.matchScore)">
                      {{ resume.matchScore }}%
                    </span>
                    <span class="resume-date">{{ resume.createdAt }}</span>
                  </p>
                </div>
                <el-button size="small" class="view-btn" @click="router.push(`/resumes/parse/${resume.id}`)">
                  查看
                </el-button>
              </div>
            </div>
          </div>
          
          <div class="related-card glass-card">
            <div class="card-header">
              <h3 class="card-title">匹配分数分布</h3>
            </div>
            <div ref="scoreChartRef" class="score-chart"></div>
          </div>
          
          <div class="related-card glass-card">
            <div class="card-header">
              <h3 class="card-title">申请趋势</h3>
            </div>
            <div ref="trendChartRef" class="trend-chart"></div>
          </div>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { jobApi } from '@/api'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { Edit, ArrowLeft, Connection, User } from '@element-plus/icons-vue'
import ParticlesBackground from '@/components/ParticlesBackground.vue'

const router = useRouter()
const route = useRoute()

const job = ref({})
const relatedResumes = ref([])
const scoreChartRef = ref(null)
const trendChartRef = ref(null)
let scoreChart = null
let trendChart = null

const getJobTypeTagType = (jobType) => {
  const map = { technical: 'success', management: 'warning', operation: 'primary', administrative: 'info' }
  return map[jobType] || ''
}

const fetchJobDetail = async () => {
  try {
    const res = await jobApi.getJobList({ page: 1, pageSize: 100 })
    const jobData = res.data.list.find(j => j.id === Number(route.params.id))
    if (jobData) {
      job.value = jobData
      initCharts(jobData)
    } else {
      ElMessage.error('岗位不存在')
    }
  } catch (error) {
    ElMessage.error('获取岗位详情失败')
  }
}

const getScoreClass = (score) => {
  if (score >= 80) return 'score-high'
  if (score >= 60) return 'score-medium'
  return 'score-low'
}

const initCharts = (jobData) => {
  if (scoreChartRef.value) {
    const scoreDistribution = jobData?.scoreDistribution || []
    const colors = [
      new echarts.graphic.LinearGradient(0, 0, 1, 1, [{ offset: 0, color: '#52C41A' }, { offset: 1, color: '#73D13D' }]),
      new echarts.graphic.LinearGradient(0, 0, 1, 1, [{ offset: 0, color: '#1890FF' }, { offset: 1, color: '#40A9FF' }]),
      new echarts.graphic.LinearGradient(0, 0, 1, 1, [{ offset: 0, color: '#FA8C16' }, { offset: 1, color: '#FFA940' }])
    ]
    scoreChart = echarts.init(scoreChartRef.value)
    scoreChart.setOption({
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
        radius: ['40%', '70%'],
        center: ['50%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 8,
          borderColor: 'rgba(255, 255, 255, 0.9)',
          borderWidth: 2
        },
        label: {
          show: true,
          color: '#595959',
          fontSize: 12,
          formatter: '{b}\n{d}%'
        },
        labelLine: {
          lineStyle: { color: 'rgba(0, 0, 0, 0.06)' }
        },
        data: scoreDistribution.length > 0
          ? scoreDistribution.map((d, index) => ({
              value: d.count,
              name: d.range,
              itemStyle: { color: colors[index % colors.length] }
            }))
          : [
              { value: 15, name: '80-100分', itemStyle: { color: colors[0] } },
              { value: 35, name: '60-79分', itemStyle: { color: colors[1] } },
              { value: 50, name: '60分以下', itemStyle: { color: colors[2] } }
            ],
        animationType: 'expansion',
        animationDuration: 1500,
        animationEasing: 'cubicOut'
      }]
    })
  }
  
  if (trendChartRef.value) {
    const trendData = jobData?.applicationTrend || []
    trendChart = echarts.init(trendChartRef.value)
    trendChart.setOption({
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
        data: trendData.map(d => d.date),
        axisLine: { lineStyle: { color: 'rgba(0, 0, 0, 0.06)' } },
        axisLabel: { color: '#595959', fontSize: 11 }
      },
      yAxis: { 
        type: 'value',
        splitLine: { lineStyle: { color: 'rgba(0, 0, 0, 0.04)', type: 'dashed' } },
        axisLabel: { color: '#595959', fontSize: 11 }
      },
      series: [{ 
        data: trendData.map(d => d.count), 
        type: 'bar',
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#52C41A' },
            { offset: 0.5, color: '#73D13D' },
            { offset: 1, color: '#1890FF' }
          ]),
          borderRadius: [6, 6, 0, 0]
        },
        barWidth: '50%',
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
}

const handleResize = () => {
  scoreChart?.resize()
  trendChart?.resize()
}

onMounted(() => {
  fetchJobDetail()
  setTimeout(() => {
    initCharts()
  }, 300)
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  scoreChart?.dispose()
  trendChart?.dispose()
})
</script>

<style scoped lang="scss">
.job-detail-page {
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
  gap: 12px;
  
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
  
  .back-btn {
    height: 44px;
    padding: 0 24px;
    font-size: 14px;
    font-weight: 600;
    border-radius: var(--radius-md);
    background: rgba(82, 196, 26, 0.15);
    color: #fff;
    border: 1px solid rgba(255, 255, 255, 0.3);
    backdrop-filter: blur(8px);
    transition: var(--transition-base);
    display: flex;
    align-items: center;
    gap: 8px;
    
    &:hover {
      background: rgba(255, 255, 255, 0.25);
      transform: translateY(-2px);
    }
    
    &:active {
      transform: translateY(0) scale(0.98);
    }
  }
}

.page-content {
  padding: 0 24px 24px;
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
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--card-border);
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.card-badge {
  padding: 4px 12px;
  border-radius: var(--radius-full);
  font-size: 12px;
  font-weight: 600;
  background: rgba(82, 196, 26, 0.08);
  color: var(--text-tertiary);
  border: 1px solid var(--card-border);
  
  &.card-badge-info {
    background: rgba(124, 58, 237, 0.15);
    color: var(--secondary-light);
    border-color: rgba(124, 58, 237, 0.3);
  }
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.04);
  border-radius: var(--radius-md);
  border: 1px solid rgba(255, 255, 255, 0.06);
  
  .info-label {
    font-size: 12px;
    color: var(--text-tertiary);
    font-weight: 500;
  }
  
  .info-value {
    font-size: 14px;
    color: var(--text-primary);
    font-weight: 500;
    
    &.info-value-accent {
      color: var(--accent-color);
      font-weight: 600;
    }
  }
}

.status-badge {
  display: inline-block;
  padding: 6px 14px;
  border-radius: var(--radius-full);
  font-size: 12px;
  font-weight: 600;
  transition: var(--transition-base);
  
  &.status-published {
    background: rgba(16, 185, 129, 0.15);
    color: var(--success-color);
    border: 1px solid rgba(16, 185, 129, 0.3);
  }
  
  &.status-unpublished {
    background: rgba(148, 163, 184, 0.15);
    color: var(--text-tertiary);
    border: 1px solid rgba(148, 163, 184, 0.3);
  }
}

.content-text {
  line-height: 1.8;
  color: var(--text-secondary);
  white-space: pre-wrap;
  font-size: 14px;
}

.match-btn {
  width: 100%;
  height: 44px;
  padding: 0 24px;
  font-size: 14px;
  font-weight: 600;
  border-radius: var(--radius-md);
  background: var(--gradient-primary);
  border: none;
  box-shadow: 0 4px 12px var(--primary-glow);
  transition: var(--transition-base);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-bottom: 16px;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px var(--primary-glow);
  }
  
  &:active {
    transform: translateY(0) scale(0.98);
  }
}

.related-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.related-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: var(--radius-md);
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid transparent;
  transition: var(--transition-base);
  
  &:hover {
    background: rgba(255, 255, 255, 0.06);
    border-color: var(--card-border);
  }
  
  .resume-avatar {
    width: 40px;
    height: 40px;
    border-radius: var(--radius-md);
    background: rgba(255, 255, 255, 0.06);
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--text-secondary);
  }
  
  .resume-info {
    flex: 1;
    
    .resume-name {
      font-size: 14px;
      font-weight: 500;
      color: var(--text-primary);
      margin: 0 0 4px 0;
    }
    
    .resume-meta {
      display: flex;
      align-items: center;
      gap: 8px;
      margin: 0;
    }
    
    .match-score {
      font-size: 12px;
      font-weight: 600;
      padding: 2px 8px;
      border-radius: var(--radius-full);
      
      &.score-high {
        background: rgba(16, 185, 129, 0.15);
        color: var(--success-color);
      }
      
      &.score-medium {
        background: rgba(245, 158, 11, 0.15);
        color: var(--accent-color);
      }
      
      &.score-low {
        background: rgba(225, 29, 72, 0.15);
        color: var(--danger-color);
      }
    }
    
    .resume-date {
      font-size: 12px;
      color: var(--text-tertiary);
    }
  }
  
  .view-btn {
    padding: 4px 12px;
    border-radius: var(--radius-md);
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid var(--card-border);
    color: var(--text-secondary);
    font-size: 12px;
    font-weight: 500;
    transition: var(--transition-base);
    
    &:hover {
      background: var(--primary-color);
      border-color: var(--primary-color);
      color: #fff;
    }
  }
}

.score-chart {
  width: 100%;
  height: 220px;
}

.trend-chart {
  width: 100%;
  height: 220px;
}

.weight-info-content {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-top: 12px;
}

.weight-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: var(--radius-sm);
  border: 1px solid var(--card-border);
  
  .weight-label {
    font-size: 12px;
    color: var(--text-tertiary);
    margin-bottom: 4px;
  }
  
  .weight-value {
    font-size: 16px;
    font-weight: 700;
    color: var(--primary-color);
  }
}
</style>
