---
name: video-gen
description: 从静态图像生成单镜头视频的智能助手。通过三维预设组合系统，用户用自然语言描述视频需求，系统自动优化提示词并生成高质量视频。触发关键词：视频、影像、画面、镜头、延时、慢动作、预设、生成视频、导出提示词、video、timelapse、preset。
---

# Video-Gen Agent Skill

## 描述

这是一个帮助用户从静态图像生成单镜头视频的智能助手。通过三维预设组合系统（视觉风格、时间采样、运镜风格），用户可以用简单的自然语言描述视频需求，系统自动优化提示词并生成高质量视频。

**核心价值**：让用户无需了解专业视频术语，只需描述想要的视频效果，系统自动转换为专业的视频生成提示词。

---

## 触发条件

当用户的请求涉及以下关键词或意图时，**应该立即激活此 skill**：

### 关键词触发

| 类别 | 关键词 | 示例 |
|------|--------|------|
| **视频类** | 视频、影像、画面、镜头 | "帮我生成一个视频"、"画面效果" |
| **效果类** | 延时、慢动作、穿梭、稳定、手持 | "做一个延时视频"、"想要慢动作效果" |
| **预设类** | 预设、风格、模板、写实、像素、油画 | "有什么预设风格？"、"写实风格" |
| **操作类** | 生成、制作、创建、导出、优化 | "生成视频"、"导出提示词" |
| **英文类** | video, generate, timelapse, preset | "generate a video" |

### 触发示例

```
✅ "帮我生成一个城市延时视频"           → 立即激活
✅ "我想把这些图片变成视频"             → 立即激活
✅ "有什么预设风格可选？"               → 立即激活
✅ "做一个赛博朋克风格的穿梭视频"       → 立即激活
✅ "导出视频提示词"                     → 立即激活

❌ "帮我生成一张图片"                   → 不触发（非视频）
❌ "写一段文字"                         → 不触发（非视频）
❌ "帮我剪辑视频"                       → 不触发（非生成类）
```

---

## 环境配置

### 前置要求

| 项目 | 要求 |
|------|------|
| Python | 3.11+ |
| video-gen 包 | 已安装（`uv pip install video-gen`） |
| 即梦 CLI (dreamina) | 已安装并登录 |

### Agent 自动配置检查清单

激活 skill 后，Agent 应执行以下检查：

1. **检查 video-gen 导入**
   ```python
   from video_gen import AgentTools
   # 如失败，提示用户安装
   ```

2. **检查 dreamina CLI**
   ```python
   status = await AgentTools.check_status()
   # 返回 installed, logged_in 状态
   ```

3. **如环境未配置，提供安装命令**
   ```bash
   # 安装 video-gen（从 GitHub）
   pip install git+https://github.com/bird2iland/Oneshot-Gen-Skill.git@main#subdirectory=video-gen-cli
   # 或
   uv pip install git+https://github.com/bird2iland/Oneshot-Gen-Skill.git@main#subdirectory=video-gen-cli
   
   # 安装即梦 CLI
   curl -fsSL https://jimeng.jianying.com/cli | bash
   
   # 登录即梦
   dreamina login
   ```

---

## 工作流程

完整工作流程分为 **7 个步骤**：

| 步骤 | 名称 | Agent 行为 | 用户行为 |
|------|------|-----------|---------|
| 1 | 触发识别 | 检测关键词，检查环境 | 表达意图 |
| 2 | 预设选择 | 列出预设，等待选择 | 选择预设或请求推荐 |
| 3 | 可选补充 | 询问参考图和描述 | 上传图片/输入描述（可选） |
| 4 | 提示词优化 | 调用优化器，展示结果 | 确认或调整 |
| 5 | 导出/生成分支 | 询问选择 | 选择导出或生成 |
| 6 | 确认并生成 | 确认参数，执行生成 | 确认参数 |
| 7 | 完成 | 展示结果，提供选项 | 下载/重试/保存 |

**详细流程说明**：参见 [references/workflow.md](references/workflow.md)

---

## 工具函数

通过 `from video_gen import AgentTools` 导入工具类：

### 预设管理

| 函数 | 说明 |
|------|------|
| `preset_list(dimension)` | 列出预设（可选维度筛选） |
| `preset_show(preset_id, dimension)` | 显示预设详情 |
| `preset_save(name, visual, time, camera)` | 保存自定义组合 |

### 提示词操作

| 函数 | 说明 |
|------|------|
| `optimize_prompt(...)` | 优化提示词（预设 + 描述） |
| `export_prompt(prompt, filename)` | 导出提示词到 txt 文件 |

### 视频生成

| 函数 | 说明 |
|------|------|
| `generate_video(...)` | 生成视频（完整参数） |
| `check_status()` | 检查系统状态 |

**详细函数说明**：参见 [references/workflow.md](references/workflow.md) 的工具函数调用部分

---

## 预设系统

### 三维预设概览

| 维度 | 说明 | 预设数量 |
|------|------|----------|
| visual | 视觉风格 | 3 个 |
| time | 时间采样 | 3 个 |
| camera | 运镜风格 | 3 个 |

### 快速参考

**视觉风格**：`realistic`（写实）、`pixel_art`（像素）、`oil_painting`（油画）

**时间采样**：`timelapse`（延时）、`slow_motion`（慢动作）、`normal`（正常）

**运镜风格**：`shuttle`（穿梭）、`gimbal`（稳定）、`handheld`（手持）

### 组合冲突

以下组合存在语义冲突，Agent 应显示警告：

| 冲突组合 | 原因 |
|---------|------|
| slow_motion + timelapse | 时间效果冲突 |
| handheld + gimbal | 运镜风格冲突 |

**详细预设说明**：参见 [references/preset_details.md](references/preset_details.md)

---

## 示例对话

### 完整流程示例

```
用户：帮我生成一个城市延时视频

Agent: 好的！我来帮你生成城市延时视频。
       首先，这是所有可用的预设：

       【视觉风格】
       - realistic: 写实风格
       - pixel_art: 像素风格
       - oil_painting: 油画风格

       【时间采样】
       - timelapse: 延时摄影
       - slow_motion: 升格慢动作
       - normal: 常规速度

       【运镜风格】
       - shuttle: 穿梭机
       - gimbal: 稳定器
       - handheld: 手持

       请选择预设组合，例如"realistic + timelapse + shuttle"。
       或说"你推荐"让我建议。

用户：realistic + timelapse + shuttle

Agent: 已选择：
       - 视觉：realistic → photorealistic, detailed
       - 时间：timelapse → time passing, accelerated
       - 运镜：shuttle → fast movement, dynamic

       是否有参考图？（可选，上传 1-9 张）

用户：[上传 2 张图片] 城市从清晨到黄昏

Agent: 优化后的提示词：
       High quality video, photorealistic detailed, timelapse time passing,
       shuttle cam fast movement, city skyline from dawn to dusk, 4K resolution

       确认吗？

用户：可以

Agent: 导出提示词，还是直接生成视频？

用户：导出提示词吧

Agent: 提示词已保存到：output/prompts/city_timelapse_20260422.txt
       你可以到即梦 Web 端使用此提示词。
```

**更多示例**：参见 [references/examples.md](references/examples.md)

---

## 错误处理

### 常见错误

| 错误 | Agent 处理 |
|------|-----------|
| 环境未配置 | 提供安装命令，引导配置 |
| 预设不存在 | 列出可用预设，建议选择 |
| 组合冲突 | 显示警告，询问是否继续 |
| 生成失败 | 分析原因，建议重试 |

**详细错误处理**：参见 [references/error_handling.md](references/error_handling.md)

---

## 参考文档

| 文档 | 内容 |
|------|------|
| [preset_details.md](references/preset_details.md) | 9 个预设详解 |
| [workflow.md](references/workflow.md) | 工作流程详解 |
| [error_handling.md](references/error_handling.md) | 错误处理策略 |
| [examples.md](references/examples.md) | 更多示例对话 |

---

## 安装

### 从 GitHub 安装

```bash
pip install git+https://github.com/bird2iland/Oneshot-Gen-Skill.git@main#subdirectory=video-gen-cli
# 或
uv pip install git+https://github.com/bird2iland/Oneshot-Gen-Skill.git@main#subdirectory=video-gen-cli
```

### 本地安装（开发）

```bash
cd video-gen
pip install -e .
# 或
uv pip install -e .
```

### 前置要求

- Python 3.11+
- 即梦 CLI（dreamina）已安装并登录

```bash
# 安装即梦 CLI
curl -fsSL https://jimeng.jianying.com/cli | bash
dreamina login
```

---

## 版本

| 属性 | 值 |
|------|-----|
| 版本 | v0.3 |
| 更新日期 | 2026-04-22 |
| 兼容平台 | Claude Code, opencode |