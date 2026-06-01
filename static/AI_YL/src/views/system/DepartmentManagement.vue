<template>
  <div class="department-management-page">
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">部门管理</h1>
        <p class="page-subtitle">管理公司部门信息</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" size="large" class="add-btn" @click="openAddDialog">
          <el-icon><Plus /></el-icon>
          <span>添加部门</span>
        </el-button>
      </div>
    </div>
    
    <div class="page-content">
      <div class="table-card glass-card">
        <el-table :data="departmentList" v-loading="loading" class="glass-table">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="name" label="部门名称" />
          <el-table-column prop="description" label="部门描述" />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.status === 1 ? 'success' : 'info'" size="small">
                {{ row.status === 1 ? '启用' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="180" fixed="right">
            <template #default="{ row }">
              <el-button size="small" type="primary" @click="openEditDialog(row)">编辑</el-button>
              <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
    
    <!-- 添加/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑部门' : '添加部门'"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form 
        ref="formRef"
        :model="form" 
        :rules="rules"
        label-width="80px"
        class="edit-form"
      >
        <el-form-item label="部门名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入部门名称" />
        </el-form-item>
        
        <el-form-item label="部门描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入部门描述" />
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
import { ref, reactive, onMounted } from 'vue'
import { departmentApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

const departmentList = ref([])
const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)

const form = reactive({
  id: null,
  name: '',
  description: ''
})

const rules = {
  name: [{ required: true, message: '请输入部门名称', trigger: 'blur' }]
}

const fetchDepartments = async () => {
  loading.value = true
  try {
    const res = await departmentApi.getDepartmentList()
    departmentList.value = res.data
  } catch (error) {
    ElMessage.error('获取部门列表失败')
  } finally {
    loading.value = false
  }
}

const openAddDialog = () => {
  isEdit.value = false
  form.id = null
  form.name = ''
  form.description = ''
  dialogVisible.value = true
}

const openEditDialog = (row) => {
  isEdit.value = true
  form.id = row.id
  form.name = row.name
  form.description = row.description || ''
  dialogVisible.value = true
}

const handleSave = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  
  saving.value = true
  try {
    if (isEdit.value) {
      await departmentApi.updateDepartment(form.id, {
        name: form.name,
        description: form.description
      })
      ElMessage.success('更新成功')
    } else {
      await departmentApi.addDepartment({
        name: form.name,
        description: form.description
      })
      ElMessage.success('添加成功')
    }
    dialogVisible.value = false
    fetchDepartments()
  } catch (error) {
    ElMessage.error(isEdit.value ? '更新失败' : '添加失败')
  } finally {
    saving.value = false
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除部门 ${row.name} 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await departmentApi.deleteDepartment(row.id)
    ElMessage.success('删除成功')
    fetchDepartments()
  } catch {
    // 取消操作
  }
}

onMounted(() => {
  fetchDepartments()
})
</script>

<style scoped lang="scss">
.department-management-page {
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
  
  .add-btn {
    height: 44px;
    padding: 0 24px;
    font-size: 15px;
    font-weight: 600;
    border-radius: var(--radius-md);
    background: rgba(255, 255, 255, 0.95);
    color: var(--primary-color);
    border: none;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    transition: var(--transition-base);
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 16px rgba(0, 0, 0, 0.03);
      background: #fff;
    }
  }
}

.page-content {
  padding: 24px;
  position: relative;
  z-index: 1;
}

.glass-card {
  background: var(--glass-bg);
  backdrop-filter: blur(12px);
  border-radius: var(--radius-lg);
  border: 1px solid var(--glass-border);
  box-shadow: var(--glass-shadow);
  padding: 24px;
}

.edit-form {
  padding: 0 12px;
}
</style>
