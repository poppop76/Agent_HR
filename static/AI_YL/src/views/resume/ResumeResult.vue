<template>
  <div class="resume-result-page">
    <ParticlesBackground />
    
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">解析结果</h1>
        <p class="page-subtitle">智能解析后的简历信息</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" class="action-btn" @click="router.push(`/resumes/preview/${resumeId}`)">
          <el-icon><View /></el-icon>
          <span>查看原文件</span>
        </el-button>
        <el-button class="action-btn" @click="router.push('/resumes')">
          <el-icon><Back /></el-icon>
          <span>返回列表</span>
        </el-button>
      </div>
    </div>
    
    <div class="page-content">
      <div v-if="loading" class="loading-container glass-card">
        <el-icon class="loading-icon" :size="48"><Loading /></el-icon>
        <p>正在加载解析结果...</p>
      </div>
      
      <div v-else-if="candidate" class="result-container">
        <div class="resume-card glass-card">
          <!-- 基本信息头部 -->
          <div class="resume-header-section">
            <div class="avatar-section">
              <div class="avatar">{{ candidate.name?.charAt(0) || '?' }}</div>
              <div class="basic-info">
                <h2 v-if="candidate.name" class="candidate-name">{{ candidate.name }}</h2>
                <div class="info-tags">
                  <span v-if="candidate.targetPosition" class="tag highlight">{{ candidate.targetPosition }}</span>
                  <span v-if="candidate.gender && candidate.gender !== '未知'" class="tag">{{ candidate.gender }}</span>
                  <span v-if="candidate.age" class="tag">{{ candidate.age }}岁</span>
                  <span v-if="candidate.education" class="tag highlight">{{ candidate.education }}</span>
                  <span v-if="candidate.candidateType" class="tag highlight">{{ candidate.candidateType }}</span>
                  <span v-if="candidate.workYears && candidate.workYears > 0 && candidate.candidateType === '有工作经验'" class="tag">{{ candidate.workYears }}年经验</span>
                </div>
              </div>
            </div>
            <div class="contact-info">
              <div v-if="candidate.phone" class="contact-item">
                <el-icon><Phone /></el-icon>
                <span>{{ candidate.phone }}</span>
              </div>
              <div v-if="candidate.email" class="contact-item">
                <el-icon><Message /></el-icon>
                <span>{{ candidate.email }}</span>
              </div>
            </div>
          </div>

          <div class="resume-body">
            <!-- 专业标签 -->
            <div v-if="candidate.skills && candidate.skills.length > 0" class="section">
              <h3 class="section-title">
                <el-icon><Star /></el-icon>
                专业标签
              </h3>
              <div class="skills-container">
                <el-tag v-for="(skill, index) in candidate.skills" :key="index" class="skill-tag" effect="plain">
                  {{ skill }}
                </el-tag>
              </div>
            </div>

            <!-- 专业技能分类 -->
            <div v-if="hasProfessionalSkills" class="section">
              <h3 class="section-title">
                <el-icon><Tools /></el-icon>
                专业技能分类
              </h3>
              <div class="professional-skills-grid">
                <div v-if="candidate.professionalSkills.languages && candidate.professionalSkills.languages.length > 0" class="skill-category">
                  <h4 class="category-title">编程语言</h4>
                  <div class="category-tags">
                    <el-tag v-for="(item, index) in candidate.professionalSkills.languages" :key="index" size="small" effect="plain">
                      {{ item }}
                    </el-tag>
                  </div>
                </div>
                <div v-if="candidate.professionalSkills.frameworks && candidate.professionalSkills.frameworks.length > 0" class="skill-category">
                  <h4 class="category-title">框架/中间件</h4>
                  <div class="category-tags">
                    <el-tag v-for="(item, index) in candidate.professionalSkills.frameworks" :key="index" size="small" effect="plain" type="success">
                      {{ item }}
                    </el-tag>
                  </div>
                </div>
                <div v-if="candidate.professionalSkills.databases && candidate.professionalSkills.databases.length > 0" class="skill-category">
                  <h4 class="category-title">数据库</h4>
                  <div class="category-tags">
                    <el-tag v-for="(item, index) in candidate.professionalSkills.databases" :key="index" size="small" effect="plain" type="danger">
                      {{ item }}
                    </el-tag>
                  </div>
                </div>
                <div v-if="candidate.professionalSkills.tools && candidate.professionalSkills.tools.length > 0" class="skill-category">
                  <h4 class="category-title">工具/平台</h4>
                  <div class="category-tags">
                    <el-tag v-for="(item, index) in candidate.professionalSkills.tools" :key="index" size="small" effect="plain" type="warning">
                      {{ item }}
                    </el-tag>
                  </div>
                </div>
                <div v-if="candidate.professionalSkills.certificates && candidate.professionalSkills.certificates.length > 0" class="skill-category">
                  <h4 class="category-title">证书/资质</h4>
                  <div class="category-tags">
                    <el-tag v-for="(item, index) in candidate.professionalSkills.certificates" :key="index" size="small" effect="plain" type="info">
                      {{ item }}
                    </el-tag>
                  </div>
                </div>
              </div>
            </div>

            <!-- 自我评价 -->
            <div v-if="candidate.selfEvaluation" class="section">
              <h3 class="section-title">
                <el-icon><User /></el-icon>
                自我评价
              </h3>
              <div class="self-evaluation-box">
                <pre>{{ candidate.selfEvaluation }}</pre>
              </div>
            </div>

            <!-- 专业技能描述 -->
            <div v-if="candidate.skillDescription" class="section">
              <h3 class="section-title">
                <el-icon><Document /></el-icon>
                专业技能描述
              </h3>
              <div class="skill-description-box">
                <pre>{{ candidate.skillDescription }}</pre>
              </div>
            </div>

            <!-- 教育经历 -->
            <div v-if="candidate.educationHistory && candidate.educationHistory.length > 0" class="section">
              <h3 class="section-title">
                <el-icon><School /></el-icon>
                教育经历
              </h3>
              <div v-for="(edu, index) in candidate.educationHistory" :key="index" class="experience-item">
                <div class="exp-header">
                  <h4 v-if="edu.school" class="company-name">{{ edu.school }}</h4>
                  <span v-if="edu.start_date || edu.end_date" class="exp-date">{{ edu.start_date || '' }} ~ {{ edu.end_date || '' }}</span>
                </div>
                <p v-if="edu.major || edu.degree" class="position">{{ edu.major || '' }}{{ edu.major && edu.degree ? ' · ' : '' }}{{ edu.degree || '' }}</p>
              </div>
            </div>

            <!-- 工作经历 -->
            <div v-if="candidate.workExperience && candidate.workExperience.length > 0" class="section">
              <h3 class="section-title">
                <el-icon><Briefcase /></el-icon>
                工作经历
              </h3>
              <div v-for="(exp, index) in candidate.workExperience" :key="index" class="experience-item">
                <div class="exp-header">
                  <h4 v-if="exp.company" class="company-name">{{ exp.company }}</h4>
                  <span v-if="exp.start_date || exp.end_date" class="exp-date">{{ exp.start_date || '' }} ~ {{ exp.end_date || '至今' }}</span>
                </div>
                <p v-if="exp.position" class="position">{{ exp.position }}</p>
                <pre v-if="exp.description" class="description-text">{{ exp.description }}</pre>
              </div>
            </div>

            <!-- 实习经历 -->
            <div v-if="candidate.internshipExperience && candidate.internshipExperience.length > 0" class="section">
              <h3 class="section-title">
                <el-icon><Coffee /></el-icon>
                实习经历
              </h3>
              <div v-for="(exp, index) in candidate.internshipExperience" :key="index" class="experience-item internship">
                <div class="exp-header">
                  <h4 v-if="exp.company" class="company-name">{{ exp.company }}</h4>
                  <span v-if="exp.start_date || exp.end_date" class="exp-date">{{ exp.start_date || '' }} ~ {{ exp.end_date || '至今' }}</span>
                </div>
                <p v-if="exp.position" class="position">{{ exp.position }}</p>
                <pre v-if="exp.description" class="description-text">{{ exp.description }}</pre>
              </div>
            </div>

            <!-- 项目经历 -->
            <div v-if="candidate.projectExperience && candidate.projectExperience.length > 0" class="section">
              <h3 class="section-title">
                <el-icon><Tickets /></el-icon>
                项目经历
              </h3>
              <div v-for="(proj, index) in candidate.projectExperience" :key="index" class="project-item">
                <div class="project-header">
                  <div class="project-title-row">
                    <h4 v-if="proj.name" class="project-name">{{ proj.name }}</h4>
                    <span v-if="proj.start_date || proj.end_date" class="project-date">{{ proj.start_date || '' }} ~ {{ proj.end_date || '' }}</span>
                  </div>
                  <p v-if="proj.role" class="project-role">{{ proj.role }}</p>
                </div>

                <pre v-if="proj.description" class="project-desc">{{ proj.description }}</pre>

                <div v-if="proj.responsibilities && proj.responsibilities.length > 0" class="project-subsection">
                  <h5 class="subsection-title">负责模块</h5>
                  <div class="responsibility-tags">
                    <el-tag v-for="(item, i) in proj.responsibilities" :key="i" size="small" effect="plain" type="primary">
                      {{ item }}
                    </el-tag>
                  </div>
                </div>

                <div v-if="proj.tech_stack && proj.tech_stack.length > 0" class="project-subsection">
                  <h5 class="subsection-title">技术栈</h5>
                  <div class="tech-tags">
                    <el-tag v-for="(tech, i) in proj.tech_stack" :key="i" size="small" effect="plain" type="success">
                      {{ tech }}
                    </el-tag>
                  </div>
                </div>

                <div v-if="proj.highlights && proj.highlights.length > 0" class="project-subsection">
                  <h5 class="subsection-title">难点亮点</h5>
                  <div v-for="(highlight, i) in proj.highlights" :key="i" class="highlight-card">
                    <h6 v-if="highlight.title" class="highlight-title">{{ highlight.title }}</h6>
                    <pre v-if="highlight.content" class="highlight-content">{{ highlight.content }}</pre>
                  </div>
                </div>

                <div v-if="proj.achievements && proj.achievements.length > 0" class="project-subsection">
                  <h5 class="subsection-title">项目成果</h5>
                  <div class="achievements-list">
                    <div v-for="(achievement, i) in proj.achievements" :key="i" class="achievement-item">
                      <el-icon><Trophy /></el-icon>
                      <span>{{ achievement }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="empty-container glass-card">
        <el-icon :size="64"><Document /></el-icon>
        <p>暂无解析结果</p>
        <el-button type="primary" @click="router.push('/resumes')">返回列表</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { resumeApi } from '@/api'
import { ElMessage } from 'element-plus'
import { 
  View, Back, Loading, Document, Phone, Message, Star, 
  Briefcase, School, Tickets, Tools, Coffee, Trophy, User
} from '@element-plus/icons-vue'
import ParticlesBackground from '@/components/ParticlesBackground.vue'

const route = useRoute()
const router = useRouter()
const resumeId = computed(() => route.params.id)

const loading = ref(true)
const candidate = ref(null)

const hasProfessionalSkills = computed(() => {
  if (!candidate.value?.professionalSkills) return false
  const ps = candidate.value.professionalSkills
  return (
    (ps.languages && ps.languages.length > 0) ||
    (ps.frameworks && ps.frameworks.length > 0) ||
    (ps.databases && ps.databases.length > 0) ||
    (ps.tools && ps.tools.length > 0) ||
    (ps.certificates && ps.certificates.length > 0)
  )
})

const fetchCandidate = async () => {
  loading.value = true
  try {
    const res = await resumeApi.getCandidateByResumeId(resumeId.value)
    candidate.value = res.data
  } catch (error) {
    if (error.response?.status === 404) {
      ElMessage.warning('该简历尚未解析或解析失败')
    } else {
      ElMessage.error('获取解析结果失败')
    }
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchCandidate()
})
</script>

<style scoped lang="scss">
.resume-result-page {
  min-height: 100%;
  position: relative;
}

.page-header {
  position: relative;
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
  padding: 32px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  overflow: hidden;
  
  &::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(245, 158, 11, 0.15) 0%, transparent 70%);
    animation: headerGlow 8s ease-in-out infinite;
  }
}

@keyframes headerGlow {
  0%, 100% { transform: scale(1); opacity: 0.5; }
  50% { transform: scale(1.2); opacity: 0.8; }
}

.header-content {
  position: relative;
  z-index: 1;
  
  .page-title {
    font-size: 24px;
    font-weight: 700;
    color: #fff;
    margin: 0 0 8px 0;
  }
  
  .page-subtitle {
    font-size: 14px;
    color: rgba(255, 255, 255, 0.85);
    margin: 0;
  }
}

.header-actions {
  position: relative;
  z-index: 1;
  display: flex;
  gap: 12px;
  
  .action-btn {
    height: 44px;
    padding: 0 24px;
    font-size: 15px;
    font-weight: 600;
    border-radius: var(--radius-md);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    transition: var(--transition-base);
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 16px rgba(0, 0, 0, 0.03);
    }
  }
}

.page-content {
  padding: 24px;
  position: relative;
  z-index: 1;
}

.glass-card {
  background: var(--glass-bg);
  backdrop-filter: blur(12px);
  border-radius: var(--radius-lg);
  border: 1px solid var(--glass-border);
  box-shadow: var(--glass-shadow);
}

.loading-container, .empty-container {
  padding: 80px;
  text-align: center;
  
  .loading-icon {
    animation: rotate 1s linear infinite;
    color: var(--primary-color);
  }
  
  p {
    margin-top: 16px;
    color: var(--text-secondary);
  }
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.result-container {
  max-width: 900px;
  margin: 0 auto;
}

.resume-card {
  overflow: hidden;
}

.resume-header-section {
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
  padding: 32px;
  color: #fff;
}

.avatar-section {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 20px;
}

.avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  font-weight: 700;
  border: 3px solid rgba(255, 255, 255, 0.3);
}

.candidate-name {
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 8px 0;
}

.info-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  
  .tag {
    padding: 4px 12px;
    background: rgba(255, 255, 255, 0.15);
    border-radius: 20px;
    font-size: 13px;
    
    &.highlight {
      background: rgba(255, 255, 255, 0.3);
      font-weight: 600;
    }
  }
}

.contact-info {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
  
  .contact-item {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
  }
}

.resume-body {
  padding: 32px;
}

.section {
  margin-bottom: 32px;
  
  &:last-child {
    margin-bottom: 0;
  }
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 16px 0;
  padding-bottom: 12px;
  border-bottom: 2px solid var(--primary-color);
}

.skills-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  
  .skill-tag {
    margin: 0;
  }
}

.professional-skills-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.skill-category {
  padding: 16px;
  background: rgba(99, 102, 241, 0.05);
  border-radius: var(--radius-md);
  border: 1px solid rgba(99, 102, 241, 0.1);
  
  .category-title {
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary);
    margin: 0 0 12px 0;
  }
  
  .category-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }
}

.self-evaluation-box,
.skill-description-box {
  padding: 16px;
  background: rgba(99, 102, 241, 0.03);
  border-radius: var(--radius-md);
  border-left: 3px solid var(--primary-color);
  
  pre {
    margin: 0;
    font-family: inherit;
    font-size: 14px;
    line-height: 1.8;
    color: var(--text-secondary);
    white-space: pre-wrap;
    word-wrap: break-word;
  }
}

.experience-item {
  padding: 16px;
  background: rgba(99, 102, 241, 0.03);
  border-radius: var(--radius-md);
  margin-bottom: 12px;
  border-left: 3px solid var(--primary-color);
  
  &:last-child {
    margin-bottom: 0;
  }
}

.experience-item.internship {
  border-left-color: #10b981;
  background: rgba(16, 185, 129, 0.03);
}

.exp-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.company-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.exp-date {
  font-size: 13px;
  color: var(--text-tertiary);
}

.position {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0 0 8px 0;
}

.description-text {
  margin: 0;
  font-family: inherit;
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-secondary);
  white-space: pre-wrap;
  word-wrap: break-word;
}

.project-item {
  padding: 20px;
  background: rgba(99, 102, 241, 0.03);
  border-radius: var(--radius-md);
  margin-bottom: 16px;
  border-left: 3px solid var(--primary-color);
  
  &:last-child {
    margin-bottom: 0;
  }
}

.project-header {
  margin-bottom: 12px;
}

.project-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.project-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.project-date {
  font-size: 13px;
  color: var(--text-tertiary);
}

.project-role {
  font-size: 14px;
  color: var(--primary-color);
  font-weight: 500;
  margin: 0;
}

.project-desc {
  margin: 0 0 16px 0;
  font-family: inherit;
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-secondary);
  white-space: pre-wrap;
  word-wrap: break-word;
}

.project-subsection {
  margin-top: 16px;
}

.subsection-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 10px 0;
  padding-left: 8px;
  border-left: 3px solid var(--primary-color);
}

.responsibility-tags,
.tech-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.highlight-card {
  padding: 12px;
  background: rgba(99, 102, 241, 0.05);
  border-radius: var(--radius-sm);
  margin-bottom: 10px;
  
  &:last-child {
    margin-bottom: 0;
  }
}

.highlight-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--primary-color);
  margin: 0 0 8px 0;
}

.highlight-content {
  margin: 0;
  font-family: inherit;
  font-size: 13px;
  line-height: 1.8;
  color: var(--text-secondary);
  white-space: pre-wrap;
  word-wrap: break-word;
}

.achievements-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.achievement-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: var(--success-color);
  font-weight: 500;
  
  .el-icon {
    flex-shrink: 0;
  }
}

@media (max-width: 768px) {
  .professional-skills-grid {
    grid-template-columns: 1fr;
  }
  
  .page-header {
    flex-direction: column;
    gap: 16px;
    text-align: center;
  }
  
  .exp-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
}
</style>