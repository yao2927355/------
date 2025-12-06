import { useState, useMemo } from 'react'
import {
  Card,
  Table,
  Button,
  Space,
  Typography,
  Tag,
  Empty,
  Modal,
  Descriptions,
  Collapse,
  message,
  Popconfirm,
  InputNumber,
  Input,
  Select,
  Image,
} from 'antd'
import {
  DownloadOutlined,
  EyeOutlined,
  DeleteOutlined,
  FileExcelOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  EditOutlined,
  SaveOutlined,
} from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import { exportExcel, RecognitionResult, VoucherData } from '../services/api'

const { Title, Text, Paragraph } = Typography
const { Panel } = Collapse

interface ResultPageProps {
  results: RecognitionResult[]
}

const ResultPage: React.FC<ResultPageProps> = ({ results }) => {
  const [selectedResult, setSelectedResult] = useState<RecognitionResult | null>(
    null
  )
  const [detailVisible, setDetailVisible] = useState(false)
  const [editingKey, setEditingKey] = useState<string | null>(null)
  const [editedResults, setEditedResults] = useState<RecognitionResult[]>([])
  const [previewImage, setPreviewImage] = useState<string>('')
  const [previewVisible, setPreviewVisible] = useState(false)

  // 初始化编辑数据
  useMemo(() => {
    setEditedResults([...results])
  }, [results])

  // 获取图片预览URL
  const getImageUrl = (record: RecognitionResult) => {
    // 优先使用API返回的image_url
    if (record.image_url) {
      // 如果image_url是绝对路径，直接使用；否则加上API前缀
      return record.image_url.startsWith('http') 
        ? record.image_url 
        : `${import.meta.env.VITE_API_URL || '/api'}${record.image_url}`
    }
    // 降级方案：使用文件名构建URL（兼容旧数据）
    return `${import.meta.env.VITE_API_URL || '/api'}/uploads/${record.filename}`
  }

  // 查看详情
  const handleViewDetail = (record: RecognitionResult) => {
    setSelectedResult(record)
    setDetailVisible(true)
  }

  // 删除记录
  const handleDelete = (index: number) => {
    const newResults = [...editedResults]
    newResults.splice(index, 1)
    setEditedResults(newResults)
    message.success('已删除')
  }

  // 导出Excel
  const handleExportExcel = async () => {
    try {
      // 只导出成功识别的凭证
      const vouchers = editedResults
        .filter((r) => r.success && r.voucher_data)
        .map((r) => r.voucher_data as VoucherData)

      if (vouchers.length === 0) {
        message.warning('没有可导出的凭证数据')
        return
      }

      const blob = await exportExcel(vouchers)

      // 下载文件
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `凭证导出_${new Date().toISOString().slice(0, 10)}.xlsx`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)

      message.success('导出成功')
    } catch (error) {
      message.error('导出失败')
      console.error(error)
    }
  }

  // 表格列定义
  const columns: ColumnsType<RecognitionResult & { index: number }> = [
    {
      title: '序号',
      dataIndex: 'index',
      key: 'index',
      width: 60,
      render: (index: number) => index + 1,
    },
    {
      title: '文件名',
      dataIndex: 'filename',
      key: 'filename',
      width: 200,
      ellipsis: true,
    },
    {
      title: '图片缩略图',
      key: 'thumbnail',
      width: 120,
      render: (_, record) => {
        const imageUrl = getImageUrl(record)
        return (
          <Image
            src={imageUrl}
            alt={record.filename}
            width={80}
            height={60}
            style={{
              objectFit: 'cover',
              borderRadius: 4,
              cursor: 'pointer',
            }}
            preview={{
              src: imageUrl,
            }}
            fallback="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iODAiIGhlaWdodD0iNjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHJlY3Qgd2lkdGg9IjgwIiBoZWlnaHQ9IjYwIiBmaWxsPSIjMmQzNjNmIi8+PHRleHQgeD0iNDAiIHk9IjMwIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTIiIGZpbGw9IiM5YWEwYTYiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj7lm77niYfliqDovb3lpLHotKU8L3RleHQ+PC9zdmc+"
          />
        )
      },
    },
    {
      title: '状态',
      dataIndex: 'success',
      key: 'success',
      width: 100,
      render: (success: boolean) =>
        success ? (
          <Tag icon={<CheckCircleOutlined />} color="success">
            成功
          </Tag>
        ) : (
          <Tag icon={<CloseCircleOutlined />} color="error">
            失败
          </Tag>
        ),
    },
    {
      title: '凭证日期',
      key: 'voucher_date',
      width: 120,
      render: (_, record) => record.voucher_data?.voucher_date || '-',
    },
    {
      title: '凭证类型',
      key: 'voucher_type',
      width: 100,
      render: (_, record) => record.voucher_data?.voucher_type || '-',
    },
    {
      title: '分录数',
      key: 'entries_count',
      width: 80,
      render: (_, record) => record.voucher_data?.entries?.length || 0,
    },
    {
      title: '错误信息',
      dataIndex: 'error',
      key: 'error',
      width: 200,
      ellipsis: true,
      render: (error: string) =>
        error ? (
          <Text type="danger" ellipsis>
            {error}
          </Text>
        ) : (
          '-'
        ),
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      fixed: 'right',
      render: (_, record, index) => (
        <Space>
          <Button
            type="text"
            icon={<EyeOutlined />}
            onClick={() => handleViewDetail(record)}
          >
            详情
          </Button>
          <Popconfirm
            title="确定删除这条记录吗？"
            onConfirm={() => handleDelete(index)}
            okText="确定"
            cancelText="取消"
          >
            <Button type="text" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      ),
    },
  ]

  // 统计信息
  const stats = useMemo(() => {
    const total = editedResults.length
    const success = editedResults.filter((r) => r.success).length
    const failed = total - success
    const entries = editedResults.reduce(
      (acc, r) => acc + (r.voucher_data?.entries?.length || 0),
      0
    )
    return { total, success, failed, entries }
  }, [editedResults])

  // 空状态
  if (results.length === 0) {
    return (
      <div style={{ padding: '48px 0', textAlign: 'center' }}>
        <Empty
          image={Empty.PRESENTED_IMAGE_SIMPLE}
          description={
            <Text style={{ color: '#9aa0a6' }}>
              暂无识别结果，请先上传凭证图片进行识别
            </Text>
          }
        />
      </div>
    )
  }

  return (
    <div style={{ padding: '24px 0' }}>
      {/* 统计卡片 */}
      <Card
        style={{
          background: '#1a2027',
          border: '1px solid #2d363f',
          marginBottom: 24,
        }}
      >
        <Space size="large" wrap>
          <div>
            <Text style={{ color: '#9aa0a6' }}>总计</Text>
            <Title level={3} style={{ margin: 0, color: '#e8eaed' }}>
              {stats.total}
            </Title>
          </div>
          <div>
            <Text style={{ color: '#9aa0a6' }}>成功</Text>
            <Title level={3} style={{ margin: 0, color: '#34a853' }}>
              {stats.success}
            </Title>
          </div>
          <div>
            <Text style={{ color: '#9aa0a6' }}>失败</Text>
            <Title level={3} style={{ margin: 0, color: '#ea4335' }}>
              {stats.failed}
            </Title>
          </div>
          <div>
            <Text style={{ color: '#9aa0a6' }}>分录总数</Text>
            <Title level={3} style={{ margin: 0, color: '#e8a838' }}>
              {stats.entries}
            </Title>
          </div>
          <div style={{ flex: 1 }} />
          <Button
            type="primary"
            size="large"
            icon={<DownloadOutlined />}
            onClick={handleExportExcel}
            disabled={stats.success === 0}
          >
            导出Excel
          </Button>
        </Space>
      </Card>

      {/* 结果表格 */}
      <Card
        title={
          <Space>
            <FileExcelOutlined />
            <span>识别结果列表</span>
          </Space>
        }
        style={{
          background: '#1a2027',
          border: '1px solid #2d363f',
        }}
      >
        <Table
          columns={columns}
          dataSource={editedResults.map((r, i) => ({ ...r, index: i, key: i }))}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条`,
          }}
          scroll={{ x: 1200 }}
          size="middle"
        />
      </Card>

      {/* 详情弹窗 */}
      <Modal
        title="凭证详情"
        open={detailVisible}
        onCancel={() => setDetailVisible(false)}
        footer={null}
        width={900}
        style={{ top: 20 }}
      >
        {selectedResult && (
          <div>
            {/* 基本信息 */}
            <Descriptions
              title="凭证基本信息"
              bordered
              size="small"
              column={3}
            >
              <Descriptions.Item label="文件名">
                {selectedResult.filename}
              </Descriptions.Item>
              <Descriptions.Item label="识别状态">
                {selectedResult.success ? (
                  <Tag color="success">成功</Tag>
                ) : (
                  <Tag color="error">失败</Tag>
                )}
              </Descriptions.Item>
              <Descriptions.Item label="凭证日期">
                {selectedResult.voucher_data?.voucher_date || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="凭证类型">
                {selectedResult.voucher_data?.voucher_type || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="凭证号">
                {selectedResult.voucher_data?.voucher_no || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="制单人">
                {selectedResult.voucher_data?.preparer || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="附件张数">
                {selectedResult.voucher_data?.attachment_count || 0}
              </Descriptions.Item>
              <Descriptions.Item label="会计年度">
                {selectedResult.voucher_data?.fiscal_year || '-'}
              </Descriptions.Item>
            </Descriptions>

            {/* 分录明细 */}
            {selectedResult.voucher_data?.entries &&
              selectedResult.voucher_data.entries.length > 0 && (
                <div style={{ marginTop: 24 }}>
                  <Title level={5}>分录明细</Title>
                  <Table
                    dataSource={selectedResult.voucher_data.entries.map(
                      (e, i) => ({ ...e, key: i })
                    )}
                    columns={[
                      {
                        title: '科目编码',
                        dataIndex: 'subject_code',
                        width: 100,
                      },
                      {
                        title: '科目名称',
                        dataIndex: 'subject_name',
                        width: 120,
                      },
                      { title: '摘要', dataIndex: 'summary', width: 150 },
                      {
                        title: '借贷方向',
                        dataIndex: 'direction',
                        width: 80,
                        render: (d: string) => (
                          <Tag color={d === '借' ? 'blue' : 'green'}>{d}</Tag>
                        ),
                      },
                      {
                        title: '金额',
                        dataIndex: 'amount',
                        width: 100,
                        align: 'right',
                        render: (a: number) =>
                          typeof a === 'number' ? a.toLocaleString() : a,
                      },
                      { title: '币种', dataIndex: 'currency', width: 80 },
                    ]}
                    pagination={false}
                    size="small"
                    scroll={{ x: 600 }}
                  />
                </div>
              )}

            {/* OCR原文 */}
            {selectedResult.ocr_text && (
              <Collapse style={{ marginTop: 24 }}>
                <Panel header="OCR识别原文" key="1">
                  <Paragraph
                    style={{
                      background: '#0f1419',
                      padding: 16,
                      borderRadius: 8,
                      whiteSpace: 'pre-wrap',
                      maxHeight: 300,
                      overflow: 'auto',
                    }}
                  >
                    {selectedResult.ocr_text}
                  </Paragraph>
                </Panel>
              </Collapse>
            )}

            {/* 错误信息 */}
            {selectedResult.error && (
              <div style={{ marginTop: 24 }}>
                <Title level={5} type="danger">
                  错误信息
                </Title>
                <Paragraph type="danger">{selectedResult.error}</Paragraph>
              </div>
            )}
          </div>
        )}
      </Modal>
    </div>
  )
}

export default ResultPage

