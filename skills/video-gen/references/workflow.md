# 视频生成工作流程详解

## 目录

- [概述](#概述)
- [步骤 1: 触发识别](#步骤-1-触发识别)
  - [Agent 行为](#步骤-1-agent-行为)
  - [用户行为](#步骤-1-用户行为)
  - [工具函数调用](#步骤-1-工具函数调用)
  - [输入/输出示例](#步骤-1-输入输出示例)
  - [分支逻辑](#步骤-1-分支逻辑)
- [步骤 2: 预设选择](#步骤-2-预设选择)
  - [Agent 行为](#步骤-2-agent-行为)
  - [用户行为](#步骤-2-用户行为)
  - [工具函数调用](#步骤-2-工具函数调用)
  - [输入/输出示例](#步骤-2-输入输出示例)
  - [分支逻辑](#步骤-2-分支逻辑)
- [步骤 3: 可选补充材料](#步骤-3-可选补充材料)
  - [Agent 行为](#步骤-3-agent-行为)
  - [用户行为](#步骤-3-用户行为)
  - [工具函数调用](#步骤-3-工具函数调用)
  - [输入/输出示例](#步骤-3-输入输出示例)
  - [分支逻辑](#步骤-3-分支逻辑)
- [步骤 4: 提示词优化](#步骤-4-提示词优化)
  - [Agent 行为](#步骤-4-agent-行为)
  - [用户行为](#步骤-4-用户行为)
  - [工具函数调用](#步骤-4-工具函数调用)
  - [输入/输出示例](#步骤-4-输入输出示例)
  - [分支逻辑](#步骤-4-分支逻辑)
- [步骤 5: 导出或生成分支](#步骤-5-导出或生成分支)
  - [Agent 行为](#步骤-5-agent-行为)
  - [用户行为](#步骤-5-用户行为)
  - [工具函数调用](#步骤-5-工具函数调用)
  - [输入/输出示例](#步骤-5-输入输出示例)
  - [分支逻辑](#步骤-5-分支逻辑)
- [步骤 6: 确认并生成](#步骤-6-确认并生成)
  - [Agent 行为](#步骤-6-agent-行为)
  - [用户行为](#步骤-6-用户行为)
  - [工具函数调用](#步骤-6-工具函数调用)
  - [输入/输出示例](#步骤-6-输入输出示例)
  - [分支逻辑](#步骤-6-分支逻辑)
- [步骤 7: 完成](#步骤-7-完成)
  - [Agent 行为](#步骤-7-agent-行为)
  - [用户行为](#步骤-7-用户行为)
  - [工具函数调用](#步骤-7-工具函数调用)
  - [输入/输出示例](#步骤-7-输入输出示例)
  - [分支逻辑](#步骤-7-分支逻辑)
- [异常处理](#异常处理)
- [最佳实践](#最佳实践)

---

## 概述

本文档详细描述视频生成 Agent 的完整工作流程，包含 7 个核心步骤。每个步骤说明 Agent 行为、用户交互、工具调用和分支逻辑，帮助开发者理解系统运作机制。

---

## 步骤 1: 触发识别

### 步骤 1: Agent 行为

Agent 持续监听用户输入，检测是否包含视频生成相关的关键词或意图。

**检测机制：**
- 关键词匹配：检测用户输入中是否包含触发词
- 语义理解：通过 LLM 判断用户意图是否为视频生成
- 上下文分析：结合对话上下文判断触发条件

**触发关键词列表：**

| 类别 | 关键词 |
|------|--------|
| 基础词 | 视频、影像、画面、镜头 |
| 技术词 | 延时、慢动作、快进、倒放 |
| 动作词 | 生成、创建、制作、渲染 |
| 场景词 | 日落、日出、城市、自然、风景 |

**触发示例：**
```
用户输入: "帮我生成一段日落延时视频"
检测结果: 匹配关键词 ["生成", "日落", "延时", "视频"]
触发状态: True
```

### 步骤 1: 用户行为

用户通过自然语言表达视频生成需求，无需使用特定命令格式。

**用户输入模式：**
- 直接描述："生成一段城市延时摄影视频"
- 简短请求："做个日落视频"
- 详细描述："我想创建一个15秒的海边日出慢动作视频，要有海浪和海鸥"

### 步骤 1: 工具函数调用

```python
# 检查环境状态
status = AgentTools.check_status()

# 返回结构
{
    "api_key_valid": True,
    "models_available": ["kling-v1", "kling-v1-5"],
    "quota_remaining": 100,
    "output_directory": "/path/to/output"
}
```

**调用时机：**
- 每次触发时调用
- 确认 API 密钥有效
- 检查配额充足
- 验证输出目录可写

### 步骤 1: 输入/输出示例

**输入示例：**

```
用户: 帮我生成一个城市夜景延时视频
```

**输出示例：**

```json
{
    "triggered": true,
    "matched_keywords": ["生成", "城市", "延时", "视频"],
    "intent": "video_generation",
    "environment_status": {
        "ready": true,
        "message": "环境就绪，进入预设选择阶段"
    }
}
```

### 步骤 1: 分支逻辑

```
触发识别
├── 检测到触发词 → 进入步骤 2
├── 未检测到触发词 → 继续监听
├── 环境检查失败 → 提示用户修复环境
│   ├── API 密钥无效 → 提示配置 API_KEY
│   ├── 配额不足 → 提示充值或等待
│   └── 输出目录不可写 → 提示检查权限
└── 意图不明确 → 询问用户确认
```

---

## 步骤 2: 预设选择

### 步骤 2: Agent 行为

Agent 展示可用预设列表，并根据用户输入智能推荐合适的预设组合。

**预设列表获取：**

```python
presets = AgentTools.preset_list()
```

**预设分类：**

| 类别 | 预设 ID | 名称 | 适用场景 |
|------|---------|------|----------|
| 风格 | realistic | 写实风格 | 真实场景还原 |
| 风格 | cinematic | 电影风格 | 叙事性画面 |
| 技术 | timelapse | 延时摄影 | 时间流逝 |
| 技术 | slowmo | 慢动作 | 动作细节 |
| 技术 | shuttle | 快门效果 | 动态模糊 |

**推荐逻辑：**
1. 分析用户描述中的关键词
2. 匹配预设标签和描述
3. 按相关性排序推荐
4. 展示 Top 3 推荐组合

### 步骤 2: 用户行为

用户有两种方式选择预设：

**方式 A: 直接指定**
```
用户: 用 realistic + timelapse + shuttle
```

**方式 B: 请求推荐**
```
用户: 你推荐一个
用户: 帮我选
用户: 不知道用哪个
```

### 步骤 2: 工具函数调用

```python
# 获取预设列表
presets = AgentTools.preset_list()

# 返回结构
{
    "presets": [
        {
            "id": "realistic",
            "name": "写实风格",
            "description": "真实场景还原，适合风景、建筑",
            "tags": ["风景", "建筑", "真实"],
            "compatible_with": ["timelapse", "slowmo"]
        },
        {
            "id": "timelapse",
            "name": "延时摄影",
            "description": "时间流逝效果，适合日落、城市",
            "tags": ["延时", "时间", "日落"],
            "compatible_with": ["realistic", "cinematic"]
        }
    ],
    "total": 12
}
```

### 步骤 2: 输入/输出示例

**输入示例 A（直接指定）：**

```
用户: 用 realistic 和 timelapse
```

**输出 A：**

```json
{
    "selected_presets": ["realistic", "timelapse"],
    "selection_method": "direct",
    "preset_details": [
        {
            "id": "realistic",
            "name": "写实风格"
        },
        {
            "id": "timelapse",
            "name": "延时摄影"
        }
    ]
}
```

**输入示例 B（请求推荐）：**

```
用户: 我想做个日落的视频，你推荐一下
```

**输出 B：**

```json
{
    "selected_presets": ["realistic", "timelapse"],
    "selection_method": "recommended",
    "recommendation_reason": "日落场景适合延时摄影效果，写实风格还原真实色彩",
    "alternatives": [
        ["cinematic", "timelapse"],
        ["realistic", "slowmo"]
    ]
}
```

### 步骤 2: 分支逻辑

```
预设选择
├── 用户直接指定 → 验证预设有效性
│   ├── 有效 → 进入步骤 3
│   └── 无效 → 提示正确预设名，重新选择
├── 用户请求推荐 → 分析描述关键词
│   ├── 关键词足够 → 推荐预设组合
│   ├── 关键词不足 → 询问更多细节
│   └── 推荐后用户确认 → 进入步骤 3
├── 用户拒绝推荐 → 再次列出所有预设
└── 用户取消 → 结束流程
```

---

## 步骤 3: 可选补充材料

### 步骤 3: Agent 行为

Agent 询问用户是否需要上传参考图片或提供额外描述。

**询问策略：**
- 友好询问，不强制要求
- 说明图片用途（参考构图、色彩、风格）
- 说明描述用途（补充细节、调整方向）

**询问模板：**

```
"是否需要上传参考图片？图片可以帮助我更好地理解你想要的效果。
你也可以直接描述更多细节，或者两者都提供。"
```

### 步骤 3: 用户行为

用户可以选择以下任一方式：

**选项 A: 上传图片**
- 上传 1-9 张参考图片
- 支持格式：JPG、PNG、WEBP
- 图片会用于风格参考和构图指导

**选项 B: 输入描述**
- 用文字补充细节
- 可以描述具体场景、氛围、色调等

**选项 C: 图片 + 描述**
- 同时上传图片和输入描述
- 描述可以对图片进行补充说明

**选项 D: 跳过**
- 直接使用之前的预设和描述
- 不上传图片，不补充描述

### 步骤 3: 工具函数调用

```python
# 上传图片（如果有）
if user_images:
    uploaded_paths = AgentTools.upload_images(user_images)

# 返回结构
{
    "images": [
        {
            "path": "/output/reference/img_001.jpg",
            "original_name": "sunset_ref.jpg",
            "size": 2048576
        }
    ],
    "total": 1
}
```

### 步骤 3: 输入/输出示例

**输入示例 A（仅上传图片）：**

```
用户: [上传图片 sunset_01.jpg]
```

**输出 A：**

```json
{
    "images_uploaded": true,
    "image_paths": ["/output/reference/sunset_01.jpg"],
    "additional_description": null,
    "proceed_to": "step_4"
}
```

**输入示例 B（仅描述）：**

```
用户: 要有金色的阳光，海浪轻柔，海鸥飞翔
```

**输出 B：**

```json
{
    "images_uploaded": false,
    "image_paths": [],
    "additional_description": "要有金色的阳光，海浪轻柔，海鸥飞翔",
    "proceed_to": "step_4"
}
```

**输入示例 C（图片 + 描述）：**

```
用户: [上传图片 sunset_ref.jpg] 
      参考这张图的光线，但要更温暖一些
```

**输出 C：**

```json
{
    "images_uploaded": true,
    "image_paths": ["/output/reference/sunset_ref.jpg"],
    "additional_description": "参考这张图的光线，但要更温暖一些",
    "proceed_to": "step_4"
}
```

**输入示例 D（跳过）：**

```
用户: 不用了，直接继续
```

**输出 D：**

```json
{
    "images_uploaded": false,
    "image_paths": [],
    "additional_description": null,
    "proceed_to": "step_4"
}
```

### 步骤 3: 分支逻辑

```
补充材料
├── 用户上传图片 → 保存图片路径 → 进入步骤 4
├── 用户输入描述 → 记录描述内容 → 进入步骤 4
├── 用户上传图片 + 描述 → 保存两者 → 进入步骤 4
├── 用户跳过 → 进入步骤 4（无补充材料）
└── 用户取消 → 返回步骤 2 重新选择预设
```

---

## 步骤 4: 提示词优化

### 步骤 4: Agent 行为

Agent 使用 AI 模型优化用户输入的提示词，结合预设风格和参考图片生成最终提示词。

**优化流程：**
1. 收集所有输入信息
   - 选定的预设 ID
   - 用户原始描述
   - 补充描述（如有）
   - 参考图片路径（如有）
2. 调用优化模型生成结构化提示词
3. 展示优化结果给用户确认
4. 根据用户反馈调整或确认

**优化原则：**
- 保留用户核心意图
- 增强技术细节
- 添加风格修饰词
- 优化时间控制参数
- 符合视频生成模型的最佳实践

### 步骤 4: 用户行为

用户查看优化后的提示词，可以：
- 确认接受
- 请求调整（指定修改方向）
- 要求重新优化

### 步骤 4: 工具函数调用

```python
optimized = AgentTools.optimize_prompt(
    preset_ids=["realistic", "timelapse"],
    user_description="日落时分海边的画面",
    additional_description="金色的阳光，海浪轻柔",
    image_paths=["/output/reference/sunset_ref.jpg"]
)

# 返回结构
{
    "original_prompt": "日落时分海边的画面",
    "optimized_prompt": "A serene sunset scene at the beach, golden sunlight casting warm hues across the horizon, gentle waves rolling onto the sandy shore, seagulls gliding gracefully in the amber sky, realistic photography style with cinematic timelapse effect, smooth motion transition from golden hour to blue hour",
    "preset_applied": ["realistic", "timelapse"],
    "optimization_notes": [
        "Added cinematic descriptors",
        "Enhanced lighting details",
        "Included motion parameters"
    ]
}
```

### 步骤 4: 输入/输出示例

**输入示例：**

```json
{
    "preset_ids": ["realistic", "timelapse"],
    "user_description": "日落海边",
    "additional_description": "金色阳光，海浪",
    "image_paths": ["/output/reference/sunset_ref.jpg"]
}
```

**输出示例：**

```json
{
    "status": "optimized",
    "result": {
        "original_prompt": "日落海边",
        "optimized_prompt": "A breathtaking sunset over a tranquil beach, golden rays of sunlight piercing through scattered clouds, gentle waves creating rhythmic patterns on the pristine sand, silhouettes of distant ships on the horizon, realistic photography with smooth timelapse motion, transitioning from warm orange to deep purple hues",
        "word_count": 45,
        "estimated_quality": "high"
    },
    "confirmation_required": true
}
```

**用户确认示例：**

```
Agent: 优化后的提示词如下：
       "A breathtaking sunset over a tranquil beach..."
       
       是否满意？可以：
       - 回复"确认"继续
       - 回复"调整"并提出修改意见
       - 回复"重试"重新优化

用户: 把金色改成橙红色，加上海鸥
```

**调整后输出：**

```json
{
    "status": "adjusted",
    "result": {
        "optimized_prompt": "A breathtaking sunset over a tranquil beach, vibrant orange-red rays of sunlight piercing through scattered clouds, gentle waves creating rhythmic patterns on the pristine sand, seagulls soaring gracefully in the golden sky, silhouettes of distant ships on the horizon, realistic photography with smooth timelapse motion, transitioning from warm orange-red to deep purple hues",
        "adjustments": [
            "Changed 'golden' to 'orange-red'",
            "Added seagull description"
        ]
    }
}
```

### 步骤 4: 分支逻辑

```
提示词优化
├── 优化成功 → 展示给用户 → 等待确认
│   ├── 用户确认 → 进入步骤 5
│   ├── 用户要求调整 → 记录调整意见 → 重新优化
│   └── 用户要求重试 → 重新优化（保留原输入）
├── 优化失败 → 提示错误原因
│   ├── 服务不可用 → 询问是否手动输入
│   └── 参数错误 → 返回步骤 3 修正
└── 用户取消 → 询问是否保存当前进度
```

---

## 步骤 5: 导出或生成分支

### 步骤 5: Agent 行为

Agent 询问用户选择下一步操作：直接生成视频或导出提示词。

**询问内容：**

```
"优化完成！请选择下一步：
A. 立即生成视频（需要消耗配额）
B. 导出提示词（可到 Web 端手动生成）"
```

**决策依据：**
- 配额充足 → 推荐生成
- 配额不足 → 建议导出
- 用户偏好 → 记录选择

### 步骤 5: 用户行为

用户选择：
- **选项 A**: 生成视频 → 进入步骤 6
- **选项 B**: 导出提示词 → 执行导出流程

### 步骤 5: 工具函数调用

**分支 A: 导出提示词**

```python
export_result = AgentTools.export_prompt(
    prompt=optimized_prompt,
    preset_ids=["realistic", "timelapse"],
    output_format="markdown"  # 或 "json", "txt"
)

# 返回结构
{
    "status": "exported",
    "file_path": "/output/prompts/sunset_beach_20240122.md",
    "content": {
        "prompt": "A breathtaking sunset...",
        "presets": ["realistic", "timelapse"],
        "created_at": "2024-01-22T15:30:00Z"
    }
}
```

**分支 B: 继续生成**

```python
# 不调用特定工具，直接进入步骤 6
# 步骤 6 会调用 generate_video()
```

### 步骤 5: 输入/输出示例

**输入示例：**

```
用户: 导出提示词
```

**输出示例：**

```
Agent: ✅ 提示词已导出
       
       文件路径: /output/prompts/sunset_beach_20240122.md
       
       你可以使用此提示词在 Web 端手动生成视频。
       
       是否还需要其他帮助？
```

### 步骤 5: 分支逻辑

```
导出或生成
├── 用户选择导出 → 分支 A
│   ├── 调用 export_prompt() → 生成文件
│   ├── 展示文件路径 → 提供后续指导
│   └── 结束当前流程
├── 用户选择生成 → 分支 B
│   └── 进入步骤 6
├── 用户犹豫 → 展示配额信息帮助决策
│   ├── 配额充足 → 推荐生成
│   └── 配额不足 → 推荐导出
└── 用户取消 → 询问是否保存进度
```

**分支 A 详细流程：**

```
导出流程
├── 调用 AgentTools.export_prompt()
├── 生成文件
│   ├── Markdown 格式（默认）
│   ├── JSON 格式（可选）
│   └── 纯文本格式（可选）
├── 写入文件到 output/prompts/
├── 返回文件路径
└── 提供后续指导
    └── "可登录 Web 端，复制提示词进行生成"
```

**分支 B 详细流程：**

```
生成流程
├── 不执行特定操作
├── 保留所有参数
└── 进入步骤 6 进行参数确认
```

---

## 步骤 6: 确认并生成

### 步骤 6: Agent 行为

Agent 展示最终生成参数，等待用户确认后开始生成视频。

**确认内容：**

| 参数 | 值 | 说明 |
|------|-----|------|
| 提示词 | 优化后的文本 | 已优化的提示词 |
| 时长 | 5s / 10s | 视频时长 |
| 比例 | 16:9 / 9:16 / 1:1 | 画面比例 |
| 模型 | kling-v1 / kling-v1-5 | 生成模型 |
| 预估配额 | 5 积分 | 消耗预估 |

**生成流程：**
1. 用户确认参数
2. 调用生成 API
3. 返回任务 ID
4. 开始轮询进度
5. 展示进度条或百分比

**进度显示：**

```
生成中... 15% ████░░░░░░░░░░░░░░░░ 预计剩余 2 分钟
```

### 步骤 6: 用户行为

用户：
- 确认参数（回复"确认"或"开始"）
- 修改参数（回复"修改时长"等）
- 取消生成

### 步骤 6: 工具函数调用

```python
# 确认参数
generation_params = {
    "prompt": optimized_prompt,
    "duration": 5,
    "aspect_ratio": "16:9",
    "model": "kling-v1-5"
}

# 开始生成
result = AgentTools.generate_video(
    prompt=optimized_prompt,
    duration=5,
    aspect_ratio="16:9",
    model="kling-v1-5",
    image_references=image_paths  # 可选
)

# 返回结构
{
    "task_id": "task_abc123xyz",
    "status": "processing",
    "estimated_time": 180,
    "queue_position": 3
}
```

**轮询进度：**

```python
# 持续查询状态
while status != "completed":
    status = AgentTools.check_generation_status(task_id)
    # 返回结构
    {
        "task_id": "task_abc123xyz",
        "status": "processing",  # 或 "completed", "failed"
        "progress": 45,
        "remaining_time": 90
    }
    time.sleep(5)
```

### 步骤 6: 输入/输出示例

**输入示例：**

```
用户: 确认，开始生成
```

**输出示例（生成中）：**

```json
{
    "task_id": "task_abc123xyz",
    "status": "processing",
    "progress": 0,
    "message": "视频生成已开始，请稍候..."
}
```

**输出示例（进度更新）：**

```json
{
    "task_id": "task_abc123xyz",
    "status": "processing",
    "progress": 67,
    "remaining_seconds": 60,
    "message": "正在渲染场景..."
}
```

**输出示例（完成）：**

```json
{
    "task_id": "task_abc123xyz",
    "status": "completed",
    "progress": 100,
    "video_path": "/output/videos/sunset_beach_20240122.mp4",
    "thumbnail_path": "/output/thumbnails/sunset_beach_20240122.jpg",
    "metadata": {
        "duration": 5,
        "resolution": "1920x1080",
        "fps": 24,
        "file_size": 15728640
    }
}
```

### 步骤 6: 分支逻辑

```
确认并生成
├── 用户确认 → 开始生成
│   ├── 调用 generate_video()
│   ├── 返回 task_id
│   ├── 开始轮询进度
│   │   ├── 进度更新 → 显示进度条
│   │   ├── 状态为 completed → 进入步骤 7
│   │   ├── 状态为 failed → 显示错误，询问重试
│   │   └── 超时 → 提示网络问题，提供任务 ID
│   └── 轮询结束
├── 用户修改参数 → 返回参数确认
│   └── 更新参数后重新确认
├── 用户取消 → 询问是否保存进度
│   ├── 保存 → 导出提示词
│   └── 不保存 → 结束流程
└── 生成失败 → 分析错误原因
    ├── 配额不足 → 提示充值
    ├── 内容违规 → 提示修改提示词
    └── 服务错误 → 提供任务 ID，建议稍后查询
```

---

## 步骤 7: 完成

### 步骤 7: Agent 行为

Agent 展示生成结果，提供后续选项。

**结果展示：**

```
✅ 视频生成完成！

视频文件: /output/videos/sunset_beach_20240122.mp4
缩略图: /output/thumbnails/sunset_beach_20240122.jpg
提示词: /output/prompts/sunset_beach_20240122.md

时长: 5秒
分辨率: 1920x1080
大小: 15MB

接下来你可以：
1. 下载视频到本地
2. 保存预设组合
3. 重新生成
4. 生成新视频
```

### 步骤 7: 用户行为

用户选择后续操作：
- 下载视频
- 保存预设组合
- 使用相同参数重新生成
- 开始新的视频生成流程

### 步骤 7: 工具函数调用

```python
# 下载视频
download_result = AgentTools.download_video(
    video_path="/output/videos/sunset_beach_20240122.mp4",
    destination="/Users/Downloads"
)

# 返回结构
{
    "status": "downloaded",
    "destination": "/Users/Downloads/sunset_beach_20240122.mp4",
    "file_size": 15728640
}
```

```python
# 保存预设组合
save_result = AgentTools.save_preset_combo(
    name="日落海边",
    presets=["realistic", "timelapse"],
    prompt_template="A breathtaking sunset over {location}..."
)

# 返回结构
{
    "status": "saved",
    "combo_id": "combo_sunset_001",
    "message": "预设组合已保存，下次可直接调用"
}
```

### 步骤 7: 输入/输出示例

**输入示例 A（下载）：**

```
用户: 下载视频
```

**输出 A：**

```json
{
    "status": "success",
    "action": "download",
    "destination": "/Users/riggyeudy/Downloads/sunset_beach_20240122.mp4",
    "message": "视频已下载到 Downloads 文件夹"
}
```

**输入示例 B（保存组合）：**

```
用户: 保存这个预设组合，叫"日落海边"
```

**输出 B：**

```json
{
    "status": "success",
    "action": "save_combo",
    "combo_id": "combo_sunset_001",
    "combo_name": "日落海边",
    "presets": ["realistic", "timelapse"],
    "message": "预设组合已保存，下次可直接使用"
}
```

**输入示例 C（重新生成）：**

```
用户: 重新生成
```

**输出 C：**

```
Agent: 将使用相同参数重新生成视频。
       确认开始？
       
用户: 确认

[返回步骤 6]
```

**输入示例 D（新建）：**

```
用户: 生成新的视频
```

**输出 D：**

```
Agent: 好的，请描述你想生成的视频。
       
[返回步骤 1]
```

### 步骤 7: 分支逻辑

```
完成
├── 用户下载视频 → 调用 download_video()
│   ├── 成功 → 显示下载路径
│   └── 失败 → 提供视频路径手动下载
├── 用户保存组合 → 调用 save_preset_combo()
│   ├── 成功 → 显示组合名称和 ID
│   └── 失败 → 提示错误
├── 用户重新生成 → 返回步骤 6（使用相同参数）
├── 用户新建视频 → 返回步骤 1
└── 用户结束 → 结束对话
```

---

## 异常处理

### 常见异常及处理

| 异常类型 | 触发场景 | 处理方式 |
|----------|----------|----------|
| APIKeyInvalid | API 密钥无效或过期 | 提示用户检查 API_KEY 环境变量 |
| QuotaExceeded | 配额不足 | 提示充值或等待重置 |
| RateLimitExceeded | 请求频率超限 | 等待后重试，提供预计等待时间 |
| ContentViolation | 内容违反政策 | 提示修改提示词，说明违规原因 |
| GenerationFailed | 生成服务失败 | 提供任务 ID，建议稍后查询 |
| NetworkError | 网络连接失败 | 重试 3 次，失败后提示检查网络 |
| InvalidParameter | 参数无效 | 指出具体参数，提示正确格式 |

### 错误恢复流程

```
异常发生
├── 可恢复错误 → 自动重试
│   ├── NetworkError → 重试 3 次
│   └── RateLimitExceeded → 等待后重试
├── 用户可修复错误 → 提示用户
│   ├── APIKeyInvalid → 检查环境变量
│   ├── ContentViolation → 修改提示词
│   └── InvalidParameter → 修正参数
└── 不可恢复错误 → 记录日志，提供支持
    └── GenerationFailed → 提供任务 ID 和支持渠道
```

---

## 最佳实践

### 提示词编写建议

1. **明确场景**：清晰描述地点、时间、氛围
2. **添加细节**：包含颜色、光线、动态元素
3. **指定风格**：使用预设组合或描述期望风格
4. **控制时长**：根据内容选择合适时长
5. **参考图片**：提供参考图可提高效果一致性

### 预设选择建议

| 场景类型 | 推荐预设组合 |
|----------|--------------|
| 自然风景 | realistic + timelapse |
| 城市景观 | cinematic + timelapse |
| 人物动作 | realistic + slowmo |
| 创意短片 | cinematic + shuttle |
| 产品展示 | realistic |

### 常见问题

**Q: 生成时间过长怎么办？**
A: 检查网络连接，或选择较短的时长。5 秒视频通常需要 2-3 分钟。

**Q: 如何提高生成质量？**
A: 优化提示词，添加参考图片，选择合适的预设组合。

**Q: 可以同时生成多个视频吗？**
A: 目前不支持并行生成，请等待当前任务完成后再开始新任务。

**Q: 生成的视频不满意怎么办？**
A: 可以使用"重新生成"功能，或调整提示词和预设后重新生成。

---

## 版本信息

- 文档版本: 1.0.0
- 更新日期: 2024-01-22
- 适用于: video-gen v1.0.0+