# Dysin

> 一个运行在 Windows 桌面上的可自定义交互精灵。

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-GPL-green)](LICENSE)
[![PySide6](https://img.shields.io/badge/GUI-PySide6-orange)](https://pypi.org/project/PySide6/)

---

## ✨ 功能

### 🎭 桌面精灵
- 透明背景的像素精灵，悬浮于桌面所有窗口之上（置顶+无边框）
- 精灵帧动画（站立 / 行走），帧序列、速度均可在 YAML 中配置
- **自动漫游**：精灵会在屏幕范围内随机走动，方向和速度受情绪影响
- **拖拽**：左键拖拽可随意移动精灵位置
- **中键聊天**：点击中键触发随机闲聊

### 😊 情绪系统
精灵拥有 11 项情绪参数，随时间自然衰减，行为与对话实时响应：

| 参数 | 说明 |
|------|------|
| `familiar` / `friendship` / `love` / `fear` / `hate` | 关系基础值 |
| `happy` / `angry` / `sorrow` / `horror` / `surprised` / `shyness` | 即时情绪 |
| `tired` / `interest` | 体力 / 兴趣 |

情绪值影响：表情切换、行走速度、移动概率/方向、聊天概率、关系等级。

情绪通过 5 级关系 (`strange` → `normal` → `friend` → `lover`) 映射到不同的对话分支。

### 💬 对话系统
- **上下文敏感**：根据时间（早晚）、关系、情绪、体力、兴趣自动选择匹配对话
- **条件+权重**：`dialogue.yaml` 中每条对话可设 `when` 条件过滤和多权重随机
- **分支对话**：某些对白可以 `goto` 到子对话状态，弹出选项菜单（积极/消极/开玩笑/不理）
- **气泡渲染**：头像 + 对话气泡背景，支持 **HTML/Markdown**（标题、粗体、斜体、代码块、删除线、链接、分割线）
- **淡入淡出**：对话气泡有 alpha 渐变动画，自动调整显示时长
- **自适应大小**：气泡根据文本内容自动伸缩（不超过屏幕 40%）

### 🎵 音乐播放
- **拖放播放**：将 `.mp3` / `.wav` 文件拖到对话气泡上即可播放
- **歌词同步**：自动加载同目录 `.lrc` 歌词文件，歌词逐行显示在气泡中
- **播放控制**：右键菜单 → 暂停 / 继续 / 停止

### 🖱️ 右键菜单

**精灵右键菜单**：聊天 · 触摸 · 不要走动/自由行动 · 音乐控制 · 离开

**对话选项菜单**：积极 / 消极 / 开玩笑 / 不理会（响应分支对话）

### 📡 外部消息（TCP/UDP）
- 监听 `127.0.0.1:7654`，可通过网络发送文本到精灵气泡
- 文本支持 Markdown 渲染，适合外部脚本/工具推送消息

### 💾 存档
- 情绪参数、关系、自定义称谓自动持久化到 `sav/sav.dat`
- 首次运行弹出名称输入框
- 每 ~30 秒自动保存

### 🌐 国际化
- 内置中文 / English 双语框架
- 语言文件：`res/text/i18n/zh_CN.json`、`en_US.json`

### 🔧 YAML 全配置
所有参数和对话由 4 个 YAML 文件驱动，无需改代码：

| 文件 | 内容 |
|------|------|
| `res/text/config.yaml` | 精灵动画、对话框尺寸字体颜色 |
| `res/text/define.yaml` | 角色名称、称谓、提示文字 |
| `res/text/function.yaml` | 功能状态与反应选项定义 |
| `res/text/dialogue.yaml` | 全部对话（19 个状态 × 多层关系） |

### 🛠️ 调试窗口
- 可查看当前所有情绪值、关系、变量状态

---

## 📦 安装与运行

### 环境要求
- Python **3.10+**
- Windows（PySide6 桌面 GUI）

### 安装依赖
```bash
pip install PySide6 PyYAML
```

### 启动
```bash
python run.pyw
# 或
python -m dysin
```

---

## 🏗️ 项目结构

```
Dysin/
├── run.pyw                    # 启动入口
├── requirements.txt
├── res/                       # 资源文件
│   ├── image/                 #   精灵帧、头像、图标、对话框素材
│   ├── sound/                 #   语音 wav 文件
│   └── text/
│       ├── config.yaml        #   精灵/对话框配置
│       ├── define.yaml        #   角色定义
│       ├── dialogue.yaml      #   对话数据
│       ├── function.yaml      #   功能状态
│       └── i18n/              #   多语言翻译
├── sav/                       # 存档目录
└── dysin/                     # 源代码包
    ├── __init__.py / __main__.py
    ├── app.py                 #   主程序入口
    ├── character.py           #   角色控制器（编排层）
    ├── core/                  #   核心逻辑
    │   ├── config.py          #     路径常量
    │   ├── setting.py         #     游戏规则、情绪更新
    │   ├── mood.py            #     情绪系统
    │   ├── language.py        #     对话引擎
    │   ├── yaml_handler.py    #     YAML 加载器
    │   ├── i18n.py            #     国际化
    │   └── frame.py           #     精灵帧切分
    ├── ui/                    #   界面组件
    │   ├── spirit.py          #     桌面精灵（QLabel）
    │   ├── dialog.py          #     对话气泡（QWidget）
    │   ├── menu.py            #     右键菜单系统
    │   ├── tray.py            #     系统托盘
    │   ├── first_run.py       #     首次运行对话框
    │   └── debug.py           #     调试窗口
    └── network/               #   网络 & 音频
        ├── server.py          #     TCP/UDP 消息服务器
        └── audio.py           #     音频播放线程
```

---

## 🎨 自定义

### 更换角色
1. 替换 `res/image/move.png`（4×4 精灵帧图，站立/行走各一行）
2. 替换 `res/image/0.png ~ 15.png`（8 种表情 × 2 个方向）
3. 修改 `res/text/define.yaml` 中的角色名称和称谓
4. 编辑 `res/text/dialogue.yaml` 自定义对话内容

### 对话格式示例
```yaml
states:
  start:
    normal:
      - text: "你来啦，{{CALLING}}。"
        weight: 1
      - text: "嗯，你好，{{CALLING}}。"
      - when: { TIMEPERIOD: "evening" }
        text: "晚上好，{{CALLING}}。"
        sound: "edo"
        icon: "2"
```

---

## 📄 许可

GPL-3.0 License
