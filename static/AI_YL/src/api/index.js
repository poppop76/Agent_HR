import api, { aiAxios } from '@/utils/request'

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
 * 部门管理接口
 */
export const departmentApi = {
  // 获取部门列表
  getDepartmentList() {
    return api.get('/department/list')
  },
  // 添加部门
  addDepartment(data) {
    return api.post('/department/add', data)
  },
  // 更新部门
  updateDepartment(id, data) {
    return api.put(`/department/update/${id}`, data)
  },
  // 删除部门
  deleteDepartment(id) {
    return api.delete(`/department/delete/${id}`)
  }
}

/**
 * 岗位管理接口
 */
export const jobApi = {
  // 获取岗位列表
  getJobList(data) {
    return api.post('/job/list', data)
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
  },
  // 上架/下架岗位
  toggleJobStatus(id) {
    return api.put(`/job/status/${id}`)
  },
  // 获取岗位详情
  getJobDetail(id) {
    return api.get(`/job/detail/${id}`)
  }
}

/**
 * 简历管理接口
 */
export const resumeApi = {
  // 上传简历
  uploadResume(formData, config = {}) {
    return api.post('/resume/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      ...config
    })
  },
  // 获取简历列表
  getResumeList(params) {
    return api.get('/resume/list', { params })
  },
  // 获取候选人详情
  getCandidateByResumeId(resumeId) {
    return api.get(`/resume/candidate/${resumeId}`)
  },
  // 删除简历
  deleteResume(id) {
    return api.delete(`/resume/delete/${id}`)
  },
  // 获取简历详情
  getResumeDetail(id) {
    return api.get(`/resume/detail/${id}`)
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
export const aiApiClient = {
  // 简历智能解析（核心）
  parseResume(data) {
    return aiAxios.post('/ai/parse-resume', data)
  },
  // 生成面试问题
  generateInterviewQuestions(data) {
    return aiAxios.post('/ai/interview-questions', data)
  },
  // 简历智能摘要
  generateResumeSummary(data) {
    return aiAxios.post('/ai/resume-summary', data)
  },
  // 薪资建议
  getSalarySuggestion(data) {
    return aiAxios.post('/ai/salary-suggestion', data)
  },
  // 对话式查询
  chatQuery(data) {
    return aiAxios.post('/ai/chat-query', data)
  },
  // 智能报告生成
  generateReport(data) {
    return aiAxios.post('/ai/report-generate', data)
  },
  // 获取报告列表
  getReportList(params) {
    return aiAxios.get('/ai/report-list', { params })
  },
  // 获取报告详情
  getReportDetail(id) {
    return aiAxios.get(`/ai/report-detail/${id}`)
  },
  // 删除报告
  deleteReport(id) {
    return aiAxios.delete(`/ai/report-delete/${id}`)
  },
  // 简历智能对比
  compareCandidates(data) {
    return aiAxios.post('/ai/candidate-compare', data)
  },
  // 人才预测
  predictTalent(data) {
    return aiAxios.post('/ai/talent-predict', data)
  }
}

// 保持向后兼容
export const aiApi = aiApiClient

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
 * 岗位类别接口
 */
export const categoryApi = {
  // 获取类别列表
  getCategoryList() {
    return api.get('/category/list')
  },
  // 添加类别
  addCategory(data) {
    return api.post('/category/add', data)
  },
  // 更新类别
  updateCategory(id, data) {
    return api.put(`/category/update/${id}`, data)
  },
  // 删除类别
  deleteCategory(id) {
    return api.delete(`/category/delete/${id}`)
  },
  // 更新类别权重
  updateCategoryWeight(id, data) {
    return api.put(`/category/weight/${id}`, data)
  }
}
