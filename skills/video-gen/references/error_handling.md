# 错误处理策略

## 目录

- [概述](#概述)
- [错误类型表](#错误类型表)
- [错误处理流程](#错误处理流程)
- [常见错误场景](#常见错误场景)
- [Agent 错误处理代码示例](#agent-错误处理代码示例)
- [错误恢复策略](#错误恢复策略)
- [最佳实践](#最佳实践)

---

## 概述

本文档定义了 Video-Gen Agent Skill 的错误处理策略，包括错误类型、处理流程、Agent 代码示例和最佳实践。

---

## 错误类型表

### 环境配置错误

| 错误码 | 错误名 | 触发条件 | Agent 处理方式 |
|--------|--------|---------|---------------|
| `JIMENG_NOT_INSTALLED` | 即梦 CLI 未安装 | `check_status()` 返回 `installed=false` | 提供安装命令 |
| `JIMENG_NOT_LOGGED_IN` | 即梦未登录 | `check_status()` 返回 `logged_in=false` | 提供登录命令 |
| `VIDEOGEN_NOT_INSTALLED` | video-gen 未安装 | 导入 AgentTools 失败 | 提供 uv 安装命令 |

### 参数验证错误

| 错误码 | 错误名 | 触发条件 | Agent 处理方式 |
|--------|--------|---------|---------------|
| `PRESET_NOT_FOUND` | 预设不存在 | `preset_show()` 找不到预设 | 列出可用预设 |
| `INVALID_DIMENSION` | 无效维度 | 维度参数不是 visual/time/camera | 提示正确维度 |
| `INVALID_PRESET_COMBINATION` | 预设组合冲突 | validator 检测冲突 | 显示警告，询问是否继续 |

### 生成执行错误

| 错误码 | 错误名 | 触发条件 | Agent 处理方式 |
|--------|--------|---------|---------------|
| `GENERATION_FAILED` | 生成失败 | `generate_video()` 返回 `success=false` | 分析原因，建议重试 |
| `TASK_TIMEOUT` | 任务超时 | 轮询超过 max_wait | 提供任务查询命令 |
| `NO_VIDEO_URL` | 无视频 URL | 任务完成但无 URL | 建议联系支持 |

### 系统错误

| 错误码 | 错误名 | 触发条件 | Agent 处理方式 |
|--------|--------|---------|---------------|
| `NETWORK_ERROR` | 网络错误 | 网络连接失败 | 建议检查网络 |
| `FILE_NOT_FOUND` | 文件不存在 | 图片路径无效 | 建议检查路径 |
| `UNKNOWN_ERROR` | 未知错误 | 其他异常 | 建议重试或联系支持 |

---

## 错误处理流程

```
错误检测
    ↓
错误分析
    ↓
生成建议
    ↓
用户决策
    ↓
重试/退出
```

### 详细流程

1. **错误检测**
   - Agent 检查函数返回值
   - 检查 `success` 字段
   - 检查 `error_code` 字段

2. **错误分析**
   - 根据 `error_code` 确定错误类型
   - 分析错误原因
   - 判断是否可恢复

3. **生成建议**
   - 根据错误类型生成解决建议
   - 提供具体命令或操作步骤

4. **用户决策**
   - 用户选择重试、调整参数或退出
   - Agent 执行用户选择

5. **重试/退出**
   - 可恢复错误：执行恢复后重试
   - 不可恢复：提供替代方案或退出

---

## 常见错误场景

### 场景 1：环境未配置

```
用户：帮我生成一个城市延时视频

Agent: [调用 check_status]
       检测到即梦 CLI 未安装。

       请执行以下命令安装：
       curl -fsSL https://jimeng.jianying.com/cli | bash

       安装后执行：
       dreamina login

       完成配置后，请重新说"生成视频"触发此 skill。
```

### 场景 2：预设不存在

```
用户：用 cyberpunk + timelapse + shuttle

Agent: [调用 preset_show]
       预设 'cyberpunk' 不存在。

       可用的视觉风格预设：
       - realistic: 写实风格
       - pixel_art: 像素风格
       - oil_painting: 油画风格

       请选择一个可用预设，或说"你推荐"让我建议。
```

### 场景 3：组合冲突

```
用户：用 realistic + slow_motion + timelapse

Agent: [调用 validator]
       检测到预设组合冲突：
       - slow_motion（慢动作）与 timelapse（延时）存在语义冲突

       建议：
       - 如需慢动作效果，使用 slow_motion + normal
       - 如需延时效果，使用 timelapse + normal

       是否继续使用此组合？（可能导致效果不佳）
```

### 场景 4：生成失败

```
用户：确认生成

Agent: [调用 generate_video]
       生成失败。错误信息：当前账号没有 VIP 权限

       建议：
       1. 升级即梦账号到 VIP
       2. 导出提示词，到 Web 端手动生成
       3. 尝试使用可灵供应商（Phase 2 功能）

       是否导出提示词？
```

### 场景 5：任务超时

```
Agent: [轮询等待]
       视频生成超时（等待超过 300 秒）

       任务 ID: task_12345

       建议：
       - 查询任务状态：dreamina task status task_12345
       - 或使用命令：video-gen task status task_12345

       任务可能仍在后台执行，请稍后查询。
```

---

## Agent 错误处理代码示例

### 环境检查错误处理

```python
async def check_environment():
    """检查环境配置"""
    from video_gen import AgentTools
    
    try:
        status = await AgentTools.check_status()
        
        if not status['installed']:
            # 环境未安装
            agent.say("检测到即梦 CLI 未安装。")
            agent.say("请执行以下命令安装：")
            agent.say("curl -fsSL https://jimeng.jianying.com/cli | bash")
            agent.say("安装后执行：dreamina login")
            return False
        
        if not status['logged_in']:
            # 未登录
            agent.say("检测到即梦 CLI 未登录。")
            agent.say("请执行：dreamina login")
            return False
        
        return True
    
    except ImportError:
        # video-gen 未安装
        agent.say("video-gen 包未安装。")
        agent.say("请执行：uv pip install video-gen")
        return False
```

### 预设不存在错误处理

```python
async def handle_preset_not_found(preset_id: str, dimension: str):
    """处理预设不存在错误"""
    from video_gen import AgentTools
    
    agent.say(f"预设 '{preset_id}' 不存在。")
    agent.say(f"可用的 {dimension} 预设：")
    
    presets = await AgentTools.preset_list(dimension)
    for preset in presets:
        agent.say(f"  - {preset['id']}: {preset['name']}")
    
    agent.say("请选择一个可用预设，或说'你推荐'让我建议。")
```

### 组合冲突警告

```python
async def check_combination_conflicts(visual: str, time: str, camera: str):
    """检查预设组合冲突"""
    conflicts = [
        (("slow_motion", "timelapse"), "时间效果冲突"),
        (("handheld", "gimbal"), "运镜风格冲突"),
    ]
    
    for (preset1, preset2), reason in conflicts:
        if preset1 in [visual, time, camera] and preset2 in [visual, time, camera]:
            agent.say(f"警告：{preset1} 与 {preset2} 存在 {reason}")
            agent.say("此组合可能导致效果不佳。")
            
            # 询问用户是否继续
            response = agent.ask("是否继续使用此组合？")
            if response.lower() not in ["是", "继续", "yes"]:
                agent.say("请调整预设组合。")
                return False
    
    return True
```

### 生成失败错误处理

```python
async def handle_generation_failure(result: dict):
    """处理生成失败"""
    error_code = result.get('error_code', 'UNKNOWN')
    error_msg = result.get('error', '未知错误')
    
    agent.say(f"生成失败：{error_msg}")
    
    if error_code == 'JIMENG_NOT_VIP':
        agent.say("当前账号没有 VIP 权限。")
        agent.say("建议：")
        agent.say("1. 升级即梦账号到 VIP")
        agent.say("2. 导出提示词，到 Web 端手动生成")
        
        response = agent.ask("是否导出提示词？")
        if response.lower() in ["是", "导出", "yes"]:
            prompt = result.get('prompt')
            if prompt:
                path = await AgentTools.export_prompt(prompt)
                agent.say(f"提示词已导出到：{path}")
    
    elif error_code == 'NETWORK_ERROR':
        agent.say("网络连接失败。")
        agent.say("请检查网络连接后重试。")
    
    else:
        agent.say("建议重试或联系支持。")
```

---

## 错误恢复策略

### 自动恢复

| 错误类型 | 自动恢复策略 |
|---------|-------------|
| 网络错误 | 自动重试 3 次 |
| 临时 API 错误 | 等待 5 秒后重试 |
| 文件读取失败 | 尝试备用路径 |

### 用户干预恢复

| 错误类型 | 用户干预策略 |
|---------|-------------|
| 环境未配置 | 提供安装命令，等待用户执行 |
| 权限不足 | 建议升级账号或切换供应商 |
| 参数无效 | 提示正确参数，等待用户重新输入 |

### 降级处理

| 错误类型 | 降级策略 |
|---------|---------|
| LLM API 失败 | 降级到规则优化（Fast 模式） |
| VIP 权限不足 | 导出提示词，用户手动生成 |
| 可灵供应商失败 | 尝试即梦供应商 |

---

## 最佳实践

### Agent 错误处理原则

1. **清晰简洁**：错误信息要简短明确
2. **提供方案**：每次错误都给出解决建议
3. **引导用户**：提供具体命令或操作步骤
4. **避免重复**：相同错误不重复提示

### 错误提示格式

```
【错误类型】xxx 错误
【问题描述】具体错误信息
【解决建议】
1. 操作步骤 A
2. 操作步骤 B
【下一步】请执行上述步骤后重试
```

### 代码规范

- 使用 `try-except` 捕获异常
- 检查返回值的 `success` 字段
- 根据 `error_code` 分支处理
- 提供用户可操作的解决方案

---

## 版本

| 属性 | 值 |
|------|-----|
| 版本 | v0.3 |
| 更新日期 | 2026-04-22 |