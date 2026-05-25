<template>
  <div :class="['sidebar', { collapsed: isCollapsed }]">
    <div class="sidebar-bg"></div>
    <div class="sidebar-flow"></div>
    <canvas ref="canvasRef" class="sidebar-particles"></canvas>
    
    <div class="sidebar-content">
      <div class="sidebar-header" @click="toggleCollapse">
        <div class="logo-wrapper">
          <div class="logo-icon">
            <el-icon :size="24"><Briefcase /></el-icon>
          </div>
          <transition name="fade">
            <h1 v-show="!isCollapsed" class="logo-text">HR智能系统</h1>
          </transition>
        </div>
      </div>

      <div class="sidebar-menu">
        <div
          v-for="item in menuItems"
          :key="item.path"
          :class="['menu-item', { active: isActive(item.path) }]"
          @click="router.push(item.path)"
        >
          <el-tooltip v-if="isCollapsed" :content="item.title" placement="right" :offset="16">
            <div class="menu-item-content">
              <div class="menu-icon">
                <el-icon :size="20"><component :is="item.icon" /></el-icon>
              </div>
            </div>
          </el-tooltip>
          <div v-else class="menu-item-content">
            <div class="menu-icon">
              <el-icon :size="20"><component :is="item.icon" /></el-icon>
            </div>
            <span class="menu-text">{{ item.title }}</span>
          </div>
          <div class="menu-item-bg"></div>
          <div class="menu-item-glow"></div>
        </div>
      </div>

      <div class="sidebar-footer">
        <el-tooltip v-if="isCollapsed" content="展开侧边栏" placement="right" :offset="16">
          <div
            class="collapse-btn"
            @click="toggleCollapse"
          >
            <el-icon :size="18">
              <DArrowRight />
            </el-icon>
          </div>
        </el-tooltip>
        <div
          v-else
          :class="['collapse-btn', { collapsed: isCollapsed }]"
          @click="toggleCollapse"
        >
          <el-icon :size="18">
            <DArrowLeft />
          </el-icon>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  Briefcase, HomeFilled, Document, Connection,
  DArrowLeft, DArrowRight, Cpu, Upload, Setting, User
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const isCollapsed = ref(false)
const canvasRef = ref(null)
let animationId = null
let particles = []

const menuItems = computed(() => {
  const items = [
    { path: '/dashboard', title: '首页', icon: 'HomeFilled' },
    { path: '/jobs', title: '岗位管理', icon: 'Briefcase' },
    { path: '/resumes/upload', title: '简历上传', icon: 'Upload' },
    { path: '/resumes', title: '简历管理', icon: 'Document' },
    { path: '/matching', title: '人岗匹配', icon: 'Connection' },
    { path: '/ai-center', title: 'AI智能中心', icon: 'Cpu' }
  ]
  
  if (authStore.isAdmin) {
    items.push({ path: '/system/user-management', title: '用户管理', icon: 'User' })
    items.push({ path: '/system/weight-config', title: '权重配置', icon: 'Setting' })
  }
  
  return items
})

const isActive = (path) => {
  if (path === '/dashboard') return route.path === path
  // 精确匹配子路由，避免 /resumes/upload 同时匹配 /resumes
  if (path === '/resumes') return route.path === path || (route.path.startsWith('/resumes/') && !route.path.startsWith('/resumes/upload'))
  return route.path === path || route.path.startsWith(path + '/')
}

const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value
}

const initParticles = () => {
  const canvas = canvasRef.value
  if (!canvas) return
  
  const ctx = canvas.getContext('2d')
  const rect = canvas.parentElement.getBoundingClientRect()
  canvas.width = rect.width
  canvas.height = rect.height
  
  particles = []
  const particleCount = 30
  
  for (let i = 0; i < particleCount; i++) {
    particles.push({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      vx: (Math.random() - 0.5) * 0.15,
      vy: (Math.random() - 0.5) * 0.15,
      radius: Math.random() * 1.2 + 0.3,
      opacity: Math.random() * 0.3 + 0.1,
      color: Math.random() > 0.5 ? '99, 102, 241' : '139, 92, 246'
    })
  }
  
  const animate = () => {
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    
    particles.forEach((particle) => {
      particle.x += particle.vx
      particle.y += particle.vy
      
      if (particle.x < 0 || particle.x > canvas.width) particle.vx *= -1
      if (particle.y < 0 || particle.y > canvas.height) particle.vy *= -1
      
      ctx.beginPath()
      ctx.arc(particle.x, particle.y, particle.radius, 0, Math.PI * 2)
      ctx.fillStyle = `rgba(${particle.color}, ${particle.opacity})`
      ctx.fill()
    })
    
    animationId = requestAnimationFrame(animate)
  }
  
  animate()
}

onMounted(() => {
  initParticles()
  
  window.addEventListener('resize', () => {
    if (canvasRef.value) {
      const rect = canvasRef.value.parentElement.getBoundingClientRect()
      canvasRef.value.width = rect.width
      canvasRef.value.height = rect.height
    }
  })
})

onUnmounted(() => {
  if (animationId) {
    cancelAnimationFrame(animationId)
  }
})
</script>

<style scoped lang="scss">
.sidebar {
  width: 240px;
  height: 100vh;
  position: fixed;
  left: 0;
  top: 0;
  z-index: 1000;
  transition: width 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  
  &.collapsed {
    width: 72px;
  }
}

.sidebar-bg {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 250, 255, 0.95) 100%);
  backdrop-filter: blur(20px);
  border-right: 1px solid var(--card-border);
}

.sidebar-flow {
  position: absolute;
  top: -100%;
  left: 0;
  width: 100%;
  height: 300%;
  background: linear-gradient(
    180deg,
    transparent 0%,
    rgba(99, 102, 241, 0.05) 25%,
    rgba(139, 92, 246, 0.05) 50%,
    rgba(245, 158, 11, 0.03) 75%,
    transparent 100%
  );
  animation: flowDown 8s linear infinite;
  pointer-events: none;
}

@keyframes flowDown {
  0% {
    transform: translateY(-33.33%);
  }
  100% {
    transform: translateY(0%);
  }
}

.sidebar-particles {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.sidebar-content {
  position: relative;
  height: 100%;
  display: flex;
  flex-direction: column;
  z-index: 1;
}

.sidebar-header {
  padding: 20px 16px;
  border-bottom: 1px solid var(--card-border);
  cursor: pointer;
  transition: var(--transition-base);
  
  &:hover {
    background: rgba(255, 255, 255, 0.03);
  }
}

.logo-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--gradient-primary);
  border-radius: var(--radius-md);
  box-shadow: 0 4px 12px var(--primary-glow);
  color: white;
  flex-shrink: 0;
}

.logo-text {
  font-size: 16px;
  font-weight: 700;
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  white-space: nowrap;
}

.sidebar-menu {
  flex: 1;
  padding: 12px;
  overflow-y: auto;
  
  &::-webkit-scrollbar {
    width: 4px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: rgba(99, 102, 241, 0.12);
    border-radius: 2px;
  }
}

.menu-group-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 1px;
  padding: 8px 12px 6px;
  margin-top: 8px;
  
  &.menu-group-divider {
    margin-top: 16px;
    padding-top: 12px;
    border-top: 1px solid var(--card-border);
  }
}

.menu-divider {
  height: 1px;
  background: var(--card-border);
  margin: 12px 8px;
}

.menu-item {
  position: relative;
  margin-bottom: 8px;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: var(--transition-base);
  overflow: hidden;
  
  &:hover {
    transform: translateX(4px);
    
    .menu-item-bg {
      opacity: 1;
    }
    
    .menu-icon {
      color: var(--text-primary);
      transform: scale(1.1);
    }
    
    .menu-text {
      color: var(--text-primary);
    }
  }
  
  &.active {
    .menu-item-bg {
      opacity: 1;
      background: var(--gradient-primary);
    }
    
    .menu-item-glow {
      opacity: 1;
      animation: glowPulse 2s ease-in-out infinite;
    }
    
    .menu-icon {
      color: white;
      filter: drop-shadow(0 0 8px rgba(255, 255, 255, 0.6));
    }
    
    .menu-text {
      color: white;
      font-weight: 600;
    }
  }
}

.menu-item-bg {
  position: absolute;
  inset: 0;
  opacity: 0;
  transition: var(--transition-base);
  border-radius: var(--radius-md);
}

.menu-item-content {
  position: relative;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  z-index: 1;
}

.menu-icon {
  color: var(--text-secondary);
  transition: var(--transition-base);
  flex-shrink: 0;
}

.menu-text {
  font-size: 14px;
  color: var(--text-secondary);
  transition: var(--transition-base);
  white-space: nowrap;
}

.menu-item-glow {
  position: absolute;
  inset: -2px;
  opacity: 0;
  border-radius: var(--radius-md);
  background: var(--gradient-primary);
  filter: blur(8px);
  transition: var(--transition-slow);
  pointer-events: none;
}

@keyframes glowPulse {
  0%, 100% {
    opacity: 0.4;
    filter: blur(8px);
  }
  50% {
    opacity: 0.6;
    filter: blur(12px);
  }
}

.sidebar-footer {
  padding: 16px 12px;
  border-top: 1px solid var(--card-border);
}

.collapse-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px;
  border-radius: var(--radius-md);
  cursor: pointer;
  color: var(--text-secondary);
  transition: var(--transition-base);
  
  &:hover {
    background: rgba(255, 255, 255, 0.05);
    color: var(--text-primary);
  }
  
  &.collapsed {
    transform: rotate(180deg);
  }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
