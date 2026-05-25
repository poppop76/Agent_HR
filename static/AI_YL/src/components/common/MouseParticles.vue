<template>
  <div class="mouse-particles" ref="particlesRef">
    <div 
      v-for="effect in appStore.clickEffects" 
      :key="effect.id"
      class="click-effect"
      :style="{ left: effect.x + 'px', top: effect.y + 'px' }"
    >
      <span v-for="i in 6" :key="i" class="particle" :style="{ '--i': i }"></span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useAppStore } from '@/stores/app'

const appStore = useAppStore()
const particlesRef = ref(null)

const handleMouseMove = (e) => {
  appStore.updateMousePosition(e.clientX, e.clientY)
}

const handleClick = (e) => {
  appStore.addClickEffect(e.clientX, e.clientY)
}

onMounted(() => {
  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('click', handleClick)
})

onUnmounted(() => {
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('click', handleClick)
})
</script>

<style scoped lang="scss">
.mouse-particles {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 9998;
}

.click-effect {
  position: absolute;
  transform: translate(-50%, -50%);
}

.particle {
  position: absolute;
  width: 8px;
  height: 8px;
  background: var(--primary-color);
  border-radius: 50%;
  animation: particleBurst 0.6s ease-out forwards;
  transform: rotate(calc(60deg * var(--i))) translateX(20px);
  opacity: 0;
}

@keyframes particleBurst {
  0% {
    transform: rotate(calc(60deg * var(--i))) translateX(0);
    opacity: 1;
  }
  100% {
    transform: rotate(calc(60deg * var(--i))) translateX(50px);
    opacity: 0;
  }
}
</style>
