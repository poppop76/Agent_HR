<template>
  <canvas ref="canvasRef" class="particles-canvas"></canvas>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const canvasRef = ref(null)
let animationId = null
let stars = []
let dataFlows = []
let interactiveParticles = []
let mouse = { x: -1000, y: -1000 }

const initParticles = () => {
  const canvas = canvasRef.value
  if (!canvas) return
  
  const ctx = canvas.getContext('2d')
  canvas.width = window.innerWidth
  canvas.height = window.innerHeight
  
  // 第一层：星空粒子
  stars = []
  const starCount = 100
  for (let i = 0; i < starCount; i++) {
    stars.push({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      radius: Math.random() * 1.5 + 0.3,
      opacity: Math.random() * 0.6 + 0.1,
      twinkleSpeed: Math.random() * 0.02 + 0.005,
      twinklePhase: Math.random() * Math.PI * 2,
      color: Math.random() > 0.5 ? '99, 102, 241' : '139, 92, 246'
    })
  }
  
  // 第二层：数据流粒子（从上往下流动）
  dataFlows = []
  const flowCount = 30
  for (let i = 0; i < flowCount; i++) {
    dataFlows.push({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      speed: Math.random() * 0.5 + 0.2,
      length: Math.random() * 40 + 20,
      opacity: Math.random() * 0.3 + 0.05,
      color: Math.random() > 0.5 ? '99, 102, 241' : '139, 92, 246'
    })
  }
  
  // 第三层：交互粒子（跟随鼠标）
  interactiveParticles = []
  const interactiveCount = 40
  for (let i = 0; i < interactiveCount; i++) {
    interactiveParticles.push({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      vx: (Math.random() - 0.5) * 0.3,
      vy: (Math.random() - 0.5) * 0.3,
      radius: Math.random() * 2 + 0.5,
      opacity: Math.random() * 0.4 + 0.1,
      color: Math.random() > 0.5 ? '99, 102, 241' : '139, 92, 246'
    })
  }
  
  const animate = () => {
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    
    // 绘制星空层
    stars.forEach(star => {
      star.twinklePhase += star.twinkleSpeed
      const currentOpacity = star.opacity * (0.5 + 0.5 * Math.sin(star.twinklePhase))
      
      ctx.beginPath()
      ctx.arc(star.x, star.y, star.radius, 0, Math.PI * 2)
      ctx.fillStyle = `rgba(${star.color}, ${currentOpacity})`
      ctx.fill()
      
      // 星星光晕
      if (star.radius > 1) {
        ctx.beginPath()
        ctx.arc(star.x, star.y, star.radius * 2, 0, Math.PI * 2)
        ctx.fillStyle = `rgba(${star.color}, ${currentOpacity * 0.2})`
        ctx.fill()
      }
    })
    
    // 绘制数据流层
    dataFlows.forEach(flow => {
      flow.y += flow.speed
      if (flow.y > canvas.height + flow.length) {
        flow.y = -flow.length
        flow.x = Math.random() * canvas.width
      }
      
      const gradient = ctx.createLinearGradient(flow.x, flow.y, flow.x, flow.y - flow.length)
      gradient.addColorStop(0, `rgba(${flow.color}, ${flow.opacity})`)
      gradient.addColorStop(1, `rgba(${flow.color}, 0)`)
      
      ctx.beginPath()
      ctx.strokeStyle = gradient
      ctx.lineWidth = 1
      ctx.moveTo(flow.x, flow.y)
      ctx.lineTo(flow.x, flow.y - flow.length)
      ctx.stroke()
    })
    
    // 绘制交互粒子层
    interactiveParticles.forEach((particle, i) => {
      // 鼠标引力
      const dx = mouse.x - particle.x
      const dy = mouse.y - particle.y
      const distance = Math.sqrt(dx * dx + dy * dy)
      
      if (distance < 200) {
        const force = (200 - distance) / 200 * 0.02
        particle.vx += dx * force * 0.01
        particle.vy += dy * force * 0.01
      }
      
      particle.x += particle.vx
      particle.y += particle.vy
      
      // 阻尼
      particle.vx *= 0.99
      particle.vy *= 0.99
      
      if (particle.x < 0 || particle.x > canvas.width) particle.vx *= -1
      if (particle.y < 0 || particle.y > canvas.height) particle.vy *= -1
      
      ctx.beginPath()
      ctx.arc(particle.x, particle.y, particle.radius, 0, Math.PI * 2)
      ctx.fillStyle = `rgba(${particle.color}, ${particle.opacity})`
      ctx.fill()
      
      // 连线
      for (let j = i + 1; j < interactiveParticles.length; j++) {
        const other = interactiveParticles[j]
        const pdx = particle.x - other.x
        const pdy = particle.y - other.y
        const pdistance = Math.sqrt(pdx * pdx + pdy * pdy)
        
        if (pdistance < 120) {
          ctx.beginPath()
          ctx.strokeStyle = `rgba(${particle.color}, ${0.12 * (1 - pdistance / 120)})`
          ctx.lineWidth = 0.5
          ctx.moveTo(particle.x, particle.y)
          ctx.lineTo(other.x, other.y)
          ctx.stroke()
        }
      }
      
      // 鼠标连线
      if (distance < 150) {
        ctx.beginPath()
        ctx.strokeStyle = `rgba(99, 102, 241, ${0.15 * (1 - distance / 150)})`
        ctx.lineWidth = 0.8
        ctx.moveTo(particle.x, particle.y)
        ctx.lineTo(mouse.x, mouse.y)
        ctx.stroke()
      }
    })
    
    // 鼠标光晕
    if (mouse.x > 0 && mouse.y > 0) {
      const mouseGlow = ctx.createRadialGradient(mouse.x, mouse.y, 0, mouse.x, mouse.y, 80)
      mouseGlow.addColorStop(0, 'rgba(99, 102, 241, 0.08)')
      mouseGlow.addColorStop(1, 'rgba(99, 102, 241, 0)')
      ctx.beginPath()
      ctx.arc(mouse.x, mouse.y, 80, 0, Math.PI * 2)
      ctx.fillStyle = mouseGlow
      ctx.fill()
    }
    
    animationId = requestAnimationFrame(animate)
  }
  
  animate()
}

const handleMouseMove = (e) => {
  mouse.x = e.clientX
  mouse.y = e.clientY
}

onMounted(() => {
  initParticles()
  window.addEventListener('mousemove', handleMouseMove)
  
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
  window.removeEventListener('mousemove', handleMouseMove)
})
</script>

<style scoped lang="scss">
.particles-canvas {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  pointer-events: none;
}
</style>
