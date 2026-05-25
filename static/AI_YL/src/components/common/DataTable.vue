<template>
  <div class="data-table">
    <!-- 工具栏 -->
    <div v-if="$slots.toolbar" class="table-toolbar">
      <slot name="toolbar"></slot>
    </div>

    <!-- 表格主体 -->
    <div class="table-wrapper">
      <!-- 加载骨架屏 -->
      <div v-if="loading" class="skeleton-wrapper">
        <div v-for="i in skeletonRows" :key="i" class="skeleton-row">
          <div v-for="col in columns" :key="col.prop" class="skeleton-cell" :style="{ width: col.width || 'auto' }">
            <div class="skeleton-line"></div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else-if="!data || data.length === 0" class="empty-state">
        <el-icon :size="64" color="#BFBFBF"><Document /></el-icon>
        <p class="empty-title">{{ emptyText }}</p>
        <p v-if="emptyDescription" class="empty-description">{{ emptyDescription }}</p>
        <div v-if="$slots.emptyAction" class="empty-action">
          <slot name="emptyAction"></slot>
        </div>
      </div>

      <!-- 数据表格 -->
      <el-table
        v-else
        v-bind="$attrs"
        :data="data"
        :border="false"
        stripe
        class="styled-table"
      >
        <slot></slot>
      </el-table>
    </div>

    <!-- 分页 -->
    <div v-if="showPagination && total > 0" class="table-pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="pageSizes"
        :background="true"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { Document } from '@element-plus/icons-vue'

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  columns: {
    type: Array,
    default: () => []
  },
  total: {
    type: Number,
    default: 0
  },
  page: {
    type: Number,
    default: 1
  },
  pageSize: {
    type: Number,
    default: 10
  },
  pageSizes: {
    type: Array,
    default: () => [10, 20, 50, 100]
  },
  showPagination: {
    type: Boolean,
    default: true
  },
  emptyText: {
    type: String,
    default: '暂无数据'
  },
  emptyDescription: {
    type: String,
    default: ''
  },
  skeletonRows: {
    type: Number,
    default: 5
  }
})

const emit = defineEmits(['update:page', 'update:pageSize', 'page-change'])

const currentPage = ref(props.page)
const pageSize = ref(props.pageSize)

watch(() => props.page, (val) => {
  currentPage.value = val
})

watch(() => props.pageSize, (val) => {
  pageSize.value = val
})

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  emit('update:pageSize', size)
  emit('page-change', { page: 1, pageSize: size })
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  emit('update:page', page)
  emit('page-change', { page, pageSize: pageSize.value })
}
</script>

<style scoped lang="scss">
.data-table {
  background: var(--gradient-card);
  backdrop-filter: var(--card-blur);
  border: 1px solid var(--card-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  position: relative;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(82,196,26,0.2), transparent);
  }
}

.table-toolbar {
  padding: 16px;
  border-bottom: 1px solid var(--card-border);
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.table-wrapper {
  position: relative;
  min-height: 200px;
}

// 骨架屏样式
.skeleton-wrapper {
  padding: 16px;
}

.skeleton-row {
  display: flex;
  gap: 16px;
  padding: 12px 0;
  border-bottom: 1px solid var(--card-border);
  
  &:last-child {
    border-bottom: none;
  }
}

.skeleton-cell {
  flex: 1;
}

.skeleton-line {
  height: 14px;
  background: linear-gradient(90deg, rgba(0,0,0,0.04) 25%, rgba(0,0,0,0.08) 50%, rgba(0,0,0,0.04) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: var(--radius-sm);
}

@keyframes shimmer {
  0% { background-position: -200% center; }
  100% { background-position: 200% center; }
}

// 空状态样式
.empty-state {
  padding: 48px 24px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 280px;
}

.empty-title {
  font-size: 16px;
  color: var(--text-secondary);
  margin-top: 16px;
  font-weight: 500;
}

.empty-description {
  font-size: 13px;
  color: var(--text-tertiary);
  margin-top: 8px;
}

.empty-action {
  margin-top: 20px;
}

// 分页样式
.table-pagination {
  padding: 16px;
  border-top: 1px solid var(--card-border);
  display: flex;
  justify-content: flex-end;
  background: rgba(0, 0, 0, 0.01);
}

:deep(.styled-table) {
  background: transparent !important;
  --el-table-bg-color: transparent;
  --el-table-tr-bg-color: transparent;
  --el-table-header-bg-color: rgba(0, 0, 0, 0.02);
  --el-table-row-hover-bg-color: rgba(82, 196, 26, 0.05);
  --el-table-border-color: var(--card-border);
  --el-table-text-color: var(--text-secondary);
  --el-table-header-text-color: var(--text-primary);
  
  &::before {
    display: none;
  }
}

:deep(.el-table th.el-table__cell) {
  background: rgba(0, 0, 0, 0.02) !important;
  color: var(--text-primary) !important;
  font-weight: 600;
  font-size: 13px;
  padding: 12px 0;
}

:deep(.el-table td.el-table__cell) {
  color: var(--text-secondary) !important;
  padding: 14px 0;
}

:deep(.el-table__row) {
  transition: var(--transition-base);
}

:deep(.el-pagination) {
  --el-pagination-bg-color: transparent;
  --el-pagination-text-color: var(--text-secondary);
  --el-pagination-button-bg-color: var(--card-bg);
  --el-pagination-hover-color: var(--primary-color);
  
  .btn-prev,
  .btn-next,
  .el-pager li {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    color: var(--text-secondary);
    border-radius: var(--radius-md);
    transition: var(--transition-base);
    
    &:hover {
      border-color: var(--primary-color);
      color: var(--primary-color);
    }
  }
  
  .el-pager li.is-active {
    background: var(--gradient-primary);
    border-color: transparent;
    color: #fff;
  }
}
</style>
