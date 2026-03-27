import streamlit as st
import json

# ==========================================
# 1. 為了不改動後端並阻斷資料庫，我們使用 Monkey-Patch 攔截資料庫查詢
# ==========================================
import src.features.cover_letter.tools as cl_tools

def _mock_get_job(job_id: str):
    return st.session_state.get("mock_job_data", {"error": "找不到職缺資料 (前端未輸入)"})

def _mock_get_opt_resume(opt_id: str):
    return st.session_state.get("mock_resume_data", {"error": "找不到優化履歷 (前端未輸入)"})

def _mock_get_desig_resume(res_id: str):
    return st.session_state.get("mock_resume_data", {"error": "找不到原始履歷 (前端未輸入)"})

# 覆蓋原有的 DB 查詢方法
cl_tools.DatabaseTools.get_job_recommendation_profile = _mock_get_job
cl_tools.DatabaseTools.get_optimize_resume = _mock_get_opt_resume
cl_tools.DatabaseTools.get_user_designated_resume = _mock_get_desig_resume

# ==========================================
# 阻止 manager 寫入資料庫: Monkey-Patch HandlerRegistry
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
# 2. 建立頁面 UI
# ==========================================
st.set_page_config(page_title="求職信生成", page_icon="📝", layout="wide")
st.title("📝 求職信生成模組 (無資料庫版)")
st.markdown("在此頁面，您可以直接貼上您的「履歷內容」與「目標職缺說明」，系統將指揮 Agent 為您量身打造求職信。完全不寫入資料庫！")

with st.form("cover_letter_form"):
    st.subheader("1. 您的履歷與經歷 (取代從 DB 抓取)")
    resume_input = st.text_area("請貼上您的履歷內容、技術亮點或自傳：", height=200, placeholder="例如：擁有三年 Python 開發經驗，熟悉 FastAPI, Docker 等...")
    
    st.subheader("2. 目標職缺資訊 (取代從 DB 抓取)")
    job_title = st.text_input("職位名稱：", value="軟體工程師 (Software Engineer)")
    job_desc = st.text_area("詳細職缺描述與要求：", height=200, placeholder="例如：需要熟悉 Python, 具有開發 RESTful API 經驗...")
    
    submitted = st.form_submit_button("🚀 呼叫 CrewAI 生成求職信")

# ==========================================
# 3. 處理表單送出邏輯
# ==========================================
if submitted:
    if not resume_input or not job_desc:
        st.warning("請完整填寫履歷內容與職缺描述！")
    else:
        # A. 將使用者的輸入存入 session_state 給 mock 函數使用
        st.session_state["mock_job_data"] = {
            "job_id": "demo_job_123",
            "job_title": job_title,
            "job_description": job_desc,
            "requirements": "以使用者上述輸入為主"
        }
        st.session_state["mock_resume_data"] = {
            "professional_summary": resume_input,
            "professional_experience": resume_input,
            "core_skills": "參考上述輸入",
            "projects": "參考上述輸入",
            "education": "參考上述輸入",
            "autobiography": ""
        }
        
        # B. 準備傳給 Manager 的 Input dict
        user_input_dict = {
            "user_id": "demo_user",  # 為了通過 manager 驗證
            "job_id": "demo_job_123",
            "optimization_id": "demo_opt_123",
            "resume_id": "demo_res_123"
        }
        
        # C. 實例化 Manager 並發布任務
        manager = CareerAgentManager()
        
        st.info("系統開始運行：正在啟動 CrewAI 的策略官與寫手代理人...")
        
        with st.spinner("🤖 代理人正在撰寫與審校求職信中，請稍候 (約 30 - 60 秒)..."):
            try:
                # 執行任務 (對應 TaskType Enum 的 COVER_LETTER 為 "cover_letter")
                result = manager.run_task("cover_letter", user_input_dict)
                
                st.success("🎉 求職信生成完畢！")
                st.markdown("## ✉️ 您的專屬求職信")
                
                # result 可能是 dict (若是 pydantic dump)
                if isinstance(result, dict) and ("content" in result or "cover_letter_content" in result):
                    content = result.get("content") or result.get("cover_letter_content", "")
                    subject = result.get("subject", "無主旨")
                    
                    st.info(f"**主旨：** {subject}")
                    st.markdown("### 正文：")
                    st.write(content.replace("\n", "\n\n"))
                    
                    with st.expander("🛠️ 查看代理人生成的 Raw JSON (Debug)"):
                        st.json(result)
                else:
                    st.json(result)
            except Exception as e:
                st.error(f"執行期間發生錯誤：{str(e)}")
