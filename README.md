# 树莓派语音小助手 🍓🗣️

[![Python 版本](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![开源协议](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![CI/CD](https://github.com/yourusername/raspberry-gemini-voice/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/raspberry-gemini-voice/actions)

## 项目简介

基于Gemini API的语音助手，专为树莓派设计，但也兼容其他平台。让你的树莓派变身话痨小助手！本项目旨在提供一个开箱即用的语音交互解决方案，适用于智能家居、教育、娱乐等多种场景。

## 功能亮点 ✨

### 核心功能
- 🎙️ 语音识别：支持普通话和英语，识别准确率高
- 🔊 语音合成：多种音色可选，支持语速、音调调节
- 🤖 Gemini集成：强大的自然语言处理能力
- 💾 智能缓存：自动缓存常用对话，提升响应速度

### 技术特性
- 🧠 模块化设计：易于扩展和维护
- 📊 详细日志：支持多级别日志记录
- ⏱️ 超时重试：自动处理网络波动
- 🔒 安全存储：敏感信息加密存储

## 快速开始 🚀

### 基本使用
```python
from src.main import VoiceAssistant

assistant = VoiceAssistant()
response = assistant.ask("今天天气怎么样？")
print(response.text)
```

### 命令行使用
```bash
python -m src.main
```

## 安装指南 📦

1. 克隆仓库：
   ```bash
   git clone https://github.com/yourusername/raspberry-gemini-voice.git
   cd raspberry-gemini-voice
   ```

2. 创建虚拟环境：
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows用户请用 `venv\Scripts\activate`
   ```

3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

4. 配置环境变量：
   ```bash
   cp .env.example .env
   # 编辑.env文件，填入你的API密钥
   ```

5. 初始化数据库：
   ```bash
   python -m src.main --init
   ```

## 配置说明 ⚙️

编辑`.env`文件配置：

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| API_KEY | Gemini API密钥 | 必填 |
| CACHE_ENABLED | 是否启用缓存 | true |
| SPEECH_RATE | 语速 | 1.0 |
| VOICE_TYPE | 音色类型 | zh-CN-XiaoxiaoNeural |

## 开发指南 👨‍💻

### 环境准备
```bash
pip install -r requirements-dev.txt
```

### 运行测试
```bash
pytest
```

### 代码质量
```bash
# 格式化代码
black .

# 代码检查
flake8

# 类型检查
mypy .
```

## 贡献指南 🤝

我们欢迎各种形式的贡献！请阅读我们的[贡献指南](CONTRIBUTING.md)了解如何参与开发。

### 如何贡献
1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 贡献者
[![Contributors](https://contrib.rocks/image?repo=yourusername/raspberry-gemini-voice)](https://github.com/yourusername/raspberry-gemini-voice/graphs/contributors)

## 项目路线图 🗺️

- [x] 基础语音识别功能
- [x] Gemini API集成
- [ ] 多语言支持
- [ ] 插件系统
- [ ] Web管理界面

## 开源协议 📜

本项目采用 MIT 开源协议 - 详情请见 [LICENSE](LICENSE) 文件。

## 项目展示 🖼️

![系统架构图](docs/images/architecture.png)
![使用示例](docs/images/demo.gif)

## API文档

详细API文档请参考：[API文档](https://yourusername.github.io/raspberry-gemini-voice/)

## 社区支持

### 问题反馈
- 提交 [Issue](https://github.com/yourusername/raspberry-gemini-voice/issues)
- 加入 [Discussions](https://github.com/yourusername/raspberry-gemini-voice/discussions)

### 常见问题
1. 如何获取API密钥？
   - 访问Gemini开发者平台注册并获取API密钥

2. 支持哪些语言？
   - 目前支持中文和英文，更多语言支持正在开发中

3. 如何贡献代码？
   - 请参考[贡献指南](CONTRIBUTING.md)

4. 遇到问题怎么办？
   - 查看[问题排查指南](docs/getting-started/troubleshooting.md)
   - 在Discussions中提问

## 使用案例

### 智能家居控制
```python
assistant = VoiceAssistant()
assistant.ask("打开客厅的灯")
```

### 教育辅助
```python
assistant.ask("解释一下量子力学的基本概念")
```

### 娱乐互动
```python
assistant.ask("讲个笑话")
```

## 性能优化建议

1. 使用缓存：启用`.env`中的`CACHE_ENABLED`
2. 优化音频采样率：根据硬件性能调整`SAMPLE_RATE`
3. 使用最新版本：定期更新项目依赖
4. 启用硬件加速：在树莓派上启用GPU加速

## 安全注意事项

1. 不要公开API密钥
2. 定期更新依赖包
3. 使用HTTPS连接
4. 启用访问控制
5. 定期备份重要数据
