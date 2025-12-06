import { useState, useEffect } from 'react'
import {
  Card,
  Form,
  Input,
  Select,
  Button,
  Space,
  Typography,
  Divider,
  message,
  Row,
  Col,
  Alert,
} from 'antd'
import {
  EyeOutlined,
  CloudOutlined,
  RobotOutlined,
  SaveOutlined,
  ReloadOutlined,
} from '@ant-design/icons'
import {
  configureOCR,
  configureLLM,
  getConfig,
  OCRConfig,
  LLMConfig,
} from '../services/api'

const { Title, Text } = Typography
const { Option } = Select

interface ConfigPageProps {
  onConfigComplete: () => void
}

// OCR提供商选项
const OCR_PROVIDERS = [
  { value: 'baidu', label: '百度OCR', needSecret: true },
  { value: 'aliyun', label: '阿里云OCR', needSecret: false },
  { value: 'tencent', label: '腾讯云OCR', needSecret: true },
  { value: 'generic', label: '自定义OCR', needSecret: false },
]

// LLM提供商选项
const LLM_PROVIDERS = [
  {
    value: 'deepseek',
    label: 'DeepSeek',
    defaultModel: 'deepseek-chat',
    defaultEndpoint: 'https://api.deepseek.com/chat/completions',
  },
  {
    value: 'doubao',
    label: '豆包（火山引擎）',
    defaultModel: 'doubao-pro-32k',
    defaultEndpoint: 'https://ark.cn-beijing.volces.com/api/v3/chat/completions',
  },
  {
    value: 'kimi',
    label: 'Kimi（月之暗面）',
    defaultModel: 'moonshot-v1-8k',
    defaultEndpoint: 'https://api.moonshot.cn/v1/chat/completions',
  },
  {
    value: 'openrouter',
    label: 'OpenRouter',
    defaultModel: 'deepseek/deepseek-chat',
    defaultEndpoint: 'https://openrouter.ai/api/v1/chat/completions',
  },
]

const ConfigPage: React.FC<ConfigPageProps> = ({ onConfigComplete }) => {
  const [ocrForm] = Form.useForm()
  const [llmForm] = Form.useForm()
  const [ocrLoading, setOcrLoading] = useState(false)
  const [llmLoading, setLlmLoading] = useState(false)
  const [showOcrSecret, setShowOcrSecret] = useState(false)
  const [showLlmKey, setShowLlmKey] = useState(false)

  // 从localStorage加载配置（只加载key）
  const loadConfigFromLocalStorage = () => {
    try {
      const savedOcrConfig = localStorage.getItem('ocr_config')
      const savedLlmConfig = localStorage.getItem('llm_config')
      
      if (savedOcrConfig) {
        const ocrConfig = JSON.parse(savedOcrConfig)
        ocrForm.setFieldsValue({
          api_key: ocrConfig.api_key || '',
          secret_key: ocrConfig.secret_key || '',
        })
      }
      
      if (savedLlmConfig) {
        const llmConfig = JSON.parse(savedLlmConfig)
        llmForm.setFieldsValue({
          api_key: llmConfig.api_key || '',
        })
      }
    } catch (error) {
      console.error('加载本地配置失败:', error)
    }
  }

  // 加载当前配置（只从localStorage加载key）
  useEffect(() => {
    loadConfigFromLocalStorage()
  }, [ocrForm, llmForm])

  // 保存OCR配置（只保存key，其他使用默认值）
  const handleSaveOCR = async () => {
    try {
      const values = await ocrForm.validateFields()
      setOcrLoading(true)

      // 只发送key，其他使用后端默认值
      const config: OCRConfig = {
        provider: 'baidu', // 使用默认值
        api_key: values.api_key,
        secret_key: values.secret_key,
        endpoint: null as any, // 使用默认值，不传此字段
      }

      // 只保存key到localStorage
      localStorage.setItem('ocr_config', JSON.stringify({
        api_key: config.api_key,
        secret_key: config.secret_key,
      }))

      await configureOCR(config)
      message.success('OCR配置保存成功（已缓存到本地）')
      onConfigComplete()
    } catch (error) {
      if (error instanceof Error) {
        message.error(error.message)
      }
    } finally {
      setOcrLoading(false)
    }
  }

  // 保存LLM配置（只保存key，其他使用默认值）
  const handleSaveLLM = async () => {
    try {
      const values = await llmForm.validateFields()
      setLlmLoading(true)

      // 只发送key，其他使用后端默认值
      const config: LLMConfig = {
        provider: 'deepseek', // 使用默认值
        api_key: values.api_key,
        model: null as any, // 使用默认值，不传此字段
        endpoint: null as any, // 使用默认值，不传此字段
      }

      // 只保存key到localStorage
      localStorage.setItem('llm_config', JSON.stringify({
        api_key: config.api_key,
      }))

      await configureLLM(config)
      message.success('大模型配置保存成功（已缓存到本地）')
      onConfigComplete()
    } catch (error) {
      if (error instanceof Error) {
        message.error(error.message)
      }
    } finally {
      setLlmLoading(false)
    }
  }

  // 百度OCR需要Secret Key
  const needSecretKey = true

  return (
    <div style={{ padding: '24px 0' }}>
      <Alert
        message="配置说明"
        description="请分别配置OCR服务和大模型服务。OCR用于识别凭证图片中的文字，大模型用于将识别的文字结构化为标准凭证格式。"
        type="info"
        showIcon
        style={{ marginBottom: 24 }}
      />

      <Row gutter={24}>
        {/* OCR配置 */}
        <Col xs={24} lg={12}>
          <Card
            title={
              <Space>
                <EyeOutlined style={{ color: '#1a5f4a' }} />
                <span>OCR服务配置</span>
              </Space>
            }
            style={{
              background: '#1a2027',
              border: '1px solid #2d363f',
              marginBottom: 24,
            }}
          >
            <Form
              form={ocrForm}
              layout="vertical"
            >
              <Alert
                message="使用百度OCR（默认）"
                description="其他配置项使用系统默认值，无需填写"
                type="info"
                showIcon
                style={{ marginBottom: 16 }}
              />

              <Form.Item
                name="api_key"
                label="API Key"
                rules={[{ required: true, message: '请输入API Key' }]}
              >
                <Input.Password
                  size="large"
                  placeholder="输入百度OCR的API Key"
                  visibilityToggle={{
                    visible: showOcrSecret,
                    onVisibleChange: setShowOcrSecret,
                  }}
                />
              </Form.Item>

              <Form.Item
                name="secret_key"
                label="Secret Key"
                rules={[{ required: true, message: '请输入Secret Key' }]}
              >
                <Input.Password
                  size="large"
                  placeholder="输入百度OCR的Secret Key"
                />
              </Form.Item>

              <Form.Item>
                <Button
                  type="primary"
                  size="large"
                  icon={<SaveOutlined />}
                  onClick={handleSaveOCR}
                  loading={ocrLoading}
                  block
                >
                  保存OCR配置
                </Button>
              </Form.Item>
            </Form>
          </Card>
        </Col>

        {/* LLM配置 */}
        <Col xs={24} lg={12}>
          <Card
            title={
              <Space>
                <RobotOutlined style={{ color: '#e8a838' }} />
                <span>大模型服务配置</span>
              </Space>
            }
            style={{
              background: '#1a2027',
              border: '1px solid #2d363f',
              marginBottom: 24,
            }}
          >
            <Form
              form={llmForm}
              layout="vertical"
            >
              <Alert
                message="使用DeepSeek（默认）"
                description="模型和端点使用系统默认值，无需填写"
                type="info"
                showIcon
                style={{ marginBottom: 16 }}
              />

              <Form.Item
                name="api_key"
                label="API Key"
                rules={[{ required: true, message: '请输入API Key' }]}
              >
                <Input.Password
                  size="large"
                  placeholder="输入DeepSeek的API Key"
                  visibilityToggle={{
                    visible: showLlmKey,
                    onVisibleChange: setShowLlmKey,
                  }}
                />
              </Form.Item>

              <Form.Item>
                <Button
                  type="primary"
                  size="large"
                  icon={<SaveOutlined />}
                  onClick={handleSaveLLM}
                  loading={llmLoading}
                  block
                >
                  保存大模型配置
                </Button>
              </Form.Item>
            </Form>
          </Card>
        </Col>
      </Row>

      {/* 使用说明 */}
      <Card
        title={
          <Space>
            <CloudOutlined />
            <span>API获取说明</span>
          </Space>
        }
        style={{
          background: '#1a2027',
          border: '1px solid #2d363f',
        }}
      >
        <Row gutter={24}>
          <Col xs={24} md={12}>
            <Title level={5} style={{ color: '#e8eaed' }}>
              OCR服务
            </Title>
            <ul style={{ color: '#9aa0a6', paddingLeft: 20 }}>
              <li>
                <Text strong style={{ color: '#e8eaed' }}>
                  百度OCR:
                </Text>{' '}
                访问{' '}
                <a
                  href="https://cloud.baidu.com/product/ocr"
                  target="_blank"
                  rel="noopener"
                  style={{ color: '#1a5f4a' }}
                >
                  百度智能云
                </a>{' '}
                创建应用获取API Key和Secret Key
              </li>
              <li>
                <Text strong style={{ color: '#e8eaed' }}>
                  阿里云OCR:
                </Text>{' '}
                访问{' '}
                <a
                  href="https://market.aliyun.com/products/57124001/cmapi00041992.html"
                  target="_blank"
                  rel="noopener"
                  style={{ color: '#1a5f4a' }}
                >
                  阿里云市场
                </a>{' '}
                购买OCR服务
              </li>
              <li>
                <Text strong style={{ color: '#e8eaed' }}>
                  腾讯云OCR:
                </Text>{' '}
                访问{' '}
                <a
                  href="https://cloud.tencent.com/product/ocr"
                  target="_blank"
                  rel="noopener"
                  style={{ color: '#1a5f4a' }}
                >
                  腾讯云
                </a>{' '}
                创建应用获取密钥
              </li>
            </ul>
          </Col>
          <Col xs={24} md={12}>
            <Title level={5} style={{ color: '#e8eaed' }}>
              大模型服务
            </Title>
            <ul style={{ color: '#9aa0a6', paddingLeft: 20 }}>
              <li>
                <Text strong style={{ color: '#e8eaed' }}>
                  DeepSeek:
                </Text>{' '}
                访问{' '}
                <a
                  href="https://platform.deepseek.com/"
                  target="_blank"
                  rel="noopener"
                  style={{ color: '#e8a838' }}
                >
                  DeepSeek开放平台
                </a>{' '}
                获取API Key
              </li>
              <li>
                <Text strong style={{ color: '#e8eaed' }}>
                  豆包:
                </Text>{' '}
                访问{' '}
                <a
                  href="https://www.volcengine.com/product/doubao"
                  target="_blank"
                  rel="noopener"
                  style={{ color: '#e8a838' }}
                >
                  火山引擎
                </a>{' '}
                创建应用获取API Key
              </li>
              <li>
                <Text strong style={{ color: '#e8eaed' }}>
                  Kimi:
                </Text>{' '}
                访问{' '}
                <a
                  href="https://platform.moonshot.cn/"
                  target="_blank"
                  rel="noopener"
                  style={{ color: '#e8a838' }}
                >
                  月之暗面
                </a>{' '}
                获取API Key
              </li>
              <li>
                <Text strong style={{ color: '#e8eaed' }}>
                  OpenRouter:
                </Text>{' '}
                访问{' '}
                <a
                  href="https://openrouter.ai/"
                  target="_blank"
                  rel="noopener"
                  style={{ color: '#e8a838' }}
                >
                  OpenRouter
                </a>{' '}
                获取API Key
              </li>
            </ul>
          </Col>
        </Row>
      </Card>
    </div>
  )
}

export default ConfigPage

