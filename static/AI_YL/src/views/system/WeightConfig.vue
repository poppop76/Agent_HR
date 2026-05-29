<template>
  <div class="weight-config-page">
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">匹配权重配置</h1>
        <p class="page-subtitle">按岗位类别配置人岗匹配权重参数</p>
      </div>
    </div>
    
    <div class="page-content">
      <div v-loading="loading" class="weight-cards">
        <el-empty v-if="!loading && weightList.length === 0" description="暂无权重配置，请先添加岗位类别" />
        
        <div v-for="item in weightList" :key="item.id" class="weight-card glass-card">
          <div class="card-header">
            <div class="card-title-area">
              <el-tag :type="getTagType(item.code)" effect="dark" size="large">
                {{ item.name }}
              </el-tag>
              <span class="job-type-desc">{{ item.description || '' }}</span>
            </div>
            <el-button 
              type="primary" 
              size="small" 
              @click="openEditDialog(item)"
              :icon="Edit"
            >编辑</el-button>
          </div>
          
          <div v-if="item.weight" class="weight-bars">
            <div class="weight-bar-item" v-for="bar in getWeightBars(item.weight)" :key="bar.label">
              <div class="bar-header">
                <span class="bar-label">{{ bar.label }}</span>
                <span class="bar-value">{{ (bar.value * 100).toFixed(0) }}%</span>
              </div>
              <el-progress 
                :percentage="Math.round(bar.value * 100)" 
                :color="bar.color"
                :stroke-width="12"
                :show-text="false"
              />
            </div>
          </div>
          <div v-else class="no-weight">暂无权重配置</div>
          
          <div v-if="item.weight" class="weight-total">
            权重合计：{{ getTotal(item.weight) }}%
          </div>
        </div>
      </div>
    </div>
    
    <!-- 编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="编辑权重配置"
      width="550px"
      :close-on-click-modal="false"
    >
      <el-form 
        v-if="editingItem" 
        :model="editingItem" 
        label-width="100px"
        class="edit-form"
      >
        <el-form-item label="岗位类别">
          <el-tag :type="getTagType(editingItem.code)" effect="dark" size="large">
            {{ editingItem.name }}
          </el-tag>
        </el-form-item>
        
        <el-divider content-position="left">权重配置（合计必须为100%）</el-divider>
        
        <el-form-item label="技能权重">
          <el-slider 
            v-model="editingItem.skillWeight" 
            :min="0" 
            :max="1" 
            :step="0.05"
            :format-tooltip="v => (v * 100).toFixed(0) + '%'"
          />
        </el-form-item>
        
        <el-form-item label="经验权重">
          <el-slider 
            v-model="editingItem.experienceWeight" 
            :min="0" 
            :max="1" 
            :step="0.05"
            :format-tooltip="v => (v * 100).toFixed(0) + '%'"
          />
        </el-form-item>
        
        <el-form-item label="学历权重">
          <el-slider 
            v-model="editingItem.educationWeight" 
            :min="0" 
            :max="1" 
            :step="0.05"
            :format-tooltip="v => (v * 100).toFixed(0) + '%'"
          />
        </el-form-item>
        
        <el-form-item label="项目权重">
          <el-slider 
            v-model="editingItem.projectWeight" 
            :min="0" 
            :max="1" 
            :step="0.05"
            :format-tooltip="v => (v * 100).toFixed(0) + '%'"
          />
        </el-form-item>
        
        <el-form-item label="权重合计">
          <span :class="totalClass">{{ getTotal(editingItem) }}%</span>
          <span v-if="getTotal(editingItem) !== 100" class="total-warning">
            （权重之和必须等于100%）
          </span>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button 
          type="primary" 
          @click="handleSave"
          :disabled="getTotal(editingItem) !== 100"
          :loading="saving"
        >保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { categoryApi } from '@/api'
import { ElMessage } from 'element-plus'
import { Edit } from '@element-plus/icons-vue'

const weightList = ref([])
const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const editingItem = ref(null)

const totalClass = computed(() => {
  if (!editingItem.value) return ''
  const total = getTotal(editingItem.value)
  if (total === 100) return 'total-ok'
  return 'total-error'
})

const getTagType = (code) => {
  const map = {
    technical: 'success',
    product: 'primary',
    marketing: 'warning',
    hr: 'info',
    finance: 'danger',
    admin: ''
  }
  return map[code] || ''
}

const getWeightBars = (weight) => {
  return [
    { label: '技能权重', value: weight.skillWeight, color: '#52C41A' },
    { label: '经验权重', value: weight.experienceWeight, color: '#1890FF' },
    { label: '学历权重', value: weight.educationWeight, color: '#FA8C16' },
    { label: '项目权重', value: weight.projectWeight, color: '#FF4D4F' }
  ]
}

const getTotal = (item) => {
  if (!item) return 0
  return Math.round(
    (item.skillWeight + item.experienceWeight + item.educationWeight + item.projectWeight) * 100
  )
}

const fetchWeights = async () => {
  loading.value = true
  try {
    const res = await categoryApi.getCategoryList()
    weightList.value = res.data
  } catch (error) {
    ElMessage.error('获取权重配置失败')
  } finally {
    loading.value = false
  }
}

const openEditDialog = (item) => {
  if (!item.weight) {
    ElMessage.warning('该类别暂无权重配置')
    return
  }
  editingItem.value = {
    id: item.id,
    code: item.code,
    name: item.name,
    skillWeight: item.weight.skillWeight,
    experienceWeight: item.weight.experienceWeight,
    educationWeight: item.weight.educationWeight,
    projectWeight: item.weight.projectWeight
  }
  dialogVisible.value = true
}

const handleSave = async () => {
  if (getTotal(editingItem.value) !== 100) {
    ElMessage.warning('权重之和必须等于100%')
    return
  }
  
  saving.value = true
  try {
    await categoryApi.updateCategoryWeight(editingItem.value.id, {
      skillWeight: editingItem.value.skillWeight,
      experienceWeight: editingItem.value.experienceWeight,
      educationWeight: editingItem.value.educationWeight,
      projectWeight: editingItem.value.projectWeight
    })
    ElMessage.success('保存成功')
    dialogVisible.value = false
    fetchWeights()
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  fetchWeights()
})
</script>

<style scoped lang="scss">
.weight-config-page {
  min-height: 100%;
  position: relative;
}

.page-header {
  position: relative;
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
  padding: 32px 24px;
  overflow: hidden;
}

.header-content {
  position: relative;
  z-index: 1;
  
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
  position: relative;
  z-index: 1;
}

.weight-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
}

.glass-card {
  background: var(--glass-bg);
  backdrop-filter: blur(12px);
  border-radius: var(--radius-lg);
  border: 1px solid var(--glass-border);
  box-shadow: var(--glass-shadow);
  transition: var(--transition-base);
  padding: 24px;
  
  &:hover {
    border-color: rgba(99, 102, 241, 0.2);
    box-shadow: 0 8px 32px rgba(99, 102, 241, 0.1);
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.card-title-area {
  display: flex;
  align-items: center;
  gap: 12px;
}

.job-type-desc {
  font-size: 14px;
  color: var(--text-secondary);
}

.weight-bars {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.weight-bar-item {
  .bar-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 8px;
  }
  
  .bar-label {
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary);
  }
  
  .bar-value {
    font-size: 14px;
    font-weight: 700;
    color: var(--primary-color);
  }
}

.no-weight {
  text-align: center;
  padding: 20px;
  color: var(--text-tertiary);
  font-size: 14px;
}

.weight-total {
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px dashed var(--glass-border);
  text-align: right;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
}

.edit-form {
  padding: 0 12px;
}

.total-ok {
  font-size: 18px;
  font-weight: 700;
  color: #52C41A;
}

.total-error {
  font-size: 18px;
  font-weight: 700;
  color: #FF4D4F;
}

.total-warning {
  font-size: 12px;
  color: #FF4D4F;
  margin-left: 8px;
}
</style>
