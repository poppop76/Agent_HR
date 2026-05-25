import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  const sidebarCollapsed = ref(false)
  const mousePosition = ref({ x: 0, y: 0 })
  const clickEffects = ref([])

  function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }

  function updateMousePosition(x, y) {
    mousePosition.value = { x, y }
  }

  function addClickEffect(x, y) {
    const id = Date.now()
    clickEffects.value.push({ id, x, y })
    setTimeout(() => {
      clickEffects.value = clickEffects.value.filter(e => e.id !== id)
    }, 600)
  }

  return {
    sidebarCollapsed,
    mousePosition,
    clickEffects,
    toggleSidebar,
    updateMousePosition,
    addClickEffect
  }
})
