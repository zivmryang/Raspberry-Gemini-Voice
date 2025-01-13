# 安装指南

## 系统要求

- 树莓派 4B 或更高版本
- Python 3.9+
- 至少 4GB 内存
- 16GB 存储空间

## 安装步骤

### 1. 设置 Python 环境

```bash
# 安装 Python 3.9
sudo apt update
sudo apt install python3.9 python3.9-venv

# 创建虚拟环境
python3.9 -m venv venv
source venv/bin/activate
```

### 2. 克隆项目

```bash
git clone https://github.com/yourusername/raspberry-gemini-voice.git
cd raspberry-gemini-voice
```

### 3. 安装依赖

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. 配置环境变量

创建 `.env` 文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置必要的 API 密钥和其他设置。

### 5. 验证安装

```bash
python src/main.py --test
```

如果看到 "System ready" 消息，说明安装成功。

## 常见问题

### 缺少依赖项

如果遇到依赖项问题，尝试：

```bash
sudo apt install portaudio19-dev
sudo apt install libasound2-dev
```

### 权限问题

如果遇到权限问题，尝试：

```bash
sudo usermod -a -G audio $USER
```

然后重新登录系统。
