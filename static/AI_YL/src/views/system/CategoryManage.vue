<template>
  <div class="category-manage-page">
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">岗位类别管理</h1>
        <p class="page-subtitle">管理岗位类别及对应权重配置</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" size="large" @click="openAddDialog" :icon="Plus">
          新增类别
        </el-button>
      </div>
    </div>
    
    <div class="page-content">
      <div v-loading="loading" class="category-cards">
        <el-empty v-if="!loading && categoryList.length === 0" description="暂无岗位类别，请点击新增" />
        
        <div v-for="item in categoryList" :key="item.id" class="category-card glass-card">
          <div class="card-header">
            <div class="card-title-area">
              <el-tag :type="getTagType(item.code)" effect="dark" size="large">
                {{ item.name }}
              </el-tag>
            </div>
            <div class="card-actions">
              <el-button type="primary" size="small" @click="openEditDialog(item)" :icon="Edit">编辑</el-button>
              <el-button type="danger" size="small" @click="handleDelete(item)" :icon="Delete">删除</el-button>
            </div>
          </div>
          
          <div class="card-body">
            <div class="desc">{{ item.description || '暂无描述' }}</div>
            <div class="status-row">
              <span class="status-label">状态：</span>
              <el-switch 
                v-model="item.status" 
                :active-value="1" 
                :inactive-value="0"
                active-text="启用"
                inactive-text="禁用"
                @change="handleStatusChange(item)"
              />
              <span class="sort-label">排序：{{ item.sortOrder }}</span>
            </div>
            
            <div v-if="item.weight" class="weight-preview">
              <div class="weight-title">权重配置</div>
              <div class="weight-items">
                <span class="w-item">技能 {{ (item.weight.skillWeight * 100).toFixed(0) }}%</span>
                <span class="w-item">经验 {{ (item.weight.experienceWeight * 100).toFixed(0) }}%</span>
                <span class="w-item">学历 {{ (item.weight.educationWeight * 100).toFixed(0) }}%</span>
                <span class="w-item">项目 {{ (item.weight.projectWeight * 100).toFixed(0) }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑类别' : '新增类别'"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form 
        ref="formRef"
        :model="form" 
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="类别编码" prop="code" v-if="!isEdit">
          <el-input v-model="form.code" placeholder="请输入英文编码，如：technical" />
        </el-form-item>
        
        <el-form-item label="类别名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入类别名称" />
        </el-form-item>
        
        <el-form-item label="类别描述">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入描述" />
        </el-form-item>
        
        <el-form-item label="排序">
          <el-input-number v-model="form.sortOrder" :min="0" :max="999" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { categoryApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete } from '@element-plus/icons-vue'

const categoryList = ref([])
const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const formRef = ref(null)
const editId = ref(null)

const isEdit = computed(() => !!editId.value)

const form = reactive({
  code: '',
  name: '',
  description: '',
  sortOrder: 0
})

const rules = {
  code: [{ required: true, message: '请输入类别编码', trigger: 'blur' }],
  name: [{ required: true, message: '请输入类别名称', trigger: 'blur' }]
}

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

const fetchCategories = async () => {
  loading.value = true
  try {
    const res = await categoryApi.getCategoryList()
    categoryList.value = res.data
  } catch (error) {
    ElMessage.error('获取类别列表失败')
  } finally {
    loading.value = false
  }
}

const openAddDialog = () => {
  editId.value = null
  form.code = ''
  form.name = ''
  form.description = ''
  form.sortOrder = 0
  dialogVisible.value = true
}

const openEditDialog = (item) => {
  editId.value = item.id
  form.code = item.code
  form.name = item.name
  form.description = item.description || ''
  form.sortOrder = item.sortOrder
  dialogVisible.value = true
}

const handleSave = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  
  saving.value = true
  try {
    if (isEdit.value) {
      await categoryApi.updateCategory(editId.value, {
        name: form.name,
        description: form.description,
        sortOrder: form.sortOrder
      })
      ElMessage.success('更新成功')
    } else {
      await categoryApi.addCategory({
        code: form.code,
        name: form.name,
        description: form.description,
        sortOrder: form.sortOrder
      })
      ElMessage.success('新增成功')
    }
    dialogVisible.value = false
    fetchCategories()
  } catch (error) {
    ElMessage.error(isEdit.value ? '更新失败' : '新增失败')
  } finally {
    saving.value = false
  }
}

const handleStatusChange = async (item) => {
  try {
    await categoryApi.updateCategory(item.id, { status: item.status })
    ElMessage.success('状态更新成功')
  } catch (error) {
    item.status = item.status === 1 ? 0 : 1
    ElMessage.error('状态更新失败')
  }
}

const handleDelete = async (item) => {
  try {
    await ElMessageBox.confirm(`确定要删除类别"${item.name}"吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await categoryApi.deleteCategory(item.id)
    ElMessage.success('删除成功')
    fetchCategories()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

onMounted(() => {
  fetchCategories()
})
</script>

<style scoped lang="scss">
.category-manage-page {
  min-height: 100%;
  position: relative;
}

.page-header {
  position: relative;
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
  padding: 32px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.header-actions {
  position: relative;
  z-index: 1;
}

.page-content {
  padding: 24px;
  position: relative;
  z-index: 1;
}

.category-cards {
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
  margin-bottom: 16px;
}

.card-title-area {
  display: flex;
  align-items: center;
  gap: 12px;
}

.category-code {
  font-size: 12px;
  color: var(--text-tertiary);
  font-family: monospace;
}

.card-actions {
  display: flex;
  gap: 8px;
}

.card-body {
  .desc {
    font-size: 14px;
    color: var(--text-secondary);
    margin-bottom: 12px;
  }
}

.status-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  
  .status-label {
    font-size: 14px;
    color: var(--text-secondary);
  }
  
  .sort-label {
    font-size: 12px;
    color: var(--text-tertiary);
  }
}

.weight-preview {
  padding: 12px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: var(--radius-md);
  border: 1px dashed var(--glass-border);
  
  .weight-title {
    font-size: 12px;
    color: var(--text-tertiary);
    margin-bottom: 8px;
  }
  
  .weight-items {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }
  
  .w-item {
    font-size: 12px;
    padding: 4px 8px;
    background: rgba(255, 255, 255, 0.05);
    border-radius: var(--radius-sm);
    color: var(--text-secondary);
  }
}
</style>
