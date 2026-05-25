<template>
  <div class="job-form-page">
    <ParticlesBackground />
    
    <div class="page-header">
      <div class="header-particles"></div>
      <div class="header-content">
        <h1 class="page-title">{{ isEdit ? '编辑岗位' : '新增岗位' }}</h1>
        <p class="page-subtitle">{{ isEdit ? '修改岗位信息，更新招聘需求' : '创建新的招聘岗位，开始招聘流程' }}</p>
      </div>
      <div class="header-actions">
        <el-button size="large" class="back-btn" @click="router.back()">
          <el-icon><ArrowLeft /></el-icon>
          <span>返回列表</span>
        </el-button>
      </div>
    </div>
    
    <div class="page-content">
      <div class="form-card glass-card">
        <div class="card-header">
          <h3 class="card-title">岗位信息</h3>
          <div class="card-badge">{{ isEdit ? '编辑' : '新增' }}</div>
        </div>
        
        <el-form 
          ref="formRef"
          :model="form"
          :rules="rules"
          label-width="120px"
          class="job-form"
        >
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="岗位类别" prop="jobType">
                <el-select v-model="form.jobType" placeholder="请选择岗位类别" class="custom-select">
                  <el-option label="技术类" value="technical" />
                  <el-option label="管理类" value="management" />
                  <el-option label="运营类" value="operation" />
                  <el-option label="行政类" value="administrative" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="所属部门" prop="department">
                <el-select v-model="form.department" placeholder="请选择部门" class="custom-select">
                  <el-option v-for="dept in departments" :key="dept" :label="dept" :value="dept" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="岗位名称" prop="name">
                <el-input v-model="form.name" placeholder="请输入岗位名称" class="custom-input" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="薪资范围" prop="salary">
                <el-input v-model="form.salary" placeholder="如：10k-20k" class="custom-input" />
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-form-item label="工作地点" prop="location">
            <el-input v-model="form.location" placeholder="请输入工作地点" class="custom-input" />
          </el-form-item>
          
          <el-form-item label="岗位职责" prop="responsibilities">
            <el-input 
              v-model="form.responsibilities" 
              type="textarea" 
              :rows="6" 
              placeholder="请输入岗位职责"
              class="custom-textarea"
            />
          </el-form-item>
          
          <el-form-item label="任职要求" prop="requirements">
            <el-input 
              v-model="form.requirements" 
              type="textarea" 
              :rows="6" 
              placeholder="请输入任职要求"
              class="custom-textarea"
            />
          </el-form-item>
          
          <el-form-item class="form-actions">
            <el-button type="primary" size="large" :loading="loading" class="submit-btn" @click="handleSubmit">
              <el-icon v-if="!loading"><Check /></el-icon>
              <span v-if="!loading">{{ isEdit ? '保存修改' : '提交岗位' }}</span>
              <span v-else>提交中...</span>
            </el-button>
            <el-button size="large" class="cancel-btn" @click="router.back()">取消</el-button>
          </el-form-item>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { jobApi } from '@/api'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Check } from '@element-plus/icons-vue'
import ParticlesBackground from '@/components/ParticlesBackground.vue'

const router = useRouter()
const route = useRoute()

const formRef = ref(null)
const loading = ref(false)
const departments = ref([])

const isEdit = computed(() => !!route.params.id)

const form = reactive({
  name: '',
  jobType: '',
  department: '',
  salary: '',
  location: '',
  responsibilities: '',
  requirements: ''
})

const rules = {
  name: [{ required: true, message: '请输入岗位名称', trigger: 'blur' }],
  jobType: [{ required: true, message: '请选择岗位类别', trigger: 'change' }],
  department: [{ required: true, message: '请选择部门', trigger: 'change' }],
  salary: [{ required: true, message: '请输入薪资范围', trigger: 'blur' }],
  location: [{ required: true, message: '请输入工作地点', trigger: 'blur' }],
  responsibilities: [{ required: true, message: '请输入岗位职责', trigger: 'blur' }],
  requirements: [{ required: true, message: '请输入任职要求', trigger: 'blur' }]
}

const fetchJobDetail = async () => {
  try {
    const res = await jobApi.getJobList({ page: 1, pageSize: 100 })
    const jobData = res.data.list.find(j => j.id === Number(route.params.id))
    if (jobData) {
      Object.assign(form, jobData)
    } else {
      ElMessage.error('岗位不存在')
    }
  } catch (error) {
    ElMessage.error('获取岗位详情失败')
  }
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  
  loading.value = true
  try {
    if (isEdit.value) {
      await jobApi.updateJob(route.params.id, form)
      ElMessage.success('更新成功')
    } else {
      await jobApi.addJob(form)
      ElMessage.success('新增成功')
    }
    router.push('/jobs')
  } catch (error) {
    ElMessage.error(isEdit.value ? '更新失败' : '新增失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  if (isEdit.value) {
    fetchJobDetail()
  }
})
</script>

<style scoped lang="scss">
.job-form-page {
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
  margin-bottom: 24px;
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
}

.job-form {
  :deep(.el-form-item__label) {
    font-size: 14px;
    color: var(--text-secondary);
    font-weight: 500;
  }
}

.custom-input {
  :deep(.el-input__wrapper) {
    border-radius: var(--radius-md);
    box-shadow: none;
    border: 1px solid var(--card-border);
    transition: var(--transition-base);
    background: rgba(255, 255, 255, 0.04);
    
    &:hover {
      border-color: var(--primary-light);
    }
    
    &.is-focus {
      border-color: var(--primary-color);
      box-shadow: 0 0 0 2px var(--primary-glow);
    }
    
    .el-input__inner {
      color: var(--text-primary);
      font-size: 14px;
      
      &::placeholder {
        color: var(--text-tertiary);
      }
    }
  }
}

.custom-select {
  width: 100%;
  
  :deep(.el-select__wrapper) {
    border-radius: var(--radius-md);
    box-shadow: none;
    border: 1px solid var(--card-border);
    transition: var(--transition-base);
    background: rgba(255, 255, 255, 0.04);
    
    &:hover {
      border-color: var(--primary-light);
    }
    
    &.is-focus {
      border-color: var(--primary-color);
      box-shadow: 0 0 0 2px var(--primary-glow);
    }
    
    .el-select__selected-item {
      color: var(--text-primary);
    }
    
    .el-select__placeholder {
      color: var(--text-tertiary);
    }
  }
}

.custom-textarea {
  :deep(.el-textarea__inner) {
    border-radius: var(--radius-md);
    box-shadow: none;
    border: 1px solid var(--card-border);
    transition: var(--transition-base);
    background: rgba(255, 255, 255, 0.04);
    color: var(--text-primary);
    font-size: 14px;
    line-height: 1.6;
    
    &:hover {
      border-color: var(--primary-light);
    }
    
    &.is-focus {
      border-color: var(--primary-color);
      box-shadow: 0 0 0 2px var(--primary-glow);
    }
    
    &::placeholder {
      color: var(--text-tertiary);
    }
  }
}

.form-actions {
  margin-top: 32px;
  margin-bottom: 0;
  display: flex;
  gap: 12px;
  
  .submit-btn {
    height: 44px;
    padding: 0 32px;
    font-size: 14px;
    font-weight: 600;
    border-radius: var(--radius-md);
    background: var(--gradient-primary);
    border: none;
    box-shadow: 0 4px 12px var(--primary-glow);
    transition: var(--transition-base);
    display: flex;
    align-items: center;
    gap: 8px;
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 16px var(--primary-glow);
    }
    
    &:active {
      transform: translateY(0) scale(0.98);
    }
  }
  
  .cancel-btn {
    height: 44px;
    padding: 0 32px;
    font-size: 14px;
    font-weight: 600;
    border-radius: var(--radius-md);
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid var(--card-border);
    color: var(--text-secondary);
    transition: var(--transition-base);
    
    &:hover {
      background: rgba(82, 196, 26, 0.1);
      border-color: var(--card-border-glow);
      color: var(--text-primary);
    }
    
    &:active {
      transform: translateY(0) scale(0.98);
    }
  }
}

.weight-info-card {
  margin-top: 20px;
  border-radius: var(--radius-md);
  background: rgba(255, 255, 255, 0.03);
  border: 1px dashed var(--card-border);
  
  :deep(.el-card__header) {
    padding: 12px 20px;
    border-bottom: 1px dashed var(--card-border);
  }
  
  :deep(.el-card__body) {
    padding: 16px 20px;
  }
}

.weight-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  
  .weight-title {
    margin: 0;
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary);
  }
}

.weight-info-content {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.weight-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: var(--radius-sm);
  
  .weight-label {
    font-size: 12px;
    color: var(--text-tertiary);
    margin-bottom: 4px;
  }
  
  .weight-value {
    font-size: 18px;
    font-weight: 700;
    color: var(--primary-color);
  }
}
</style>
