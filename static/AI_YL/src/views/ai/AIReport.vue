<template>
  <div class="ai-report-page">
    <div class="page-header">
      <el-button text @click="$router.push('/ai-center')" class="back-btn">
        <el-icon><ArrowLeft /></el-icon>
        <span>返回 AI 中心</span>
      </el-button>
      <h1 class="page-title">智能报告中心</h1>
      <p class="page-subtitle">一键生成专业的招聘数据分析报告</p>
    </div>

    <div class="page-content">
      <el-row :gutter="20">
        <el-col :xs="24" :md="7">
          <div class="form-card glass-card">
            <h3 class="card-title">报告配置</h3>
            <el-form :model="form" label-position="top">
              <el-form-item label="报告类型">
                <el-select v-model="form.reportType" placeholder="请选择报告类型" style="width: 100%">
                  <el-option label="招聘周报" value="weekly" />
                  <el-option label="招聘月报" value="monthly" />
                  <el-option label="季度报告" value="quarterly" />
                  <el-option label="综合报告" value="recruitment" />
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
                <span>{{ loading ? '生成中...' : '生成报告' }}</span>
              </el-button>
            </el-form>

            <el-divider />

            <div class="report-history">
              <div class="history-header">
                <h4>历史报告</h4>
                <span class="history-count">共 {{ reportList.length }} 份</span>
              </div>
              <div class="history-list" v-if="reportList.length > 0">
                <div v-for="item in reportList" :key="item.id" class="history-item">
                  <div class="history-content" @click="loadReport(item)">
                    <span class="history-title">{{ item.title }}</span>
                    <span class="history-date">{{ formatDate(item.createdAt) }}</span>
                    <span class="history-period">{{ item.period }}</span>
                  </div>
                  <div class="history-actions">
                    <el-button 
                      size="small" 
                      icon="View" 
                      @click.stop="loadReport(item)"
                      title="查看">
                    </el-button>
                    <el-button 
                      size="small" 
                      icon="Delete" 
                      type="danger" 
                      @click.stop="handleDelete(item.id)"
                      title="删除">
                    </el-button>
                  </div>
                </div>
              </div>
              <el-empty v-else description="暂无历史报告" :image-size="60" />
            </div>
          </div>
        </el-col>

        <el-col :xs="24" :md="17">
          <div class="result-card glass-card" v-if="result">
            <!-- 报告头部 -->
            <div class="report-header">
              <div class="header-left">
                <div class="report-icon">📊</div>
                <div>
                  <h2 class="report-title">{{ result.title }}</h2>
                  <div class="report-meta">
                    <el-tag type="primary" class="type-tag">{{ getReportTypeName(result.title) }}</el-tag>
                    <span class="report-period">📅 {{ result.period }}</span>
                  </div>
                </div>
              </div>
              <div class="header-right">
                <div class="report-badge">
                  <span class="badge-icon">✓</span>
                  <span>已生成</span>
                </div>
              </div>
            </div>

            <!-- 核心结论 -->
            <div class="report-summary" v-if="result.summary">
              <div class="summary-header">
                <div class="summary-icon">🎯</div>
                <h4>核心结论</h4>
              </div>
              <div class="summary-content">
                <p>{{ result.summary }}</p>
              </div>
            </div>

            <!-- 关键指标 -->
            <div class="report-stats" v-if="result.keyMetrics">
              <div class="section-header">
                <div class="section-icon">📊</div>
                <h4>关键指标</h4>
              </div>
              <div class="stats-grid">
                <div class="stat-card" v-if="result.keyMetrics.newResumes !== undefined">
                  <div class="stat-icon-wrapper blue-gradient">
                    <span class="stat-emoji">📥</span>
                  </div>
                  <div class="stat-info">
                    <span class="stat-value">{{ result.keyMetrics.newResumes }}</span>
                    <span class="stat-label">新增简历</span>
                  </div>
                  <div class="stat-trend positive">
                    <span>↑ 12%</span>
                  </div>
                </div>
                <div class="stat-card" v-if="result.keyMetrics.totalCandidates !== undefined">
                  <div class="stat-icon-wrapper green-gradient">
                    <span class="stat-emoji">👥</span>
                  </div>
                  <div class="stat-info">
                    <span class="stat-value">{{ result.keyMetrics.totalCandidates }}</span>
                    <span class="stat-label">累计候选人</span>
                  </div>
                  <div class="stat-trend positive">
                    <span>↑ 8%</span>
                  </div>
                </div>
                <div class="stat-card" v-if="result.keyMetrics.matchCount !== undefined">
                  <div class="stat-icon-wrapper purple-gradient">
                    <span class="stat-emoji">🔗</span>
                  </div>
                  <div class="stat-info">
                    <span class="stat-value">{{ result.keyMetrics.matchCount }}</span>
                    <span class="stat-label">匹配次数</span>
                  </div>
                  <div class="stat-trend neutral">
                    <span>--</span>
                  </div>
                </div>
                <div class="stat-card" v-if="result.keyMetrics.avgScore !== undefined">
                  <div class="stat-icon-wrapper orange-gradient">
                    <span class="stat-emoji">⭐</span>
                  </div>
                  <div class="stat-info">
                    <span class="stat-value">{{ result.keyMetrics.avgScore }}</span>
                    <span class="stat-label">平均匹配分</span>
                  </div>
                  <div class="stat-trend positive">
                    <span>↑ 5%</span>
                  </div>
                </div>
                <div class="stat-card" v-if="result.keyMetrics.interviewCount !== undefined">
                  <div class="stat-icon-wrapper teal-gradient">
                    <span class="stat-emoji">🎯</span>
                  </div>
                  <div class="stat-info">
                    <span class="stat-value">{{ result.keyMetrics.interviewCount }}</span>
                    <span class="stat-label">安排面试</span>
                  </div>
                  <div class="stat-trend negative">
                    <span>↓ 3%</span>
                  </div>
                </div>
                <div class="stat-card" v-if="result.keyMetrics.offerCount !== undefined">
                  <div class="stat-icon-wrapper red-gradient">
                    <span class="stat-emoji">✈️</span>
                  </div>
                  <div class="stat-info">
                    <span class="stat-value">{{ result.keyMetrics.offerCount }}</span>
                    <span class="stat-label">发放offer</span>
                  </div>
                  <div class="stat-trend positive">
                    <span>↑ 15%</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- 趋势分析 -->
            <div class="report-trends" v-if="result.trends && result.trends.length > 0">
              <div class="section-header">
                <div class="section-icon">📈</div>
                <h4>趋势分析</h4>
              </div>
              <div class="trends-chart">
                <div class="chart-bars">
                  <div v-for="(item, idx) in result.trends" :key="idx" class="bar-item">
                    <div class="bar-wrapper">
                      <div 
                        class="bar-fill" 
                        :style="{ height: getBarHeight(item.value) + '%' }"
                        :class="getChangeClass(item.change)"
                      ></div>
                    </div>
                    <span class="bar-label">{{ item.period }}</span>
                    <span class="bar-value">{{ item.value }}</span>
                    <span class="bar-change" :class="getChangeClass(item.change)">
                      {{ item.change }}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <!-- 关键洞察 -->
            <div class="report-insights" v-if="result.insights && result.insights.length > 0">
              <div class="section-header">
                <div class="section-icon">💡</div>
                <h4>关键洞察</h4>
              </div>
              <div class="insight-list">
                <div v-for="(insight, idx) in result.insights" :key="idx" class="insight-card">
                  <div class="insight-badge">{{ idx + 1 }}</div>
                  <div class="insight-content">
                    <h5 class="insight-title">{{ insight.title }}</h5>
                    <p class="insight-desc">{{ insight.content }}</p>
                  </div>
                  <div class="insight-icon">💡</div>
                </div>
              </div>
            </div>

            <!-- 工作亮点 -->
            <div class="report-highlights" v-if="result.highlights && result.highlights.length > 0">
              <div class="section-header">
                <div class="section-icon">✨</div>
                <h4>工作亮点</h4>
              </div>
              <div class="highlights-grid">
                <div v-for="(item, idx) in result.highlights" :key="idx" class="highlight-card">
                  <div class="highlight-icon">✓</div>
                  <span class="highlight-text">{{ item }}</span>
                </div>
              </div>
            </div>

            <!-- 问题与建议 -->
            <div class="report-issues" v-if="result.issues && result.issues.length > 0">
              <div class="section-header">
                <div class="section-icon">⚠️</div>
                <h4>问题与建议</h4>
              </div>
              <div class="issues-list">
                <div v-for="(issue, idx) in result.issues" :key="idx" class="issue-card">
                  <div class="issue-header">
                    <div class="issue-icon">❗</div>
                    <span class="issue-title">待改进项 {{ idx + 1 }}</span>
                  </div>
                  <div class="issue-body">
                    <div class="issue-item">
                      <span class="issue-label">问题</span>
                      <span class="issue-text">{{ issue.issue }}</span>
                    </div>
                    <div class="suggestion-item">
                      <span class="suggestion-label">建议</span>
                      <span class="suggestion-text">{{ issue.suggestion }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 下期计划 -->
            <div class="report-next" v-if="result.nextPlan">
              <div class="section-header">
                <div class="section-icon">📋</div>
                <h4>下期工作计划</h4>
              </div>
              <div class="next-plan-card">
                <div class="plan-icon">🎯</div>
                <p class="plan-content">{{ result.nextPlan }}</p>
              </div>
            </div>

            <!-- 报告正文 -->
            <div class="report-content" v-if="result.content">
              <div class="section-header">
                <div class="section-icon">📄</div>
                <h4>详细报告</h4>
              </div>
              <div class="content-body" v-html="renderContent(result.content)"></div>
            </div>

            <!-- 报告底部 -->
            <div class="report-footer">
              <div class="footer-info">
                <span class="footer-label">生成时间</span>
                <span class="footer-value">{{ result.createdAt || formatDate(new Date().toISOString()) }}</span>
              </div>
              <div class="footer-actions">
                <el-button size="small" icon="Download">导出报告</el-button>
                <el-button size="small" icon="Refresh" @click="handleGenerate">重新生成</el-button>
              </div>
            </div>
          </div>

          <div class="empty-card glass-card" v-else>
            <div class="empty-content">
              <div class="empty-illustration">
                <div class="empty-icon">📊</div>
                <div class="empty-decoration">
                  <span class="deco deco-1">📈</span>
                  <span class="deco deco-2">📋</span>
                  <span class="deco deco-3">💡</span>
                </div>
              </div>
              <h3>智能招聘报告</h3>
              <p>选择报告类型和时间范围，点击"生成报告"按钮获取专业的招聘数据分析报告</p>
              <div class="feature-grid">
                <div class="feature-card">
                  <span class="feature-icon">📊</span>
                  <span class="feature-text">数据可视化分析</span>
                </div>
                <div class="feature-card">
                  <span class="feature-icon">📈</span>
                  <span class="feature-text">趋势洞察</span>
                </div>
                <div class="feature-card">
                  <span class="feature-icon">💡</span>
                  <span class="feature-text">智能建议</span>
                </div>
              </div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { aiApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, MagicStick, View, Delete } from '@element-plus/icons-vue'

const loading = ref(false)
const result = ref(null)
const reportList = ref([])

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
    
    // 检查是否服务不可用（欠费等错误）
    if (res.code === '500' || (res.data === null && res.msg === '服务暂时不可用，请稍后重试')) {
      ElMessage.error(res.msg || '服务暂时不可用，请稍后重试')
      return
    }
    
    result.value = res.data
    ElMessage.success('报告生成成功')
    fetchReportList()
  } catch (error) {
    console.error('报告生成失败:', error)
    ElMessage.error('报告生成失败')
  } finally {
    loading.value = false
  }
}

const fetchReportList = async () => {
  try {
    const res = await aiApi.getReportList({ page: 1, pageSize: 10 })
    reportList.value = res.data.list || []
  } catch (error) {
    console.error('获取报告列表失败')
  }
}

const loadReport = async (item) => {
  try {
    const res = await aiApi.getReportDetail(item.id)
    const reportData = res.data
    // 构建完整的报告结果
    result.value = {
      id: reportData.id,
      title: reportData.title,
      period: reportData.period,
      summary: '',
      content: reportData.content,
      keyMetrics: {
        newResumes: reportData.newResumes,
        totalCandidates: 0,
        matchCount: reportData.matchCount,
        avgScore: reportData.avgScore || 0,
        interviewCount: 0,
        offerCount: 0
      },
      trends: [],
      insights: [],
      highlights: [],
      issues: [],
      nextPlan: ''
    }
    ElMessage.success('报告加载成功')
  } catch (error) {
    console.error('加载报告失败:', error)
    // 降级处理：使用列表项数据
    result.value = {
      id: item.id,
      title: item.title,
      period: item.period,
      summary: '',
      content: '',
      keyMetrics: {
        newResumes: item.newResumes,
        totalCandidates: 0,
        matchCount: item.matchCount,
        avgScore: item.avgScore || 0,
        interviewCount: 0,
        offerCount: 0
      },
      trends: [],
      insights: [],
      highlights: [],
      issues: [],
      nextPlan: ''
    }
    ElMessage.warning('报告详情获取失败，显示基本信息')
  }
}

const handleDelete = async (id) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这份报告吗？',
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await aiApi.deleteReport(id)
    ElMessage.success('删除成功')
    fetchReportList()
    // 如果当前显示的是被删除的报告，清空显示
    if (result.value && result.value.id === id) {
      result.value = null
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  // 显示完整时间，精确到分钟
  // 格式：YYYY-MM-DD HH:MM
  const date = new Date(dateStr)
  if (isNaN(date.getTime())) {
    // 如果解析失败，尝试截取字符串
    const parts = dateStr.split(' ')
    if (parts.length >= 2) {
      const timePart = parts[1]
      const timeParts = timePart.split(':')
      if (timeParts.length >= 2) {
        return `${parts[0]} ${timeParts[0]}:${timeParts[1]}`
      }
      return dateStr
    }
    return dateStr
  }
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${year}-${month}-${day} ${hours}:${minutes}`
}

const getReportTypeName = (title) => {
  if (title.includes('周')) return '周报'
  if (title.includes('月')) return '月报'
  if (title.includes('季度')) return '季度报告'
  return '综合报告'
}

const getChangeClass = (change) => {
  if (!change) return ''
  return change.startsWith('+') ? 'change-up' : 'change-down'
}

const renderContent = (content) => {
  if (!content) return ''
  
  // 规范化内容格式 - 处理各种表格格式
  let formatted = content
  
  // 处理引用块 (> 文本)
  formatted = formatted.replace(/^>\s+(.+)$/gm, '<blockquote class="content-blockquote">$1</blockquote>')
  
  // 处理分隔线 (--- 或 ***)
  formatted = formatted.replace(/^[-*]{3,}$/gm, '<hr class="content-divider">')
  
  // 处理 Markdown 表格
  const tableRegex = /\|(.+)\|\n\|[-:\s]+\|[-:\s]+\|[-:\s]+\|/g
  formatted = formatted.replace(tableRegex, (match) => {
    const lines = match.trim().split('\n')
    const headerLine = lines[0]
    const dataLines = lines.slice(2)
    
    // 解析表头
    const headers = headerLine.split('|')
      .map(h => h.trim())
      .filter(h => h && !/^[-:]+$/.test(h))
    
    // 解析数据行
    const rows = dataLines.map(line => {
      const cells = line.split('|')
        .map(c => c.trim())
        .filter(c => c && !/^[-:]+$/.test(c))
      return cells
    }).filter(row => row.length > 0)
    
    // 构建HTML表格
    let tableHtml = '<div class="content-table-wrapper"><table class="content-table"><thead><tr>'
    headers.forEach(h => {
      tableHtml += `<th>${h}</th>`
    })
    tableHtml += '</tr></thead><tbody>'
    rows.forEach(row => {
      tableHtml += '<tr>'
      row.forEach(cell => {
        tableHtml += `<td>${cell}</td>`
      })
      tableHtml += '</tr>'
    })
    tableHtml += '</tbody></table></div>'
    
    return tableHtml
  })
  
  // 处理标题
  formatted = formatted.replace(/^##\s+(.+)$/gm, '<h3 class="content-h3">$1</h3>')
  formatted = formatted.replace(/^###\s+(.+)$/gm, '<h4 class="content-h4">$1</h4>')
  
  // 处理加粗
  formatted = formatted.replace(/\*\*(.+?)\*\*/g, '<strong class="content-strong">$1</strong>')
  
  // 处理代码行（反引号包裹的内容）
  formatted = formatted.replace(/`([^`]+)`/g, '<code class="content-code">$1</code>')
  
  // 处理列表项
  formatted = formatted.replace(/^[-*]\s+(.+)$/gm, '<li class="content-list-item">$1</li>')
  formatted = formatted.replace(/^\d+\.\s+(.+)$/gm, '<li class="content-list-item numbered">$1</li>')
  
  // 处理段落（连续的非空行）
  formatted = formatted.replace(/\n\n+/g, '</p><p class="content-paragraph">')
  
  // 包装成段落
  if (!formatted.startsWith('<h') && !formatted.startsWith('<li') && !formatted.startsWith('<blockquote') && !formatted.startsWith('<div') && !formatted.startsWith('<hr')) {
    formatted = '<p class="content-paragraph">' + formatted + '</p>'
  }
  
  // 清理空段落
  formatted = formatted.replace(/<p class="content-paragraph"><\/p>/g, '')
  formatted = formatted.replace(/<p class="content-paragraph">(<h[34])/g, '$1')
  formatted = formatted.replace(/(<\/h[34]>)<\/p>/g, '$1')
  
  return formatted
}

onMounted(() => {
  fetchReportList()
})
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
  height: 100%;
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

.report-history {
  .history-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    
    h4 {
      font-size: 14px;
      color: var(--text-primary);
      margin: 0;
    }
    
    .history-count {
      font-size: 12px;
      color: var(--text-secondary);
      background: var(--primary-glow);
      padding: 2px 8px;
      border-radius: var(--radius-sm);
    }
  }

  .history-list {
    max-height: 400px;
    overflow-y: auto;
  }

  .history-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 12px;
    border-radius: var(--radius-sm);
    cursor: pointer;
    transition: all 0.2s;
    margin-bottom: 8px;
    background: var(--primary-glow);
    border: 1px solid transparent;

    &:hover {
      background: var(--primary-light);
      border-color: var(--primary-color);
    }

    .history-content {
      flex: 1;
      min-width: 0;
      cursor: pointer;
      
      .history-title {
        display: block;
        font-size: 13px;
        color: var(--text-primary);
        margin-bottom: 4px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }

      .history-date {
        font-size: 11px;
        color: var(--text-secondary);
        margin-right: 12px;
      }

      .history-period {
        font-size: 11px;
        color: var(--primary-color);
        background: rgba(102, 126, 234, 0.1);
        padding: 2px 6px;
        border-radius: var(--radius-xs);
      }
    }

    .history-actions {
      display: flex;
      gap: 4px;
      opacity: 0;
      transition: opacity 0.2s;
      
      button {
        padding: 4px 8px;
        font-size: 12px;
      }
    }
    
    &:hover .history-actions {
      opacity: 1;
    }
  }
}

.result-card {
  .report-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 24px;
    padding: 20px;
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
    border-radius: var(--radius-lg);
    border: 1px solid rgba(102, 126, 234, 0.2);

    .header-left {
      display: flex;
      align-items: center;
      gap: 16px;
    }

    .report-icon {
      width: 48px;
      height: 48px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: var(--primary-color);
      border-radius: var(--radius-md);
      font-size: 24px;
    }

    .report-title {
      font-size: 22px;
      font-weight: 700;
      color: var(--text-primary);
      margin: 0 0 8px 0;
    }

    .report-meta {
      display: flex;
      align-items: center;
      gap: 12px;

      .type-tag {
        background: var(--primary-color);
        border: none;
        color: #fff;
      }

      .report-period {
        font-size: 13px;
        color: var(--text-secondary);
      }
    }

    .header-right {
      .report-badge {
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 8px 12px;
        background: rgba(103, 194, 58, 0.1);
        border-radius: var(--radius-md);
        color: #67c23a;
        font-size: 12px;
        font-weight: 500;

        .badge-icon {
          width: 16px;
          height: 16px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: #67c23a;
          color: #fff;
          border-radius: 50%;
          font-size: 10px;
        }
      }
    }
  }

  .section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 16px;

    .section-icon {
      font-size: 18px;
    }

    h4 {
      font-size: 16px;
      font-weight: 600;
      color: var(--text-primary);
      margin: 0;
      padding-left: 8px;
      border-left: 3px solid var(--primary-color);
    }
  }
}

.report-summary {
  margin-bottom: 24px;
  padding: 20px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.08), rgba(118, 75, 162, 0.08));
  border-radius: var(--radius-lg);
  border: 1px solid rgba(102, 126, 234, 0.15);

  .summary-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 12px;

    .summary-icon {
      font-size: 20px;
    }

    h4 {
      font-size: 16px;
      font-weight: 600;
      color: var(--text-primary);
      margin: 0;
    }
  }

  .summary-content {
    padding: 12px 16px;
    background: rgba(255, 255, 255, 0.8);
    border-radius: var(--radius-md);

    p {
      margin: 0;
      font-size: 14px;
      line-height: 1.8;
      color: var(--text-primary);
    }
  }
}

.report-stats {
  margin-bottom: 24px;

  .stats-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;

    @media (max-width: 768px) {
      grid-template-columns: repeat(2, 1fr);
    }
  }

  .stat-card {
    padding: 20px;
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: var(--radius-lg);
    transition: all 0.3s;

    &:hover {
      border-color: var(--primary-color);
      transform: translateY(-4px);
      box-shadow: 0 8px 24px rgba(102, 126, 234, 0.15);
    }

    .stat-icon-wrapper {
      width: 44px;
      height: 44px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: var(--radius-md);
      margin-bottom: 12px;

      .stat-emoji {
        font-size: 22px;
      }

      &.blue-gradient {
        background: linear-gradient(135deg, #667eea, #764ba2);
      }

      &.green-gradient {
        background: linear-gradient(135deg, #11998e, #38ef7d);
      }

      &.purple-gradient {
        background: linear-gradient(135deg, #a855f7, #6366f1);
      }

      &.orange-gradient {
        background: linear-gradient(135deg, #f093fb, #f5576c);
      }

      &.teal-gradient {
        background: linear-gradient(135deg, #4facfe, #00f2fe);
      }

      &.red-gradient {
        background: linear-gradient(135deg, #fa709a, #fee140);
      }
    }

    .stat-info {
      display: flex;
      flex-direction: column;
      margin-bottom: 8px;

      .stat-value {
        font-size: 28px;
        font-weight: 700;
        color: var(--text-primary);
        line-height: 1.2;
      }

      .stat-label {
        font-size: 13px;
        color: var(--text-secondary);
        margin-top: 4px;
      }
    }

    .stat-trend {
      display: inline-flex;
      align-items: center;
      padding: 4px 8px;
      border-radius: var(--radius-sm);
      font-size: 12px;
      font-weight: 500;

      &.positive {
        background: rgba(103, 194, 58, 0.1);
        color: #67c23a;
      }

      &.negative {
        background: rgba(255, 103, 103, 0.1);
        color: #ff6767;
      }

      &.neutral {
        background: rgba(144, 147, 153, 0.1);
        color: #909399;
      }
    }
  }
}

.report-trends {
  margin-bottom: 24px;

  .trends-chart {
    padding: 20px;
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: var(--radius-lg);
  }

  .chart-bars {
    display: flex;
    justify-content: space-around;
    align-items: flex-end;
    height: 200px;
    padding-top: 20px;
  }

  .bar-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    flex: 1;
    max-width: 80px;
  }

  .bar-wrapper {
    width: 32px;
    height: 150px;
    background: rgba(102, 126, 234, 0.1);
    border-radius: var(--radius-sm);
    display: flex;
    align-items: flex-end;
    overflow: hidden;
  }

  .bar-fill {
    width: 100%;
    border-radius: var(--radius-sm);
    transition: height 0.5s ease;
    background: linear-gradient(180deg, #667eea, #764ba2);

    &.change-up {
      background: linear-gradient(180deg, #67c23a, #85ce61);
    }

    &.change-down {
      background: linear-gradient(180deg, #ff6767, #ffa940);
    }
  }

  .bar-label {
    font-size: 11px;
    color: var(--text-secondary);
    text-align: center;
  }

  .bar-value {
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary);
  }

  .bar-change {
    font-size: 11px;
    font-weight: 500;
    padding: 2px 6px;
    border-radius: var(--radius-xs);

    &.change-up {
      color: #67c23a;
      background: rgba(103, 194, 58, 0.1);
    }

    &.change-down {
      color: #ff6767;
      background: rgba(255, 103, 103, 0.1);
    }
  }
}

.report-insights {
  margin-bottom: 24px;

  .insight-list {
    display: grid;
    grid-template-columns: repeat(1, 1fr);
    gap: 16px;
  }

  .insight-card {
    display: flex;
    align-items: flex-start;
    gap: 16px;
    padding: 20px;
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: var(--radius-lg);
    transition: all 0.3s;

    &:hover {
      border-color: var(--primary-color);
      box-shadow: 0 4px 16px rgba(102, 126, 234, 0.1);
    }

    .insight-badge {
      width: 28px;
      height: 28px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: linear-gradient(135deg, #667eea, #764ba2);
      color: #fff;
      border-radius: var(--radius-md);
      font-size: 14px;
      font-weight: 600;
      flex-shrink: 0;
    }

    .insight-content {
      flex: 1;

      .insight-title {
        font-size: 15px;
        font-weight: 600;
        color: var(--text-primary);
        margin: 0 0 8px 0;
      }

      .insight-desc {
        font-size: 13px;
        line-height: 1.7;
        color: var(--text-secondary);
        margin: 0;
      }
    }

    .insight-icon {
      font-size: 24px;
      opacity: 0.5;
    }
  }
}

.report-highlights {
  margin-bottom: 24px;

  .highlights-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
  }

  .highlight-card {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px 20px;
    background: rgba(103, 194, 58, 0.08);
    border: 1px solid rgba(103, 194, 58, 0.2);
    border-radius: var(--radius-md);
    transition: all 0.3s;

    &:hover {
      background: rgba(103, 194, 58, 0.12);
      border-color: rgba(103, 194, 58, 0.4);
      transform: translateY(-2px);
    }

    .highlight-icon {
      width: 20px;
      height: 20px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: #67c23a;
      color: #fff;
      border-radius: 50%;
      font-size: 12px;
      font-weight: 700;
    }

    .highlight-text {
      font-size: 13px;
      color: var(--text-primary);
      font-weight: 500;
    }
  }
}

.report-issues {
  margin-bottom: 24px;

  .issues-list {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .issue-card {
    padding: 20px;
    background: rgba(255, 171, 145, 0.08);
    border: 1px solid rgba(255, 145, 108, 0.2);
    border-radius: var(--radius-lg);

    .issue-header {
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 16px;

      .issue-icon {
        font-size: 20px;
      }

      .issue-title {
        font-size: 14px;
        font-weight: 600;
        color: #e67e22;
      }
    }

    .issue-body {
      padding-left: 30px;
    }

    .issue-item, .suggestion-item {
      display: flex;
      gap: 12px;
      margin-bottom: 12px;

      &:last-child {
        margin-bottom: 0;
      }
    }

    .issue-label, .suggestion-label {
      font-size: 12px;
      font-weight: 600;
      padding: 2px 8px;
      border-radius: var(--radius-xs);
      flex-shrink: 0;
    }

    .issue-label {
      background: rgba(230, 126, 34, 0.15);
      color: #e67e22;
    }

    .suggestion-label {
      background: rgba(103, 194, 58, 0.15);
      color: #67c23a;
    }

    .issue-text, .suggestion-text {
      font-size: 13px;
      line-height: 1.6;
      color: var(--text-primary);
    }
  }
}

.report-next {
  margin-bottom: 24px;

  .next-plan-card {
    display: flex;
    gap: 16px;
    padding: 20px;
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.08), rgba(118, 75, 162, 0.08));
    border: 1px solid rgba(102, 126, 234, 0.15);
    border-radius: var(--radius-lg);

    .plan-icon {
      font-size: 28px;
      flex-shrink: 0;
    }

    .plan-content {
      margin: 0;
      font-size: 14px;
      line-height: 1.8;
      color: var(--text-primary);
    }
  }
}

.report-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: var(--radius-md);
  margin-top: 24px;

  .footer-info {
    display: flex;
    align-items: center;
    gap: 8px;

    .footer-label {
      font-size: 12px;
      color: var(--text-secondary);
    }

    .footer-value {
      font-size: 13px;
      color: var(--text-primary);
      font-weight: 500;
    }
  }

  .footer-actions {
    display: flex;
    gap: 8px;
  }
}

.report-content {
  margin-bottom: 24px;

  .content-body {
    padding: 24px;
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: var(--radius-lg);
    font-size: 14px;
    line-height: 1.8;
    color: var(--text-primary);

    .content-h3 {
      font-size: 18px;
      font-weight: 700;
      color: var(--text-primary);
      margin: 32px 0 16px 0;
      padding: 12px 16px;
      background: linear-gradient(135deg, rgba(102, 126, 234, 0.08), rgba(118, 75, 162, 0.08));
      border-left: 4px solid var(--primary-color);
      border-radius: var(--radius-md);
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .content-h4 {
      font-size: 15px;
      font-weight: 600;
      color: var(--text-primary);
      margin: 24px 0 12px 0;
      padding: 8px 12px;
      background: var(--primary-glow);
      border-left: 3px solid var(--primary-color);
      border-radius: var(--radius-sm);
    }

    .content-paragraph {
      margin: 12px 0;
      text-indent: 2em;
      line-height: 1.9;
    }

    .content-list-item {
      margin: 10px 0;
      padding: 8px 12px;
      background: rgba(102, 126, 234, 0.03);
      border-left: 2px solid var(--primary-color);
      border-radius: var(--radius-sm);
      text-indent: 0;
      
      &.numbered {
        background: rgba(118, 75, 162, 0.03);
        border-left-color: #764ba2;
      }
    }

    .content-strong {
      color: var(--primary-color);
      font-weight: 700;
      background: rgba(102, 126, 234, 0.1);
      padding: 2px 6px;
      border-radius: var(--radius-xs);
    }

    .content-code {
      font-family: 'Courier New', monospace;
      background: rgba(0, 0, 0, 0.05);
      padding: 2px 6px;
      border-radius: var(--radius-xs);
      font-size: 13px;
      color: #e83e8c;
    }

    .content-blockquote {
      margin: 16px 0;
      padding: 12px 16px;
      background: linear-gradient(135deg, rgba(102, 126, 234, 0.05), rgba(118, 75, 162, 0.05));
      border-left: 4px solid var(--primary-color);
      border-radius: var(--radius-md);
      font-style: italic;
      color: var(--text-secondary);
    }

    .content-divider {
      margin: 24px 0;
      border: none;
      height: 2px;
      background: linear-gradient(90deg, transparent, var(--primary-color), transparent);
      opacity: 0.3;
    }

    .content-table-wrapper {
      margin: 20px 0;
      overflow-x: auto;
      border-radius: var(--radius-md);
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }

    .content-table {
      width: 100%;
      border-collapse: collapse;
      background: var(--card-bg);

      thead {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));

        th {
          padding: 12px 16px;
          text-align: left;
          font-weight: 600;
          color: var(--text-primary);
          border-bottom: 2px solid var(--primary-color);
          font-size: 13px;
        }
      }

      tbody {
        tr {
          &:nth-child(even) {
            background: rgba(102, 126, 234, 0.02);
          }

          &:hover {
            background: rgba(102, 126, 234, 0.05);
          }

          td {
            padding: 12px 16px;
            border-bottom: 1px solid var(--card-border);
            color: var(--text-primary);
            font-size: 13px;
          }
        }
      }
    }
  }
}

.empty-card {
  .empty-content {
    text-align: center;
    padding: 60px 20px;

    .empty-illustration {
      position: relative;
      display: inline-block;
      margin-bottom: 24px;

      .empty-icon {
        font-size: 64px;
        display: block;
      }

      .empty-decoration {
        position: absolute;
        top: -10px;
        left: -20px;
        right: -20px;
        bottom: -10px;

        .deco {
          position: absolute;
          font-size: 24px;
          animation: float 3s ease-in-out infinite;

          &.deco-1 {
            top: 0;
            right: -10px;
            animation-delay: 0s;
          }

          &.deco-2 {
            bottom: 10px;
            left: -15px;
            animation-delay: 1s;
          }

          &.deco-3 {
            top: 20px;
            left: -25px;
            animation-delay: 2s;
          }
        }
      }
    }

    h3 {
      font-size: 18px;
      font-weight: 600;
      color: var(--text-primary);
      margin: 0 0 8px 0;
    }

    p {
      font-size: 13px;
      color: var(--text-secondary);
      margin: 0 0 24px 0;
    }

    .feature-grid {
      display: flex;
      justify-content: center;
      gap: 24px;
      flex-wrap: wrap;
    }

    .feature-card {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 8px;
      padding: 16px 24px;
      background: var(--primary-glow);
      border-radius: var(--radius-md);

      .feature-icon {
        font-size: 28px;
      }

      .feature-text {
        font-size: 13px;
        color: var(--text-primary);
        font-weight: 500;
      }
    }
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-10px);
  }
}

.report-trends, .report-insights, .report-highlights, .report-issues, .report-next, .report-content {
  margin-bottom: 24px;
}

.change-up {
  color: #67c23a;
  font-weight: 600;
}

.change-down {
  color: #f56c6c;
  font-weight: 600;
}

.el-divider {
  margin: 24px 0;
}
</style>
