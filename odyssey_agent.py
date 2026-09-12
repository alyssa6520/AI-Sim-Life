import os
import sys
import copy
import json
from datetime import datetime

import streamlit as st
from streamlit import session_state as ss

from config import Config


st.set_page_config(
    page_title="🧭 AI模拟人生 · 奥德赛计划",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header { text-align: center; padding: 1rem 0; }
    .step-card { border-radius: 12px; padding: 1.2rem; margin: 0.8rem 0; 
                 border-left: 5px solid #6366f1; background: #f8f9ff; }
    .step-card h3 { margin-top: 0; color: #4338ca; }
    .dimension-bar { height: 10px; border-radius: 5px; background: #e0e7ff; margin: 4px 0 10px 0; }
    .dimension-fill { height: 100%; border-radius: 5px; 
                      background: linear-gradient(90deg, #818cf8, #4f46e5); }
    .path-card { border-radius: 12px; padding: 1.2rem; margin: 0.8rem 0; border: 2px solid #e0e7ff; }
    .path-a { border-color: #fbbf24; background: #fffbeb; }
    .path-b { border-color: #34d399; background: #ecfdf5; }
    .path-c { border-color: #f472b6; background: #fdf2f8; }
    .risk-tag { display: inline-block; padding: 3px 10px; border-radius: 12px; 
                font-size: 0.85rem; margin: 2px 4px; }
    .tag-high { background: #fee2e2; color: #b91c1c; }
    .tag-mid { background: #fef3c7; color: #92400e; }
    .tag-low { background: #d1fae5; color: #065f46; }
    .experiment-box { border: 2px dashed #6366f1; border-radius: 12px; padding: 1.2rem; 
                      background: #eef2ff; margin: 1rem 0; }
    .timeline-item { padding: 0.6rem 0.8rem; margin: 0.3rem 0; 
                     border-left: 3px solid #6366f1; background: #ffffff; 
                     border-radius: 0 8px 8px 0; }
    .nav-btn { width: 100%; }
    .step-indicator { display: flex; justify-content: space-between; margin: 1rem 0 2rem 0; }
    .step-dot { width: 36px; height: 36px; border-radius: 50%; display: flex; 
                align-items: center; justify-content: center; font-weight: 700; 
                background: #e5e7eb; color: #6b7280; font-size: 0.9rem; 
                position: relative; z-index: 2; }
    .step-dot.active { background: #6366f1; color: white; box-shadow: 0 0 0 4px #e0e7ff; }
    .step-dot.done { background: #10b981; color: white; }
    .step-line { flex: 1; height: 3px; background: #e5e7eb; margin: 16px -4px; z-index: 1; }
    .step-line.done { background: #10b981; }
    .result-box { background: white; border-radius: 10px; padding: 1rem; 
                  border: 1px solid #e5e7eb; margin: 0.5rem 0; white-space: pre-wrap; }
    .section-title { font-size: 1.1rem; font-weight: 600; color: #374151; 
                     margin: 0.8rem 0 0.4rem 0; }
</style>
""", unsafe_allow_html=True)


STEPS = [
    {"key": "profile", "name": "个人信息", "icon": "👤"},
    {"key": "scan", "name": "现状扫描", "icon": "🔍"},
    {"key": "simulate", "name": "五年模拟", "icon": "⏳"},
    {"key": "odyssey", "name": "三条路径", "icon": "🗺️"},
    {"key": "risk", "name": "风险评估", "icon": "⚠️"},
    {"key": "transfer", "name": "可迁移能力", "icon": "🔄"},
    {"key": "experiment", "name": "30天实验", "icon": "🧪"},
]


def get_llm_client():
    if not Config.OPENAI_API_KEY:
        return None
    try:
        from openai import OpenAI
        return OpenAI(
            api_key=Config.OPENAI_API_KEY,
            base_url=Config.OPENAI_BASE_URL
        )
    except Exception:
        return None


def call_llm(system_prompt: str, user_prompt: str, temperature: float = 0.8) -> str:
    client = get_llm_client()
    if not client:
        return "⚠️ 请先在设置页面配置 OpenAI API Key 才能使用 AI 推演功能。"
    try:
        resp = client.chat.completions.create(
            model=Config.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=3000,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ AI 调用出错：{str(e)}"


def render_step_indicator(current_idx: int):
    cols = st.columns(len(STEPS) * 2 - 1)
    for i, step in enumerate(STEPS):
        with cols[i * 2]:
            cls = "active" if i == current_idx else ("done" if i < current_idx else "")
            st.markdown(
                f'<div class="step-dot {cls}" title="{step["name"]}">{step["icon"] if i < current_idx else i + 1}</div>',
                unsafe_allow_html=True
            )
        if i < len(STEPS) - 1:
            with cols[i * 2 + 1]:
                line_cls = "done" if i < current_idx else ""
                st.markdown(f'<div class="step-line {line_cls}"></div>', unsafe_allow_html=True)


def render_sidebar():
    with st.sidebar:
        st.markdown("## 🧭 AI模拟人生")
        st.markdown("---")

        st.markdown("#### 📋 推演流程")
        for i, step in enumerate(STEPS):
            icon = step["icon"]
            name = step["name"]
            if i < ss.current_step_idx:
                st.markdown(f"✅ **{icon} {i+1}. {name}**")
            elif i == ss.current_step_idx:
                st.markdown(f"👉 **{icon} {i+1}. {name}**")
            else:
                st.markdown(f"⬜ {i+1}. {name}")

        st.markdown("---")
        st.markdown("#### 💡 核心理念")
        st.info(
            "不要在脑子里选中一条路之后全部 all in。"
            "要用最小的成本先试一下——想开咖啡店就先周末兼职试试，"
            "想转行做内容就先发几篇文章试试。"
            "做完之后身体的反馈比任何规划都准。"
        )

        st.markdown("---")
        if st.button("🔄 重新开始", use_container_width=True, type="secondary"):
            keys_to_clear = [k for k in ss.keys() if k not in {"current_step_idx"}]
            for k in keys_to_clear:
                del ss[k]
            ss.current_step_idx = 0
            st.rerun()


def init_default_profile():
    if "profile" not in ss:
        ss.profile = {
            "age": "",
            "job": "",
            "skills": "",
            "relationships": "",
            "stress": "",
            "desire": "",
            "income": "",
            "city": "",
            "health": "",
        }


def get_avatar_url(prompt: str) -> str:
    import urllib.parse
    import time
    safe_prompt = urllib.parse.quote(prompt)
    ts = int(time.time())
    return f"https://coresg-normal.trae.ai/api/ide/v1/text_to_image?prompt={safe_prompt}&image_size=square&_ts={ts}"


def render_step_profile():
    st.markdown("<div class='section-title'>👤 创建你的基础档案</div>", unsafe_allow_html=True)
    st.info("💡 第一次不用填太多！只要告诉我你最基础的信息，剩下的可以边走边补充。")

    c1, c2 = st.columns(2)
    age = c1.text_input("🎂 你的年龄", ss.profile.get("age", ""))
    job = c2.text_input("💼 当前职业/状态", ss.profile.get("job", ""))
    
    desire = st.text_input("✨ 目前最想做的一件事 / 最渴望的改变", ss.profile.get("desire", ""))
    pressure = st.text_input("💥 目前最大的压力来源", ss.profile.get("pressure", ""))

    with st.expander("📝 补充更多隐藏设定（选填，填了推演更准，随时可改）"):
        skills = st.text_area("🛠️ 你有什么技能或爱好？", ss.profile.get("skills", ""))
        relation = st.text_area("👥 人际关系现状（单身/已婚/父母期待等）", ss.profile.get("relation", ""))
        health = st.text_area("❤️ 健康状况", ss.profile.get("health", ""))

    if st.button("🚀 开始推演 →", key="btn_profile", type="primary"):
        ss.profile.update({
            "age": age, "job": job, "skills": skills,
            "relation": relation, "health": health,
            "pressure": pressure, "desire": desire
        })
        
        ss.current_step_idx = 1
        st.rerun()


def build_profile_text() -> str:
    p = ss.profile
    lines = []
    lines.append(f"- 年龄：{p.get('age', '未提供')}")
    lines.append(f"- 职业/状态：{p.get('job', '未提供')}")
    lines.append(f"- 核心渴望：{p.get('desire', '未提供')}")
    lines.append(f"- 压力来源：{p.get('pressure', '未提供')}")
    if p.get('skills'): lines.append(f"- 技能/特长：{p['skills']}")
    if p.get('relation'): lines.append(f"- 人际关系：{p['relation']}")
    if p.get('health'): lines.append(f"- 健康状况：{p['health']}")
    
    # Check if there is dynamic feedback updated in later steps
    if ss.get("dynamic_feedback"):
        lines.append(f"- 用户最新补充/强调条件：{ss.dynamic_feedback}")
        
    return "\n".join(lines)


SYSTEM_SCAN = """你是一位专业的人生设计教练，基于斯坦福人生设计课的方法论工作。
你的风格：理性温暖、具体务实、不鸡汤、不贩卖焦虑，会给出结构化、可落地的分析。

接下来请根据用户提供的真实个人信息，从【健康、工作、财富、关系、精神】五个维度进行现状扫描：
1. 每个维度打 0-10 分，并给出 1-2 句打分理由（具体、不空泛）
2. 最后指出用户最容易忽视的 2-3 个潜在风险，风险要结合用户的实际情况

输出时请使用清晰的 Markdown 结构化排版，包含：
- 一个总体概览段落
- 每个维度包含：标题 + 分数（例如 工作：7/10） + 理由
- 最后列出"⚠️ 容易忽视的风险"小节
"""


def render_step_scan():
    st.markdown('<div class="step-card"><h3>🔍 步骤 2：现状扫描</h3>'
                '<p>从健康、工作、财富、关系、精神五个维度，对你的当前人生进行一次体检式扫描。</p></div>',
                unsafe_allow_html=True)

    profile_text = build_profile_text()

    if "scan_result" not in ss:
        with st.spinner("🤖 AI 正在进行现状扫描，约 10-20 秒..."):
            ss.scan_result = call_llm(
                system_prompt=SYSTEM_SCAN,
                user_prompt=f"以下是我的真实个人信息，请进行现状扫描：\n\n{profile_text}",
                temperature=0.7,
            )

    st.markdown("### 📊 扫描结果")
    st.markdown(ss.scan_result)
    st.caption("💡 提示：如果对结果不满意，可以点击下方按钮重新生成一次。")

    col1, col2, col_next = st.columns([2, 2, 5])
    with col1:
        if st.button("🔁 重新扫描", use_container_width=True):
            if "scan_result" in ss:
                del ss.scan_result
            st.rerun()
    with col_next:
        if st.button("⏳ 下一步：五年模拟 →", use_container_width=True, type="primary"):
            ss.current_step_idx = 2
            st.rerun()

    col_back, _ = st.columns([1, 8])
    with col_back:
        if st.button("← 返回"):
            ss.current_step_idx = 0
            st.rerun()


SYSTEM_SIMULATE = """你是一位极具画面感的未来观察者。请基于用户提供的当前真实情况，
推演"如果接下来五年完全不做任何重大改变——不换工作、不换城市、不转型、不做人生重大决策，
只是沿着现在的轨道继续努力"，五年后某一个普通工作日的真实一天。

请具体描写：
1. 几点起床、早晨的状态（精力、心情）
2. 早餐吃什么、通勤方式和时间
3. 上午做什么样的工作内容、和谁互动、当时的心情
4. 午餐、午休情况
5. 下午的工作、典型的挑战或疲惫感
6. 下班时间、晚上的安排（家庭/娱乐/学习/加班）
7. 睡前的心理活动（满足感、焦虑感、对生活的评价）
8. 大概的收入水平和生活状态

要求：
- 不要理想化，也不要过度灾难化，基于现实逻辑推演
- 写出具体的场景、对话碎片、身体感受，让读者有代入感
- 最后用一段话总结这一天的整体状态（用 0-10 分评价"开心程度"、"意义感"、"疲惫感"）
- 全文 600-1000 字，第一人称视角
"""


def render_step_simulate():
    st.markdown('<div class="step-card"><h3>⏳ 步骤 3：五年不变模拟</h3>'
                '<p>如果接下来五年完全不做重大改变，继续沿着现在的轨道走，'
                '五年后你普通的一天会是什么样子？</p></div>', unsafe_allow_html=True)

    profile_text = build_profile_text()
    ctx = f"【用户当前情况】\n{profile_text}\n\n【现状扫描结果】\n{ss.get('scan_result', '')}"

    if "simulate_result" not in ss:
        with st.spinner("🤖 AI 正在推演你五年后的一天，约 10-20 秒..."):
            ss.simulate_result = call_llm(
                system_prompt=SYSTEM_SIMULATE,
                user_prompt=ctx,
                temperature=0.85,
            )

    st.markdown("### 🎬 五年后的一天（不变版）")
    st.markdown('<div class="result-box">', unsafe_allow_html=True)
    st.markdown(ss.simulate_result)
    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2, col_next = st.columns([2, 2, 5])
    with col1:
        if st.button("🔁 重新推演", use_container_width=True):
            if "simulate_result" in ss:
                del ss.simulate_result
            st.rerun()
    with col_next:
        if st.button("🗺️ 下一步：奥德赛三条路径 →", use_container_width=True, type="primary"):
            ss.current_step_idx = 3
            st.rerun()

    col_back, _ = st.columns([1, 8])
    with col_back:
        if st.button("← 返回"):
            ss.current_step_idx = 1
            st.rerun()


SYSTEM_ODYSSEY = """你是一位顶级的斯坦福人生设计课导师。
请基于用户当前情况，设计三条完全不同、但逻辑成立的「奥德赛路径」（未来 5 年的职业与生活发展线）。

【路径设定规则】
- 路径 A（稳妥延展）：在现有行业/技能基础上，做出一次较小的转型，解决当前最大痛点。
- 路径 B（激进转型）：完全抛弃现在的行业，去追求用户"目前最想做的事/渴望"，哪怕听起来不切实际。
- 路径 C（野路子/黑天鹅）：如果路径 A 和 B 都走不通，利用用户的某个边缘技能/特长，去赚一种完全不同维度的钱，或者过一种彻底不同的生活方式。

【输出格式要求】
对于每条路径，必须严格按以下结构输出（不要擅自增加或减少结构）：

### 路径 [A/B/C]：[简短的路径名称，不超过10个字]
#### 🌟 核心理念
用一句话概括这条路径的主轴。

#### 📅 五年时间线
- **第 1 年**：[关键动作]
- **第 2-3 年**：[关键动作]
- **第 4-5 年**：[关键动作及最终状态]

#### 💰 现实预估
- **财务状态**：[收入预估及财务压力]
- **生活状态**：[时间自由度、健康、关系变化]

---
(请重复以上格式输出三条路径)
"""


def render_step_odyssey():
    st.markdown('<div class="step-card"><h3>🗺️ 步骤 4：奥德赛计划 · 三条人生路径</h3>'
                '<p>人生不是单选。基于你的现状，我们推演三条完全不同的方向——'
                '一条最稳、一条最燃、一条最意想不到。</p></div>', unsafe_allow_html=True)

    profile_text = build_profile_text()
    ctx = (f"【用户当前情况】\n{profile_text}\n\n"
           f"【现状扫描】\n{ss.get('scan_result', '')}\n\n"
           f"【五年不变模拟】\n{ss.get('simulate_result', '')}")

    if "odyssey_result" not in ss:
        with st.spinner("🤖 AI 正在设计三条人生路径，约 15-30 秒..."):
            ss.odyssey_result = call_llm(
                system_prompt=SYSTEM_ODYSSEY,
                user_prompt=ctx,
                temperature=0.9,
            )

    st.markdown("### 🌊 三条奥德赛路径")
    
    # 交互式反馈区（放在结果上方或下方）
    with st.expander("💬 路线不满意？点此补充条件让 AI 重算", expanded=False):
        feedback = st.text_input("想改什么？（比如：我不想离开现在的城市，或者我其实还会弹吉他）", key="odyssey_fb")
        if st.button("🔄 补充条件并重新推演"):
            ss.dynamic_feedback = feedback
            if "odyssey_result" in ss: del ss.odyssey_result
            st.rerun()

    # 解析头像并渲染（去除可能残留的 AVATAR 标签，兼容旧缓存）
    text = ss.odyssey_result
    import re
    text = re.sub(r'\[AVATAR:\s*.*?\s*\]', '', text)
    paths = re.split(r'(?=### 路径 [A-C])', text)
    
    for path_text in paths:
        if not path_text.strip(): continue
        
        st.markdown('<div class="result-box">', unsafe_allow_html=True)
        st.markdown(path_text, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    col1, col2, col_next = st.columns([2, 2, 5])
    with col1:
        if st.button("🔁 重新设计", use_container_width=True):
            if "odyssey_result" in ss:
                del ss.odyssey_result
            st.rerun()
    with col_next:
        if st.button("⚠️ 下一步：风险评估 →", use_container_width=True, type="primary"):
            ss.current_step_idx = 4
            st.rerun()

    col_back, _ = st.columns([1, 8])
    with col_back:
        if st.button("← 返回"):
            ss.current_step_idx = 2
            st.rerun()


SYSTEM_RISK = """你是一位冷静务实的风险分析师，也是温暖的人生教练。
现在针对用户的三条奥德赛人生路径，请逐一进行深度风险评估。

请严格按以下结构输出：

## 一、逐条路径风险分析

### 对路径 A 的评估
1. 🕳️ 可能低估了什么风险？（列出 2-3 个最容易被忽视的坑，具体说明）
2. 🚪 我必须放弃什么？（具体的时间、身份、关系、金钱、稳定性……）
3. 🔥 最难熬的时刻是什么？大概在第几个月出现？

### 对路径 B 的评估 （同上结构）

### 对路径 C 的评估 （同上结构）

## 二、三条路径的共同元素
请找出 3 个在三条路径中都会出现、无论走哪条都离不开的核心元素。
（例如：某种底层能力、某类关系、某种习惯、某个主题……）
这些共同元素非常重要——它们是你无论如何都离不开的"人生锚点"。

## 三、如果只能选一个
假设因为某种原因（比如时间窗口、家人要求、健康限制）你必须立刻三选一，
请分析哪一个的"代价总和"是你最能够接受的？
- 代价包括：金钱损失、时间成本、关系冲突、心理压力、机会成本
- 给出你的建议选择，并说明为什么这个代价组合对你来说最可承受
- 注意：不代表"最好"，只代表"代价最能扛"
"""


def render_step_risk():
    st.markdown('<div class="step-card"><h3>⚠️ 步骤 5：风险评估</h3>'
                '<p>每条路都有代价。看清每条路真正要放弃什么、哪些东西其实无论选哪条都要。</p></div>',
                unsafe_allow_html=True)

    profile_text = build_profile_text()
    ctx = (f"【用户当前情况】\n{profile_text}\n\n"
           f"【三条奥德赛路径】\n{ss.get('odyssey_result', '')}")

    if "risk_result" not in ss:
        with st.spinner("🤖 AI 正在进行深度风险评估，约 15-30 秒..."):
            ss.risk_result = call_llm(
                system_prompt=SYSTEM_RISK,
                user_prompt=ctx,
                temperature=0.75,
            )

    st.markdown("### 🔬 风险评估报告")
    st.markdown(ss.risk_result)

    col1, col2, col_next = st.columns([2, 2, 5])
    with col1:
        if st.button("🔁 重新评估", use_container_width=True):
            if "risk_result" in ss:
                del ss.risk_result
            st.rerun()
    with col_next:
        if st.button("🔄 下一步：可迁移能力 →", use_container_width=True, type="primary"):
            ss.current_step_idx = 5
            st.rerun()

    col_back, _ = st.columns([1, 8])
    with col_back:
        if st.button("← 返回"):
            ss.current_step_idx = 3
            st.rerun()


SYSTEM_TRANSFER = """你是一位职业转型专家，擅长挖掘人的可迁移能力（Transferable Skills）。
现在假设一个极端场景：用户现在所在的行业/岗位，在明天突然彻底消失了（比如政策禁止、技术淘汰），
用户必须立刻转做一个【和现在完全不搭边、完全不同】的事情。

请基于用户现有技能、三条路径中的共同元素、以及用户的性格/兴趣，推演出：

## 🔧 可迁移能力清单
先总结用户身上最值钱、能跨行业使用的 5-7 个核心可迁移能力，
每个能力给一个简短说明（如何从原行业迁移到陌生行业）。

## 🎲 三个完全不同的 Plan B
列出 3 个和现在行业/岗位完全不同的方向，每个方向要说明：
- 方向名称 & 典型职位
- 为什么用户能做：用哪几个可迁移能力衔接
- 前 3 个月的入门路径：怎么找第一份相关工作/怎么接第一单
- 第一年的收入预期：最低/正常/理想三种情况
- 这个方向的"隐藏红利"：除了钱以外能带来什么

三个方向要求差异巨大（比如不要同时列出"产品经理"和"项目经理"，那太像了；
应该是"社区咖啡店主理人"和"儿童编程老师"和"企业内训师"这种跨域的组合）。

## 🪨 最后的锚点
如果连这三个 Plan B 都走不通，还有什么"兜底饭碗"是用户无论如何都能吃上的？
这个兜底方案不需要体面，但要真实可落地。
"""


def render_step_transfer():
    st.markdown('<div class="step-card"><h3>🔄 步骤 6：可迁移能力推演</h3>'
                '<p>假如你现在的行业明天就没了——你身上哪些能力能"带得走"？'
                '你还能去做什么完全不同的事？</p></div>', unsafe_allow_html=True)

    profile_text = build_profile_text()
    ctx = (f"【用户当前情况】\n{profile_text}\n\n"
           f"【风险评估（含共同元素）】\n{ss.get('risk_result', '')}\n\n"
           f"【三条奥德赛路径】\n{ss.get('odyssey_result', '')}")

    if "transfer_result" not in ss:
        with st.spinner("🤖 AI 正在推演可迁移能力和转型方向，约 15-30 秒..."):
            ss.transfer_result = call_llm(
                system_prompt=SYSTEM_TRANSFER,
                user_prompt=ctx,
                temperature=0.85,
            )

    st.markdown("### 🌱 可迁移能力 & 备选方向")
    st.markdown(ss.transfer_result)

    col1, col2, col_next = st.columns([2, 2, 5])
    with col1:
        if st.button("🔁 重新推演", use_container_width=True):
            if "transfer_result" in ss:
                del ss.transfer_result
            st.rerun()
    with col_next:
        if st.button("🧪 下一步：30天实验设计 →", use_container_width=True, type="primary"):
            ss.current_step_idx = 6
            st.rerun()

    col_back, _ = st.columns([1, 8])
    with col_back:
        if st.button("← 返回"):
            ss.current_step_idx = 4
            st.rerun()


SYSTEM_EXPERIMENT = """你是一位"最小可行人生实验"的设计专家。
核心理念：不要 all in，用最低成本先试 30 天，让身体的真实感受告诉你答案。

请基于以下信息完成最后一步：
1. 对三条奥德赛路径分别给出【综合评分】（0-10 分），评分维度包括：
   - 适配度（和用户性格/资源的匹配度）
   - 风险可控度
   - 长期幸福度预测
   - 综合总分
   并为每条路径给出一句一句话点评。

2. 基于上面的综合评估 + 用户"最想做的事"，选出【最推荐先做 30 天实验的那一条路径】。

3. 为这条路径设计一个【30 天最小可行人生实验】，要求：

### 🎯 实验目标
一句话说明：这 30 天要验证什么假设？（不要验证"我喜不喜欢"这种主观问题，
要验证"我能不能坚持做 X 并拿到 Y 反馈"这种客观问题）

### 📋 实验规则（必须具体）
- 每周做什么（列出 3-5 项具体动作）
- 每天花多长时间（精确到分钟）
- 什么时间做（早起/午休/下班后/周末）
- 禁止什么（比如 禁止只看不做、禁止提前辞职、禁止大额投入）

### 📅 4 周时间线（每周要产出什么）
- 第 1 周：具体任务 + 产出物
- 第 2 周：具体任务 + 产出物
- 第 3 周：具体任务 + 产出物
- 第 4 周：具体任务 + 产出物

### 📐 30 天后的判断标准（必须可量化，不要"感觉对不对"）
至少列出 5 条判断标准，每条都可以用 是/否 或 数字 回答。
例如：
- 有 ≥ 3 天我是被这个事情唤醒而不是被闹钟
- 累计投入时间 ≥ 目标时间的 80%
- 拿到了 ≥ 1 个外部正反馈（付费/好评/邀约）
- 身体没有出现明显不适感（失眠/焦虑加剧/慢性疼痛）
- 做完 30 天后我依然愿意再做 30 天

### 🚦 决策矩阵
根据 30 天结果，该如何决策：
- 全部/大部分标准满足 → 继续加码到 90 天，并考虑半切换
- 一半满足一半不满足 → 调整实验变量，再做 30 天
- 大部分不满足 → 果断停止，换另一条路径做实验

输出要求：结构清晰、所有任务具体可执行、所有标准可量化。
"""


def render_step_experiment():
    st.markdown('<div class="step-card"><h3>🧪 步骤 7：30天人生实验</h3>'
                '<p>不要用脑子选，用身体试。基于你最倾向的路径，设计一个最低成本的 30 天实验。</p></div>',
                unsafe_allow_html=True)

    profile_text = build_profile_text()
    ctx = (f"【用户当前情况】\n{profile_text}\n\n"
           f"【三条奥德赛路径】\n{ss.get('odyssey_result', '')}\n\n"
           f"【风险评估】\n{ss.get('risk_result', '')}\n\n"
           f"【可迁移能力推演】\n{ss.get('transfer_result', '')}")

    if "experiment_result" not in ss:
        with st.spinner("🤖 AI 正在评估打分并设计 30 天实验，约 20-40 秒..."):
            ss.experiment_result = call_llm(
                system_prompt=SYSTEM_EXPERIMENT,
                user_prompt=ctx,
                temperature=0.8,
            )

    st.markdown("### 📈 三条路径综合评分")
    st.markdown(ss.experiment_result)

    st.markdown("---")
    st.markdown("#### 🎁 推演完成")
    st.success(
        "🌟 恭喜！你已经完成了整套奥德赛计划的 AI 推演。\n\n"
        "最后请记住三句话：\n"
        "1. **AI 不能替你做决定**——它只是帮你把脑子里模糊的纠结，变成清晰的结构化选项。\n"
        "2. **身体的反馈比任何规划都准**——先做 30 天实验，不要想清楚再做，要做了才能想清楚。\n"
        "3. **没有最优解，只有当前解**——人生是连续的决策，选什么都可以，随时可以改。\n\n"
        "祝你走出属于自己的那条路 🧭"
    )

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🔁 重新设计实验", use_container_width=True):
            if "experiment_result" in ss:
                del ss.experiment_result
            st.rerun()
    with col2:
        if st.button("🔄 重新开始整套推演", use_container_width=True, type="primary"):
            keys_to_clear = [k for k in ss.keys() if k not in {"current_step_idx"}]
            for k in keys_to_clear:
                del ss[k]
            ss.current_step_idx = 0
            st.rerun()

    col_back, _ = st.columns([1, 8])
    with col_back:
        if st.button("← 返回"):
            ss.current_step_idx = 5
            st.rerun()


def main():
    if "current_step_idx" not in ss:
        ss.current_step_idx = 0
    if "profile" not in ss:
        init_default_profile()

    render_sidebar()

    st.markdown(
        '<div class="main-header"><h1>🧭 AI模拟人生 · 奥德赛计划</h1>'
        '<p style="color:#666;">基于斯坦福人生设计课方法论，通过 6 轮 AI 结构化推演，'
        '帮你找到属于自己的人生方向</p></div>',
        unsafe_allow_html=True
    )

    render_step_indicator(ss.current_step_idx)

    if not Config.OPENAI_API_KEY:
        st.warning(
            "⚠️ 请先配置 OpenAI API Key 才能使用 AI 推演功能。\n\n"
            "你可以复制本项目的 `.env.example` 为 `.env`，填入你的 API Key；"
            "或者打开【同声传译学习助手】里的 ⚙️ 设置 页面进行配置。"
        )

    current_key = STEPS[ss.current_step_idx]["key"]
    if current_key == "profile":
        render_step_profile()
    elif current_key == "scan":
        render_step_scan()
    elif current_key == "simulate":
        render_step_simulate()
    elif current_key == "odyssey":
        render_step_odyssey()
    elif current_key == "risk":
        render_step_risk()
    elif current_key == "transfer":
        render_step_transfer()
    elif current_key == "experiment":
        render_step_experiment()


if __name__ == "__main__":
    main()
