# API 客户端文档

## 概述

API 客户端模块负责与外部服务进行通信，包括：

- 语音识别服务
- 自然语言处理服务
- 文本转语音服务

## 主要功能

- 统一的 API 请求处理
- 自动重试机制
- 请求限流控制
- 错误处理与恢复
- 请求日志记录

## 使用示例

### 初始化客户端

```python
from src.api_client.client import APIClient

client = APIClient(
    api_key="your_api_key",
    base_url="https://api.example.com",
    timeout=10,
    max_retries=3
)
```

### 发送请求

```python
response = client.post(
    endpoint="/recognize",
    data={
        "audio": "base64_encoded_audio",
        "language": "zh-CN"
    }
)

if response.success:
    print("识别结果:", response.data)
else:
    print("请求失败:", response.error)
```

## 配置参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| api_key | str | 无 | API 密钥 |
| base_url | str | 无 | 基础 URL |
| timeout | int | 10 | 请求超时时间（秒） |
| max_retries | int | 3 | 最大重试次数 |
| rate_limit | int | 10 | 每秒最大请求数 |
| log_level | str | "INFO" | 日志级别 |

## 错误处理

### 常见错误码

| 错误码 | 说明 | 处理建议 |
|--------|------|----------|
| 400 | 请求参数错误 | 检查请求参数 |
| 401 | 认证失败 | 检查 API 密钥 |
| 429 | 请求过多 | 降低请求频率 |
| 500 | 服务器错误 | 稍后重试 |

### 重试机制

- 自动重试 3 次
- 指数退避策略
- 可配置重试次数

## 性能优化

- 连接池管理
- 请求批处理
- 异步请求支持
- 缓存机制
