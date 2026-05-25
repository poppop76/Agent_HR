<template>
  <transition name="loading-fade">
    <div v-if="loadingStore.loading" class="neon-loading-overlay">
      <!-- 背景粒子 -->
      <canvas ref="canvasRef" class="loading-particles"></canvas>
      
      <!-- 极光背景 -->
      <div class="aurora-bg"></div>
      
      <div class="loading-content">
        <!-- AI 机器人动画 -->
        <div class="robot-container">
          <div class="robot-body">
            <!-- 机器人头部 -->
            <div class="robot-head">
              <div class="robot-antenna">
                <div class="antenna-ball"></div>
              </div>
              <div class="robot-face">
                <div class="robot-eye left-eye">
                  <div class="eye-pupil"></div>
                </div>
                <div class="robot-eye right-eye">
                  <div class="eye-pupil"></div>
                </div>
                <div class="robot-mouth"></div>
              </div>
            </div>
            <!-- 机器人身体 -->
            <div class="robot-torso">
              <div class="torso-core"></div>
            </div>
            <!-- 扫描光环 -->
            <div class="scan-ring"></div>
          </div>
        </div>
        
        <!-- 加载文字 -->
        <div class="loading-text-wrapper">
          <p class="loading-main-text">{{ loadingStore.loadingText }}</p>
          <p class="loading-sub-text">AI 智能处理中，请稍候...</p>
        </div>
        
        <!-- 霓虹进度条 -->
        <div class="neon-progress">
          <div class="progress-track">
            <div class="progress-fill" :style="{ width: progressWidth + '%' }">
              <div class="progress-glow"></div>
            </div>
          </div>
          <div class="progress-dots">
            <span v-for="i in 3" :key="i" :style="{ animationDelay: (i * 0.2) + 's' }"></span>
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useLoadingStore } from '@/stores/loading'

const loadingStore = useLoadingStore()
const canvasRef = ref(null)
const progressWidth = ref(0)
let animationId = null
let particles = []
let progressInterval = null

const initParticles = () => {
  const canvas = canvasRef.value
  if (!canvas) return
  
  const ctx = canvas.getContext('2d')
  canvas.width = window.innerWidth
  canvas.height = window.innerHeight
  
  particles = []
  const particleCount = 60
  
  for (let i = 0; i < particleCount; i++) {
    particles.push({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      vx: (Math.random() - 0.5) * 0.3,
      vy: (Math.random() - 0.5) * 0.3,
      radius: Math.random() * 2 + 0.5,
      opacity: Math.random() * 0.5 + 0.1,
      color: Math.random() > 0.5 ? '99, 102, 241' : '139, 92, 246'
    })
  }
  
  const animate = () => {
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    
    particles.forEach((particle, i) => {
      particle.x += particle.vx
      particle.y += particle.vy
      
      if (particle.x < 0 || particle.x > canvas.width) particle.vx *= -1
      if (particle.y < 0 || particle.y > canvas.height) particle.vy *= -1
      
      ctx.beginPath()
      ctx.arc(particle.x, particle.y, particle.radius, 0, Math.PI * 2)
      ctx.fillStyle = `rgba(${particle.color}, ${particle.opacity})`
      ctx.fill()
      
      // 连线
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particle.x - particles[j].x
        const dy = particle.y - particles[j].y
        const distance = Math.sqrt(dx * dx + dy * dy)
        
        if (distance < 100) {
          ctx.beginPath()
          ctx.strokeStyle = `rgba(${particle.color}, ${0.15 * (1 - distance / 100)})`
          ctx.lineWidth = 0.5
          ctx.moveTo(particle.x, particle.y)
          ctx.lineTo(particles[j].x, particles[j].y)
          ctx.stroke()
        }
      }
    })
    
    animationId = requestAnimationFrame(animate)
  }
  
  animate()
}

// 模拟进度条动画
const startProgressAnimation = () => {
  progressWidth.value = 0
  progressInterval = setInterval(() => {
    if (progressWidth.value < 90) {
      progressWidth.value += Math.random() * 3
    }
  }, 200)
}

const stopProgressAnimation = () => {
  if (progressInterval) {
    clearInterval(progressInterval)
    progressInterval = null
  }
}

onMounted(() => {
  initParticles()
  startProgressAnimation()
  
  window.addEventListener('resize', () => {
    if (canvasRef.value) {
      canvasRef.value.width = window.innerWidth
      canvasRef.value.height = window.innerHeight
    }
  })
})

onUnmounted(() => {
  if (animationId) {
    cancelAnimationFrame(animationId)
  }
  stopProgressAnimation()
})
</script>

<style scoped lang="scss">
.neon-loading-overlay {
  position: fixed;
  inset: 0;
  background: var(--bg-dark);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
  overflow: hidden;
}

.loading-particles {
  position: absolute;
  inset: 0;
  z-index: 1;
}

.aurora-bg {
  position: absolute;
  inset: 0;
  background: 
    radial-gradient(ellipse at 20% 50%, rgba(99, 102, 241, 0.08) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 50%, rgba(139, 92, 246, 0.06) 0%, transparent 50%),
    radial-gradient(ellipse at 50% 80%, rgba(245, 158, 11, 0.04) 0%, transparent 50%);
  animation: auroraShift 8s ease-in-out infinite;
  z-index: 0;
}

@keyframes auroraShift {
  0%, 100% { opacity: 0.8; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.1); }
}

.loading-content {
  position: relative;
  z-index: 2;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 32px;
}

// 机器人动画
.robot-container {
  position: relative;
  width: 120px;
  height: 140px;
}

.robot-body {
  position: relative;
  width: 100%;
  height: 100%;
  animation: robotFloat 3s ease-in-out infinite;
}

@keyframes robotFloat {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.robot-head {
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 70px;
  height: 60px;
  background: linear-gradient(135deg, #1E293B, #334155);
  border-radius: 20px 20px 15px 15px;
  border: 2px solid rgba(99, 102, 241, 0.3);
  box-shadow: var(--neon-purple);
}

.robot-antenna {
  position: absolute;
  top: -18px;
  left: 50%;
  transform: translateX(-50%);
  width: 2px;
  height: 14px;
  background: linear-gradient(to top, rgba(99, 102, 241, 0.3), #6366F1);
}

.antenna-ball {
  position: absolute;
  top: -6px;
  left: 50%;
  transform: translateX(-50%);
  width: 10px;
  height: 10px;
  background: #6366F1;
  border-radius: 50%;
  box-shadow: 0 0 10px #6366F1, 0 0 20px rgba(99, 102, 241, 0.3);
  animation: antennaPulse 1.5s ease-in-out infinite;
}

@keyframes antennaPulse {
  0%, 100% { box-shadow: 0 0 10px #6366F1, 0 0 20px rgba(99, 102, 241, 0.3); }
  50% { box-shadow: 0 0 15px #6366F1, 0 0 30px rgba(99, 102, 241, 0.4), 0 0 50px rgba(99, 102, 241, 0.15); }
}

.robot-face {
  position: absolute;
  inset: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.robot-eyes {
  display: flex;
  gap: 16px;
}

.robot-eye {
  width: 16px;
  height: 16px;
  background: #1E293B;
  border-radius: 50%;
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(99, 102, 241, 0.3);
}

.eye-pupil {
  position: absolute;
  width: 8px;
  height: 8px;
  background: #8B5CF6;
  border-radius: 50%;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  box-shadow: 0 0 8px #8B5CF6;
  animation: eyeLook 4s ease-in-out infinite;
}

@keyframes eyeLook {
  0%, 40%, 100% { transform: translate(-50%, -50%); }
  10%, 30% { transform: translate(-30%, -50%); }
  50%, 70% { transform: translate(-70%, -50%); }
}

.robot-mouth {
  width: 20px;
  height: 6px;
  background: linear-gradient(90deg, transparent, #6366F1, transparent);
  border-radius: 3px;
  animation: mouthTalk 2s ease-in-out infinite;
}

@keyframes mouthTalk {
  0%, 100% { height: 6px; }
  50% { height: 10px; }
}

.robot-torso {
  position: absolute;
  top: 65px;
  left: 50%;
  transform: translateX(-50%);
  width: 50px;
  height: 55px;
  background: linear-gradient(135deg, #1E293B, #334155);
  border-radius: 10px 10px 20px 20px;
  border: 2px solid rgba(99, 102, 241, 0.3);
  box-shadow: var(--neon-blue);
  display: flex;
  align-items: center;
  justify-content: center;
}

.torso-core {
  width: 20px;
  height: 20px;
  background: radial-gradient(circle, #6366F1, #8B5CF6);
  border-radius: 50%;
  box-shadow: 0 0 15px rgba(99, 102, 241, 0.4);
  animation: corePulse 2s ease-in-out infinite;
}

@keyframes corePulse {
  0%, 100% { transform: scale(1); opacity: 0.8; }
  50% { transform: scale(1.2); opacity: 1; }
}

.scan-ring {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 100px;
  height: 100px;
  border: 2px solid rgba(99, 102, 241, 0.15);
  border-radius: 50%;
  animation: scanExpand 2s ease-out infinite;
}

@keyframes scanExpand {
  0% { width: 60px; height: 60px; opacity: 1; border-width: 2px; }
  100% { width: 140px; height: 140px; opacity: 0; border-width: 1px; }
}

// 加载文字
.loading-text-wrapper {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.loading-main-text {
  font-size: 20px;
  font-weight: 700;
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: 2px;
}

.loading-sub-text {
  font-size: 13px;
  color: var(--text-tertiary);
  animation: textFade 2s ease-in-out infinite;
}

@keyframes textFade {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

// 霓虹进度条
.neon-progress {
  width: 280px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.progress-track {
  width: 100%;
  height: 4px;
  background: rgba(99, 102, 241, 0.06);
  border-radius: 2px;
  overflow: hidden;
  position: relative;
}

.progress-fill {
  height: 100%;
  background: var(--gradient-primary);
  border-radius: 2px;
  transition: width 0.3s ease;
  position: relative;
  box-shadow: 0 0 10px rgba(99, 102, 241, 0.3);
}

.progress-glow {
  position: absolute;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 100%;
  background: rgba(255, 255, 255, 0.6);
  filter: blur(4px);
  animation: glowPulse 1s ease-in-out infinite;
}

@keyframes glowPulse {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}

.progress-dots {
  display: flex;
  gap: 6px;
  
  span {
    width: 6px;
    height: 6px;
    background: var(--primary-color);
    border-radius: 50%;
    animation: dotBounce 1.4s ease-in-out infinite;
    box-shadow: 0 0 6px rgba(99, 102, 241, 0.3);
  }
}

@keyframes dotBounce {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
  40% { transform: scale(1); opacity: 1; }
}

// 转场动画
.loading-fade-enter-active,
.loading-fade-leave-active {
  transition: opacity 0.4s ease;
}

.loading-fade-enter-from,
.loading-fade-leave-to {
  opacity: 0;
}
</style>
