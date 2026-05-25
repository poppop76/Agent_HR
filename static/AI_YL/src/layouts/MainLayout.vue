<template>
  <div class="main-layout">
    <ParticlesBackground />
    <CustomCursor />
    
    <!-- 移动端遮罩层 -->
    <div v-if="isMobile" class="sidebar-overlay" @click="closeSidebar"></div>
    
    <Sidebar :class="{ 'sidebar-drawer': isMobile }" />
    
    <div class="main-wrapper" :class="{ 'mobile-expanded': !isMobile }">
      <MainNavbar @menu-toggle="toggleSidebar" />
      <BreadcrumbNav />
      <div class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="fade-montage" mode="out-in">
            <keep-alive :include="cachedViews">
              <component :is="Component" />
            </keep-alive>
          </transition>
        </router-view>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import MainNavbar from '@/components/common/MainNavbar.vue'
import BreadcrumbNav from '@/components/common/BreadcrumbNav.vue'
import Sidebar from '@/components/common/Sidebar.vue'
import ParticlesBackground from '@/components/ParticlesBackground.vue'
import CustomCursor from '@/components/common/CustomCursor.vue'

const cachedViews = ref([
  'JobList',
  'ResumeList',
  'CandidateList',
  'StatisticsReport'
])

const isMobile = ref(false)

const checkMobile = () => {
  isMobile.value = window.innerWidth < 768
}

const closeSidebar = () => {
  // 移动端点击遮罩层关闭侧边栏（可通过事件总线或 store 控制）
}

const toggleSidebar = () => {
  // 移动端触发侧边栏显示
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})
</script>

<style scoped lang="scss">
.main-layout {
  height: 100vh;
  display: flex;
  position: relative;
}

.sidebar-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 999;
  backdrop-filter: blur(2px);
}

.main-wrapper {
  flex: 1;
  margin-left: 240px;
  display: flex;
  flex-direction: column;
  height: 100vh;
  transition: margin-left 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.main-content {
  flex: 1;
  overflow-y: auto;
  background: transparent;
  position: relative;
  z-index: 1;
}

// 移动端适配
@media (max-width: 768px) {
  .main-wrapper {
    margin-left: 0 !important;
  }
  
  .sidebar-drawer {
    position: fixed;
    left: 0;
    top: 0;
    z-index: 1000;
    transform: translateX(-100%);
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    
    &.show {
      transform: translateX(0);
    }
  }
}
</style>
