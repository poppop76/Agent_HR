import api from '@/utils/request'

/**
 * 认证相关接口
 */
export const authApi = {
  // 用户登录
  login(data) {
    return api.post('/auth/login', data)
  }
}

/**
 * 用户管理接口（仅管理员）
 */
export const userApi = {
  // 获取用户列表
  getUserList() {
    return api.get('/user/list')
  },
  // 添加用户
  addUser(data) {
    return api.post('/user/add', data)
  },
  // 更新用户
  updateUser(id, data) {
    return api.put(`/user/update/${id}`, data)
  },
  // 删除用户
  deleteUser(id) {
    return api.delete(`/user/delete/${id}`)
  }
}

/**
 * 岗位管理接口
 */
export const jobApi = {
  // 获取岗位列表
  getJobList(params) {
    return api.get('/job/list', { params })
  },
  // 新增岗位
  addJob(data) {
    return api.post('/job/add', data)
  },
  // 编辑岗位
  updateJob(id, data) {
    return api.put(`/job/update/${id}`, data)
  },
  // 删除岗位
  deleteJob(id) {
    return api.delete(`/job/delete/${id}`)
  }
}

/**
 * 简历管理接口
 */
export const resumeApi = {
  // 上传简历
  uploadResume(formData) {
    return api.post('/resume/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  // 获取简历列表
  getResumeList(params) {
    return api.get('/resume/list', { params })
  },
  // 删除简历
  deleteResume(id) {
    return api.delete(`/resume/delete/${id}`)
  }
}

/**
 * 人岗匹配接口
 */
export const matchingApi = {
  // 执行人岗匹配
  performMatching(data) {
    return api.post('/matching/run', data)
  },
  // 获取匹配结果列表
  getMatchingResultList(params) {
    return api.get('/matching/resultList', { params })
  },
  // 获取匹配报告
  getMatchingReport(id) {
    return api.get(`/matching/report/${id}`)
  }
}

/**
 * AI 智能模块接口（Agent 核心能力）
 */
export const aiApi = {
  // 简历智能解析（核心）
  parseResume(data) {
    return api.post('/ai/parse-resume', data)
  },
  // 生成面试问题
  generateInterviewQuestions(data) {
    return api.post('/ai/interview-questions', data)
  },
  // 简历智能摘要
  generateResumeSummary(data) {
    return api.post('/ai/resume-summary', data)
  },
  // 薪资建议
  getSalarySuggestion(data) {
    return api.post('/ai/salary-suggestion', data)
  },
  // 对话式查询
  chatQuery(data) {
    return api.post('/ai/chat-query', data)
  },
  // 智能报告生成
  generateReport(data) {
    return api.post('/ai/report-generate', data)
  },
  // 获取报告列表
  getReportList(params) {
    return api.get('/ai/report-list', { params })
  },
  // 获取报告详情
  getReportDetail(id) {
    return api.get(`/ai/report-detail/${id}`)
  },
  // 删除报告
  deleteReport(id) {
    return api.delete(`/ai/report-delete/${id}`)
  },
  // 简历智能对比
  compareCandidates(data) {
    return api.post('/ai/candidate-compare', data)
  },
  // 人才预测
  predictTalent(data) {
    return api.post('/ai/talent-predict', data)
  }
}

/**
 * 数据统计接口（简化版）
 */
export const statisticsApi = {
  // 获取概览统计
  getOverview(params) {
    return api.get('/statistics/overview', { params })
  }
}

/**
 * 权重配置接口（仅管理员）
 */
export const weightApi = {
  // 获取所有权重配置
  getWeightList() {
    return api.get('/weight/list')
  },
  // 更新权重配置
  updateWeight(id, data) {
    return api.put(`/weight/update/${id}`, data)
  }
}
