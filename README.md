# Oneshot-Gen-Skill

**单镜头视频生成项目** - 通过三维预设组合系统提供精准的镜头控制能力

[![Version](https://img.shields.io/badge/version-0.8.0-blue.svg)](https://github.com/bird2iland/Oneshot-Gen-Skill)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## 📋 目录

- [项目概述](#-项目概述)
- [工作原理](#-工作原理)
- [项目结构](#-项目结构)
- [快速开始](#-快速开始)
- [安装指南](#-安装指南)
- [使用示例](#-使用示例)
- [CLI 命令](#-cli-命令)
- [输出说明](#-输出说明)
- [开发指南](#-开发指南)

---

##  项目概述

Oneshot-Gen-Skill 是一个**Agent 驱动的智能视频生成系统**，包含三个核心组件：

| 组件 | 说明 | 使用场景 |
|------|------|----------|
| **Skill** | Agent 技能包，自动化工作流 | Agent 对话式视频生成 |
| **CLI** | 命令行工具，视频生成引擎 | 脚本化/批量化视频生成 |
| **GUI** | 图形界面，预设和凭证管理 | 可视化管理预设和 API Key |

**核心价值**：
- 🎨 **三维预设系统**：视觉风格 × 时间采样 × 运镜风格，精准控制镜头语言
- 🤖 **Agent 自动化**：自然语言交互，自动优化提示词，一键生成视频
- 🔧 **灵活部署**：支持 CLI、GUI、Agent 三种使用方式
- 📦 **跨平台**：macOS、Windows、Linux 全平台支持

---

## 🔧 工作原理

```
┌─────────────────────────────────────────────────────────────┐
│                    用户交互层                                │
├─────────────────┬─────────────────┬─────────────────────────┤
│   Agent Skill   │   CLI 工具      │   GUI 管理工具          │
│   (对话式)      │   (命令行)      │   (可视化)              │
└────────────────┴────────┬────────┴──────────┬──────────────┘
         │                 │                   │
         └─────────────────┼───────────────────┘
                           ↓
         ┌─────────────────────────────────────┐
         │       video-gen-cli 核心引擎         │
         │  - 预设系统 (Preset Registry)       │
         │  - 优化器 (Rule + LLM Optimizer)    │
         │  - 供应商路由 (Provider Router)     │
         │  - 视频引擎 (Video Engine)          │
         └─────────────────────────────────────┘
                           ↓
         ┌─────────────────────────────────────┐
         │        视频生成供应商                │
         │  - 即梦 (Jimeng/Dreamina)           │
         │  - 可灵 (Kling)                     │
         │  - Veo (待集成)                     │
         └─────────────────────────────────────┘
```

### 工作流程

1. **用户输入**：自然语言描述 + 参考图（可选）
2. **预设选择**：从三维预设库中选择视觉/时间/运镜预设
3. **提示词优化**：规则优化 + LLM 增强，生成专业提示词
4. **队列提交**：提交到视频生成队列
5. **自动生成**：Worker 自动调用供应商 API 生成视频
6. **下载通知**：下载完成的视频并通知用户

---

## 📁 项目结构

```
Oneshot-Gen Skill/
├── .gitignore                    # Git 排除配置
├── README.md                     # 项目说明（本文件）
├── LICENSE                       # MIT 许可证
│
├── skills/                       # Agent Skill 包
│   └── video-gen/
│       ├── SKILL.md              # Skill 主文档（≤500 行）
│       ├── references/           # 参考资料
│       │   ├── preset_details.md
│       │   ├── workflow.md
│       │   ├── error_handling.md
│       │   └── examples.md
│       └── assets/
│           └── templates/
│               └── prompt_export_template.txt
│
├── video-gen-cli/                # CLI 工具（核心引擎）
│   ├── pyproject.toml            # Python 项目配置
│   ├── README.md                 # CLI 使用说明
│   ├── src/video_gen/
│   │   ├── __init__.py           # 导出 AgentTools
│   │   ├── core/                 # 核心模块
│   │   │   ├── engine.py         # 视频引擎
│   │   │   ├── data_store.py     # 统一数据存储
│   │   │   ├── types.py          # 类型定义
│   │   │   └── errors.py         # 错误类型
│   │   ├── presets/              # 预设系统
│   │   ├── optimizers/           # 优化器系统
│   │   ├── providers/            # 供应商系统
│   │   ├── cli/                  # CLI 命令
│   │   └── agent_tools/          # Agent 工具函数
│   ├── tests/                    # 单元测试
│   ├── config/                   # 配置文件
│   │   ├── custom_presets.yaml   # 自定义预设
│   │   └── batch_example.yaml    # 批量处理示例
│   └── data/                     # 数据目录（不提交到 Git）
│       ├── presets.json          # 预设数据
│       ├── credentials.json      # API Key（加密）
│       └── config.yaml           # 配置信息
│
└── video-gen-gui/                # GUI 管理工具
    ├── package.json              # 前端依赖
    ├── src/                      # React 前端
    │   ├── pages/
    │   │   ├── PresetList.tsx    # 预设列表
    │   │   ├── Composer.tsx      # 组合编辑器
    │   │   ├── Credentials.tsx   # 凭证管理
    │   │   └── Config.tsx        # 配置编辑
    │   ├── stores/               # 状态管理
    │   └── utils/                # 工具函数
    └── src-tauri/                # Rust 后端
        ├── Cargo.toml
        ├── src/
        │   ├── commands.rs       # Tauri 命令
        │   └── lib.rs
        └── tauri.conf.json
```

---

## 🚀 快速开始

### 30 秒快速体验

```bash
# 1. 克隆项目
git clone https://github.com/bird2iland/Oneshot-Gen-Skill.git
cd Oneshot-Gen Skill

# 2. 安装 CLI
cd video-gen-cli
pip install -e .

# 3. 安装即梦 CLI
curl -fsSL https://jimeng.jianying.com/cli | bash
dreamina login

# 4. 测试
video-gen check
video-gen preset list
```

---

## 📦 安装指南

### 方式 1：完整安装（推荐）

```bash
# 克隆项目
git clone https://github.com/bird2iland/Oneshot-Gen-Skill.git
cd Oneshot-Gen Skill

# 安装 CLI
cd video-gen-cli
pip install -e .

# 安装 GUI（可选）
cd ../video-gen-gui
npm install
npm run tauri dev
```

### 方式 2：仅使用 CLI

```bash
pip install git+https://github.com/bird2iland/Oneshot-Gen-Skill.git@main#subdirectory=video-gen-cli
```

### 方式 3：Agent Skill 安装

```bash
# 在 Agent 项目根目录
mkdir -p .claude/skills
ln -s ../../Oneshot-Gen Skill/skills/video-gen .claude/skills/video-gen
```

### 前置要求

| 依赖 | 版本 | 安装命令 |
|------|------|----------|
| Python | 3.11+ | `python3 --version` |
| Node.js | 18+ | `brew install node` |
| Rust | 1.70+ | `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs \| sh` |
| 即梦 CLI | 最新版 | `curl -fsSL https://jimeng.jianying.com/cli \| bash` |

### 登录即梦

```bash
dreamina login
# 跟随浏览器完成 OAuth 认证
```

---

## 💡 使用示例

### Agent Skill 使用

```
用户：帮我生成一个城市延时视频

Agent: 好的！我来帮你生成城市延时视频。

首先，这是所有可用的预设：

【视觉风格】
- realistic: 写实风格（真实感、细节丰富）
- pixel_art: 像素风格（复古像素艺术）
- oil_painting: 油画风格（艺术油画质感）

【时间采样】
- timelapse: 延时摄影（时间压缩效果）
- slow_motion: 升格慢动作（时间拉伸效果）
- normal: 常规速度（正常时间流）

【运镜风格】
- shuttle: 穿梭机（快速穿梭运动）
- gimbal: 稳定器（平滑稳定运镜）
- handheld: 手持（自然晃动感）

请选择预设组合，例如"realistic + timelapse + shuttle"。

用户：用 realistic + timelapse + shuttle

Agent: 好的！请上传参考图（可选），并描述你想要的效果。

用户：[上传 2 张图片] 城市从清晨到黄昏

Agent: 让我优化提示词...

【优化后的提示词】
High quality video, photorealistic detailed realistic, timelapse time 
passing accelerated, shuttle cam fast movement dynamic, city skyline 
from dawn to dusk, 4K resolution, cinematic lighting

现在生成视频还是导出提示词？

用户：直接生成

Agent: 视频生成中...（预计 2-3 分钟）
✅ 生成完成！视频已保存到：output/videos/city_timelapse_20260423.mp4
```

### CLI 使用

```bash
# 交互式生成
video-gen gen --interactive

# 直接生成
video-gen gen \
  --visual realistic \
  --time timelapse \
  --camera shuttle \
  --image img1.png \
  --image img2.png \
  --description "城市从清晨到黄昏"

# 批量生成
video-gen batch --input batch.yaml

# 导出提示词
video-gen export --prompt "city timelapse" --output prompt.txt
```

### GUI 使用

```bash
cd video-gen-gui
npm run tauri dev

# 功能：
# - 预设可视化列表（卡片展示、搜索筛选）
# - 组合编辑器（三维预设选择、冲突检测）
# - 凭证管理（API Key 存储、连接测试）
# - 配置编辑（config.yaml 可视化编辑）
```

---

## 🛠 CLI 命令

### 预设管理

```bash
# 列出所有预设
video-gen preset list

# 按维度列出
video-gen preset list --dimension visual
video-gen preset list --dimension time
video-gen preset list --dimension camera

# 查看预设详情
video-gen preset show realistic

# 保存自定义预设组合
video-gen preset save --name city_style \
  --visual realistic \
  --time timelapse \
  --camera shuttle

# 删除预设
video-gen preset delete city_style
```

### 凭证管理

```bash
# 设置 API Key
video-gen credential set jimeng --api-key "your-api-key"
video-gen credential set kling --api-key "your-api-key"

# 查看凭证
video-gen credential list

# 删除凭证
video-gen credential delete jimeng
```

### 配置管理

```bash
# 查看配置
video-gen config show

# 修改配置
video-gen config set default_provider jimeng
video-gen config set default_duration 10
```

### 视频生成

```bash
# 交互式生成
video-gen gen --interactive

# 直接生成
video-gen gen \
  --visual realistic \
  --time timelapse \
  --camera shuttle \
  --image img1.png \
  --image img2.png \
  --description "城市从清晨到黄昏" \
  --duration 5 \
  --ratio "16:9"

# 批量生成
video-gen batch --input batch.yaml
```

### 系统检查

```bash
# 检查系统状态
video-gen check
```

---

## 📤 输出说明

### 输出目录结构

```
video-gen-cli/output/
├── prompts/              # 导出的提示词
│   ├── city_timelapse_20260423_193045.txt
│   └── ...
└── videos/               # 生成的视频
    ├── city_timelapse_20260423_193045.mp4
    └── ...
```

### 提示词文件格式

```txt
# city_timelapse_20260423_193045.txt

High quality video, photorealistic detailed realistic, timelapse time 
passing accelerated, shuttle cam fast movement dynamic, city skyline 
from dawn to dusk, 4K resolution, cinematic lighting

---
Generated by Video-Gen CLI
Timestamp: 2026-04-23 19:30:45
Presets: realistic + timelapse + shuttle
```

### 视频文件命名

```
{preset_name}_{timestamp}.mp4
示例：city_timelapse_20260423_193045.mp4
```

---

## 👨‍ 开发指南

### 环境设置

```bash
# 克隆项目
git clone https://github.com/bird2iland/Oneshot-Gen-Skill.git
cd Oneshot-Gen Skill

# 创建虚拟环境
cd video-gen-cli
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# .\venv\Scripts\Activate  # Windows

# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest tests/

# 类型检查
mypy src/

# 代码格式化
ruff check src/
ruff format src/
```

### GUI 开发

```bash
cd video-gen-gui

# 安装依赖
npm install

# 开发模式
npm run tauri dev

# 构建发布版
npm run tauri build

# 清理构建产物
cargo clean
rm -rf node_modules
```

### 提交规范

```bash
# 功能开发
git commit -m "feat: 添加批量导出功能"

# 修复 bug
git commit -m "fix: 修复预设删除功能"

# 文档更新
git commit -m "docs: 更新 README 安装说明"

# 代码优化
git commit -m "refactor: 重构数据存储模块"
```

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📞 联系方式

- GitHub: [@bird2iland](https://github.com/bird2iland)
- 项目地址：https://github.com/bird2iland/Oneshot-Gen-Skill

---

## 🙏 致谢

感谢以下项目和团队：

- [Tauri](https://tauri.app/) - 跨平台桌面应用框架
- [即梦](https://jimeng.jianying.com/) - 视频生成平台
- [可灵](https://kling.kuaishou.com/) - 视频生成平台

---

*最后更新：2026-04-23*
