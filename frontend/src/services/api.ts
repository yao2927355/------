import axios, { AxiosInstance } from 'axios'

// API基础URL
// 支持环境变量配置，方便部署到Vercel等平台
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

// 创建axios实例
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 600000, // 10分钟超时（批量识别OCR+LLM可能需要较长时间）
})

// 响应拦截器
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const message = error.response?.data?.detail || error.message || '请求失败'
    return Promise.reject(new Error(message))
  }
)

// ============ 类型定义 ============

export interface OCRConfig {
  provider: string
  api_key: string
  secret_key?: string
  endpoint?: string
}

export interface LLMConfig {
  provider: string
  api_key: string
  model?: string
  endpoint?: string
}

export interface VoucherEntry {
  subject_code: string
  subject_name: string
  summary: string
  direction: string
  amount: number | string
  currency: string
  exchange_rate: number
  original_amount: number | string
  quantity?: number | string
  unit_price?: number | string
  settlement_method: string
  settlement_date: string
  settlement_no: string
  business_date: string
  employee_no: string
  employee_name: string
  partner_no: string
  partner_name: string
  product_no: string
  product_name: string
  department: string
  project: string
}

export interface VoucherData {
  voucher_date: string
  voucher_type: string
  voucher_no: string
  preparer: string
  attachment_count: number
  fiscal_year: string
  entries: VoucherEntry[]
}

export interface RecognitionResult {
  success: boolean
  filename: string
  image_url?: string  // 图片URL，用于显示缩略图
  ocr_text?: string
  voucher_data?: VoucherData
  error?: string
}

export interface BatchRecognitionResult {
  total: number
  success_count: number
  failed_count: number
  results: RecognitionResult[]
}

export interface SubjectInfo {
  code: string
  name: string
  category: string
}

export interface ConfigStatus {
  ocr?: {
    provider: string
    api_key: string
  }
  llm?: {
    provider: string
    api_key: string
    model?: string
    endpoint?: string
  }
}

export interface HealthStatus {
  status: string
  ocr_configured: boolean
  llm_configured: boolean
}

// ============ API函数 ============

// 配置OCR
export const configureOCR = async (config: OCRConfig): Promise<{ message: string; provider: string }> => {
  return api.post('/config/ocr', config)
}

// 配置LLM
export const configureLLM = async (config: LLMConfig): Promise<{ message: string; provider: string; model: string; endpoint: string }> => {
  return api.post('/config/llm', config)
}

// 获取当前配置
export const getConfig = async (): Promise<ConfigStatus> => {
  return api.get('/config')
}

// 识别单张凭证
export const recognizeSingle = async (file: File): Promise<RecognitionResult> => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/recognize/single', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

// 批量识别凭证
export const recognizeBatch = async (files: File[]): Promise<BatchRecognitionResult> => {
  const formData = new FormData()
  files.forEach((file) => {
    formData.append('files', file)
  })
  return api.post('/recognize/batch', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

// 导出Excel
export const exportExcel = async (vouchers: VoucherData[]): Promise<Blob> => {
  const response = await axios.post(`${API_BASE_URL}/export/excel`, vouchers, {
    responseType: 'blob',
  })
  return response.data
}

// 下载模板
export const downloadTemplate = async (): Promise<Blob> => {
  const response = await axios.get(`${API_BASE_URL}/export/template`, {
    responseType: 'blob',
  })
  return response.data
}

// 获取会计科目列表
export const getSubjects = async (): Promise<SubjectInfo[]> => {
  return api.get('/subjects')
}

// 健康检查
export const healthCheck = async (): Promise<HealthStatus> => {
  return api.get('/health')
}

export default api

