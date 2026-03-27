import streamlit as st
import json
import logging

# ==========================================
# 0. Mock Data Templates (預設範本)
# ==========================================
# (1) 後端缺口範本
BACKEND_GAP = """【目標職位】：後端軟體工程師 (Backend Engineer)
【現況與目標落差】：
1. 缺乏處理高併發 (High Concurrency) 與分散式系統的經驗。
2. 尚未有實際使用 Message Queue (如 RabbitMQ, Kafka) 進行非同步處理的實績。
3. 容器化與 CI/CD 部署經驗薄弱，履歷上僅有本機開發經驗。
"""

# (2) 前端轉職者範本
FRONTEND_GAP = """【目標職位】：前端工程師 (Frontend Engineer)
【現況與目標落差】：
1. 履歷上的作品集多為切版練習或 Todo list，缺乏串接真實複雜 API 的經驗。
2. 未曾處理過前端的狀態管理 (State Management, 如 Redux/Zustand) 與效能優化。
3. 缺乏使用者驗證 (Authentication) 與權限控管 (RBAC) 實作經驗。
"""

# ==========================================
# 1. 阻止資料庫讀取與寫入 (Monkey Patching)
# ==========================================
import src.features.projects.tools as project_tools

def _mock_get_gap_analysis(user_id: str):
    # 直接回傳畫面上的輸入框內容，截斷對應資料庫的存取
    return st.session_state.get("mock_gap_analysis_data", "找不到缺口分析資料")

project_tools.DatabaseTools.get_gap_analysis = _mock_get_gap_analysis

import src.core.agent_engine.result_handlers as handlers
class MockHandler:
    def process(self, data, **kwargs):
        pass # 確保產出不會被寫進資料庫

original_get_handler = handlers.HandlerRegistry.get_handler
def _mock_get_handler(self, task_type):
    return MockHandler()
handlers.HandlerRegistry.get_handler = _mock_get_handler

# 引入核心控制器
from src.core.agent_engine.manager import CareerAgentManager

# ==========================================
# 2. 頁面 UI 與狀態管理
# ==========================================
st.set_page_config(page_title="專案建議模組", page_icon="🏗️", layout="wide")
st.title("🏗️ Side Project 推薦專案模組 (無資料庫版)")
st.markdown("本模組專注於突破 **「履歷實戰力不足」** 的痛點。只要填入您的能力缺口報告，架構師與 QA 審核 Agent 便會為您量身打造一份能寫進履歷、證明特定能力的四階段 MVP 開發企劃。")

if "form_gap_text" not in st.session_state:
    st.session_state.form_gap_text = BACKEND_GAP

st.subheader("一鍵注入測試場景 (Mock Data Injectors)")
col_mock1, col_mock2, _ = st.columns([1, 1, 2])
with col_mock1:
    if st.button("🚀 載入【後端缺口：缺乏高併發與雲端經驗】測試包"):
        st.session_state.form_gap_text = BACKEND_GAP
        st.rerun()
with col_mock2:
    if st.button("🎨 載入【前端轉職：缺乏複雜 API 與狀態管理】測試包"):
        st.session_state.form_gap_text = FRONTEND_GAP
        st.rerun()

st.markdown("---")

with st.form("project_form"):
    st.subheader("缺口分析輸入區 (Payload Inspector)")
    st.markdown("此欄位取代了原本向 Agent 請求 `FetchUserGapAnalysis` 的資料庫抓取行為。")
    input_gap = st.text_area("請輸入目標職位與目前能力缺口：", value=st.session_state.form_gap_text, height=200)
    submitted = st.form_submit_button("⚡ 開始生成 Side Project 藍圖 (Execute Pipeline)")

# ==========================================
# 3. 處理表單送出邏輯與圖表渲染
# ==========================================
if submitted:
    if not input_gap:
        st.warning("請填寫缺口分析資料！")
    else:
        # 將資料存入 session state 給 Monkey-patch 取用
        st.session_state["mock_gap_analysis_data"] = input_gap
        
        manager = CareerAgentManager()
        st.info("系統開始運行：架構師 Agent 與工業界 QA Agent 正在兵推策略中...")
        
        with st.spinner("🤖 正在為您量身規劃最小可行性專案 (MVP) 與分階段任務... (約需 1 - 2 分鐘，請耐心等候)"):
            try:
                # 執行 project_rec 任務 (TasksEnum 為 PROJECT_REC = "project_rec")
                result = manager.run_task("project_rec", {"user_id": "demo_user"})
                st.success("🎉 Side Project 企劃書生成完畢！")
                
                # --- 渲染結果 (Report Rendering) ---
                if isinstance(result, dict) and "project_name" in result:
                    st.markdown(f"## 🏆 {result.get('project_name', '未命名專案')}")
                    
                    st.markdown("### 💡 專案核心價值與影響力")
                    st.info(result.get("overall_resume_impact", "無資訊"))
                    st.markdown(f"**⚡ 難度與時程評估**：`{result.get('difficulty', '未知')}`")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("### 🎯 針對的求職弱項")
                        for gap in result.get("capability_gaps_addressed", []):
                            st.write(f"- {gap}")
                    with col2:
                        st.markdown("### 🛠️ 建議技術棧")
                        for tech in result.get("tech_stack", []):
                            st.write(f"- {tech}")
                            
                    st.markdown("---")
                    st.markdown("### 🛤️ 四階段實作藍圖 (Phases)")
                    phases = result.get("project_phases", [])
                    
                    if phases:
                        # 創建標籤頁 Tabs 讓四大階段可以點選切換，減少頁面冗長感
                        tabs = st.tabs([p.get("phase_name", f"Phase {i+1}") for i, p in enumerate(phases)])
                        
                        for i, tab in enumerate(tabs):
                            p = phases[i]
                            with tab:
                                st.markdown(f"**🎯 階段目標**：{p.get('phase_goal', '')}")
                                st.markdown("**📝 實作任務 (Checklist)**：")
                                for task in p.get("tasks", []):
                                    st.write(f"- [ ] {task}")
                                    
                                # 把寫進履歷的關鍵展現出來
                                st.warning(f"**💼 上傳履歷的價值 (Resume Value)**：\n\n{p.get('resume_value', '')}")
                    
                    with st.expander("🛠️ 查看代理人生成的 Raw JSON (Debug)"):
                        st.json(result)
                else:
                    # 容錯處理：如果 Agent 回傳的不是符合 pydantic 結構的 dict
                    st.error("⚠️ Agent 返回的結構非預期，下方為原始輸出：")
                    st.json(result)
                    
            except Exception as e:
                st.error(f"企劃生成期間系統發生錯誤：{str(e)}")
