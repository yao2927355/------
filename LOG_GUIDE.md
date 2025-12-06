# 日志查看指南

## 📝 日志文件说明

系统会在 `backend/logs/` 目录下生成以下日志文件：

| 日志文件 | 说明 | 用途 |
|---------|------|------|
| `app.log` | 所有日志 | 包含所有级别的日志信息 |
| `error.log` | 错误日志 | 仅包含 ERROR 和 CRITICAL 级别的日志 |
| `request.log` | 请求日志 | 记录所有API请求和响应 |
| `ocr.log` | OCR日志 | 记录OCR服务的调用情况 |
| `llm.log` | LLM日志 | 记录大模型服务的调用情况 |

## 🚀 快速查看日志

### 方式一：使用日志查看脚本（推荐）⭐

**macOS / Linux:**
```bash
./view-logs.sh
```

**Windows:**
```bash
view-logs.bat
```

脚本提供交互式菜单，可以选择查看不同类型的日志。

### 方式二：使用 tail 命令（macOS / Linux）

#### 查看所有日志
```bash
tail -f backend/logs/app.log
```

#### 查看错误日志
```bash
tail -f backend/logs/error.log
```

#### 查看请求日志
```bash
tail -f backend/logs/request.log
```

#### 查看OCR日志
```bash
tail -f backend/logs/ocr.log
```

#### 查看LLM日志
```bash
tail -f backend/logs/llm.log
```

#### 同时查看多个日志文件
```bash
tail -f backend/logs/*.log
```

### 方式三：使用 PowerShell（Windows）

#### 查看所有日志
```powershell
Get-Content backend\logs\app.log -Wait -Tail 50
```

#### 查看错误日志
```powershell
Get-Content backend\logs\error.log -Wait -Tail 50
```

#### 查看请求日志
```powershell
Get-Content backend\logs\request.log -Wait -Tail 50
```

## 📊 日志内容示例

### 请求日志示例
```
2025-01-15 10:30:45 - [POST] /api/recognize/single - IP: 127.0.0.1 - User-Agent: Mozilla/5.0
2025-01-15 10:30:50 - [POST] /api/recognize/single - Status: 200 - Time: 5.234s
```

### OCR日志示例
```
2025-01-15 10:30:46 - INFO - 开始OCR识别 - 文件: voucher.jpg, 大小: 123456 bytes
2025-01-15 10:30:48 - INFO - OCR识别完成 - 文件: voucher.jpg, 耗时: 2.35s, 识别文字长度: 456
```

### LLM日志示例
```
2025-01-15 10:30:48 - INFO - 开始LLM识别 - 文件: voucher.jpg, OCR文本长度: 456
2025-01-15 10:30:51 - INFO - LLM识别完成 - 文件: voucher.jpg, 耗时: 3.21s
```

### 错误日志示例
```
2025-01-15 10:30:45 - ERROR - OCR识别失败 - 文件: voucher.jpg, 错误: API调用超时
Traceback (most recent call last):
  ...
```

## 🔍 常用日志查看命令

### 查看最后N行
```bash
# 查看最后100行
tail -n 100 backend/logs/app.log

# 查看最后50行并实时跟踪
tail -n 50 -f backend/logs/app.log
```

### 搜索日志内容
```bash
# 搜索包含"错误"的日志
grep "错误" backend/logs/app.log

# 搜索包含"OCR"的日志（不区分大小写）
grep -i "ocr" backend/logs/app.log

# 实时搜索
tail -f backend/logs/app.log | grep "错误"
```

### 统计日志
```bash
# 统计错误数量
grep -c "ERROR" backend/logs/error.log

# 统计今天的请求数
grep "$(date +%Y-%m-%d)" backend/logs/request.log | wc -l
```

### 查看特定时间段的日志
```bash
# 查看今天的日志
grep "$(date +%Y-%m-%d)" backend/logs/app.log

# 查看特定时间的日志（例如：10:30-10:35）
grep "10:3[0-5]" backend/logs/app.log
```

## 🛠️ 日志管理

### 清理旧日志

日志文件会自动轮转（每个文件最大10MB，保留5个备份），但也可以手动清理：

```bash
# 清理所有日志文件
rm -f backend/logs/*.log*

# 清理旧的备份文件
rm -f backend/logs/*.log.*
```

### 查看日志文件大小
```bash
# 查看所有日志文件大小
ls -lh backend/logs/

# 查看日志目录总大小
du -sh backend/logs/
```

## 💡 调试技巧

### 1. 实时监控错误
```bash
tail -f backend/logs/error.log
```

### 2. 监控API请求
```bash
tail -f backend/logs/request.log | grep -E "(POST|GET|PUT|DELETE)"
```

### 3. 监控OCR性能
```bash
tail -f backend/logs/ocr.log | grep "耗时"
```

### 4. 查看完整的请求流程
```bash
# 在一个终端查看请求日志
tail -f backend/logs/request.log

# 在另一个终端查看OCR日志
tail -f backend/logs/ocr.log

# 在第三个终端查看LLM日志
tail -f backend/logs/llm.log
```

## 📱 在IDE中查看

如果你使用 VS Code 或其他IDE，可以直接打开日志文件：

1. 打开 `backend/logs/` 目录
2. 选择要查看的日志文件
3. 使用IDE的"跟随文件"功能实时查看更新

## ⚠️ 注意事项

1. **日志文件会持续增长**：定期清理旧日志，或使用日志轮转功能
2. **敏感信息**：日志中可能包含API Key的部分信息（已脱敏），但请注意保护
3. **性能影响**：大量日志写入可能影响性能，生产环境建议调整日志级别
4. **磁盘空间**：确保有足够的磁盘空间存储日志文件

