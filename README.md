# 🎭 AI-Sim-Life · AI 模拟人生「奥德赛计划」

一个基于 LLM 的**职业人生推演应用**：输入你的现状，AI 为你模拟五年人生、生成三条职业路径、推演风险、盘点可迁移能力，并给出可立即执行的 30 天实验计划。

**在线体验**：<https://ai-sim-life-utc9vibhqtmayakx2kccnx.streamlit.app>

## ✨ 功能特性

- **7 步结构化向导**：个人信息 → 现状扫描 → 五年模拟 → 三条路径 → 风险评估 → 可迁移能力 → 30 天实验，将开放式的职业规划问题拆解为可逐步完成的流程
- **6 组 System Prompt 工程**：每一步独立设计角色设定、输出格式约束与温度参数（0.7–0.9），使 LLM 输出结构化、可对比、可执行
- **文生图头像**：根据用户描述自动生成个性化 AI 头像
- **会话状态管理**：每步产出沉淀为后续步骤的上下文，支持随时回退修改

## 🖼️ 界面预览

<!-- TODO: 替换为实际截图 -->
![screenshot placeholder](docs/screenshot.png)

## 🛠️ 技术栈

| 层 | 技术 |
|---|---|
| 界面 | Streamlit |
| LLM | OpenAI 兼容 API（可配置任意 base_url / 模型） |
| 部署 | Streamlit Community Cloud |

## 🚀 本地运行

```bash
git clone https://github.com/alyssa6520/AI-Sim-Life.git
cd AI-Sim-Life
pip install -r requirements.txt

# 配置环境变量（支持任意 OpenAI 兼容接口）
cp .env.example .env
# 编辑 .env 填入你的 API Key

streamlit run odyssey_agent.py
```

## ⚙️ 环境变量

| 变量 | 说明 | 默认值 |
|---|---|---|
| `OPENAI_API_KEY` | LLM API 密钥（必填） | — |
| `OPENAI_BASE_URL` | OpenAI 兼容 API 地址 | `https://api.openai.com/v1` |
| `OPENAI_MODEL` | 模型名称 | `gpt-3.5-turbo` |

## 📁 目录结构

```
AI-Sim-Life/
├── odyssey_agent.py   # 主应用：7 步向导 + Prompt 定义 + Streamlit UI（约 700 行）
├── config.py          # 环境变量加载与配置
└── requirements.txt   # 依赖清单
```

## 📄 License

[MIT](LICENSE)
