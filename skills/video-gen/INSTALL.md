# Skill 安装指南

本文档说明如何将 video-gen Skill 集成到 Agent 环境中。

---

## 目录结构

```
Oneshot-Gen Skill/
└── skills/
    └── video-gen/
        ├── SKILL.md              # Skill 主文档
        ├── references/           # 参考资料
        │   ├── preset_details.md
        │   ├── workflow.md
        │   ├── error_handling.md
        │   └── examples.md
        └── assets/
            └── templates/
                └── prompt_export_template.txt
```

---

## 安装方式

### 方式 1：软链接（推荐）

**优点**：
- ✅ 自动同步更新
- ✅ 不复制文件，保持整洁
- ✅ 开发友好

**步骤**：

```bash
# 1. 在 Agent 项目根目录创建 .claude/skills 目录
cd /path/to/your/agent-project
mkdir -p .claude/skills

# 2. 创建软链接
ln -s ../../Oneshot-Gen Skill/skills/video-gen .claude/skills/video-gen

# 3. 验证
ls -la .claude/skills/video-gen
# 应该看到 -> ../../Oneshot-Gen Skill/skills/video-gen
```

**验证安装**：
```bash
# 检查 SKILL.md 是否可读
cat .claude/skills/video-gen/SKILL.md | head -10
```

---

### 方式 2：复制文件

**优点**：
- ✅ 独立部署
- ✅ 不依赖原路径

**缺点**：
- ❌ 更新需手动复制
- ❌ 占用额外空间

**步骤**：

```bash
# 1. 在 Agent 项目根目录创建 .claude/skills 目录
cd /path/to/your/agent-project
mkdir -p .claude/skills

# 2. 复制 video-gen 文件夹
cp -r /path/to/Oneshot-Gen Skill/skills/video-gen .claude/skills/

# 3. 验证
ls -la .claude/skills/video-gen
```

---

### 方式 3：Git 子模块

**优点**：
- ✅ 版本控制
- ✅ 易于更新

**步骤**：

```bash
# 1. 在 Agent 项目根目录添加子模块
cd /path/to/your/agent-project
git submodule add https://github.com/bird2iland/Oneshot-Gen-Skill.git skills

# 2. 创建软链接
mkdir -p .claude/skills
ln -s ../skills/video-gen .claude/skills/video-gen
```

---

## 环境配置

### 前置要求

| 项目 | 要求 | 检查命令 |
|------|------|----------|
| Python | 3.11+ | `python3 --version` |
| video-gen-cli | 已安装 | `video-gen --version` |
| 即梦 CLI | 已安装并登录 | `dreamina login` |

### 安装 video-gen-cli

```bash
# 从 GitHub 安装
pip install git+https://github.com/bird2iland/Oneshot-Gen-Skill.git@main#subdirectory=video-gen-cli

# 或本地安装（开发模式）
cd /path/to/Oneshot-Gen Skill/video-gen-cli
pip install -e .
```

### 安装即梦 CLI

```bash
# 安装
curl -fsSL https://jimeng.jianying.com/cli | bash

# 登录
dreamina login
# 跟随浏览器完成 OAuth 认证
```

---

## Skill 首次使用流程

当用户首次使用 Skill 时，Agent 应自动执行以下步骤：

### 步骤 1：检查 Skill 是否可用

```python
try:
    from video_gen import AgentTools
    print("✅ video-gen 已安装")
except ImportError:
    print("❌ video-gen 未安装")
    print("请运行：pip install git+https://github.com/bird2iland/Oneshot-Gen-Skill.git@main#subdirectory=video-gen-cli")
    return
```

### 步骤 2：检查环境状态

```python
from video_gen import AgentTools

status = await AgentTools.check_status()
print(f"video-gen 版本：{status.get('version')}")
print(f"即梦 CLI: {'✅ 已安装' if status.get('dreamina_installed') else '❌ 未安装'}")
print(f"即梦登录：{'✅ 已登录' if status.get('dreamina_logged_in') else '❌ 未登录'}")
```

### 步骤 3：引导用户完成配置

**如果环境未配置完成**：

```
检测到环境未配置完成，请先执行以下步骤：

1. 安装 video-gen-cli
   pip install git+https://github.com/bird2iland/Oneshot-Gen-Skill.git@main#subdirectory=video-gen-cli

2. 安装即梦 CLI
   curl -fsSL https://jimeng.jianying.com/cli | bash

3. 登录即梦
   dreamina login

完成上述步骤后，请告诉我"已配置完成"，我会继续帮你生成视频。
```

**如果环境已配置完成**：

```
✅ 环境检查通过！所有组件已就绪。

我可以帮你：
- 从图片生成视频
- 优化视频提示词
- 管理预设组合
- 导出提示词

请告诉我你想生成什么样的视频，或者上传参考图片。
```

---

## Skill 工作流程

当环境配置完成后，Skill 按以下流程工作：

```
用户请求
    ↓
[步骤 1] 触发识别
    ↓
[步骤 2] 预设选择（用户主导）
    ↓
[步骤 3] 可选补充材料（图片 + 描述）
    ↓
[步骤 4] 提示词优化
    ↓
[步骤 5] 导出或生成（分支）
    ↓
[步骤 6] 确认并生成
    ↓
[步骤 7] 完成并通知
```

详细工作流程参见 [SKILL.md](SKILL.md#工作流程)。

---

## 常见问题

### Q1: 软链接失效怎么办？

**A**: 检查原路径是否存在：
```bash
ls -la .claude/skills/video-gen
# 如果显示 broken，说明原路径变更

# 重新创建软链接
rm .claude/skills/video-gen
ln -s ../../Oneshot-Gen Skill/skills/video-gen .claude/skills/video-gen
```

### Q2: Skill 不触发怎么办？

**A**: 检查触发关键词是否匹配，或手动指定：
```
请使用 video-gen Skill 帮我生成视频
```

### Q3: 如何更新 Skill？

**A**: 
- **软链接方式**：自动同步，无需操作
- **复制方式**：重新复制 `skills/video-gen` 文件夹
- **子模块方式**：`git submodule update --remote`

---

## 最佳实践

### 1. 使用软链接

推荐在开发环境使用软链接，自动同步更新。

### 2. 定期更新

```bash
# 拉取最新代码
cd Oneshot-Gen Skill
git pull origin main

# 更新子模块
git submodule update --remote
```

### 3. 版本锁定

生产环境建议锁定版本：
```bash
pip install git+https://github.com/bird2iland/Oneshot-Gen-Skill.git@v0.8.0#subdirectory=video-gen-cli
```

---

## 参考文档

- [SKILL.md](SKILL.md) - Skill 主文档
- [workflow.md](references/workflow.md) - 工作流程详解
- [examples.md](references/examples.md) - 示例对话
- [README.md](../../README.md) - 项目总览

---

*最后更新：2026-04-23*
