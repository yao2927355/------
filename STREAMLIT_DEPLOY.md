# Streamlit Community Cloud 部署指南

## 部署步骤

### 1. 准备代码

确保项目结构如下：
```
财务凭证识别/
├── streamlit_app.py          # Streamlit主应用（已创建）
├── requirements.txt          # Python依赖（已创建）
├── .streamlit/
│   └── config.toml          # Streamlit配置（已创建）
└── backend/
    └── app/                  # 后端应用代码
        ├── config.py
        ├── models.py
        ├── services/
        ├── data/
        └── ...
```

### 2. 推送到GitHub

```bash
# 初始化git（如果还没有）
git init

# 添加文件
git add .
git commit -m "准备部署到Streamlit"

# 添加远程仓库（替换为你的GitHub仓库地址）
git remote add origin https://github.com/你的用户名/财务凭证识别.git

# 推送到GitHub
git push -u origin main
```

### 3. 部署到Streamlit Community Cloud

1. 访问 [Streamlit Community Cloud](https://share.streamlit.io/)
2. 使用GitHub账号登录
3. 点击 "New app"
4. 选择你的GitHub仓库
5. 配置：
   - **Main file path**: `streamlit_app.py`
   - **Branch**: `main` (或你的主分支)
6. 点击 "Deploy"

### 4. 环境变量（可选）

如果需要配置环境变量，在Streamlit Cloud的App设置中添加：
- 无需环境变量，所有配置通过界面完成

### 5. 访问应用

部署完成后，你会获得一个类似 `https://你的应用名.streamlit.app` 的URL

## 功能说明

### 密码保护
- 默认密码：`li123456`
- 首次访问需要输入密码

### API配置
- OCR服务：只需填写百度OCR的API Key和Secret Key
- 大模型服务：只需填写DeepSeek的API Key
- 其他配置使用系统默认值

### 使用流程
1. 输入密码进入系统
2. 在「API配置」页面配置OCR和LLM的API Key
3. 在「上传凭证」页面上传图片
4. 点击「开始识别」进行批量识别
5. 在「识别结果」页面查看结果并导出Excel

## 注意事项

1. **文件大小限制**：Streamlit Cloud有文件大小限制，建议单张图片不超过10MB
2. **超时限制**：Streamlit Cloud有执行时间限制，批量处理时建议每批不超过10张
3. **存储限制**：上传的文件不会持久化存储，刷新页面后需要重新上传
4. **API Key安全**：API Key存储在session state中，刷新页面后需要重新配置

## 故障排查

### 导入错误
如果遇到模块导入错误，检查：
- `backend/app/` 目录结构是否正确
- `requirements.txt` 是否包含所有依赖

### 识别失败
- 检查API Key是否正确配置
- 查看Streamlit Cloud的日志输出
- 确认网络连接正常

### 性能问题
- 减少批量处理的文件数量
- 检查API服务的响应时间

## 本地测试

在部署前，可以在本地测试：

```bash
# 安装依赖
pip install -r requirements.txt

# 运行Streamlit应用
streamlit run streamlit_app.py
```

访问 http://localhost:8501 查看效果。

