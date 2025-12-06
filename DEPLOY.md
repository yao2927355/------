# 部署指南

## 🚀 推荐部署方案

### 方案一：前端Vercel + 后端Railway（最推荐）⭐

**优点：**
- ✅ 前端全球CDN加速，访问速度快
- ✅ 后端不受超时限制，支持长时间处理
- ✅ 免费额度足够个人使用
- ✅ 部署简单，自动CI/CD

**架构：**
```
用户 → Vercel (前端) → Railway (后端) → OCR/LLM API
```

### 方案二：全栈Railway

**优点：**
- ✅ 前后端统一管理
- ✅ 支持Docker部署
- ✅ 简单易用

## 📦 部署步骤

### 1. 后端部署到Railway

#### 步骤1：准备代码
确保代码已推送到GitHub仓库。

#### 步骤2：创建Railway项目
1. 访问 https://railway.app
2. 使用GitHub账号登录
3. 点击 "New Project" → "Deploy from GitHub repo"
4. 选择你的仓库

#### 步骤3：配置服务
1. 在项目设置中，选择 `backend` 目录
2. Railway会自动检测 `Dockerfile`
3. 设置环境变量（可选）：
   ```
   DEBUG=false
   ALLOWED_ORIGINS=https://your-frontend.vercel.app
   ```

#### 步骤4：获取部署地址
Railway会生成一个URL，如：`https://your-app.railway.app`

### 2. 前端部署到Vercel

#### 步骤1：安装Vercel CLI（可选）
```bash
npm i -g vercel
```

#### 步骤2：部署
```bash
cd frontend
vercel login
vercel
```

或者通过GitHub集成：
1. 访问 https://vercel.com
2. 使用GitHub账号登录
3. 点击 "Add New Project"
4. 导入你的GitHub仓库
5. 配置：
   - **Root Directory**: `frontend`
   - **Framework Preset**: Vite
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

#### 步骤3：配置环境变量
在Vercel项目设置 → Environment Variables 中添加：
```
VITE_API_URL=https://your-backend.railway.app
```

#### 步骤4：重新部署
环境变量添加后，Vercel会自动重新部署。

### 3. 配置CORS

在Railway的环境变量中添加：
```
ALLOWED_ORIGINS=https://your-frontend.vercel.app,http://localhost:3000
```

## 🔧 其他部署选项

### Render.com

#### 后端部署
1. 访问 https://render.com
2. 创建新的 Web Service
3. 连接GitHub仓库
4. 配置：
   - **Root Directory**: `backend`
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Fly.io

#### 后端部署
```bash
# 安装flyctl
curl -L https://fly.io/install.sh | sh

# 登录
fly auth login

# 初始化（在backend目录）
cd backend
fly launch

# 部署
fly deploy
```

## 📝 环境变量清单

### Railway（后端）
```
DEBUG=false
ALLOWED_ORIGINS=https://your-frontend.vercel.app
# OCR配置（可选，也可以通过前端配置）
OCR_PROVIDER=baidu
OCR_API_KEY=your_key
OCR_SECRET_KEY=your_secret
# LLM配置（可选，也可以通过前端配置）
LLM_PROVIDER=deepseek
LLM_API_KEY=your_key
LLM_MODEL=deepseek-chat
```

### Vercel（前端）
```
VITE_API_URL=https://your-backend.railway.app
```

## ✅ 部署检查清单

- [ ] 后端已部署并可以访问 `/api/health`
- [ ] 前端已部署并可以访问
- [ ] 环境变量已正确配置
- [ ] CORS配置正确，前端可以调用后端API
- [ ] 测试上传凭证图片功能
- [ ] 测试Excel导出功能

## 🆘 常见问题

### Q: 前端无法连接后端？
**A:** 检查以下几点：
1. `VITE_API_URL` 环境变量是否正确
2. 后端CORS配置是否允许前端域名
3. 后端服务是否正常运行

### Q: 后端超时？
**A:** Railway等平台支持长时间运行，不会有超时问题。如果使用Vercel Serverless Functions，建议改用Railway。

### Q: 如何更新部署？
**A:** 
- **Vercel**: 推送代码到GitHub，自动部署
- **Railway**: 推送代码到GitHub，自动部署

### Q: 如何查看日志？
**A:**
- **Vercel**: 项目页面 → Deployments → 点击部署 → Logs
- **Railway**: 项目页面 → 点击服务 → Logs

## 💰 成本估算

### 免费方案
- **Vercel**: 免费（个人项目足够）
- **Railway**: $5/月免费额度（通常够用）
- **总计**: 基本免费

### 如果流量较大
- **Vercel Pro**: $20/月
- **Railway**: 按使用量付费
- **建议**: 先使用免费方案，根据实际使用情况升级

## 🎯 最终效果

部署完成后：
- **前端**: `https://your-app.vercel.app`
- **后端**: `https://your-backend.railway.app`
- **API文档**: `https://your-backend.railway.app/api/docs`

访问前端地址即可开始使用！

