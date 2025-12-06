# 李会计凭证识别系统

一个基于 OCR 和大模型的财务凭证自动识别系统，可以批量识别凭证图片并导出为标准 Excel 格式。

## 功能特点

- 📷 **凭证图片识别**：支持批量上传凭证图片，自动识别凭证内容
- 🤖 **AI智能提取**：使用大模型将OCR文本结构化为标准凭证格式
- 📊 **Excel导出**：按照标准模板导出凭证数据
- 🔧 **灵活配置**：支持多种OCR服务和大模型提供商
- 📋 **会计科目匹配**：内置常用会计科目表，自动匹配科目编码
- 📝 **完整日志**：详细的请求日志、OCR日志、LLM日志，方便调试和监控

## 技术栈

### 后端
- Python 3.11+
- FastAPI
- httpx (异步HTTP客户端)
- openpyxl (Excel处理)

### 前端
- React 18
- TypeScript
- Ant Design 5
- Vite

## 📖 文档

- [部署指南](DEPLOY.md) - 详细的部署说明
- [日志查看指南](LOG_GUIDE.md) - 如何查看和调试日志

## 快速开始

### 方式一：一键启动（推荐）⭐

**macOS / Linux:**
```bash
cd 财务凭证识别
./start.sh
```

**Windows:**
```bash
cd 财务凭证识别
start.bat
```

一键启动脚本会自动：
- ✅ 检查Python和Node.js环境
- ✅ 创建并激活虚拟环境
- ✅ 安装所有依赖
- ✅ 启动后端和前端服务
- ✅ 显示服务访问地址

启动后访问：
- 🌐 前端: http://localhost:3000
- 🔧 后端: http://localhost:8000
- 📚 API文档: http://localhost:8000/api/docs

### 方式二：Docker部署（生产环境）

```bash
# 克隆项目
git clone <repository-url>
cd 财务凭证识别

# 启动服务
docker-compose up -d

# 访问应用
# 前端: http://localhost
# API文档: http://localhost:8000/api/docs
```

### 方式三：手动启动（开发调试）

#### 后端

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

## 配置说明

### OCR服务配置

支持以下OCR服务提供商：

| 提供商 | 说明 | 需要Secret Key |
|--------|------|----------------|
| 百度OCR | 百度智能云OCR服务 | 是 |
| 阿里云OCR | 阿里云市场OCR服务 | 否 |
| 腾讯云OCR | 腾讯云OCR服务 | 是 |
| 自定义 | 任意兼容的OCR API | 否 |

### 大模型配置

支持以下大模型提供商：

| 提供商 | 默认模型 | API端点 |
|--------|----------|---------|
| DeepSeek | deepseek-chat | https://api.deepseek.com/chat/completions |
| 豆包（火山引擎） | doubao-pro-32k | https://ark.cn-beijing.volces.com/api/v3/chat/completions |
| Kimi（月之暗面） | moonshot-v1-8k | https://api.moonshot.cn/v1/chat/completions |
| OpenRouter | deepseek/deepseek-chat | https://openrouter.ai/api/v1/chat/completions |

## Excel输出格式

导出的Excel包含以下字段：

| 字段 | 说明 |
|------|------|
| 编制日期 | 凭证编制日期 |
| 凭证类型 | 记账凭证/收款凭证/付款凭证/转账凭证 |
| 凭证序号 | 凭证序号 |
| 凭证号 | 凭证编号 |
| 制单人 | 制单人姓名 |
| 附件张数 | 附件数量 |
| 会计年度 | 会计年度（如202511） |
| 科目编码 | 会计科目编码 |
| 科目名称 | 会计科目名称 |
| 凭证摘要 | 业务摘要 |
| 借贷方向 | 借/贷 |
| 金额 | 金额 |
| 币种 | 币种（默认人民币） |
| 汇率 | 汇率（默认1） |
| 原币金额 | 原币金额 |
| 数量 | 数量 |
| 单价 | 单价 |
| 结算方式名称 | 结算方式 |
| 结算日期 | 结算日期 |
| 结算票号 | 结算票号 |
| 业务日期 | 业务日期 |
| 员工编号 | 员工编号 |
| 员工姓名 | 员工姓名 |
| 往来单位编号 | 往来单位编号 |
| 往来单位名称 | 往来单位名称 |
| 货品编号 | 货品编号 |
| 货品名称 | 货品名称 |
| 部门名称 | 部门名称 |
| 项目名称 | 项目名称 |

## 内置会计科目

系统内置了常用会计科目表，包括：

- **资产类**（1xxx）：库存现金、银行存款、应收账款等
- **负债类**（2xxx）：短期借款、应付账款、应付职工薪酬等
- **所有者权益类**（4xxx）：实收资本、资本公积、盈余公积等
- **成本类**（5xxx）：生产成本、制造费用
- **损益类**（6xxx）：主营业务收入、管理费用、财务费用等

## API文档

启动后端服务后，访问以下地址查看API文档：

- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## 云部署建议

### 服务器要求

- CPU: 2核+
- 内存: 4GB+
- 存储: 20GB+
- 带宽: 5Mbps+

### 部署步骤

1. 准备一台云服务器（阿里云、腾讯云等）
2. 安装 Docker 和 Docker Compose
3. 上传项目代码
4. 执行 `docker-compose up -d`
5. 配置域名和SSL证书（可选）

### 安全建议

- 配置HTTPS
- 设置防火墙规则
- 定期更新系统和依赖
- API Key等敏感信息通过环境变量配置

## 许可证

MIT License

