# 贡献指南

欢迎来到树莓派语音小助手项目！我们非常欢迎各种形式的贡献。这是一个完全开源的项目，以下是参与项目开发和使用的指南。

## 公开使用指南

### 快速开始
1. 克隆仓库：
   ```bash
   git clone https://github.com/yourusername/raspberry-gemini-voice.git
   ```

2. 查看[README.md](README.md)获取完整安装说明

3. 加入社区：
   - [Discussions](https://github.com/yourusername/raspberry-gemini-voice/discussions)
   - [Slack 频道](https://your-slack-link.com)

### 使用建议
- 查看[示例代码](examples/)获取使用灵感
- 参考[API文档](docs/api/)了解详细接口
- 查看[常见问题](docs/faq.md)解决常见问题

## 如何贡献

### 报告问题
- 使用 [Issue 模板](.github/ISSUE_TEMPLATE/bug_report.md) 报告问题
- 提供详细的错误描述和复现步骤
- 如果可能，附上相关日志和截图

### 提交代码
1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 代码规范
- 遵循 PEP 8 代码风格
- 使用类型注解
- 保持函数简洁（不超过30行）
- 添加必要的单元测试

## 开发环境

### 环境准备
```bash
# 克隆项目
git clone https://github.com/yourusername/raspberry-gemini-voice.git
cd raspberry-gemini-voice

# 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements-dev.txt
```

### 运行测试
```bash
pytest
```

### 代码质量检查
```bash
# 格式化代码
black .

# 代码检查
flake8

# 类型检查
mypy .
```

## 贡献者公约

我们遵循 [贡献者公约](https://www.contributor-covenant.org/)，请确保您的行为符合该公约。

## 新手任务

查看标记为 "good first issue" 的问题，这些是适合新贡献者开始的任务。

## 社区参与

### 问题反馈
- 使用 [Issue 模板](.github/ISSUE_TEMPLATE/bug_report.md) 报告问题
- 在 [Discussions](https://github.com/yourusername/raspberry-gemini-voice/discussions) 中讨论想法

### 功能建议
- 使用 [Feature Request 模板](.github/ISSUE_TEMPLATE/feature_request.md)
- 参与功能设计讨论

### 社区活动
- 参与每月社区会议
- 贡献教程和文档
- 帮助其他用户解决问题

## 联系方式

如有任何问题，请通过以下方式联系我们：
- 项目维护者：yourusername
- 邮箱：yourusername@example.com
- Slack：加入我们的 [Slack 频道](https://your-slack-link.com)
- 社区论坛：[Discussions](https://github.com/yourusername/raspberry-gemini-voice/discussions)

## 致谢

感谢所有贡献者的支持！查看我们的[贡献者列表](https://github.com/yourusername/raspberry-gemini-voice/graphs/contributors)
