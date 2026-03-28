import streamlit as st
import json

# ==========================================
# 1. 阻止資料庫讀取: Monkey-Patch resume 的 tools
# ==========================================
import src.features.resume.tools as resume_tools

def _mock_get_resume(user_id: str):
    return st.session_state.get("mock_resume_data", {"error": "前端未提供履歷資料"})

def _mock_get_survey(user_id: str):
    return st.session_state.get("mock_target_role", "未指定目標職位")

def _mock_get_analysis(user_id: str):
    return st.session_state.get("mock_analysis_data", {"error": "前端未提供分析資料"})

# 覆蓋原有的 DB 查詢方法
resume_tools.DatabaseTools.get_user_resume = _mock_get_resume
resume_tools.DatabaseTools.get_user_survey = _mock_get_survey
resume_tools.DatabaseTools.get_resume_analysis = _mock_get_analysis

# ==========================================
# 2. 阻止 manager 寫入資料庫: Monkey-Patch HandlerRegistry
# ==========================================
import src.core.agent_engine.result_handlers as handlers
class MockHandler:
    def process(self, data, **kwargs):
        pass # 什麼都不做，不寫入 DB

original_get_handler = handlers.HandlerRegistry.get_handler
def _mock_get_handler(self, task_type):
    return MockHandler()
handlers.HandlerRegistry.get_handler = _mock_get_handler

# 必須引用真正的執行模組
from src.core.agent_engine.manager import CareerAgentManager

# ==========================================
# 3. 建立頁面 UI 與 Session State 快取
# ==========================================
st.set_page_config(page_title="履歷生成與優化", page_icon="📄", layout="wide")
st.title("📄 履歷診斷與優化模組")
st.markdown("""
### 說明：
填寫完基本資料後，先產出「診斷分析報告」進行審閱，確認後再決定是否一鍵交由 AI 進行「履歷再造」。""")

# 狀態管理
if "step1_done" not in st.session_state:
    st.session_state.step1_done = False
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "opt_result" not in st.session_state:
    st.session_state.opt_result = None

with st.form("resume_input_form"):
    st.subheader("1. 您的原始履歷")
    # 此處可以提供預設長文，避免每次都要重打
    resume_input_default = st.session_state.get("mock_resume_data", {}).get("structured_data", "")
    resume_input = st.text_area("請貼上您的現有經歷、學歷與技能：", height=200, value=resume_input_default, placeholder="例如：台大資工系畢業，曾在某科技擔任軟體工程師，負責開發前後端系統...")
    
    st.subheader("2. 您的目標職位")
    roles = [
        "前端工程師", 
        "後端工程師", 
        "全端工程師", 
        "資料科學家/數據分析師", 
        "AI 工程師", 
        "DevOps/SRE 工程師"
    ]
    
    # 若有前次填寫紀錄則讀取，否則預設為後端工程師
    default_role = st.session_state.get("mock_target_role", "後端工程師")
    if default_role in roles:
        default_index = roles.index(default_role)
    else:
        default_index = 1
        
    target_role = st.selectbox("針對什麼職位進行優化？", options=roles, index=default_index)
    
    submitted_analysis = st.form_submit_button("🚀 第一步：執行履歷分析")

# ==========================================
# 4. 處理第一階層：履歷分析 (resume_analysis)
# ==========================================
if submitted_analysis:
    if not resume_input or not target_role:
        st.warning("請完整填寫履歷內容與目標職位！")
    else:
        # 將資料放入 session_state 供 Patch 函式讀取，並記錄填寫資料
        st.session_state["mock_resume_data"] = {"structured_data": resume_input}
        st.session_state["mock_target_role"] = target_role
        
        manager = CareerAgentManager()
        st.info("系統開始運行：即將啟動 CrewAI...")
        
        with st.spinner("🤖 步驟一：資深招募顧問正在進行履歷「嚴苛診斷分析」... (約需 30-60 秒)"):
            try:
                # 重設先前的結果
                st.session_state.analysis_result = None
                st.session_state.opt_result = None
                
                result = manager.run_task("resume_analysis", {"user_id": "demo_user"})
                st.session_state.analysis_result = result
                st.session_state["mock_analysis_data"] = result
                st.session_state.step1_done = True
                
            except Exception as e:
                st.error(f"分析期間發生錯誤：{str(e)}")

# 若第一步分析完成，把結果亮出來
if st.session_state.step1_done and st.session_state.analysis_result:
    st.success("✅ 履歷分析完成！請檢視以下診斷報告。")
    res = st.session_state.analysis_result
    
    if isinstance(res, dict) and "candidate_positioning" in res:
        st.markdown("## 📊 履歷診斷分析報告")
        
        st.markdown("### 🎯 候選人定位與落差")
        st.info(f"**定位**：{res.get('candidate_positioning', '')}")
        st.warning(f"**目標落差**：{res.get('target_role_gap_summary', '')}")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 💪 核心優勢")
            for s in res.get("overall_strengths", []):
                st.write(f"- {s}")
        with col2:
            st.markdown("### ⚠️ 核心劣勢")
            for w in res.get("overall_weaknesses", []):
                st.write(f"- {w}")
                
        st.markdown("### 🚨 關鍵問題清單")
        for i, issue in enumerate(res.get("critical_issues", [])):
            with st.expander(f"問題 {i+1}｜{issue.get('section', '未知區塊')} - {issue.get('diagnosis_dimension', '')}", expanded=True):
                st.markdown(f"**原句**：`{issue.get('original_text', '')}`")
                st.markdown(f"**影響**：{issue.get('issue_reason', '')}")
                st.markdown("**改善方向**：")
                for imp in issue.get('improvement_direction', []):
                    st.write(f"- {imp}")
                    
        st.markdown("### 🔮 面試預測")
        st.error(f"**ATS 風險等級**：{res.get('ats_risk_level', '')}")
        st.write(res.get("screening_outcome_prediction", ""))
        
        with st.expander("🛠️ 查看代理人生成的 Raw JSON (Debug)"):
            st.json(res)
    else:
        st.json(res)
        
    st.markdown("---")
    
    # 這裡顯示第二部的按鈕
    st.subheader("覺得這些建議不錯嗎？讓系統直接幫您改到好！")
    
    # Streamlit 不允許兩個 form_submit_button 產生接力，我們直接在外面放 btn
    if st.button("🚀 第二步：依照上述分析報告，正式優化履歷"):
        manager = CareerAgentManager()
        with st.spinner("🤖 步驟二：履歷策略顧問正在將分析結果轉化為「優化版履歷」... (約需 30-60 秒)"):
            try:
                # 第二部需要跑 resume_opt 任務
                # 確保前一階段分析結果還在
                st.session_state["mock_analysis_data"] = st.session_state.analysis_result
                
                # [FIX] 以直接注入的方式將前端狀態塞給 Agent，避免 Agent 工具惰性與斷層幻覺
                payload = {
                    "user_id": "demo_user",
                    "resume_content": st.session_state.get("mock_resume_data", {}).get("structured_data", ""),
                    "analysis_content": json.dumps(st.session_state.analysis_result, ensure_ascii=False) if st.session_state.analysis_result else ""
                }
                opt_result = manager.run_task("resume_opt", payload)
                st.session_state.opt_result = opt_result
            except Exception as e:
                st.error(f"優化期間發生錯誤：{str(e)}")

# ==========================================
# 5. 處理第二階層：跑完優化的結果展示
# ==========================================
if st.session_state.opt_result:
    opt_result = st.session_state.opt_result
    st.success("🎉 履歷優化完成！")
    
    st.markdown("## 📄 您優化過後的亮點履歷 (STAR 架構)")
    if isinstance(opt_result, dict) and "professional_summary" in opt_result:
        st.markdown("### 🌟 專業摘要 (Summary)")
        st.info(opt_result.get("professional_summary", ""))
        
        st.markdown("### 🛠️ 核心技能")
        skills = opt_result.get("core_skills", [])
        st.write("、".join(skills) if isinstance(skills, list) else skills)
        
        st.markdown("### 💼 工作經歷")
        for exp in opt_result.get("professional_experience", []):
            st.write(f"- {exp}")
            
        st.markdown("### 🚀 專案經驗")
        for proj in opt_result.get("projects", []):
            st.write(f"- {proj}")
            
        st.markdown("### 🎓 學歷")
        for edu in opt_result.get("education", []):
            st.write(f"- {edu}")
            
        st.markdown("### 📖 自傳 (Autobiography)")
        st.write(opt_result.get("autobiography", ""))
        
        with st.expander("🛠️ 查看代理人生成的 Raw JSON (Debug)"):
            st.json(opt_result)
    else:
        st.json(opt_result)
