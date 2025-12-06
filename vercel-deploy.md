# Vercel 部署指南

## 📋 部署方案

### 方案一：前端Vercel + 后端其他平台（推荐）⭐

**优点：**
- ✅ 前端部署简单，全球CDN加速
- ✅ 后端不受超时限制
- ✅ 成本低（Vercel免费额度足够）

**后端推荐平台：**
- **Railway** (railway.app) - 简单易用，有免费额度
- **Render** (render.com) - 免费计划可用
- **Fly.io** (fly.io) - 全球部署
- **腾讯云/阿里云** - 国内访问快

### 方案二：全栈Vercel（需改造）

**限制：**
- ⚠️ Serverless Functions 超时限制（Hobby: 10秒，Pro: 60秒）
- ⚠️ OCR + LLM 处理可能需要更长时间
- ⚠️ 需要将后端改为 Serverless Functions

## 🚀 方案一：前端部署到Vercel

### 步骤1：准备前端代码

前端代码已经准备好，只需要配置API地址。

### 步骤2：修改API地址

在 `frontend/src/services/api.ts` 中，将API地址改为你的后端地址：

```typescript
// 开发环境
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

// 或者直接设置
const API_BASE_URL = 'https://your-backend.railway.app/api'
```

### 步骤3：创建环境变量

在 Vercel 项目设置中添加环境变量：
- `VITE_API_URL`: 你的后端API地址（如：https://your-backend.railway.app）

### 步骤4：部署到Vercel

**方式A：通过Vercel CLI**
```bash
cd frontend
npm i -g vercel
vercel login
vercel
```

**方式B：通过GitHub集成**
1. 将代码推送到GitHub
2. 在 Vercel 官网导入项目
3. 选择 `frontend` 目录
4. 配置环境变量
5. 点击部署

### 步骤5：配置vercel.json

更新 `frontend/vercel.json` 中的后端地址：

```json
{
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "https://your-backend-url.com/api/$1"
    }
  ]
}
```

## 🔧 方案二：后端部署到Railway（推荐）

### 为什么选择Railway？

- ✅ 免费额度：$5/月
- ✅ 支持Docker部署
- ✅ 自动HTTPS
- ✅ 简单易用

### 部署步骤

1. **注册Railway账号**
   - 访问 https://railway.app
   - 使用GitHub登录

2. **创建新项目**
   - 点击 "New Project"
   - 选择 "Deploy from GitHub repo"
   - 选择你的仓库

3. **配置服务**
   - 选择 `backend` 目录
   - Railway会自动检测Dockerfile
   - 设置环境变量（如果需要）

4. **获取部署地址**
   - Railway会生成一个URL，如：`https://your-app.railway.app`
   - 这就是你的后端地址

5. **更新前端配置**
   - 在Vercel环境变量中设置：`VITE_API_URL=https://your-app.railway.app`

## 📝 环境变量配置

### Vercel（前端）

在Vercel项目设置 → Environment Variables 中添加：

```
VITE_API_URL=https://your-backend.railway.app
```

### Railway（后端）

在Railway项目设置 → Variables 中添加（可选，也可以通过前端配置）：

```
DEBUG=false
```

## 🔄 完整部署流程

1. **后端部署到Railway**
   ```bash
   # 推送代码到GitHub
   git push origin main
   
   # 在Railway中连接仓库并部署
   ```

2. **前端部署到Vercel**
   ```bash
   cd frontend
   vercel
   # 或通过GitHub集成
   ```

3. **配置CORS**
   
   在 `backend/app/main.py` 中更新CORS设置：
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=[
           "https://your-frontend.vercel.app",
           "http://localhost:3000",  # 开发环境
       ],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

## 🎯 最终效果

- **前端**: `https://your-app.vercel.app`
- **后端**: `https://your-backend.railway.app`
- **API文档**: `https://your-backend.railway.app/api/docs`

## 💡 其他部署选项

### Render.com

```bash
# 创建 render.yaml
services:
  - type: web
    name: voucher-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Fly.io

```bash
# 安装flyctl
curl -L https://fly.io/install.sh | sh

# 初始化
fly launch

# 部署
fly deploy
```

## ⚠️ 注意事项

1. **CORS配置**：确保后端允许Vercel域名访问
2. **环境变量**：敏感信息（API Key）不要提交到代码库
3. **超时处理**：如果使用Vercel Serverless Functions，需要实现异步处理
4. **文件上传**：Vercel有文件大小限制，大文件建议直接上传到后端

## 🆘 常见问题

**Q: Vercel部署后API调用失败？**
A: 检查CORS配置和后端地址是否正确

**Q: 后端超时怎么办？**
A: 使用Railway等支持长时间运行的服务，不要用Vercel Serverless Functions

**Q: 如何更新部署？**
A: 推送代码到GitHub，Vercel和Railway都会自动重新部署

