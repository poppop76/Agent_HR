<template>
  <div class="matching-report-page page-container">
    <div class="card-container">
      <div class="flex-between mb-20">
        <h2 class="section-title" style="margin: 0">匹配报告</h2>
        <el-button @click="router.back()">返回</el-button>
      </div>
      
      <div class="report-header">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="候选人">{{ report.candidateName || '未知候选人' }}</el-descriptions-item>
          <el-descriptions-item label="目标岗位">{{ report.jobName || '未知岗位' }}</el-descriptions-item>
          <el-descriptions-item label="匹配时间">{{ report.matchTime || '未知时间' }}</el-descriptions-item>
          <el-descriptions-item label="总分">
            <span :class="getScoreClass(report.totalScore)" class="total-score">
              {{ report.totalScore || '0' }}
            </span>
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </div>
    
    <div class="card-container">
      <h3 class="subsection-title">各维度得分明细</h3>
      <el-row :gutter="20">
        <el-col :span="12">
          <div ref="radarChartRef" class="radar-chart"></div>
        </el-col>
        <el-col :span="12">
          <el-row :gutter="10">
            <el-col :span="12" v-for="dimension in dimensions" :key="dimension.name">
              <div class="dimension-card">
                <div class="dimension-header">
                  <el-icon :size="24" :color="dimension.color"><component :is="dimension.icon" /></el-icon>
                  <span>{{ dimension.name }}</span>
                </div>
                <div class="dimension-score" :class="getScoreClass(report[dimension.key])">
                  {{ report[dimension.key] || '0' }}
                </div>
                <el-progress 
                  :percentage="report[dimension.key] || 0" 
                  :color="dimension.color"
                  :stroke-width="8"
                />
              </div>
            </el-col>
          </el-row>
        </el-col>
      </el-row>
    </div>
    
    <div v-if="report.weightInfo" class="card-container">
      <h3 class="subsection-title">权重配置</h3>
      <div class="weight-config-card">
        <div class="weight-config-header">
          <el-tag :type="getJobTypeTagType(report.weightInfo.jobType)" effect="dark" size="large">{{ report.weightInfo.jobTypeDesc || report.weightInfo.jobType }}</el-tag>
          <span class="weight-desc">{{ report.weightInfo.jobTypeDesc }}</span>
        </div>
        <div class="weight-config-content">
          <div class="weight-config-item">
            <span class="weight-config-label">技能权重</span>
            <span class="weight-config-value">{{ (report.weightInfo.skillWeight * 100).toFixed(0) }}%</span>
          </div>
          <div class="weight-config-item">
            <span class="weight-config-label">经验权重</span>
            <span class="weight-config-value">{{ (report.weightInfo.experienceWeight * 100).toFixed(0) }}%</span>
          </div>
          <div class="weight-config-item">
            <span class="weight-config-label">学历权重</span>
            <span class="weight-config-value">{{ (report.weightInfo.educationWeight * 100).toFixed(0) }}%</span>
          </div>
          <div class="weight-config-item">
            <span class="weight-config-label">项目权重</span>
            <span class="weight-config-value">{{ (report.weightInfo.projectWeight * 100).toFixed(0) }}%</span>
          </div>
        </div>
      </div>
    </div>
    
    <div class="card-container">
      <h3 class="subsection-title">简历与JD对比</h3>
      <el-table :data="comparisonData" border style="width: 100%">
        <el-table-column prop="dimension" label="维度" width="150" />
        <el-table-column prop="requirement" label="岗位要求" />
        <el-table-column prop="candidate" label="候选人情况" />
        <el-table-column prop="match" label="匹配度" width="100">
          <template #default="{ row }">
            <el-tag :type="row.match === '高' ? 'success' : row.match === '中' ? 'warning' : 'danger'">
              {{ row.match }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </div>
    
    <div class="card-container">
      <h3 class="subsection-title">匹配亮点</h3>
      <ul class="highlights-list">
        <li v-for="(item, index) in report.highlights" :key="index">{{ item || '暂无亮点' }}</li>
      </ul>
    </div>
    
    <div class="card-container">
      <h3 class="subsection-title">不足之处</h3>
      <ul class="highlights-list">
        <li v-for="(item, index) in report.weaknesses" :key="index">{{ item || '暂无不足' }}</li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { matchingApi } from '@/api'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { Download, Trophy, Briefcase, School, FolderOpened } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()

const report = ref({})
const radarChartRef = ref(null)
let radarChart = null

const dimensions = [
  { name: '技能匹配', key: 'skillScore', color: '#52C41A', icon: 'Trophy' },
  { name: '经验匹配', key: 'experienceScore', color: '#1890FF', icon: 'Briefcase' },
  { name: '学历匹配', key: 'educationScore', color: '#FA8C16', icon: 'School' },
  { name: '项目匹配', key: 'projectScore', color: '#FF4D4F', icon: 'FolderOpened' }
]

const comparisonData = computed(() => {
  return report.value.comparison || []
})

const getScoreClass = (score) => {
  if (score >= 80) return 'text-success'
  if (score >= 60) return 'text-primary'
  if (score >= 40) return 'text-warning'
  return 'text-danger'
}

const getJobTypeTagType = (jobType) => {
  const map = { technical: 'success', management: 'warning', operation: 'primary', administrative: 'info' }
  return map[jobType] || ''
}

const initRadarChart = () => {
  if (!radarChartRef.value) return
  
  radarChart = echarts.init(radarChartRef.value)
  radarChart.setOption({
    backgroundColor: 'transparent',
    tooltip: { 
      trigger: 'item',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: 'rgba(82, 196, 26, 0.2)',
      borderWidth: 1,
      textStyle: { color: '#262626' },
      extraCssText: 'backdrop-filter: blur(12px); border-radius: 12px; box-shadow: 0 4px 16px rgba(0,0,0,0.08);'
    },
    radar: {
      indicator: dimensions.map(d => ({ name: d.name, max: 100 })),
      radius: '70%',
      axisName: {
        color: '#595959',
        fontSize: 12,
        fontWeight: 600
      },
      axisLine: {
        lineStyle: { color: 'rgba(0, 0, 0, 0.06)' }
      },
      splitLine: {
        lineStyle: { color: 'rgba(0, 0, 0, 0.06)' }
      },
      splitArea: {
        areaStyle: {
          color: ['rgba(82, 196, 26, 0.02)', 'rgba(82, 196, 26, 0.04)']
        }
      }
    },
    series: [{
      type: 'radar',
      data: [{
        value: dimensions.map(d => report.value[d.key] || 0),
        name: '匹配度',
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 1, 1, [
            { offset: 0, color: '#52C41A' },
            { offset: 1, color: '#1890FF' }
          ])
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(82, 196, 26, 0.3)' },
            { offset: 1, color: 'rgba(24, 144, 255, 0.1)' }
          ])
        },
        lineStyle: {
          width: 3,
          color: new echarts.graphic.LinearGradient(0, 0, 1, 1, [
            { offset: 0, color: '#52C41A' },
            { offset: 1, color: '#1890FF' }
          ])
        }
      }],
      animationDuration: 1500,
      animationEasing: 'cubicOut'
    }]
  })
}

const fetchReport = async () => {
  try {
    const res = await matchingApi.getMatchingReport(route.params.id)
    report.value = res.data
    setTimeout(() => initRadarChart(), 300)
  } catch (error) {
    ElMessage.error('获取匹配报告失败')
  }
}

const handleResize = () => {
  radarChart?.resize()
}

onMounted(() => {
  fetchReport()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  radarChart?.dispose()
})
</script>

<style scoped lang="scss">
.section-title {
  font-size: 18px;
  color: #303133;
}

.subsection-title {
  font-size: 16px;
  color: #303133;
  margin-bottom: 15px;
}

.report-header {
  margin-bottom: 20px;
}

.total-score {
  font-size: 24px;
  font-weight: bold;
}

.dimension-card {
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
  text-align: center;
  margin-bottom: 15px;
}

.dimension-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-bottom: 15px;
  font-weight: 500;
}

.dimension-score {
  font-size: 32px;
  font-weight: bold;
  margin-bottom: 15px;
}

.highlights-list {
  list-style: none;
  padding: 0;
  
  li {
    padding: 10px 0;
    border-bottom: 1px solid #ebeef5;
    color: #606266;
    
    &:before {
      content: '✓';
      color: var(--success-color);
      margin-right: 10px;
      font-weight: bold;
    }
  }
}

.radar-chart {
  width: 100%;
  height: 320px;
}

.weight-config-card {
  padding: 20px;
  background: var(--glass-bg);
  border-radius: var(--radius-lg);
  border: 1px solid var(--glass-border);
  backdrop-filter: blur(12px);
}

.weight-config-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px dashed var(--glass-border);
  
  .weight-desc {
    font-size: 13px;
    color: var(--text-tertiary);
    line-height: 1.5;
  }
}

.weight-config-content {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.weight-config-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: var(--radius-md);
  border: 1px solid var(--glass-border);
  
  .weight-config-label {
    font-size: 13px;
    color: var(--text-secondary);
    margin-bottom: 8px;
  }
  
  .weight-config-value {
    font-size: 20px;
    font-weight: 700;
    color: var(--primary-color);
  }
}
</style>
