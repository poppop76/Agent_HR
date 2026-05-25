<template>
  <div id="app">
    <router-view v-slot="{ Component }">
      <transition name="fade-slide" mode="out-in">
        <keep-alive :include="cachedViews">
          <component :is="Component" />
        </keep-alive>
      </transition>
    </router-view>
    <LoadingOverlay />
    <MouseParticles />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import LoadingOverlay from '@/components/common/LoadingOverlay.vue'
import MouseParticles from '@/components/common/MouseParticles.vue'

const cachedViews = ref([
  'JobList',
  'ResumeList',
  'CandidateList',
  'StatisticsReport'
])
</script>
