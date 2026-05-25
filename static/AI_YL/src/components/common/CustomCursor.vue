<template>
  <div class="custom-cursor" ref="cursorRef" :class="{ 'cursor-hover': isHovering }"></div>
  <div class="cursor-dot" ref="dotRef"></div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const cursorRef = ref(null)
const dotRef = ref(null)
const isHovering = ref(false)

let mouseX = 0
let mouseY = 0
let cursorX = 0
let cursorY = 0
let animationId = null

const handleMouseMove = (e) => {
  mouseX = e.clientX
  mouseY = e.clientY
  
  if (dotRef.value) {
    dotRef.value.style.left = mouseX + 'px'
    dotRef.value.style.top = mouseY + 'px'
  }
}

const handleMouseOver = (e) => {
  const target = e.target
  if (target.matches('a, button, .icon-btn, .menu-item, .el-button, .el-input__wrapper, .el-select__wrapper, [role="button"], [onclick], .feature-item, .collapse-btn, .login-btn')) {
    isHovering.value = true
  }
}

const handleMouseOut = () => {
  isHovering.value = false
}

const animateCursor = () => {
  const ease = 0.15
  cursorX += (mouseX - cursorX) * ease
  cursorY += (mouseY - cursorY) * ease
  
  if (cursorRef.value) {
    cursorRef.value.style.left = cursorX + 'px'
    cursorRef.value.style.top = cursorY + 'px'
  }
  
  animationId = requestAnimationFrame(animateCursor)
}

onMounted(() => {
  window.addEventListener('mousemove', handleMouseMove)
  window.addEventListener('mouseover', handleMouseOver)
  window.addEventListener('mouseout', handleMouseOut)
  
  // 初始化位置
  cursorX = window.innerWidth / 2
  cursorY = window.innerHeight / 2
  
  animateCursor()
})

onUnmounted(() => {
  window.removeEventListener('mousemove', handleMouseMove)
  window.removeEventListener('mouseover', handleMouseOver)
  window.removeEventListener('mouseout', handleMouseOut)
  
  if (animationId) {
    cancelAnimationFrame(animationId)
  }
})
</script>

<style scoped lang="scss">
.custom-cursor {
  position: fixed;
  width: 20px;
  height: 20px;
  border: 2px solid rgba(99, 102, 241, 0.5);
  border-radius: 50%;
  pointer-events: none;
  z-index: 99999;
  transition: width 0.2s ease, height 0.2s ease, border-color 0.2s ease;
  transform: translate(-50%, -50%);
  
  &.cursor-hover {
    width: 40px;
    height: 40px;
    border-color: rgba(139, 92, 246, 0.5);
  }
}

.cursor-dot {
  position: fixed;
  width: 6px;
  height: 6px;
  background: #6366F1;
  border-radius: 50%;
  pointer-events: none;
  z-index: 99999;
  transform: translate(-50%, -50%);
  box-shadow: 0 0 8px rgba(99, 102, 241, 0.3);
}

// 移动端隐藏自定义光标
@media (max-width: 768px) {
  .custom-cursor,
  .cursor-dot {
    display: none;
  }
}
</style>
