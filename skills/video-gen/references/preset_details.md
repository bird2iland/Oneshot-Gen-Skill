# 预设详解文档 (Preset Details)

本详细说明了视频生成系统中 9 个核心预设的功能、特性和使用场景。

---

## 目录

- [概述](#概述)
  - [预设系统架构](#预设系统架构)
  - [三个维度说明](#三个维度说明)
  - [预设组合原则](#预设组合原则)
- [视觉风格预设 (Visual Style Presets)](#视觉风格预设-visual-style-presets)
  - [realistic - 写实风格](#realistic---写实风格)
  - [pixel_art - 像素风格](#pixel_art---像素风格)
  - [oil_painting - 油画风格](#oil_painting---油画风格)
- [时间采样预设 (Time Sampling Presets)](#时间采样预设-time-sampling-presets)
  - [timelapse - 延时摄影](#timelapse---延时摄影)
  - [slow_motion - 升格慢动作](#slow_motion---升格慢动作)
  - [normal - 常规速度](#normal---常规速度)
- [运镜风格预设 (Camera Movement Presets)](#运镜风格预设-camera-movement-presets)
  - [shuttle - 穿梭机](#shuttle---穿梭机)
  - [gimbal - 稳定器](#gimbal---稳定器)
  - [handheld - 手持](#handheld---手持)
- [预设组合指南](#预设组合指南)
  - [推荐组合](#推荐组合)
  - [冲突组合](#冲突组合)
  - [高级组合技巧](#高级组合技巧)
- [使用最佳实践](#使用最佳实践)
- [附录](#附录)

---

## 概述

### 预设系统架构

预设系统采用三维正交设计，每个维度独立控制视频生成的特定方面：

| 维度 | 英文名称 | 中文名称 | 控制内容 | 预设数量 |
|------|----------|----------|----------|----------|
| 视觉风格 | Visual Style | 视觉风格 | 画面渲染风格和美学效果 | 3 |
| 时间采样 | Time Sampling | 时间采样 | 时间流速和播放速度 | 3 |
| 运镜风格 | Camera Movement | 运镜风格 | 镜头运动方式和稳定度 | 3 |

**组合公式：** `最终预设 = 视觉风格 + 时间采样 + 运镜风格`

理论组合数：3 × 3 × 3 = 27 种（需排除冲突组合）

### 三个维度说明

#### 视觉风格维度

视觉风格决定视频的整体美学呈现，影响：
- 渲染管线选择
- 后处理效果
- 色彩校正风格
- 纹理细节处理

#### 时间采样维度

时间采样控制视频的时间感知，影响：
- 播放速度
- 帧率处理
- 运动模糊
- 时间压缩/拉伸效果

#### 运镜风格维度

运镜风格定义镜头的运动特性，影响：
- 镜头稳定性
- 运动轨迹
- 动态感
- 视觉叙事方式

### 预设组合原则

**基本原则：**

1. **兼容性原则**：同一维度内预设互斥，不同维度间预设兼容
2. **美学一致原则**：组合后的预设应在美学上协调统一
3. **场景适配原则**：根据具体使用场景选择最合适的预设组合
4. **冲突避免原则**：某些预设组合会产生冲突，需要避免

**冲突矩阵：**

| 预设 A | 冲突预设 | 原因 |
|--------|----------|------|
| timelapse | slow_motion | 时间采样方向相反 |
| gimbal | handheld | 运镜稳定特性相反 |

---

## 视觉风格预设 (Visual Style Presets)

---

### realistic - 写实风格

#### 基本信息

| 属性 | 值 |
|------|-----|
| **预设 ID** | `realistic` |
| **中文名称** | 写实风格 |
| **英文名称** | Realistic Style |
| **所属维度** | 视觉风格 (Visual Style) |
| **优先级** | 高（默认预设） |

#### 描述

写实风格致力于呈现最接近真实世界的视觉效果，通过高精度的渲染和自然的光照处理，创造出具有照片级真实感的视频内容。该风格适用于大多数正式场景和商业应用，是系统默认的视觉风格预设。

#### 关键词列表

| 关键词 | 描述 |
|--------|------|
| `photorealistic` | 照片级真实感 |
| `detailed` | 高细节呈现 |
| `realistic` | 写实风格 |
| `high fidelity` | 高保真度 |
| `natural lighting` | 自然光照效果 |
| `true-to-life` | 逼真还原 |
| `sharp focus` | 锐利对焦 |
| `cinematic` | 电影质感 |
| `8K quality` | 8K画质 |
| `HDR` | 高动态范围 |

#### 适用场景

| 场景类型 | 具体应用 | 推荐指数 |
|----------|----------|----------|
| 城市风光 | 城市宣传片、建筑展示、街景记录 | ★★★★★ |
| 自然景观 | 自然纪录片、风景拍摄、环境展示 | ★★★★★ |
| 人物视频 | 人物访谈、肖像展示、日常记录 | ★★★★★ |
| 产品展示 | 商业广告、产品宣传片、电商视频 | ★★★★☆ |
| 活动记录 | 会议记录、活动剪辑、现场拍摄 | ★★★★☆ |
| 教育培训 | 在线课程、操作演示、教学视频 | ★★★★☆ |

#### 与其他预设的组合建议

**推荐组合：**

| 组合名称 | 组合配置 | 效果描述 | 适用场景 |
|----------|----------|----------|----------|
| 城市延时穿梭 | realistic + timelapse + shuttle | 真实感强的城市延时穿梭效果 | 城市宣传片、建筑展示 |
| 稳定风光 | realistic + gimbal | 平滑稳定的风光视频 | 自然风景、风光摄影 |
| 日常记录 | realistic + normal + handheld | 自然真实的日常记录风格 | Vlog、生活记录 |
| 专业商业 | realistic + slow_motion + gimbal | 高质感商业广告效果 | 产品广告、品牌宣传 |

**组合效果评分：**

| 时间采样 | 运镜风格 | 效果评分 | 备注 |
|----------|----------|----------|------|
| timelapse | shuttle | ★★★★★ | 最佳组合：城市延时 |
| timelapse | gimbal | ★★★★☆ | 适合静态场景延时 |
| slow_motion | gimbal | ★★★★★ | 商业广告常用 |
| slow_motion | handheld | ★★★☆☆ | 艺术表达使用 |
| normal | gimbal | ★★★★☆ | 稳定专业感 |
| normal | handheld | ★★★★☆ | 自然纪录片感 |
| normal | shuttle | ★★★☆☆ | 特殊动态效果 |

#### 使用示例

**示例 1：城市宣传片**

```
预设配置：realistic + timelapse + shuttle
提示词：Aerial view of modern city skyline at sunset, photorealistic, timelapse, shuttle cam movement
输出效果：展现城市日落时分的延时穿梭效果，建筑灯光渐亮，车流穿梭
```

**示例 2：自然风光纪录片**

```
预设配置：realistic + slow_motion + gimbal
提示词：Mountain landscape with flowing river, photorealistic, slow motion, gimbal shot, smooth movement
输出效果：平滑稳定的山间河流慢动作，展现水的流动细节
```

**示例 3：产品广告**

```
预设配置：realistic + normal + gimbal
提示词：Luxury watch product shot, photorealistic, detailed texture, gimbal tracking shot
输出效果：专业的产品展示视频，平滑运镜展现产品细节
```

---

### pixel_art - 像素风格

#### 基本信息

| 属性 | 值 |
|------|-----|
| **预设 ID** | `pixel_art` |
| **中文名称** | 像素风格 |
| **英文名称** | Pixel Art Style |
| **所属维度** | 视觉风格 (Visual Style) |
| **优先级** | 中 |

#### 描述

像素风格通过模拟经典8位和16位游戏机的视觉效果，创造出独特的复古数字美学。该风格以像素为基本单位构建画面，具有强烈的怀旧感和游戏化特征，适合创意表达和复古主题内容。

#### 关键词列表

| 关键词 | 描述 |
|--------|------|
| `pixel art` | 像素艺术风格 |
| `retro` | 复古风格 |
| `8-bit style` | 8位风格 |
| `nostalgic` | 怀旧感 |
| `game aesthetic` | 游戏美学 |
| `low resolution` | 低分辨率效果 |
| `blocky` | 块状像素感 |
| `sprite` | 精灵图风格 |
| `NES style` | 红白机风格 |
| `chiptune aesthetic` | 芯片音乐美学 |

#### 适用场景

| 场景类型 | 具体应用 | 推荐指数 |
|----------|----------|----------|
| 复古游戏 | 游戏宣传片、复古游戏展示、像素游戏开发 | ★★★★★ |
| 创意视频 | 艺术创作、实验性视频、创意短片 | ★★★★☆ |
| 怀旧内容 | 怀旧主题、回忆录、年代感视频 | ★★★★☆ |
| 社交媒体 | 短视频、表情包动画、趣味内容 | ★★★★☆ |
| 音乐视频 | 电子音乐MV、芯片音乐配乐视频 | ★★★★☆ |
| 教育娱乐 | 编程教学、游戏设计课程 | ★★★☆☆ |

#### 与其他预设的组合建议

**推荐组合：**

| 组合名称 | 组合配置 | 效果描述 | 适用场景 |
|----------|----------|----------|----------|
| 复古叙事 | pixel_art + normal + handheld | 自然真实的复古叙事风格 | 怀旧短片、回忆录 |
| 像素冒险 | pixel_art + timelapse + shuttle | 快速动态的像素冒险效果 | 游戏宣传片、动作场景 |
| 像素慢动作 | pixel_art + slow_motion + gimbal | 独特的艺术慢动作效果 | 创意短片、艺术表达 |

**组合效果评分：**

| 时间采样 | 运镜风格 | 效果评分 | 备注 |
|----------|----------|----------|------|
| timelapse | shuttle | ★★★★☆ | 动态像素效果 |
| timelapse | gimbal | ★★★☆☆ | 稳定像素延时 |
| slow_motion | gimbal | ★★★★☆ | 艺术慢动作 |
| slow_motion | handheld | ★★★☆☆ | 实验性效果 |
| normal | gimbal | ★★★☆☆ | 平稳像素动画 |
| normal | handheld | ★★★★★ | 最佳组合：复古叙事 |
| normal | shuttle | ★★★★☆ | 动态像素效果 |

#### 使用示例

**示例 1：复古游戏宣传片**

```
预设配置：pixel_art + normal + handheld
提示词：8-bit pixel art game scene, retro video game aesthetic, character walking through forest, normal speed, handheld camera feel
输出效果：模拟经典游戏画面的角色行走动画，带有自然的手持镜头感
```

**示例 2：怀旧主题视频**

```
预设配置：pixel_art + slow_motion + gimbal
提示词：Pixel art sunset over pixelated city, slow motion, smooth gimbal movement, nostalgic atmosphere
输出效果：像素风格的城市日落慢动作，平滑稳定的运镜增强艺术感
```

**示例 3：创意短片**

```
预设配置：pixel_art + timelapse + shuttle
提示词：Pixel art timelapse of building construction, shuttle cam movement, retro game aesthetic
输出效果：像素风格的建筑建造延时，快速穿梭的动态效果
```

---

### oil_painting - 油画风格

#### 基本信息

| 属性 | 值 |
|------|-----|
| **预设 ID** | `oil_painting` |
| **中文名称** | 油画风格 |
| **英文名称** | Oil Painting Style |
| **所属维度** | 视觉风格 (Visual Style) |
| **优先级** | 中 |

#### 描述

油画风格将视频转化为具有传统油画艺术感的视觉呈现，模拟画笔笔触和油画特有的质感。该风格适合艺术性表达、创意视频和需要强烈艺术气息的内容，能够将普通场景转化为艺术作品。

#### 关键词列表

| 关键词 | 描述 |
|--------|------|
| `oil painting` | 油画风格 |
| `artistic` | 艺术感 |
| `brush strokes` | 画笔笔触 |
| `painterly` | 绘画质感 |
| `impressionist` | 印象派风格 |
| `textured` | 纹理感 |
| `canvas` | 画布质感 |
| `classic art` | 经典艺术 |
| `rich colors` | 丰富色彩 |
| `expressive` | 表现力强 |

#### 适用场景

| 场景类型 | 具体应用 | 推荐指数 |
|----------|----------|----------|
| 艺术视频 | 艺术创作视频、画廊展示、艺术短片 | ★★★★★ |
| 创意表达 | 实验性视频、艺术项目、创意广告 | ★★★★★ |
| 风景艺术化 | 风景艺术处理、自然风光艺术化 | ★★★★☆ |
| 文化内容 | 文化遗产展示、博物馆内容、历史主题 | ★★★★☆ |
| 音乐视频 | 艺术MV、情感表达视频 | ★★★★☆ |
| 品牌艺术 | 艺术品牌宣传片、高端品牌形象 | ★★★☆☆ |

#### 与其他预设的组合建议

**推荐组合：**

| 组合名称 | 组合配置 | 效果描述 | 适用场景 |
|----------|----------|----------|----------|
| 艺术慢动作 | oil_painting + slow_motion + gimbal | 油画风格的平滑慢动作效果 | 风景艺术、情感表达 |
| 艺术延时 | oil_painting + timelapse + shuttle | 动态艺术延时效果 | 城市艺术化、创意表达 |
| 静态艺术 | oil_painting + normal + gimbal | 平稳的艺术展示效果 | 画廊展示、艺术短片 |

**组合效果评分：**

| 时间采样 | 运镜风格 | 效果评分 | 备注 |
|----------|----------|----------|------|
| timelapse | shuttle | ★★★★☆ | 动态艺术效果 |
| timelapse | gimbal | ★★★★☆ | 稳定艺术延时 |
| slow_motion | gimbal | ★★★★★ | 最佳组合：艺术慢动作 |
| slow_motion | handheld | ★★★★☆ | 自然艺术感 |
| normal | gimbal | ★★★★☆ | 平稳艺术展示 |
| normal | handheld | ★★★☆☆ | 纪录片艺术风格 |
| normal | shuttle | ★★★☆☆ | 特殊艺术效果 |

#### 使用示例

**示例 1：风景艺术化视频**

```
预设配置：oil_painting + slow_motion + gimbal
提示词：Oil painting style landscape, golden wheat field at sunset, slow motion, smooth gimbal tracking, impressionist brush strokes
输出效果：油画风格的金色麦田日落慢动作，平滑运镜展现艺术质感
```

**示例 2：城市艺术短片**

```
预设配置：oil_painting + timelapse + shuttle
提示词：Oil painting style city timelapse, shuttle cam movement, impressionist urban landscape
输出效果：油画风格的城市延时穿梭，将城市景观艺术化呈现
```

**示例 3：文化主题视频**

```
预设配置：oil_painting + normal + gimbal
提示词：Oil painting style classical architecture, painterly effect, gimbal smooth tracking, artistic heritage
输出效果：油画风格的古典建筑平稳运镜展示，适合文化遗产主题
```

---

## 时间采样预设 (Time Sampling Presets)

---

### timelapse - 延时摄影

#### 基本信息

| 属性 | 值 |
|------|-----|
| **预设 ID** | `timelapse` |
| **中文名称** | 延时摄影 |
| **英文名称** | Time-lapse |
| **所属维度** | 时间采样 (Time Sampling) |
| **优先级** | 高 |

#### 描述

延时摄影通过加速时间流逝，将长时间的过程压缩到短时间内呈现。该预设适合展现时间变化、物体移动、光影变迁等需要时间压缩效果的场景，能够创造独特的视觉体验。

#### 关键词列表

| 关键词 | 描述 |
|--------|------|
| `timelapse` | 延时摄影 |
| `time-lapse` | 延时摄影（备选拼写） |
| `time passing` | 时间流逝 |
| `accelerated time` | 加速时间 |
| `fast forward` | 快进效果 |
| `time compression` | 时间压缩 |
| `speed up` | 加速 |
| `time progression` | 时间推进 |
| `hours in seconds` | 数小时浓缩于秒 |
| `temporal acceleration` | 时间加速 |

#### 适用场景

| 场景类型 | 具体应用 | 推荐指数 |
|----------|----------|----------|
| 城市延时 | 城市宣传片、建筑建造、城市风光 | ★★★★★ |
| 日出日落 | 自然风光、天空变化、光影展示 | ★★★★★ |
| 植物生长 | 自然纪录片、植物成长、生态展示 | ★★★★★ |
| 交通流动 | 交通展示、人流记录、车流展示 | ★★★★☆ |
| 云层变化 | 天气展示、云海流动、天空景观 | ★★★★☆ |
| 星空轨迹 | 星空摄影、天文延时、夜间景观 | ★★★★☆ |

#### 冲突说明

**冲突预设：** `slow_motion`

**冲突原因：** 延时摄影与升格慢动作的时间采样方向相反。延时摄影加速时间，慢动作减缓时间，两者在物理逻辑上互斥，无法同时应用。

**解决方案：** 
- 如需展示时间流逝的某些细节，可分段处理：前半段延时，后半段慢动作
- 或使用 normal 预设作为中间过渡

#### 与其他预设的组合建议

**推荐组合：**

| 组合名称 | 组合配置 | 效果描述 | 适用场景 |
|----------|----------|----------|----------|
| 城市穿梭延时 | realistic + timelapse + shuttle | 真实感城市穿梭延时 | 城市宣传片、建筑展示 |
| 艺术延时 | oil_painting + timelapse + gimbal | 油画风格的稳定延时 | 艺术视频、创意表达 |
| 复古延时 | pixel_art + timelapse + shuttle | 像素风格的动态延时 | 复古游戏、创意内容 |

**组合效果评分：**

| 视觉风格 | 运镜风格 | 效果评分 | 备注 |
|----------|----------|----------|------|
| realistic | shuttle | ★★★★★ | 最佳组合：城市穿梭 |
| realistic | gimbal | ★★★★☆ | 稳定风光延时 |
| realistic | handheld | ★★★☆☆ | 自然纪录片感 |
| pixel_art | shuttle | ★★★★☆ | 动态像素效果 |
| pixel_art | gimbal | ★★★☆☆ | 稳定像素延时 |
| oil_painting | shuttle | ★★★★☆ | 动态艺术效果 |
| oil_painting | gimbal | ★★★★☆ | 稳定艺术延时 |

#### 使用示例

**示例 1：城市夜景延时**

```
预设配置：realistic + timelapse + shuttle
提示词：Urban city skyline at night, timelapse from dusk to night, shuttle cam movement, city lights turning on, photorealistic
输出效果：城市黄昏到夜晚的延时穿梭，灯光逐渐亮起，展现城市活力
```

**示例 2：星空轨迹延时**

```
预设配置：realistic + timelapse + gimbal
提示词：Night sky timelapse with star trails, gimbal stabilized, photorealistic, clear mountain sky
输出效果：稳定拍摄的星空轨迹延时，星星划过天际的壮美景象
```

**示例 3：植物生长延时**

```
预设配置：realistic + timelapse + gimbal
提示词：Flower blooming timelapse, natural lighting, gimbal shot, photorealistic, days compressed to seconds
输出效果：花朵绽放的全过程延时，展现生命的美好瞬间
```

---

### slow_motion - 升格慢动作

#### 基本信息

| 属性 | 值 |
|------|-----|
| **预设 ID** | `slow_motion` |
| **中文名称** | 升格慢动作 |
| **英文名称** | Slow Motion |
| **所属维度** | 时间采样 (Time Sampling) |
| **优先级** | 高 |

#### 描述

升格慢动作通过降低播放速度，展现快速运动中的细节和瞬间。该预设能够捕捉人眼难以察觉的细节，增强动作的表现力和情感张力，常用于运动、动作、情感表达等场景。

#### 关键词列表

| 关键词 | 描述 |
|--------|------|
| `slow motion` | 慢动作 |
| `high speed` | 高速摄影 |
| `smooth` | 平滑流畅 |
| `slo-mo` | 慢动作（口语） |
| `temporal stretch` | 时间拉伸 |
| `frame interpolation` | 帧插值 |
| `detailed motion` | 细节动作 |
| `time dilation` | 时间膨胀 |
| `fluid movement` | 流畅运动 |
| `crystallized moment` | 凝固瞬间 |

#### 适用场景

| 场景类型 | 具体应用 | 推荐指数 |
|----------|----------|----------|
| 运动细节 | 体育运动、动作捕捉、极限运动 | ★★★★★ |
| 自然流畅 | 水流、瀑布、自然元素 | ★★★★★ |
| 情感表达 | 情感场景、人物特写、氛围营造 | ★★★★☆ |
| 产品展示 | 产品广告、细节展示、高端商业 | ★★★★☆ |
| 自然现象 | 雨滴、烟雾、爆炸、破碎 | ★★★★☆ |
| 动物行为 | 动物运动、鸟类飞行、快速动物 | ★★★★☆ |

#### 冲突说明

**冲突预设：** `timelapse`

**冲突原因：** 升格慢动作与延时摄影的时间采样方向相反。慢动作减速时间，延时摄影加速时间，两者在物理逻辑上互斥，无法同时应用。

**解决方案：** 
- 如需展示快慢对比，可分段处理
- 或使用 normal 预设作为过渡

#### 与其他预设的组合建议

**推荐组合：**

| 组合名称 | 组合配置 | 效果描述 | 适用场景 |
|----------|----------|----------|----------|
| 商业慢动作 | realistic + slow_motion + gimbal | 专业的商业广告慢动作 | 产品广告、品牌宣传 |
| 艺术慢动作 | oil_painting + slow_motion + gimbal | 油画风格的艺术慢动作 | 艺术视频、创意表达 |
| 自然纪录 | realistic + slow_motion + handheld | 自然真实的慢动作记录 | 纪录片、自然拍摄 |

**组合效果评分：**

| 视觉风格 | 运镜风格 | 效果评分 | 备注 |
|----------|----------|----------|------|
| realistic | gimbal | ★★★★★ | 最佳组合：商业广告 |
| realistic | handheld | ★★★★☆ | 自然纪录片感 |
| realistic | shuttle | ★★★☆☆ | 特殊动态效果 |
| pixel_art | gimbal | ★★★★☆ | 艺术慢动作 |
| pixel_art | handheld | ★★★☆☆ | 实验性效果 |
| oil_painting | gimbal | ★★★★★ | 艺术慢动作 |
| oil_painting | handheld | ★★★★☆ | 自然艺术感 |

#### 使用示例

**示例 1：水流慢动作**

```
预设配置：realistic + slow_motion + gimbal
提示词：Water flowing over rocks in slow motion, photorealistic, gimbal stabilized, smooth movement, natural lighting
输出效果：平滑稳定的水流慢动作，展现水的细腻流动和波光粼粼
```

**示例 2：运动瞬间**

```
预设配置：realistic + slow_motion + handheld
提示词：Athlete jumping in slow motion, photorealistic, handheld camera, dynamic angle, detailed motion capture
输出效果：自然手持感的运动慢动作，捕捉跳跃的精彩瞬间
```

**示例 3：艺术表达**

```
预设配置：oil_painting + slow_motion + gimbal
提示词：Oil painting style slow motion of falling petals, gimbal smooth tracking, impressionist brush strokes, artistic
输出效果：油画风格的花瓣飘落慢动作，艺术感强烈的视觉呈现
```

---

### normal - 常规速度

#### 基本信息

| 属性 | 值 |
|------|-----|
| **预设 ID** | `normal` |
| **中文名称** | 常规速度 |
| **英文名称** | Normal Speed |
| **所属维度** | 时间采样 (Time Sampling) |
| **优先级** | 高（默认预设） |

#### 描述

常规速度预设保持视频的正常播放速度，不进行时间压缩或拉伸处理。该预设是系统默认的时间采样设置，适用于大多数标准视频场景，是叙事视频和基础内容的首选。

#### 关键词列表

| 关键词 | 描述 |
|--------|------|
| `normal speed` | 常规速度 |
| `natural flow` | 自然流畅 |
| `standard playback` | 标准播放 |
| `real-time` | 实时 |
| `normal timing` | 常规时序 |
| `regular pace` | 常规节奏 |
| `standard rate` | 标准速率 |
| `default timing` | 默认时序 |
| `natural rhythm` | 自然节奏 |
| `unchanged speed` | 不变速 |

#### 适用场景

| 场景类型 | 具体应用 | 推荐指数 |
|----------|----------|----------|
| 叙事视频 | 故事片、短片、叙事内容 | ★★★★★ |
| 基础场景 | 日常记录、常规拍摄 | ★★★★★ |
| 教育培训 | 教学视频、操作演示、课程内容 | ★★★★☆ |
| 采访对话 | 人物访谈、对话场景 | ★★★★☆ |
| 产品介绍 | 产品展示、功能介绍 | ★★★★☆ |
| 活动记录 | 会议、活动、现场记录 | ★★★★☆ |

#### 与其他预设的组合建议

**推荐组合：**

| 组合名称 | 组合配置 | 效果描述 | 适用场景 |
|----------|----------|----------|----------|
| 自然纪录 | realistic + normal + handheld | 自然真实的记录风格 | 纪录片、Vlog、日常 |
| 专业展示 | realistic + normal + gimbal | 平稳专业的展示效果 | 商业视频、产品介绍 |
| 复古叙事 | pixel_art + normal + handheld | 像素风格的叙事视频 | 复古游戏、怀旧内容 |
| 艺术短片 | oil_painting + normal + gimbal | 油画风格的艺术短片 | 艺术创作、文化内容 |

**组合效果评分：**

| 视觉风格 | 运镜风格 | 效果评分 | 备注 |
|----------|----------|----------|------|
| realistic | gimbal | ★★★★☆ | 专业稳定感 |
| realistic | handheld | ★★★★★ | 最佳组合：自然纪录 |
| realistic | shuttle | ★★★☆☆ | 特殊动态效果 |
| pixel_art | gimbal | ★★★☆☆ | 平稳像素动画 |
| pixel_art | handheld | ★★★★★ | 复古叙事风格 |
| oil_painting | gimbal | ★★★★☆ | 平稳艺术展示 |
| oil_painting | handheld | ★★★☆☆ | 纪录片艺术感 |

#### 使用示例

**示例 1：日常Vlog**

```
预设配置：realistic + normal + handheld
提示词：Daily vlog walking through city streets, normal speed, handheld camera feel, photorealistic, natural flow
输出效果：自然真实的城市街道行走记录，具有手持镜头的生活感
```

**示例 2：产品介绍**

```
预设配置：realistic + normal + gimbal
提示词：Product showcase video, normal speed, gimbal stabilized tracking shot, photorealistic, professional
输出效果：平稳专业的产品展示视频，适合商业用途
```

**示例 3：复古游戏叙事**

```
预设配置：pixel_art + normal + handheld
提示词：8-bit pixel art game story scene, normal speed, handheld documentary feel, retro nostalgic
输出效果：像素风格的游戏叙事视频，具有复古怀旧感
```

---

## 运镜风格预设 (Camera Movement Presets)

---

### shuttle - 穿梭机

#### 基本信息

| 属性 | 值 |
|------|-----|
| **预设 ID** | `shuttle` |
| **中文名称** | 穿梭机 |
| **英文名称** | Shuttle Cam |
| **所属维度** | 运镜风格 (Camera Movement) |
| **优先级** | 中 |

#### 描述

穿梭机运镜模拟高速移动的动态效果，创造强烈的动感和视觉冲击力。该预设适合快速穿越场景、动态展示和需要强烈运动感的视频内容，常用于城市穿梭、场景过渡和动感展示。

#### 关键词列表

| 关键词 | 描述 |
|--------|------|
| `shuttle cam` | 穿梭机镜头 |
| `fast movement` | 快速移动 |
| `dynamic` | 动态感 |
| `speed` | 速度感 |
| `rapid transit` | 快速穿越 |
| `flying through` | 飞越感 |
| `velocity` | 高速 |
| `kinetic` | 运动感 |
| `whoosh` | 呼啸感 |
| `immersive movement` | 沉浸式运动 |

#### 适用场景

| 场景类型 | 具体应用 | 推荐指数 |
|----------|----------|----------|
| 城市穿梭 | 城市宣传片、建筑穿梭、街道穿越 | ★★★★★ |
| 动态展示 | 动态场景、运动展示、动感视频 | ★★★★☆ |
| 场景过渡 | 场景切换、空间转换、过渡效果 | ★★★★☆ |
| 广告创意 | 创意广告、品牌宣传片 | ★★★★☆ |
| 音乐视频 | 动感MV、节奏感强的视频 | ★★★★☆ |
| 极限运动 | 极限运动展示、高速运动 | ★★★★☆ |

#### 与其他预设的组合建议

**推荐组合：**

| 组合名称 | 组合配置 | 效果描述 | 适用场景 |
|----------|----------|----------|----------|
| 城市穿梭延时 | realistic + timelapse + shuttle | 真实感的城市穿梭延时 | 城市宣传片、建筑展示 |
| 动态像素 | pixel_art + timelapse + shuttle | 像素风格的动态穿梭 | 游戏宣传片、复古内容 |
| 艺术穿梭 | oil_painting + timelapse + shuttle | 油画风格的艺术穿梭 | 艺术视频、创意表达 |

**组合效果评分：**

| 视觉风格 | 时间采样 | 效果评分 | 备注 |
|----------|----------|----------|------|
| realistic | timelapse | ★★★★★ | 最佳组合：城市穿梭 |
| realistic | slow_motion | ★★★☆☆ | 特殊动态效果 |
| realistic | normal | ★★★☆☆ | 常规动态视频 |
| pixel_art | timelapse | ★★★★☆ | 动态像素效果 |
| pixel_art | normal | ★★★★☆ | 动态像素动画 |
| oil_painting | timelapse | ★★★★☆ | 动态艺术效果 |
| oil_painting | normal | ★★★☆☆ | 艺术动态视频 |

#### 使用示例

**示例 1：城市穿梭**

```
预设配置：realistic + timelapse + shuttle
提示词：Flying through city streets at sunset, shuttle cam movement, timelapse effect, photorealistic, dynamic motion
输出效果：夕阳下快速穿梭城市街道的延时效果，展现城市活力
```

**示例 2：游戏场景穿梭**

```
预设配置：pixel_art + normal + shuttle
提示词：8-bit pixel art game world, shuttle cam flying through level, retro aesthetic, fast movement
输出效果：像素风格游戏世界的快速穿梭，复古游戏感强烈
```

**示例 3：艺术空间穿梭**

```
预设配置：oil_painting + timelapse + shuttle
提示词：Oil painting style art gallery timelapse, shuttle cam movement, impressionist, dynamic visual
输出效果：油画风格的艺术画廊穿梭延时，独特的视觉体验
```

---

### gimbal - 稳定器

#### 基本信息

| 属性 | 值 |
|------|-----|
| **预设 ID** | `gimbal` |
| **中文名称** | 稳定器 |
| **英文名称** | Gimbal Shot |
| **所属维度** | 运镜风格 (Camera Movement) |
| **优先级** | 高 |

#### 描述

稳定器运镜提供平滑稳定的镜头运动，消除抖动和不稳定因素，创造专业级的画面质感。该预设适合需要稳定画面的专业拍摄，常用于风光视频、商业广告和专业内容制作。

#### 关键词列表

| 关键词 | 描述 |
|--------|------|
| `gimbal shot` | 稳定器镜头 |
| `smooth` | 平滑 |
| `stabilized` | 稳定 |
| `steady` | 稳固 |
| `tracking` | 跟踪拍摄 |
| `fluid movement` | 流畅运动 |
| `professional` | 专业级 |
| `cinematic smooth` | 电影级平滑 |
| `drift` | 漂移感 |
| `gliding` | 滑行感 |

#### 适用场景

| 场景类型 | 具体应用 | 推荐指数 |
|----------|----------|----------|
| 风光视频 | 自然风光、风景摄影、旅游视频 | ★★★★★ |
| 专业拍摄 | 商业广告、品牌宣传、企业视频 | ★★★★★ |
| 产品展示 | 产品广告、电商视频、细节展示 | ★★★★☆ |
| 建筑展示 | 建筑摄影、室内设计、空间展示 | ★★★★☆ |
| 活动记录 | 婚礼、会议、正式活动 | ★★★★☆ |
| 教育培训 | 在线课程、教学视频、演示 | ★★★★☆ |

#### 冲突说明

**冲突预设：** `handheld`

**冲突原因：** 稳定器与手持的运镜特性相反。稳定器追求平滑稳定，手持追求自然晃动，两者在视觉效果上互斥，无法同时应用。

**解决方案：** 
- 根据场景需求选择：专业展示用 gimbal，自然记录用 handheld
- 如需混合效果，可在不同片段分别应用

#### 与其他预设的组合建议

**推荐组合：**

| 组合名称 | 组合配置 | 效果描述 | 适用场景 |
|----------|----------|----------|----------|
| 专业风光 | realistic + normal + gimbal | 平稳专业的风光展示 | 自然风光、旅游视频 |
| 商业广告 | realistic + slow_motion + gimbal | 高质感商业慢动作 | 产品广告、品牌宣传 |
| 艺术慢动作 | oil_painting + slow_motion + gimbal | 油画风格的艺术慢动作 | 艺术视频、创意表达 |

**组合效果评分：**

| 视觉风格 | 时间采样 | 效果评分 | 备注 |
|----------|----------|----------|------|
| realistic | timelapse | ★★★★☆ | 稳定风光延时 |
| realistic | slow_motion | ★★★★★ | 最佳组合：商业广告 |
| realistic | normal | ★★★★☆ | 专业稳定感 |
| pixel_art | timelapse | ★★★☆☆ | 稳定像素延时 |
| pixel_art | slow_motion | ★★★★☆ | 艺术慢动作 |
| pixel_art | normal | ★★★☆☆ | 平稳像素动画 |
| oil_painting | timelapse | ★★★★☆ | 稳定艺术延时 |
| oil_painting | slow_motion | ★★★★★ | 艺术慢动作 |
| oil_painting | normal | ★★★★☆ | 平稳艺术展示 |

#### 使用示例

**示例 1：风光视频**

```
预设配置：realistic + normal + gimbal
提示词：Mountain landscape with lake reflection, gimbal smooth tracking, photorealistic, professional cinematic
输出效果：平滑稳定的风光视频，展现山脉和湖泊的宁静之美
```

**示例 2：产品广告**

```
预设配置：realistic + slow_motion + gimbal
提示词：Luxury car commercial shot, slow motion, gimbal stabilized, photorealistic, smooth tracking
输出效果：专业级的产品广告慢动作，平滑运镜展现汽车细节
```

**示例 3：艺术表达**

```
预设配置：oil_painting + slow_motion + gimbal
提示词：Oil painting style flower garden, slow motion, gimbal smooth movement, artistic brush strokes
输出效果：油画风格的花园慢动作，平滑运镜增强艺术感
```

---

### handheld - 手持

#### 基本信息

| 属性 | 值 |
|------|-----|
| **预设 ID** | `handheld` |
| **中文名称** | 手持 |
| **英文名称** | Handheld Camera |
| **所属维度** | 运镜风格 (Camera Movement) |
| **优先级** | 中 |

#### 描述

手持运镜模拟自然的手持拍摄效果，保留轻微的抖动和晃动，创造真实感和临场感。该预设适合纪录片风格、自然记录和需要真实感的视频内容，能够增强观众的代入感。

#### 关键词列表

| 关键词 | 描述 |
|--------|------|
| `handheld` | 手持拍摄 |
| `natural movement` | 自然运动 |
| `documentary` | 纪录片风格 |
| `organic` | 有机感 |
| `authentic` | 真实感 |
| `raw` | 原始感 |
| `candid` | 自然抓拍 |
| `verité` | 真实电影风格 |
| `immersive` | 沉浸感 |
| `POV feel` | 第一人称感 |

#### 适用场景

| 场景类型 | 具体应用 | 推荐指数 |
|----------|----------|----------|
| 纪录片 | 自然纪录片、人物纪录片 | ★★★★★ |
| Vlog | 生活记录、旅行Vlog、日常 | ★★★★★ |
| 真实记录 | 现场记录、活动记录、新闻 | ★★★★☆ |
| 情感表达 | 情感视频、人物特写 | ★★★★☆ |
| 街头摄影 | 街景记录、城市漫步 | ★★★★☆ |
| 独立电影 | 独立影片、艺术短片 | ★★★★☆ |

#### 冲突说明

**冲突预设：** `gimbal`

**冲突原因：** 手持与稳定器的运镜特性相反。手持追求自然晃动，稳定器追求平滑稳定，两者在视觉效果上互斥，无法同时应用。

**解决方案：** 
- 根据场景需求选择：真实记录用手持，专业展示用 gimbal
- 可在不同片段分别应用以创造对比

#### 与其他预设的组合建议

**推荐组合：**

| 组合名称 | 组合配置 | 效果描述 | 适用场景 |
|----------|----------|----------|----------|
| 自然纪录 | realistic + normal + handheld | 自然真实的记录风格 | 纪录片、Vlog、日常 |
| 复古叙事 | pixel_art + normal + handheld | 像素风格的复古叙事 | 游戏叙事、怀旧内容 |
| 自然慢动作 | realistic + slow_motion + handheld | 自然真实感的慢动作 | 自然纪录片、情感表达 |

**组合效果评分：**

| 视觉风格 | 时间采样 | 效果评分 | 备注 |
|----------|----------|----------|------|
| realistic | timelapse | ★★★☆☆ | 自然纪录片感 |
| realistic | slow_motion | ★★★★☆ | 自然慢动作 |
| realistic | normal | ★★★★★ | 最佳组合：自然纪录 |
| pixel_art | timelapse | ★★★☆☆ | 实验性效果 |
| pixel_art | slow_motion | ★★★☆☆ | 艺术实验 |
| pixel_art | normal | ★★★★★ | 复古叙事风格 |
| oil_painting | timelapse | ★★★☆☆ | 纪录片艺术风格 |
| oil_painting | slow_motion | ★★★★☆ | 自然艺术感 |
| oil_painting | normal | ★★★☆☆ | 纪录片艺术感 |

#### 使用示例

**示例 1：自然纪录片**

```
预设配置：realistic + normal + handheld
提示词：Nature documentary walking through forest, handheld camera feel, photorealistic, authentic and raw
输出效果：自然真实的森林行走纪录片风格，手持镜头增强临场感
```

**示例 2：生活Vlog**

```
预设配置：realistic + normal + handheld
提示词：Daily life vlog in cafe, handheld natural movement, photorealistic, candid authentic feel
输出效果：自然真实的咖啡厅日常生活记录，具有真实的生活感
```

**示例 3：复古游戏叙事**

```
预设配置：pixel_art + normal + handheld
提示词：8-bit pixel art game story, handheld documentary style, retro nostalgic, narrative feel
输出效果：像素风格的游戏叙事，手持镜头增强复古纪录片感
```

---

## 预设组合指南

### 推荐组合

以下是最常用的预设组合及其最佳应用场景：

#### 专业商业类

| 组合名称 | 配置 | 应用场景 | 效果描述 |
|----------|------|----------|----------|
| 商业标准 | realistic + normal + gimbal | 产品介绍、企业宣传 | 专业稳定的展示效果 |
| 商业慢动作 | realistic + slow_motion + gimbal | 产品广告、品牌宣传 | 高质感商业慢动作 |
| 商业延时 | realistic + timelapse + shuttle | 城市宣传、建筑展示 | 动感城市穿梭效果 |

#### 自然记录类

| 组合名称 | 配置 | 应用场景 | 效果描述 |
|----------|------|----------|----------|
| 自然纪录 | realistic + normal + handheld | 纪录片、Vlog | 自然真实的记录风格 |
| 自然风光 | realistic + timelapse + gimbal | 自然风光、风景摄影 | 平稳稳定的风光延时 |
| 自然慢动作 | realistic + slow_motion + handheld | 自然纪录片 | 自然真实感的慢动作 |

#### 艺术创意类

| 组合名称 | 配置 | 应用场景 | 效果描述 |
|----------|------|----------|----------|
| 艺术慢动作 | oil_painting + slow_motion + gimbal | 艺术视频、创意表达 | 油画风格的艺术慢动作 |
| 艺术延时 | oil_painting + timelapse + shuttle | 艺术短片、创意视频 | 动态艺术穿梭效果 |
| 艺术展示 | oil_painting + normal + gimbal | 画廊展示、艺术短片 | 平稳的艺术展示效果 |

#### 复古怀旧类

| 组合名称 | 配置 | 应用场景 | 效果描述 |
|----------|------|----------|----------|
| 复古叙事 | pixel_art + normal + handheld | 游戏叙事、怀旧内容 | 像素风格的复古叙事 |
| 复古动态 | pixel_art + timelapse + shuttle | 游戏宣传、复古广告 | 动态像素穿梭效果 |
| 复古艺术 | pixel_art + slow_motion + gimbal | 创意短片、艺术表达 | 像素风格的艺术慢动作 |

### 冲突组合

以下预设组合存在冲突，应避免使用：

| 冲突预设 A | 冲突预设 B | 冲突原因 | 解决方案 |
|------------|------------|----------|----------|
| timelapse | slow_motion | 时间采样方向相反 | 选择其中之一，或分段处理 |
| gimbal | handheld | 运镜稳定特性相反 | 根据场景选择：稳定或自然 |

**冲突处理建议：**

1. **时间采样冲突处理：**
   - 如需展示快慢对比，可分段处理视频
   - 使用 normal 预设作为过渡

2. **运镜风格冲突处理：**
   - 专业展示场景使用 gimbal
   - 自然记录场景使用 handheld
   - 可在不同片段分别应用

### 高级组合技巧

#### 1. 场景适配原则

| 场景类型 | 推荐视觉风格 | 推荐时间采样 | 推荐运镜风格 |
|----------|--------------|--------------|--------------|
| 城市宣传片 | realistic | timelapse | shuttle/gimbal |
| 自然纪录片 | realistic | normal/slow_motion | handheld |
| 产品广告 | realistic | slow_motion/normal | gimbal |
| 艺术创作 | oil_painting | slow_motion | gimbal |
| 游戏宣传 | pixel_art | timelapse/normal | shuttle/handheld |
| Vlog生活 | realistic | normal | handheld |

#### 2. 情感氛围选择

| 情感氛围 | 视觉风格建议 | 时间采样建议 | 运镜风格建议 |
|----------|--------------|--------------|--------------|
| 专业正式 | realistic | normal | gimbal |
| 自然真实 | realistic | normal | handheld |
| 艺术唯美 | oil_painting | slow_motion | gimbal |
| 复古怀旧 | pixel_art | normal | handheld |
| 动感活力 | realistic | timelapse | shuttle |
| 慢雅静谧 | oil_painting | slow_motion | gimbal |

#### 3. 内容类型匹配

| 内容类型 | 最佳组合 | 备选组合 |
|----------|----------|----------|
| 风光摄影 | realistic + timelapse + gimbal | realistic + slow_motion + gimbal |
| 城市风光 | realistic + timelapse + shuttle | realistic + normal + gimbal |
| 人物访谈 | realistic + normal + gimbal | realistic + normal + handheld |
| 产品展示 | realistic + slow_motion + gimbal | realistic + normal + gimbal |
| 艺术短片 | oil_painting + slow_motion + gimbal | oil_painting + normal + gimbal |
| 游戏视频 | pixel_art + normal + handheld | pixel_art + timelapse + shuttle |

---

## 使用最佳实践

### 预设选择流程

```
1. 确定视频类型和目的
   ↓
2. 选择视觉风格（realistic / pixel_art / oil_painting）
   ↓
3. 选择时间采样（timelapse / slow_motion / normal）
   ↓
4. 选择运镜风格（shuttle / gimbal / handheld）
   ↓
5. 检查预设冲突
   ↓
6. 应用预设组合
```

### 常见错误避免

| 错误类型 | 错误示例 | 正确做法 |
|----------|----------|----------|
| 时间冲突 | timelapse + slow_motion | 选择其一，或分段处理 |
| 运镜冲突 | gimbal + handheld | 根据场景选择一种 |
| 风格不匹配 | pixel_art用于产品广告 | 产品广告使用realistic |
| 场景不符 | handheld用于商业广告 | 商业广告使用gimbal |

### 性能优化建议

1. **渲染性能：**
   - realistic 风格：标准性能需求
   - pixel_art 风格：较低性能需求
   - oil_painting 风格：较高性能需求

2. **时间采样影响：**
   - timelapse：需要处理大量原始帧
   - slow_motion：需要高帧率源素材
   - normal：标准处理需求

3. **运镜复杂度：**
   - shuttle：高复杂度动态计算
   - gimbal：中等复杂度稳定处理
   - handheld：较低复杂度抖动模拟

---

## 附录

### 预设快速参考表

#### 视觉风格预设

| 预设ID | 名称 | 核心特征 | 适用场景 |
|--------|------|----------|----------|
| realistic | 写实风格 | 照片级真实感 | 商业、风光、人物 |
| pixel_art | 像素风格 | 复古8位效果 | 游戏、创意、怀旧 |
| oil_painting | 油画风格 | 艺术绘画质感 | 艺术、创意、文化 |

#### 时间采样预设

| 预设ID | 名称 | 核心特征 | 适用场景 |
|--------|------|----------|----------|
| timelapse | 延时摄影 | 时间压缩加速 | 城市延时、自然变化 |
| slow_motion | 升格慢动作 | 时间拉伸减速 | 运动细节、情感表达 |
| normal | 常规速度 | 标准播放速度 | 叙事、基础内容 |

#### 运镜风格预设

| 预设ID | 名称 | 核心特征 | 适用场景 |
|--------|------|----------|----------|
| shuttle | 穿梭机 | 高速动态穿梭 | 城市穿梭、动感展示 |
| gimbal | 稳定器 | 平滑稳定运镜 | 专业拍摄、风光视频 |
| handheld | 手持 | 自然真实晃动 | 纪录片、Vlog、真实记录 |

### 预设组合速查表

| 场景 | 视觉风格 | 时间采样 | 运镜风格 |
|------|----------|----------|----------|
| 城市宣传片 | realistic | timelapse | shuttle |
| 自然风光 | realistic | normal/timelapse | gimbal |
| 产品广告 | realistic | slow_motion | gimbal |
| 自然纪录片 | realistic | normal | handheld |
| Vlog生活 | realistic | normal | handheld |
| 艺术视频 | oil_painting | slow_motion | gimbal |
| 游戏宣传 | pixel_art | timelapse | shuttle |
| 复古叙事 | pixel_art | normal | handheld |
| 商业标准 | realistic | normal | gimbal |

### 关键词索引

#### A-E
- `8-bit style` - pixel_art
- `accelerated time` - timelapse
- `artistic` - oil_painting
- `authentic` - handheld
- `brush strokes` - oil_painting
- `canvas` - oil_painting
- `candid` - handheld
- `cinematic` - realistic
- `classic art` - oil_painting
- `detailed` - realistic
- `documentary` - handheld
- `dynamic` - shuttle
- `expressive` - oil_painting
- `fast forward` - timelapse
- `fast movement` - shuttle
- `fluid movement` - gimbal
- `flying through` - shuttle
- `frame interpolation` - slow_motion
- `game aesthetic` - pixel_art

#### F-N
- `gliding` - gimbal
- `HDR` - realistic
- `handheld` - handheld
- `high fidelity` - realistic
- `high speed` - slow_motion
- `immersive` - handheld
- `immersive movement` - shuttle
- `kinetic` - shuttle
- `natural flow` - normal
- `natural lighting` - realistic
- `natural movement` - handheld
- `nostalgic` - pixel_art
- `NES style` - pixel_art
- `normal speed` - normal
- `normal timing` - normal

#### O-S
- `oil painting` - oil_painting
- `organic` - handheld
- `painterly` - oil_painting
- `photorealistic` - realistic
- `pixel art` - pixel_art
- `POV feel` - handheld
- `professional` - gimbal
- `rapid transit` - shuttle
- `raw` - handheld
- `real-time` - normal
- `realistic` - realistic
- `regular pace` - normal
- `retro` - pixel_art
- `rich colors` - oil_painting
- `sharp focus` - realistic
- `shuttle cam` - shuttle
- `slow motion` - slow_motion
- `slo-mo` - slow_motion
- `smooth` - gimbal, slow_motion
- `speed` - shuttle
- `speed up` - timelapse
- `sprite` - pixel_art
- `stabilized` - gimbal
- `standard playback` - normal
- `standard rate` - normal
- `steady` - gimbal
- `temporal acceleration` - timelapse
- `temporal stretch` - slow_motion
- `textured` - oil_painting
- `time compression` - timelapse
- `time dilation` - slow_motion
- `time passing` - timelapse
- `time progression` - timelapse
- `time-lapse` - timelapse
- `timelapse` - timelapse
- `tracking` - gimbal
- `true-to-life` - realistic
- `unchanged speed` - normal
- `velocity` - shuttle
- `verité` - handheld
- `whoosh` - shuttle
- `8K quality` - realistic

---

**文档版本：** v1.0  
**最后更新：** 2026-04-22  
**维护者：** Video Generation Team

---

*本文档详细说明了视频生成系统的 9 个核心预设。如需进一步信息，请参考其他技术文档。*