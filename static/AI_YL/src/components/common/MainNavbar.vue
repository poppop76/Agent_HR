<template>
  <div class="main-navbar">
    <div class="navbar-glow"></div>
    <div class="navbar-content">
      <div class="navbar-left">
        <div class="icon-btn mobile-menu-btn" @click="$emit('menu-toggle')">
          <el-icon :size="20"><Fold /></el-icon>
        </div>
        <h2 class="page-title">{{ currentTitle }}</h2>
      </div>
      
      <div class="navbar-center">
        <div class="search-wrapper">
          <el-icon class="search-icon"><Search /></el-icon>
          <el-input
            v-model="searchQuery"
            placeholder="全局搜索..."
            class="global-search"
            clearable
          />
        </div>
      </div>
      
      <div class="navbar-right">
        <el-badge :value="3" :max="99" class="notification-badge">
          <div class="icon-btn" @click="showNotifications">
            <el-icon :size="20"><Bell /></el-icon>
          </div>
        </el-badge>
        
        <el-dropdown @command="handleUserCommand" trigger="click">
          <div class="user-info">
            <el-avatar :size="36" :icon="UserFilled" class="user-avatar" />
            <div class="user-details">
              <span class="user-name">{{ authStore.userName || 'HR用户' }}</span>
              <span class="user-role">{{ authStore.userRole === 'admin' ? '管理员' : 'HR' }}</span>
            </div>
            <el-icon :size="12" class="dropdown-icon"><ArrowDown /></el-icon>
          </div>
          <template #dropdown>
            <el-dropdown-menu class="user-dropdown">
              <el-dropdown-item command="logout">
                <el-icon :size="16"><SwitchButton /></el-icon>退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { 
  UserFilled, ArrowDown, User, Setting, SwitchButton, Bell, Search, Fold
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

defineEmits(['menu-toggle'])

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const searchQuery = ref('')

const currentTitle = computed(() => {
  const pathMap = {
    '/dashboard': '首页概览',
    '/jobs': '岗位管理',
    '/resumes': '简历管理',
    '/matching': '人岗匹配',
    '/ai-center': 'AI智能中心'
  }
  
  for (const [path, title] of Object.entries(pathMap)) {
    if (route.path.startsWith(path)) {
      return title
    }
  }
  
  return 'HR智能系统'
})

const showNotifications = () => {
  ElMessage.info('暂无新通知')
}

const handleUserCommand = (command) => {
  if (command === 'logout') {
    authStore.logout()
    router.push('/login')
  }
}
</script>

<style scoped lang="scss">
.main-navbar {
  height: 64px;
  background: var(--card-bg);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-bottom: 1px solid var(--card-border);
  box-shadow: 0 2px 16px rgba(0, 0, 0, 0.16);
  position: relative;
  z-index: 100;
  overflow: hidden;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(139,92,246,0.2), transparent);
  }
}

.navbar-glow {
  position: absolute;
  top: -50%;
  left: -10%;
  width: 120%;
  height: 200%;
  background: radial-gradient(ellipse at center, var(--primary-glow) 0%, transparent 70%);
  opacity: 0.15;
  pointer-events: none;
  animation: navbarGlow 6s ease-in-out infinite;
}

@keyframes navbarGlow {
  0%, 100% { opacity: 0.1; transform: scale(1); }
  50% { opacity: 0.2; transform: scale(1.05); }
}

.navbar-content {
  height: 100%;
  display: flex;
  align-items: center;
  padding: 0 24px;
  max-width: 100%;
  position: relative;
  z-index: 1;
}

.navbar-left {
  min-width: 200px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.mobile-menu-btn {
  display: none;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.navbar-center {
  flex: 1;
  display: flex;
  justify-content: center;
  padding: 0 24px;
}

.search-wrapper {
  position: relative;
  width: 100%;
  max-width: 400px;
  
  .search-icon {
    position: absolute;
    left: 12px;
    top: 50%;
    transform: translateY(-50%);
    color: var(--text-tertiary);
    z-index: 1;
    pointer-events: none;
  }
  
  :deep(.global-search) {
    .el-input__wrapper {
      background: rgba(30, 41, 59, 0.6);
      backdrop-filter: blur(8px);
      box-shadow: none;
      border: 1px solid var(--card-border);
      border-radius: var(--radius-lg);
      padding-left: 36px;
      transition: var(--transition-base);
      
      &:hover {
        background: rgba(51, 65, 85, 0.6);
        border-color: var(--card-border-glow);
      }
      
      &.is-focus {
        background: rgba(51, 65, 85, 0.8);
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
}

.navbar-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.notification-badge {
  :deep(.el-badge__content) {
    background: var(--accent-color);
    border: none;
  }
}

.icon-btn {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  cursor: pointer;
  transition: var(--transition-base);
  
  &:hover {
    background: rgba(255, 255, 255, 0.08);
    color: var(--text-primary);
  }
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: var(--radius-lg);
  transition: var(--transition-base);
  
  &:hover {
    background: rgba(255, 255, 255, 0.08);
  }
}

.user-avatar {
  background: var(--gradient-primary);
  color: #fff;
  box-shadow: 0 2px 8px var(--primary-glow);
}

.user-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.user-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.user-role {
  font-size: 12px;
  color: var(--text-tertiary);
}

.dropdown-icon {
  color: var(--text-tertiary);
  transition: var(--transition-base);
}

.user-dropdown {
  background: var(--bg-color);
  border: 1px solid var(--card-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--card-shadow-hover);
  
  :deep(.el-dropdown-menu__item) {
    padding: 10px 16px;
    font-size: 14px;
    color: var(--text-secondary);
    transition: var(--transition-base);
    
    &:hover {
      background: rgba(255, 255, 255, 0.08);
      color: var(--text-primary);
    }
    
    .el-icon {
      margin-right: 8px;
    }
  }
}

// 移动端适配
@media (max-width: 768px) {
  .mobile-menu-btn {
    display: flex;
  }
  
  .navbar-center {
    display: none;
  }
  
  .navbar-left {
    min-width: auto;
  }
  
  .user-details {
    display: none;
  }
  
  .navbar-content {
    padding: 0 12px;
  }
}
</style>
