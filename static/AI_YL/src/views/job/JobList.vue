<template>
  <div class="job-list-page">
    <div class="page-header">
      <div class="header-particles"></div>
      <div class="header-content">
        <h1 class="page-title">管理您的招聘岗位</h1>
        <p class="page-subtitle">创建、编辑和管理所有岗位信息</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" size="large" class="action-btn" @click="router.push('/jobs/add')">
          <el-icon><Plus /></el-icon>
          <span>新增岗位</span>
        </el-button>
      </div>
    </div>
    
    <div class="page-content">
      <div class="search-card glass-card">
        <el-form :inline="true" :model="searchForm" class="search-form">
          <el-form-item label="岗位名称">
            <el-input v-model="searchForm.name" placeholder="请输入岗位名称" clearable class="custom-input" />
          </el-form-item>
          <el-form-item label="部门">
            <el-select v-model="searchForm.department" placeholder="请选择部门" clearable class="custom-select">
              <el-option v-for="dept in departments" :key="dept" :label="dept" :value="dept" />
            </el-select>
          </el-form-item>
          <el-form-item label="分类">
            <el-select v-model="searchForm.category" placeholder="请选择分类" clearable class="custom-select">
              <el-option label="技术岗" value="技术岗" />
              <el-option label="职能岗" value="职能岗" />
              <el-option label="销售岗" value="销售岗" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" class="search-btn" @click="fetchJobs">搜索</el-button>
            <el-button class="reset-btn" @click="resetSearch">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <div class="table-card glass-card">
        <el-table :data="jobs" style="width: 100%" v-loading="loading" class="glass-table">
          <el-table-column prop="name" label="岗位名称" />
          <el-table-column prop="department" label="部门" />
          <el-table-column prop="category" label="分类" />
          <el-table-column prop="salary" label="薪资范围" />
          <el-table-column prop="location" label="工作地点" />
          <el-table-column prop="status" label="状态">
            <template #default="{ row }">
              <span :class="['status-badge', `status-${row.status}`]">
                {{ row.status === 'published' ? '已上架' : '已下架' }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="320">
            <template #default="{ row }">
              <el-button size="small" class="action-btn-small" @click="router.push(`/jobs/detail/${row.id}`)">详情</el-button>
              <el-button size="small" type="primary" class="action-btn-small" @click="router.push(`/jobs/edit/${row.id}`)">编辑</el-button>
              <el-button size="small" :type="row.status === 'published' ? 'warning' : 'success'" class="action-btn-small" @click="toggleStatus(row)">
                {{ row.status === 'published' ? '下架' : '上架' }}
              </el-button>
              <el-button size="small" type="danger" class="action-btn-small" @click="handleDelete(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
        
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          class="glass-pagination"
          layout="total, sizes, prev, pager, next"
          @size-change="fetchJobs"
          @current-change="fetchJobs"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { jobApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

const router = useRouter()

const jobs = ref([])
const departments = ref(['技术部', '产品部', '市场部', '人力资源部', '财务部', '行政部'])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

const searchForm = reactive({
  name: '',
  department: '',
  category: ''
})

const fetchJobs = async () => {
  loading.value = true
  try {
    const res = await jobApi.getJobList({
      page: page.value,
      pageSize: pageSize.value,
      ...searchForm
    })
    jobs.value = res.data.list
    total.value = res.data.total
  } catch (error) {
    console.error('获取岗位列表失败')
  } finally {
    loading.value = false
  }
}

const resetSearch = () => {
  searchForm.name = ''
  searchForm.department = ''
  searchForm.category = ''
  page.value = 1
  fetchJobs()
}

const toggleStatus = async (row) => {
  const newStatus = row.status === 'published' ? 'unpublished' : 'published'
  try {
    await jobApi.updateJob(row.id, { status: newStatus })
    ElMessage.success('操作成功')
    fetchJobs()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const handleDelete = (row) => {
  ElMessageBox.confirm('确定要删除该岗位吗?', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await jobApi.deleteJob(row.id)
      ElMessage.success('删除成功')
      fetchJobs()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  })
}

onMounted(() => {
  fetchJobs()
})
</script>

<style scoped lang="scss">
.job-list-page {
  min-height: 100%;
  background: transparent;
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

.glass-card {
  background: var(--gradient-card);
  backdrop-filter: blur(12px);
  border-radius: var(--radius-lg);
  box-shadow: var(--card-shadow);
  border: 1px solid var(--card-border);
  padding: 20px;
  margin-bottom: 20px;
  transition: var(--transition-base);
  
  &:hover {
    box-shadow: var(--card-shadow-hover);
    border-color: var(--card-border-glow);
  }
}

.search-form {
  :deep(.el-form-item) {
    margin-bottom: 0;
  }
  
  :deep(.el-form-item__label) {
    font-size: 14px;
    color: var(--text-secondary);
    font-weight: 500;
  }
}

.custom-input,
.custom-select {
  :deep(.el-input__wrapper),
  :deep(.el-select__wrapper) {
    background: rgba(255, 255, 255, 0.06);
    backdrop-filter: blur(8px);
    border-radius: var(--radius-md);
    box-shadow: none;
    border: 1px solid var(--card-border);
    transition: var(--transition-base);
    
    &:hover {
      border-color: var(--card-border-glow);
      background: rgba(82, 196, 26, 0.08);
    }
    
    &.is-focus {
      border-color: var(--primary-color);
      box-shadow: 0 0 0 2px var(--primary-glow);
      background: rgba(82, 196, 26, 0.1);
    }
    
    .el-input__inner,
    .el-select__input {
      color: var(--text-primary);
      font-size: 14px;
      
      &::placeholder {
        color: var(--text-tertiary);
      }
    }
  }
}

.search-btn,
.reset-btn {
  border-radius: var(--radius-md);
  padding: 10px 24px;
  font-size: 14px;
  font-weight: 600;
  transition: var(--transition-base);
  height: 40px;
}

.search-btn {
  background: var(--gradient-primary);
  border: none;
  box-shadow: 0 2px 8px var(--primary-glow);
  
  &:hover {
    box-shadow: 0 4px 12px var(--primary-glow);
    transform: translateY(-2px);
  }
}

.reset-btn {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid var(--card-border);
  color: var(--text-secondary);
  
  &:hover {
    background: rgba(82, 196, 26, 0.1);
    border-color: var(--card-border-glow);
    color: var(--text-primary);
  }
}

.glass-table {
  :deep(.el-table__header) {
    th {
      background: rgba(255, 255, 255, 0.04);
      color: var(--text-secondary);
      font-weight: 600;
      font-size: 14px;
      border: none;
      border-bottom: 1px solid var(--card-border);
    }
  }
  
  :deep(.el-table__body) {
    tr {
      transition: var(--transition-base);
      
      &:hover {
        background: rgba(255, 255, 255, 0.06) !important;
        
        td {
          border-bottom-color: var(--card-border-glow);
        }
      }
    }
    
    td {
      font-size: 14px;
      color: var(--text-secondary);
      border: none;
      border-bottom: 1px solid var(--card-border);
      padding: 14px 0;
    }
  }
  
  :deep(.el-table__inner-wrapper) {
    border-collapse: separate;
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

.action-btn-small {
  border-radius: var(--radius-md);
  padding: 8px 14px;
  font-size: 13px;
  font-weight: 600;
  transition: var(--transition-base);
  height: 32px;
  
  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  }
  
  &:active {
    transform: translateY(0) scale(0.98);
  }
}

.glass-pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
  padding: 16px 0;
  
  :deep(.el-pagination) {
    .btn-prev,
    .btn-next,
    .el-pager li {
      border-radius: var(--radius-md);
      min-width: 36px;
      height: 36px;
      line-height: 36px;
      font-size: 14px;
      background: rgba(255, 255, 255, 0.06);
      border: 1px solid var(--card-border);
      color: var(--text-secondary);
      transition: var(--transition-base);
      
      &:hover {
        background: rgba(82, 196, 26, 0.1);
        border-color: var(--card-border-glow);
        color: var(--text-primary);
      }
    }
    
    .el-pager li.is-active {
      background: var(--gradient-primary);
      border-color: transparent;
      color: #fff;
      box-shadow: 0 2px 8px var(--primary-glow);
    }
    
    .el-pagination__total,
    .el-pagination__sizes {
      color: var(--text-secondary);
    }
  }
}
</style>
