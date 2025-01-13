# 配置指南

## 配置文件结构

项目使用 `.env` 文件进行配置，主要包含以下部分：

```ini
# API 配置
OPENAI_API_KEY=your_api_key_here
SPEECH_RECOGNITION_API_KEY=your_api_key_here
TEXT_TO_SPEECH_API_KEY=your_api_key_here

# Cloudflare 配置
CLOUDFLARE_API_KEY=your_api_key_here
CLOUDFLARE_ACCOUNT_ID=your_account_id
CLOUDFLARE_ZONE_ID=your_zone_id
CLOUDFLARE_WORKER_NAME=gemini-proxy

# 音频配置
AUDIO_INPUT_DEVICE=0
AUDIO_OUTPUT_DEVICE=1
SAMPLE_RATE=16000
CHANNELS=1

# 系统配置
LANGUAGE=zh-CN
DEBUG=true
LOG_LEVEL=INFO
```

## Cloudflare 配置步骤

### 1. 创建 Cloudflare 账户
- 访问 [Cloudflare](https://www.cloudflare.com/) 注册账户
- 完成邮箱验证

### 2. 添加域名
- 在 Cloudflare 控制台添加你的域名
- 按照提示修改 DNS 服务器
- 等待 DNS 生效（通常需要几分钟）

### 3. 创建 Worker
1. 进入 Workers 页面
2. 点击 "Create a Service"
3. 输入服务名称：`gemini-proxy`
4. 选择 HTTP handler 模板
5. 部署以下代码：

```javascript
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  const url = new URL(request.url)
  const apiUrl = 'https://generativelanguage.googleapis.com'

  // 添加认证头
  const headers = new Headers(request.headers)
  headers.set('x-goog-api-key', request.headers.get('cf-api-key'))

  // 转发请求
  return fetch(apiUrl + url.pathname + url.search, {
    method: request.method,
    headers: headers,
    body: request.body
  })
}
```

### 4. 配置环境变量
- 在 Worker 设置页面添加环境变量：
  - `CF_API_KEY`: 你的 Gemini API 密钥
- 设置路由：
  - `*.yourdomain.com/gemini/*`

### 5. 测试配置
- 使用 curl 测试代理是否工作：
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "cf-api-key: your_api_key" \
  https://yourdomain.com/gemini/v1/models
```

## 其他配置

### API 配置
- `OPENAI_API_KEY`: OpenAI API 密钥
- `SPEECH_RECOGNITION_API_KEY`: 语音识别服务 API 密钥
- `TEXT_TO_SPEECH_API_KEY`: 文本转语音服务 API 密钥

### 音频配置
- `AUDIO_INPUT_DEVICE`: 音频输入设备索引
- `AUDIO_OUTPUT_DEVICE`: 音频输出设备索引
- `SAMPLE_RATE`: 采样率 (Hz)
- `CHANNELS`: 音频通道数 (1=单声道, 2=立体声)

### 系统配置
- `LANGUAGE`: 系统语言 (zh-CN, en-US 等)
- `DEBUG`: 调试模式 (true/false)
- `LOG_LEVEL`: 日志级别 (DEBUG, INFO, WARNING, ERROR)

## 联调测试

### 测试流程

1. 在树莓派上运行测试脚本：
```bash
python src/tests/integration_test.py
```

2. 测试脚本将执行以下步骤：
   - 通过 Cloudflare Worker 发送测试请求
   - 验证 Gemini API 响应
   - 检查音频输入输出设备
   - 验证完整工作流程

3. 预期输出：
```
[INFO] Starting integration test...
[SUCCESS] Cloudflare connection established
[SUCCESS] Gemini API response received
[SUCCESS] Audio devices working
[SUCCESS] Full workflow completed
```

### 常见错误处理

#### 1. Cloudflare 连接失败
- 检查 Worker 是否部署成功
- 验证 API 密钥是否正确
- 检查 DNS 是否生效
- 查看 Cloudflare 控制台日志

#### 2. Gemini API 无响应
- 检查 Worker 代码是否正确转发请求
- 验证 Gemini API 密钥
- 检查 API 配额是否用完
- 查看 Gemini API 状态页面

#### 3. 音频设备问题
- 检查音频设备索引是否正确
- 验证设备权限
- 测试音频输入输出
- 查看系统日志

#### 4. 完整工作流程失败
- 检查各组件日志
- 验证环境变量
- 测试单个组件
- 查看错误堆栈

## 配置验证

运行配置验证：
```bash
python src/config_validator.py
```

如果配置正确，将显示 "Configuration valid" 消息。
