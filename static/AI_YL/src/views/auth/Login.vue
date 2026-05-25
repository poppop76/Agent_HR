<template>
  <div class="login-page">
    <!-- 极光背景 -->
    <div class="aurora-background">
      <div class="aurora-layer aurora-1"></div>
      <div class="aurora-layer aurora-2"></div>
      <div class="aurora-layer aurora-3"></div>
      <canvas ref="canvasRef" class="particle-canvas"></canvas>
    </div>
    
    <div class="login-container">
      <div class="left-brand">
        <div class="brand-content">
          <!-- AI 机器人吉祥物 -->
          <div class="robot-mascot">
            <div class="robot-body">
              <div class="robot-head">
                <div class="robot-antenna">
                  <div class="antenna-ball"></div>
                </div>
                <div class="robot-face">
                  <div class="robot-eyes">
                    <div class="robot-eye left-eye">
                      <div class="eye-pupil"></div>
                    </div>
                    <div class="robot-eye right-eye">
                      <div class="eye-pupil"></div>
                    </div>
                  </div>
                  <div class="robot-mouth"></div>
                </div>
              </div>
              <div class="robot-torso">
                <div class="torso-core"></div>
              </div>
              <div class="scan-ring"></div>
            </div>
          </div>
          
          <h1 class="brand-title">HR智能简历解析</h1>
          <p class="brand-subtitle">新一代智能招聘解决方案，让人才匹配更高效</p>
          
          <div class="brand-features">
            <div class="feature-item">
              <div class="feature-icon">
                <el-icon><Cpu /></el-icon>
              </div>
              <div class="feature-text">
                <h3>AI智能解析</h3>
                <p>自动识别简历关键信息</p>
              </div>
            </div>
            <div class="feature-item">
              <div class="feature-icon">
                <el-icon><Connection /></el-icon>
              </div>
              <div class="feature-text">
                <h3>精准匹配</h3>
                <p>多维度评估人岗匹配度</p>
              </div>
            </div>
            <div class="feature-item">
              <div class="feature-icon">
                <el-icon><DataAnalysis /></el-icon>
              </div>
              <div class="feature-text">
                <h3>数据分析</h3>
                <p>可视化统计招聘全流程</p>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="right-login">
        <div class="login-card">
          <div class="card-glow"></div>
          <div class="login-header">
            <h2 class="login-title">欢迎登录</h2>
            <p class="login-subtitle">请输入您的账号信息</p>
          </div>
          
          <el-form 
            ref="loginFormRef"
            :model="loginForm"
            :rules="loginRules"
            class="login-form"
            @keyup.enter="handleLogin"
          >
            <el-form-item prop="username">
              <div class="input-wrapper">
                <el-icon class="input-icon"><User /></el-icon>
                <el-input
                  v-model="loginForm.username"
                  placeholder="请输入账号"
                  size="large"
                  class="custom-input"
                />
              </div>
            </el-form-item>
            
            <el-form-item prop="password">
              <div class="input-wrapper">
                <el-icon class="input-icon"><Lock /></el-icon>
                <el-input
                  v-model="loginForm.password"
                  type="password"
                  placeholder="请输入密码"
                  size="large"
                  class="custom-input"
                  show-password
                />
              </div>
            </el-form-item>
            
            <el-form-item class="login-options">
              <el-checkbox v-model="loginForm.remember" class="custom-checkbox">记住密码</el-checkbox>
              <el-link type="primary" class="forgot-link" @click="router.push('/forgot-password')">忘记密码?</el-link>
            </el-form-item>
            
            <el-form-item>
              <el-button
                type="primary"
                size="large"
                class="login-btn"
                :loading="loading"
                @click="handleLogin"
              >
                <span v-if="!loading">登 录</span>
                <span v-else>登录中...</span>
              </el-button>
            </el-form-item>
          </el-form>
          
          <div class="login-footer">
            <div class="footer-divider"></div>
            <p> 2024 HR智能简历解析系统 · 让招聘更智能</p>
            <div class="demo-accounts">
              <p class="demo-title">测试账号（无需后端）</p>
              <div class="demo-item">
                <span class="demo-label">管理员：</span>
                <span class="demo-value">admin / 123456</span>
              </div>
              <div class="demo-item">
                <span class="demo-label">HR用户：</span>
                <span class="demo-value">hr / 123456</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useLoadingStore } from '@/stores/loading'
import { ElMessage } from 'element-plus'
import { User, Lock, Cpu, Connection, DataAnalysis } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const loadingStore = useLoadingStore()
const canvasRef = ref(null)

const loginFormRef = ref(null)
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: '',
  remember: false
})

const loginRules = {
  username: [{ required: true, message: '请输入账号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const handleLogin = async () => {
  const valid = await loginFormRef.value.validate().catch(() => false)
  if (!valid) return
  
  loading.value = true
  try {
    await authStore.login({
      username: loginForm.username,
      password: loginForm.password
    })
    ElMessage.success('登录成功')
    const redirect = route.query.redirect || '/dashboard'
    router.push(redirect)
  } catch (error) {
    ElMessage.error('账号或密码错误')
  } finally {
    loading.value = false
  }
}

let animationId = null
let particles = []

const initCanvas = () => {
  const canvas = canvasRef.value
  if (!canvas) return
  
  const ctx = canvas.getContext('2d')
  canvas.width = window.innerWidth
  canvas.height = window.innerHeight
  
  particles = []
  const particleCount = 80
  
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
      
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particle.x - particles[j].x
        const dy = particle.y - particles[j].y
        const distance = Math.sqrt(dx * dx + dy * dy)
        
        if (distance < 120) {
          ctx.beginPath()
          ctx.strokeStyle = `rgba(${particle.color}, ${0.1 * (1 - distance / 120)})`
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

onMounted(() => {
  initCanvas()
  
  window.addEventListener('resize', () => {
    if (canvasRef.value) {
      canvasRef.value.width = window.innerWidth
      canvasRef.value.height = window.innerHeight
    }
  })
  
  if (authStore.isLoggedIn) {
    router.push('/dashboard')
  }
})

onUnmounted(() => {
  if (animationId) {
    cancelAnimationFrame(animationId)
  }
})
</script>

<style scoped lang="scss">
.login-page {
  width: 100%;
  height: 100vh;
  position: relative;
  overflow: hidden;
  background: var(--bg-dark);
  background: linear-gradient(135deg, #F5F5F4 0%, #FAFAF9 50%, #F5F5F4 100%);
}

// 极光背景
.aurora-background {
  position: absolute;
  inset: 0;
  z-index: 0;
  overflow: hidden;
}

.aurora-layer {
  position: absolute;
  inset: -50%;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.4;
}

.aurora-1 {
  background: radial-gradient(circle, rgba(99, 102, 241, 0.12) 0%, transparent 70%);
  animation: auroraMove1 15s ease-in-out infinite;
}

.aurora-2 {
  background: radial-gradient(circle, rgba(139, 92, 246, 0.08) 0%, transparent 70%);
  animation: auroraMove2 18s ease-in-out infinite;
}

.aurora-3 {
  background: radial-gradient(circle, rgba(245, 158, 11, 0.06) 0%, transparent 70%);
  animation: auroraMove3 20s ease-in-out infinite;
}

@keyframes auroraMove1 {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(30%, 20%) scale(1.1); }
  66% { transform: translate(-20%, -30%) scale(0.9); }
}

@keyframes auroraMove2 {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(-30%, -20%) scale(1.2); }
  66% { transform: translate(20%, 30%) scale(0.8); }
}

@keyframes auroraMove3 {
  0%, 100% { transform: translate(0, 0) scale(1); }
  50% { transform: translate(40%, -40%) scale(1.1); }
}

.particle-canvas {
  position: absolute;
  inset: 0;
  z-index: 1;
}

.login-container {
  width: 100%;
  height: 100%;
  display: flex;
  position: relative;
  z-index: 10;
}

.left-brand {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  position: relative;
  z-index: 2;
}

.brand-content {
  max-width: 520px;
  animation: fadeInLeft 0.6s ease-out;
}

@keyframes fadeInLeft {
  from {
    opacity: 0;
    transform: translateX(-30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

// AI 机器人吉祥物
.robot-mascot {
  position: relative;
  width: 140px;
  height: 160px;
  margin: 0 auto 24px;
}

.robot-body {
  position: relative;
  width: 100%;
  height: 100%;
  animation: robotFloat 3s ease-in-out infinite;
}

@keyframes robotFloat {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-12px); }
}

.robot-head {
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 80px;
  height: 70px;
  background: linear-gradient(135deg, #1E293B, #334155);
  border-radius: 24px 24px 18px 18px;
  border: 2px solid rgba(99, 102, 241, 0.4);
  box-shadow: var(--neon-purple);
}

.robot-antenna {
  position: absolute;
  top: -20px;
  left: 50%;
  transform: translateX(-50%);
  width: 2px;
  height: 16px;
  background: linear-gradient(to top, rgba(99, 102, 241, 0.3), #6366F1);
}

.antenna-ball {
  position: absolute;
  top: -7px;
  left: 50%;
  transform: translateX(-50%);
  width: 12px;
  height: 12px;
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
  inset: 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.robot-eyes {
  display: flex;
  gap: 18px;
}

.robot-eye {
  width: 18px;
  height: 18px;
  background: #1E293B;
  border-radius: 50%;
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(99, 102, 241, 0.3);
  box-shadow: 0 0 8px rgba(99, 102, 241, 0.2);
}

.eye-pupil {
  position: absolute;
  width: 10px;
  height: 10px;
  background: #8B5CF6;
  border-radius: 50%;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  box-shadow: 0 0 10px #8B5CF6;
  animation: eyeLook 4s ease-in-out infinite;
}

@keyframes eyeLook {
  0%, 40%, 100% { transform: translate(-50%, -50%); }
  10%, 30% { transform: translate(-30%, -50%); }
  50%, 70% { transform: translate(-70%, -50%); }
}

.robot-mouth {
  width: 24px;
  height: 8px;
  background: linear-gradient(90deg, transparent, #6366F1, transparent);
  border-radius: 4px;
  animation: mouthTalk 2s ease-in-out infinite;
}

@keyframes mouthTalk {
  0%, 100% { height: 8px; }
  50% { height: 12px; }
}

.robot-torso {
  position: absolute;
  top: 75px;
  left: 50%;
  transform: translateX(-50%);
  width: 60px;
  height: 65px;
  background: linear-gradient(135deg, #1E293B, #334155);
  border-radius: 12px 12px 24px 24px;
  border: 2px solid rgba(99, 102, 241, 0.4);
  box-shadow: var(--neon-blue);
  display: flex;
  align-items: center;
  justify-content: center;
}

.torso-core {
  width: 24px;
  height: 24px;
  background: radial-gradient(circle, #6366F1, #8B5CF6);
  border-radius: 50%;
  box-shadow: 0 0 20px rgba(99, 102, 241, 0.4);
  animation: corePulse 2s ease-in-out infinite;
}

@keyframes corePulse {
  0%, 100% { transform: scale(1); opacity: 0.8; }
  50% { transform: scale(1.3); opacity: 1; }
}

.scan-ring {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 120px;
  height: 120px;
  border: 2px solid rgba(99, 102, 241, 0.15);
  border-radius: 50%;
  animation: scanExpand 2s ease-out infinite;
}

@keyframes scanExpand {
  0% { width: 80px; height: 80px; opacity: 1; border-width: 2px; }
  100% { width: 160px; height: 160px; opacity: 0; border-width: 1px; }
}

.brand-title {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 12px;
  line-height: 1.4;
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-align: center;
}

.brand-subtitle {
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 400;
  margin-bottom: 32px;
  line-height: 1.5;
  text-align: center;
}

.brand-features {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: var(--card-bg);
  backdrop-filter: blur(8px);
  border-radius: var(--radius-lg);
  border: 1px solid var(--card-border);
  transition: var(--transition-base);
  
  &:hover {
    background: var(--card-bg-hover);
    transform: translateX(4px);
    border-color: var(--primary-color);
    box-shadow: 0 0 12px rgba(99, 102, 241, 0.12);
  }
}

.feature-icon {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md);
  background: var(--gradient-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
  box-shadow: 0 0 10px rgba(99, 102, 241, 0.15);
}

.feature-text {
  h3 {
    font-size: 14px;
    font-weight: 600;
    margin-bottom: 4px;
    color: var(--text-primary);
  }
  
  p {
    font-size: 12px;
    color: var(--text-tertiary);
    margin: 0;
  }
}

.right-login {
  width: 45%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  position: relative;
  z-index: 2;
}

.login-card {
  width: 100%;
  max-width: 400px;
  padding: 0;
  background: var(--gradient-card);
  backdrop-filter: blur(16px);
  border-radius: var(--radius-xl);
  box-shadow: var(--card-shadow);
  position: relative;
  overflow: hidden;
  animation: cardEntrance 0.5s ease-out;
  border: 1px solid var(--card-border);
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: var(--gradient-neon);
    background-size: 300% 100%;
    animation: neonFlow 3s ease infinite;
  }
}

@keyframes neonFlow {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.card-glow {
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle at center, rgba(99, 102, 241, 0.08) 0%, transparent 60%);
  opacity: 0.3;
  pointer-events: none;
  animation: glowRotate 8s linear infinite;
}

@keyframes glowRotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes cardEntrance {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.login-header {
  text-align: center;
  padding: 32px 32px 0;
  position: relative;
  z-index: 1;
}

.login-title {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 8px;
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.login-subtitle {
  font-size: 12px;
  color: var(--text-tertiary);
  font-weight: 400;
}

.login-form {
  padding: 24px 32px;
  margin-top: 0;
  position: relative;
  z-index: 1;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  width: 100%;
}

.input-icon {
  position: absolute;
  left: 12px;
  font-size: 16px;
  color: var(--text-tertiary);
  z-index: 1;
  transition: var(--transition-base);
}

.custom-input {
  width: 100%;
  
  :deep(.el-input__wrapper) {
    padding: 10px 12px 10px 40px;
    border-radius: var(--radius-md);
    background: var(--card-bg) !important;
    backdrop-filter: blur(8px);
    border: 1px solid var(--card-border);
    box-shadow: none !important;
    transition: var(--transition-base);
    
    &:hover {
      border-color: var(--card-border-glow);
    }
    
    &.is-focus {
      border-color: var(--primary-color);
      box-shadow: 0 0 0 2px var(--primary-glow), var(--neon-purple) !important;
    }
    
    .el-input__inner {
      color: var(--text-primary);
      font-size: 14px;
      background: transparent;
      
      &::placeholder {
        color: var(--text-tertiary);
      }
    }
  }
  
  &:hover .input-icon {
    color: var(--primary-color);
  }
}

.login-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
}

.custom-checkbox {
  :deep(.el-checkbox__label) {
    color: var(--text-secondary);
    font-size: 12px;
  }
}

.forgot-link {
  font-size: 12px;
  font-weight: 500;
  color: var(--primary-light);
}

.login-btn {
  width: 100%;
  height: 44px;
  font-size: 14px;
  font-weight: 600;
  border-radius: var(--radius-md);
  background: var(--gradient-primary);
  border: none;
  box-shadow: var(--neon-purple);
  transition: var(--transition-base);
  position: relative;
  overflow: hidden;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
    transition: left 0.5s;
  }
  
  &:hover {
    box-shadow: 0 0 20px rgba(99, 102, 241, 0.2), 0 0 40px rgba(99, 102, 241, 0.08);
    transform: translateY(-2px);
    
    &::before {
      left: 100%;
    }
  }
  
  &:active {
    transform: translateY(0) scale(0.98);
  }
}

.login-footer {
  text-align: center;
  padding: 0 32px 24px;
  position: relative;
  z-index: 1;
}

.footer-divider {
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--card-border), transparent);
  margin-bottom: 12px;
}

.login-footer p {
  color: var(--text-tertiary);
  font-size: 12px;
  font-weight: 400;
}

.demo-accounts {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px dashed var(--card-border);
}

.demo-title {
  color: var(--text-secondary);
  font-size: 12px;
  font-weight: 600;
  margin-bottom: 8px;
}

.demo-item {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 4px;
  margin-bottom: 4px;
  font-size: 12px;
}

.demo-label {
  color: var(--text-tertiary);
}

.demo-value {
  color: var(--primary-light);
  font-weight: 600;
  font-family: monospace;
}

@media (max-width: 1200px) {
  .login-container {
    flex-direction: column;
  }
  
  .left-brand {
    display: none;
  }
  
  .right-login {
    width: 100%;
    padding: 20px;
  }
}
</style>
