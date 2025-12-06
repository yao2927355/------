import { useState, useEffect } from 'react'
import {
  Layout,
  Typography,
  Tabs,
  Space,
  Tag,
  message,
  Input,
  Button,
  Card,
  Form,
} from 'antd'
import {
  CloudUploadOutlined,
  SettingOutlined,
  FileExcelOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  LockOutlined,
} from '@ant-design/icons'
import UploadPage from './pages/UploadPage'
import ConfigPage from './pages/ConfigPage'
import ResultPage from './pages/ResultPage'
import { healthCheck, HealthStatus } from './services/api'
import type { RecognitionResult } from './services/api'

const { Header, Content } = Layout
const { Title, Text } = Typography

// 密码常量
const APP_PASSWORD = 'li123456'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [activeTab, setActiveTab] = useState('upload')
  const [healthStatus, setHealthStatus] = useState<HealthStatus | null>(null)
  const [recognitionResults, setRecognitionResults] = useState<RecognitionResult[]>([])
  const [passwordForm] = Form.useForm()

  // 检查是否已认证（从localStorage）
  useEffect(() => {
    const authStatus = localStorage.getItem('app_authenticated')
    if (authStatus === 'true') {
      setIsAuthenticated(true)
    }
  }, [])

  // 处理密码验证
  const handlePasswordSubmit = (values: { password: string }) => {
    if (values.password === APP_PASSWORD) {
      setIsAuthenticated(true)
      localStorage.setItem('app_authenticated', 'true')
      message.success('验证成功')
    } else {
      message.error('密码错误，请重新输入')
      passwordForm.resetFields()
    }
  }

  // 检查服务状态
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const status = await healthCheck()
        setHealthStatus(status)
      } catch {
        message.error('无法连接到后端服务')
      }
    }
    checkHealth()
    // 每30秒检查一次
    const interval = setInterval(checkHealth, 30000)
    return () => clearInterval(interval)
  }, [])

  // 处理识别完成
  const handleRecognitionComplete = (results: RecognitionResult[]) => {
    setRecognitionResults(results)
    setActiveTab('result')
  }

  // 处理配置完成
  const handleConfigComplete = async () => {
    try {
      const status = await healthCheck()
      setHealthStatus(status)
      message.success('配置已更新')
    } catch {
      message.error('更新状态失败')
    }
  }

  // 如果未认证，显示密码输入页面
  if (!isAuthenticated) {
    return (
      <Layout style={{ minHeight: '100vh', background: '#0f1419' }}>
        <Content
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '24px',
          }}
        >
          <Card
            style={{
              width: '100%',
              maxWidth: 400,
              background: '#1a2027',
              border: '1px solid #2d363f',
            }}
          >
            <Space direction="vertical" size="large" style={{ width: '100%' }}>
              <div style={{ textAlign: 'center' }}>
                <LockOutlined
                  style={{
                    fontSize: 48,
                    color: '#1a5f4a',
                    marginBottom: 16,
                  }}
                />
                <Title level={3} style={{ color: '#e8eaed', marginBottom: 8 }}>
                  李会计凭证识别系统
                </Title>
                <Text style={{ color: '#9aa0a6' }}>请输入密码以继续</Text>
              </div>

              <Form
                form={passwordForm}
                onFinish={handlePasswordSubmit}
                layout="vertical"
                size="large"
              >
                <Form.Item
                  name="password"
                  rules={[{ required: true, message: '请输入密码' }]}
                >
                  <Input.Password
                    placeholder="请输入密码"
                    prefix={<LockOutlined />}
                    autoFocus
                    onPressEnter={() => passwordForm.submit()}
                  />
                </Form.Item>

                <Form.Item>
                  <Button
                    type="primary"
                    htmlType="submit"
                    block
                    style={{
                      background: '#1a5f4a',
                      borderColor: '#1a5f4a',
                      height: 48,
                    }}
                  >
                    验证密码
                  </Button>
                </Form.Item>
              </Form>
            </Space>
          </Card>
        </Content>
      </Layout>
    )
  }

  const tabItems = [
    {
      key: 'upload',
      label: (
        <span>
          <CloudUploadOutlined />
          上传凭证
        </span>
      ),
      children: (
        <UploadPage
          onRecognitionComplete={handleRecognitionComplete}
          isConfigured={healthStatus?.ocr_configured && healthStatus?.llm_configured}
        />
      ),
    },
    {
      key: 'result',
      label: (
        <span>
          <FileExcelOutlined />
          识别结果
          {recognitionResults.length > 0 && (
            <Tag color="green" style={{ marginLeft: 8 }}>
              {recognitionResults.length}
            </Tag>
          )}
        </span>
      ),
      children: <ResultPage results={recognitionResults} />,
    },
    {
      key: 'config',
      label: (
        <span>
          <SettingOutlined />
          API配置
        </span>
      ),
      children: <ConfigPage onConfigComplete={handleConfigComplete} />,
    },
  ]

  return (
    <Layout style={{ minHeight: '100vh' }}>
      {/* 头部 */}
      <Header
        style={{
          background: 'linear-gradient(135deg, #1a5f4a 0%, #134436 100%)',
          padding: '0 32px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          boxShadow: '0 4px 20px rgba(0, 0, 0, 0.3)',
        }}
      >
        <Space align="center">
          <div
            style={{
              width: 40,
              height: 40,
              borderRadius: 8,
              background: 'rgba(255, 255, 255, 0.15)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginRight: 12,
            }}
          >
            <FileExcelOutlined style={{ fontSize: 24, color: '#e8a838' }} />
          </div>
          <Title
            level={4}
            style={{
              margin: 0,
              color: '#fff',
              fontWeight: 600,
              letterSpacing: 1,
            }}
          >
            李会计凭证识别系统
          </Title>
        </Space>

        {/* 状态指示器 */}
        <Space size="large">
          <Space>
            <Text style={{ color: 'rgba(255,255,255,0.7)' }}>OCR服务:</Text>
            {healthStatus?.ocr_configured ? (
              <Tag icon={<CheckCircleOutlined />} color="success">
                已配置
              </Tag>
            ) : (
              <Tag icon={<CloseCircleOutlined />} color="error">
                未配置
              </Tag>
            )}
          </Space>
          <Space>
            <Text style={{ color: 'rgba(255,255,255,0.7)' }}>大模型服务:</Text>
            {healthStatus?.llm_configured ? (
              <Tag icon={<CheckCircleOutlined />} color="success">
                已配置
              </Tag>
            ) : (
              <Tag icon={<CloseCircleOutlined />} color="error">
                未配置
              </Tag>
            )}
          </Space>
        </Space>
      </Header>

      {/* 主内容区 */}
      <Content
        style={{
          padding: '24px 32px',
          background: '#0f1419',
          minHeight: 'calc(100vh - 64px)',
        }}
      >
        <Tabs
          activeKey={activeTab}
          onChange={setActiveTab}
          items={tabItems}
          size="large"
          style={{
            background: '#1a2027',
            borderRadius: 12,
            padding: '16px 24px',
            boxShadow: '0 4px 20px rgba(0, 0, 0, 0.2)',
          }}
        />
      </Content>
    </Layout>
  )
}

export default App

