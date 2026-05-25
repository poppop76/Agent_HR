import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/Login.vue'),
    meta: { title: '登录', requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    redirect: '/dashboard',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '首页', icon: 'HomeFilled' }
      },
      {
        path: 'jobs',
        name: 'JobList',
        component: () => import('@/views/job/JobList.vue'),
        meta: { title: '岗位管理', icon: 'Briefcase' }
      },
      {
        path: 'jobs/add',
        name: 'JobAdd',
        component: () => import('@/views/job/JobForm.vue'),
        meta: { title: '新增岗位', icon: 'Plus' }
      },
      {
        path: 'jobs/edit/:id',
        name: 'JobEdit',
        component: () => import('@/views/job/JobForm.vue'),
        meta: { title: '编辑岗位', icon: 'Edit' }
      },
      {
        path: 'jobs/detail/:id',
        name: 'JobDetail',
        component: () => import('@/views/job/JobDetail.vue'),
        meta: { title: '岗位详情', icon: 'View' }
      },
      {
        path: 'resumes/upload',
        name: 'ResumeUpload',
        component: () => import('@/views/resume/ResumeUpload.vue'),
        meta: { title: '简历上传', icon: 'Upload' }
      },
      {
        path: 'resumes',
        name: 'ResumeList',
        component: () => import('@/views/resume/ResumeList.vue'),
        meta: { title: '简历管理', icon: 'Document' }
      },
      {
        path: 'matching',
        name: 'Matching',
        component: () => import('@/views/matching/Matching.vue'),
        meta: { title: '人岗匹配', icon: 'Connection' }
      },
      {
        path: 'matching/report/:id',
        name: 'MatchingReport',
        component: () => import('@/views/matching/MatchingReport.vue'),
        meta: { title: '匹配报告', icon: 'Tickets' }
      },
      {
        path: 'ai-center',
        name: 'AICenter',
        component: () => import('@/views/ai/AICenter.vue'),
        meta: { title: 'AI智能中心', icon: 'Cpu' }
      },
      {
        path: 'ai-center/interview',
        name: 'AIInterview',
        component: () => import('@/views/ai/AIInterview.vue'),
        meta: { title: 'AI面试助手', icon: 'ChatDotRound' }
      },
      {
        path: 'ai-center/chat',
        name: 'AIChat',
        component: () => import('@/views/ai/AIChat.vue'),
        meta: { title: 'AI对话查询', icon: 'ChatLineRound' }
      },
      {
        path: 'ai-center/report',
        name: 'AIReport',
        component: () => import('@/views/ai/AIReport.vue'),
        meta: { title: '智能报告', icon: 'Notebook' }
      },
      {
        path: 'ai-center/summary',
        name: 'AISummary',
        component: () => import('@/views/ai/AISummary.vue'),
        meta: { title: '简历摘要', icon: 'Document' }
      },
      {
        path: 'ai-center/salary',
        name: 'AISalary',
        component: () => import('@/views/ai/AISalary.vue'),
        meta: { title: '薪资建议', icon: 'Money' }
      },
      {
        path: 'ai-center/predict',
        name: 'AIPredict',
        component: () => import('@/views/ai/AIPredict.vue'),
        meta: { title: '人才预测', icon: 'TrendCharts' }
      },
      {
        path: 'system/weight-config',
        name: 'WeightConfig',
        component: () => import('@/views/system/WeightConfig.vue'),
        meta: { title: '权重配置', icon: 'Setting', requiresAdmin: true }
      },
      {
        path: 'system/user-management',
        name: 'UserManagement',
        component: () => import('@/views/system/UserManagement.vue'),
        meta: { title: '用户管理', icon: 'User', requiresAdmin: true }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0, behavior: 'smooth' }
    }
  }
})

router.beforeEach((to, from, next) => {
  document.title = `${to.meta.title || ''} - HR智能简历解析系统`
  
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth !== false && !authStore.isLoggedIn) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else if (to.meta.requiresAdmin && !authStore.isAdmin) {
    next({ name: 'Dashboard' })
  } else {
    next()
  }
})

export default router
