<template>
  <div class="breadcrumb-nav">
    <el-breadcrumb separator="/">
      <el-breadcrumb-item 
        v-for="(item, index) in breadcrumbs" 
        :key="index"
        :to="item.path ? { path: item.path } : undefined"
      >
        <el-icon v-if="item.icon" :size="14" class="breadcrumb-icon">
          <component :is="item.icon" />
        </el-icon>
        {{ item.title }}
      </el-breadcrumb-item>
    </el-breadcrumb>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { HomeFilled, Briefcase, Document, Connection, DataAnalysis, Setting, User, Cpu } from '@element-plus/icons-vue'

const route = useRoute()

const iconMap = {
  '首页': 'HomeFilled',
  '岗位管理': 'Briefcase',
  '简历管理': 'Document',
  '人岗匹配': 'Connection',
  '统计报表': 'DataAnalysis',
  '系统管理': 'Setting',
  '个人中心': 'User',
  'AI智能中心': 'Cpu'
}

const breadcrumbs = computed(() => {
  const matched = route.matched
  const crumbs = []
  
  matched.forEach((item) => {
    if (item.meta && item.meta.title) {
      crumbs.push({
        title: item.meta.title,
        path: item.path !== route.path ? item.path : undefined,
        icon: iconMap[item.meta.title] || null
      })
    }
  })
  
  return crumbs
})
</script>

<style scoped lang="scss">
.breadcrumb-nav {
  padding: 12px 20px;
  background: var(--card-bg);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--card-border);
  position: relative;
  
  &::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(139,92,246,0.15), transparent);
  }
}

:deep(.el-breadcrumb) {
  font-size: 14px;
  
  .el-breadcrumb__item {
    .el-breadcrumb__inner {
      color: var(--text-secondary);
      font-weight: 400;
      transition: var(--transition-base);
      display: flex;
      align-items: center;
      gap: 4px;
      
      &:hover {
        color: var(--primary-color);
      }
      
      &.is-link {
        &:hover {
          color: var(--primary-color);
        }
      }
    }
    
    &:last-child .el-breadcrumb__inner {
      color: var(--text-primary);
      font-weight: 600;
    }
    
    .el-breadcrumb__separator {
      color: var(--text-tertiary);
      font-weight: 300;
    }
  }
}

.breadcrumb-icon {
  color: var(--text-tertiary);
  flex-shrink: 0;
}
</style>
