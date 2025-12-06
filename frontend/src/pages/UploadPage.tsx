import { useState } from 'react'
import {
  Upload,
  Button,
  Space,
  Alert,
  Progress,
  Card,
  Typography,
  List,
  Tag,
  Spin,
  Row,
  Col,
  Image,
} from 'antd'
import {
  InboxOutlined,
  CloudUploadOutlined,
  FileImageOutlined,
  DeleteOutlined,
  PlayCircleOutlined,
} from '@ant-design/icons'
import type { UploadFile, UploadProps } from 'antd'
import { recognizeBatch, RecognitionResult } from '../services/api'

const { Dragger } = Upload
const { Title, Text } = Typography

interface UploadPageProps {
  onRecognitionComplete: (results: RecognitionResult[]) => void
  isConfigured?: boolean
}

const UploadPage: React.FC<UploadPageProps> = ({
  onRecognitionComplete,
  isConfigured = false,
}) => {
  const [fileList, setFileList] = useState<UploadFile[]>([])
  const [isProcessing, setIsProcessing] = useState(false)
  const [progress, setProgress] = useState(0)
  const [currentFile, setCurrentFile] = useState('')
  const [previewImage, setPreviewImage] = useState<string>('')
  const [previewVisible, setPreviewVisible] = useState(false)
  const [currentBatch, setCurrentBatch] = useState(0)
  const [totalBatches, setTotalBatches] = useState(0)

  // 上传配置
  const uploadProps: UploadProps = {
    name: 'file',
    multiple: true,
    accept: 'image/*,.jpg,.jpeg,.png,.gif,.bmp,.webp',
    fileList,
    beforeUpload: (file) => {
      // 验证文件类型
      const isImage = file.type.startsWith('image/')
      if (!isImage) {
        return Upload.LIST_IGNORE
      }
      // 验证文件大小（10MB）
      const isLt10M = file.size / 1024 / 1024 < 10
      if (!isLt10M) {
        return Upload.LIST_IGNORE
      }
      return false // 阻止自动上传
    },
    onChange: ({ fileList: newFileList }) => {
      setFileList(newFileList)
    },
    onRemove: (file) => {
      const newFileList = fileList.filter((item) => item.uid !== file.uid)
      setFileList(newFileList)
    },
  }

  // 开始识别（自动分批处理，每批10张）
  const handleStartRecognition = async () => {
    if (fileList.length === 0) {
      return
    }

    setIsProcessing(true)
    setProgress(0)
    setCurrentFile('')

    // 保存文件列表用于识别
    const filesToProcess = fileList
      .map((f) => f.originFileObj)
      .filter((f): f is File => f !== undefined)

    // 立即清空文件列表（上传完成后不显示文件列表）
    setFileList([])

    // 分批处理：每批10张
    const BATCH_SIZE = 10
    const batches: File[][] = []
    for (let i = 0; i < filesToProcess.length; i += BATCH_SIZE) {
      batches.push(filesToProcess.slice(i, i + BATCH_SIZE))
    }

    setTotalBatches(batches.length)
    setCurrentBatch(0)

    const allResults: RecognitionResult[] = []

    try {
      // 依次处理每一批
      for (let batchIndex = 0; batchIndex < batches.length; batchIndex++) {
        const batch = batches[batchIndex]
        setCurrentBatch(batchIndex + 1)
        
        // 计算该批次的进度范围
        const batchStartProgress = (batchIndex / batches.length) * 100
        const batchEndProgress = ((batchIndex + 1) / batches.length) * 100
        const batchProgressRange = batchEndProgress - batchStartProgress
        
        // 设置初始进度
        setProgress(Math.floor(batchStartProgress))
        
        setCurrentFile(
          `正在处理第 ${batchIndex + 1}/${batches.length} 批，共 ${batch.length} 张图片...`
        )

        // 在等待API响应期间，模拟进度更新
        let progressInterval: NodeJS.Timeout | null = null
        let simulatedProgress = 0
        
        try {
          // 启动模拟进度更新（每2秒更新一次，最多到该批次的90%）
          progressInterval = setInterval(() => {
            simulatedProgress += 2
            if (simulatedProgress < 90) {
              const currentProgress = batchStartProgress + (batchProgressRange * simulatedProgress / 100)
              setProgress(Math.min(Math.floor(currentProgress), Math.floor(batchEndProgress * 0.9)))
            } else {
              // 达到90%后停止增长，等待实际完成
              if (progressInterval) {
                clearInterval(progressInterval)
                progressInterval = null
              }
            }
          }, 2000)

          // 调用批量识别API（每批独立超时10分钟）
          const result = await recognizeBatch(batch)
          
          // 停止模拟进度更新
          if (progressInterval) {
            clearInterval(progressInterval)
            progressInterval = null
          }
          
          // 合并结果
          allResults.push(...result.results)
          
          // 更新进度到该批次完成
          setProgress(Math.floor(batchEndProgress))
          
          console.log(
            `第 ${batchIndex + 1}/${batches.length} 批处理完成: ` +
            `成功 ${result.success_count}，失败 ${result.failed_count}`
          )
        } catch (error) {
          // 停止模拟进度更新
          if (progressInterval) {
            clearInterval(progressInterval)
            progressInterval = null
          }
          
          console.error(`第 ${batchIndex + 1} 批识别失败:`, error)
          
          // 即使某批失败，也继续处理下一批
          // 为失败的批次创建错误结果
          batch.forEach((file) => {
            allResults.push({
              success: false,
              filename: file.name,
              error: error instanceof Error ? error.message : '识别失败',
            })
          })
          
          // 更新进度到该批次完成（即使失败）
          setProgress(Math.floor(batchEndProgress))
        }
      }

      setProgress(100)
      setCurrentFile('所有批次处理完成！')

      // 传递所有结果到父组件
      onRecognitionComplete(allResults)
    } catch (error) {
      console.error('识别过程出错:', error)
      setCurrentFile('处理过程中出现错误')
    } finally {
      setIsProcessing(false)
      setCurrentFile('')
      setCurrentBatch(0)
      setTotalBatches(0)
    }
  }

  // 清空所有文件
  const handleClearAll = () => {
    setFileList([])
  }

  return (
    <div style={{ padding: '24px 0' }}>
      {/* 配置提示 */}
      {!isConfigured && (
        <Alert
          message="请先配置API"
          description="在使用凭证识别功能之前，请先在「API配置」页面配置OCR服务和大模型服务。"
          type="warning"
          showIcon
          style={{ marginBottom: 24 }}
        />
      )}

      {/* 上传区域 */}
      <Card
        style={{
          background: '#1a2027',
          border: '1px solid #2d363f',
          marginBottom: 24,
        }}
      >
        <Dragger
          {...uploadProps}
          disabled={isProcessing}
          style={{
            background: 'transparent',
            border: '2px dashed #2d363f',
            borderRadius: 12,
            padding: '48px 24px',
          }}
        >
          <p className="ant-upload-drag-icon">
            <InboxOutlined
              style={{ fontSize: 64, color: '#1a5f4a', opacity: 0.8 }}
            />
          </p>
          <Title level={4} style={{ color: '#e8eaed', marginBottom: 8 }}>
            点击或拖拽上传凭证图片
          </Title>
          <Text style={{ color: '#9aa0a6' }}>
            支持 JPG、PNG、GIF、BMP、WebP 格式，单个文件不超过 10MB
          </Text>
          <br />
          <Text style={{ color: '#9aa0a6' }}>
            可以一次上传多张凭证图片进行批量识别
          </Text>
        </Dragger>
      </Card>

      {/* 文件列表 */}
      {fileList.length > 0 && (
        <Card
          title={
            <Space>
              <FileImageOutlined />
              <span>待识别文件 ({fileList.length})</span>
            </Space>
          }
          extra={
            <Button
              type="text"
              danger
              icon={<DeleteOutlined />}
              onClick={handleClearAll}
              disabled={isProcessing}
            >
              清空
            </Button>
          }
          style={{
            background: '#1a2027',
            border: '1px solid #2d363f',
            marginBottom: 24,
          }}
        >
          <Row gutter={[16, 16]}>
            {fileList.map((file) => {
              const imageUrl = file.thumbUrl || (file.originFileObj ? URL.createObjectURL(file.originFileObj) : '')
              return (
                <Col key={file.uid} xs={12} sm={8} md={6} lg={4} xl={3}>
                  <Card
                    hoverable
                    style={{
                      background: '#242d36',
                      border: '1px solid #2d363f',
                      borderRadius: 8,
                      overflow: 'hidden',
                      cursor: 'pointer',
                    }}
                    bodyStyle={{ padding: 8 }}
                    cover={
                      <div 
                        style={{ position: 'relative', paddingTop: '75%', background: '#1a2027' }}
                        onClick={() => {
                          if (imageUrl) {
                            setPreviewImage(imageUrl)
                            setPreviewVisible(true)
                          }
                        }}
                      >
                        {imageUrl ? (
                          <Image
                            src={imageUrl}
                            alt={file.name}
                            style={{
                              position: 'absolute',
                              top: 0,
                              left: 0,
                              width: '100%',
                              height: '100%',
                              objectFit: 'cover',
                            }}
                            preview={{
                              src: imageUrl,
                              visible: previewVisible && previewImage === imageUrl,
                              onVisibleChange: (visible) => {
                                setPreviewVisible(visible)
                                if (!visible) {
                                  setPreviewImage('')
                                }
                              },
                            }}
                          />
                        ) : (
                          <div
                            style={{
                              position: 'absolute',
                              top: 0,
                              left: 0,
                              width: '100%',
                              height: '100%',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                            }}
                          >
                            <FileImageOutlined style={{ color: '#1a5f4a', fontSize: 32 }} />
                          </div>
                        )}
                      </div>
                    }
                    actions={[
                      <Button
                        type="text"
                        danger
                        icon={<DeleteOutlined />}
                        onClick={(e) => {
                          e.stopPropagation() // 阻止事件冒泡
                          const newFileList = fileList.filter((item) => item.uid !== file.uid)
                          setFileList(newFileList)
                        }}
                        disabled={isProcessing}
                        style={{ color: '#ea4335' }}
                      />,
                    ]}
                  >
                    <div style={{ textAlign: 'center' }}>
                      <Text
                        style={{
                          color: '#e8eaed',
                          fontSize: 12,
                          display: 'block',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap',
                        }}
                        title={file.name}
                      >
                        {file.name}
                      </Text>
                      <Tag color="default" style={{ marginTop: 4, fontSize: 11 }}>
                        {((file.size || 0) / 1024).toFixed(1)} KB
                      </Tag>
                    </div>
                  </Card>
                </Col>
              )
            })}
          </Row>
        </Card>
      )}

      {/* 处理进度 */}
      {isProcessing && (
        <Card
          style={{
            background: '#1a2027',
            border: '1px solid #2d363f',
            marginBottom: 24,
          }}
        >
          <Space direction="vertical" style={{ width: '100%' }}>
            <Space>
              <Spin />
              <Text style={{ color: '#e8eaed' }}>{currentFile}</Text>
            </Space>
            {totalBatches > 1 && (
              <Text style={{ color: '#9aa0a6', fontSize: 12 }}>
                批次进度: {currentBatch}/{totalBatches}（每批最多10张，每批独立超时10分钟）
              </Text>
            )}
            <Progress
              percent={progress}
              status="active"
              strokeColor={{
                '0%': '#1a5f4a',
                '100%': '#2d8b6a',
              }}
            />
          </Space>
        </Card>
      )}

      {/* 操作按钮 */}
      <Space size="large">
        <Button
          type="primary"
          size="large"
          icon={<PlayCircleOutlined />}
          onClick={handleStartRecognition}
          disabled={fileList.length === 0 || isProcessing || !isConfigured}
          loading={isProcessing}
          style={{
            height: 48,
            paddingLeft: 32,
            paddingRight: 32,
            fontSize: 16,
          }}
        >
          {isProcessing ? '识别中...' : '开始识别'}
        </Button>

        <Button
          size="large"
          icon={<CloudUploadOutlined />}
          onClick={() => {
            const input = document.querySelector(
              '.ant-upload input'
            ) as HTMLInputElement
            input?.click()
          }}
          disabled={isProcessing}
          style={{
            height: 48,
            paddingLeft: 32,
            paddingRight: 32,
          }}
        >
          选择文件
        </Button>
      </Space>
    </div>
  )
}

export default UploadPage

