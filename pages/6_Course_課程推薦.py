import streamlit as st
import json
import logging
import pandas as pd

# ==========================================
# 0. Mock Data Templates (預設範本)
# ==========================================
FRONTEND_MOCK = {
    "role": "前端工程師",
    "match_score": 30,
    "gap_description": "履歷上的作品集多為靜態切版或簡單的 Todo List。缺乏與後端 API 進行非同步資料交換的經驗，也沒有使用過如 Redux 等複雜狀態管理工具的實績。完全沒有接觸過效能優化與測試撰寫。"
}

BACKEND_MOCK = {
    "role": "後端工程師",
    "match_score": 85,
    "gap_description": "本身已具備穩定的 API 開發與資料庫 CRUD 能力。但面試資深職位時，缺乏處理高併發 (High Concurrency) 與微服務架構 (Microservices) 的設計經驗。對於 Message Queue 和快取機制 (Redis) 只有概念，缺乏實戰應用的成果。"
}

# ==========================================
# 1. 攔截資料庫讀取與寫入 (Monkey Patching)
# ==========================================
from src.features.course.course_matching import CourseRecommendationService

# A. 攔截使用者缺口讀取 (Mocking fetch_user_gap)
def _mock_fetch_user_gap(self, user_id: str):
    # 改為截取前端輸入的暫存變數
    mock_data = st.session_state.get("mock_course_gap_data")
    if mock_data:
        return mock_data
    return None

CourseRecommendationService.fetch_user_gap = _mock_fetch_user_gap

# B. 攔截寫入資料庫：覆寫 HandlerRegistry
import src.core.agent_engine.result_handlers as handlers
class MockHandler:
    def process(self, data, **kwargs):
        pass # 禁止寫回資料庫

original_get_handler = handlers.HandlerRegistry.get_handler
def _mock_get_handler(self, task_type):
    return MockHandler()

handlers.HandlerRegistry.get_handler = _mock_get_handler

# ==========================================
# 2. 頁面 UI 與狀態管理
# ==========================================
st.set_page_config(page_title="課程與路徑推薦", page_icon="📚", layout="wide")
st.title("📚 課程推薦與路線規劃模組 (Hybrid 真實搜尋版)")
st.markdown("本模組專注於 **「將能力缺口轉化為具體學習路線」**。展示重點：輸入端使用 Mock 假資料，但**演算法部分會真實打入 Supabase 資料庫**撈取線上課程進行媒合排序，最後將篩選出來的 Top 5 結果丟給 CrewAI 的 Agent 進行「路徑戰略設計」。")

roles = ["前端工程師", "後端工程師", "全端工程師", "資料科學家/數據分析師", "AI 工程師", "DevOps/SRE 工程師"]

if "form_course_role" not in st.session_state:
    st.session_state.form_course_role = FRONTEND_MOCK["role"]
if "form_course_score" not in st.session_state:
    st.session_state.form_course_score = FRONTEND_MOCK["match_score"]
if "form_course_gap" not in st.session_state:
    st.session_state.form_course_gap = FRONTEND_MOCK["gap_description"]

st.subheader("一鍵注入測試場景 (Mock Input Injectors)")
col_m1, col_m2, _ = st.columns([1, 1, 2])
with col_m1:
    if st.button("🌱 載入【前端轉職新手】(媒合度 30%)"):
        st.session_state.form_course_role = FRONTEND_MOCK["role"]
        st.session_state.form_course_score = FRONTEND_MOCK["match_score"]
        st.session_state.form_course_gap = FRONTEND_MOCK["gap_description"]
        st.rerun()
with col_m2:
    if st.button("🚀 載入【資深後端進階】(媒合度 85%)"):
        st.session_state.form_course_role = BACKEND_MOCK["role"]
        st.session_state.form_course_score = BACKEND_MOCK["match_score"]
        st.session_state.form_course_gap = BACKEND_MOCK["gap_description"]
        st.rerun()

st.markdown("---")

with st.form("course_input_form"):
    st.subheader("缺口參數輸入區 (Payload Inspector)")
    
    col_input1, col_input2 = st.columns([1, 2])
    with col_input1:
        default_index = roles.index(st.session_state.form_course_role) if st.session_state.form_course_role in roles else 0
        input_role = st.selectbox("目標職位 (Role)", options=roles, index=default_index)
        input_score = st.slider("綜合媒合分數 (Match Score)", min_value=0, max_value=100, value=st.session_state.form_course_score)
        
    with col_input2:
        input_gap = st.text_area("能力落差說明 (Gap Description)", value=st.session_state.form_course_gap, height=150)
        
    submitted = st.form_submit_button("⚡ 開始全鏈路分析 (演算法搜尋 + Agent 路線編排)")

# ==========================================
# 3. 處理表單送出邏輯
# ==========================================
if submitted:
    if not input_gap:
        st.warning("請填寫能力落差說明")
    else:
        # A. 將 Mock 參數塞入 Session 供 _mock_fetch_user_gap 取用
        st.session_state["mock_course_gap_data"] = {
            "role": input_role,
            "match_score": input_score,
            "gap_description": input_gap
        }
        
        # B. 啟動演算法層
        st.info("🔄 階段一：正在打入 Supabase 資料庫，執行演算法篩選與權重排序...")
        service = CourseRecommendationService()
        
        # 為了將中繼結果顯示出來，我們手動跑一次演算法推導過程 (僅供展示)
        user_level = service.score_to_user_level(input_score)
        all_courses = service.fetch_candidate_courses(input_role)
        if not all_courses:
            st.error(f"資料庫中找不到與 `{input_role}` 相關的課程，請確認資料庫內有對應的種子資料。")
            st.stop()
            
        scored_courses = service.normalize_course_difficulty(all_courses)
        ranked = service.rank_courses(scored_courses, input_score, user_level)
        top_courses_raw = ranked[:5]
        
        st.markdown("#### 🔍 演算法海選結果 (Algorithm Top 5 Picks)")
        st.markdown("此清單為**完全未使用 LLM**，純靠關聯算法於 Supabase 計算撈出的最佳候選課程。")
        df_courses = pd.DataFrame(top_courses_raw)
        if not df_courses.empty:
            # 優先顯示這些有價值的參數欄位
            display_cols = ["course_name", "level", "course_level", "priority_score", "quality_score", "rating"]
            valid_cols = [c for c in display_cols if c in df_courses.columns]
            st.dataframe(df_courses[valid_cols], use_container_width=True)
            
        # C. 啟動 Agent 層
        st.info("🤖 階段二：正在啟動 CrewAI 的職涯分析師與路線設計師，請稍候 (約需 1 - 2 分鐘)...")
        with st.spinner("AI 正在深度解析您的技能樹並為這些課程安排學習戰略..."):
            try:
                # 這裡直接呼叫 service 的主流程 (它會重新再抓一次，但我們已經補好 Mock 了)
                result = service.get_recommendations("demo_user", top_k=5)
                
                st.success("🎉 學習路線圖生成完畢！")
                
                # --- 渲染結果 (Report Rendering) ---
                if isinstance(result, dict) and "overall_strategy" in result:
                    st.markdown("## 🗺️ 個人專屬進階路線圖 (Career Roadmap)")
                    
                    st.markdown("### 🎯 學習戰略大綱")
                    st.info(result.get("overall_strategy", ""))
                    
                    st.markdown("### 🏆 核心能力里程碑 (Key Milestones)")
                    for stone in result.get("key_milestones", []):
                        st.write(f"- {stone}")
                        
                    st.markdown("---")
                    st.markdown("### 📚 嚴選推薦路徑 (Learning Pathway)")
                    
                    pathway = result.get("learning_pathway", [])
                    if pathway:
                        for course in pathway:
                            # 支援 pydantic 轉型的 dict
                            st.markdown(f"#### 第 {course.get('priority_order', '?')} 序位：[{course.get('course_name', '未知課程名稱')}]({course.get('url', '#')})")
                            col_c1, col_c2 = st.columns([1, 2])
                            with col_c1:
                                st.markdown(f"**難度**：`{course.get('level', '')}`")
                                st.markdown(f"**類別**：{course.get('course_type', '不限')}")
                                st.markdown(f"**時長**：{course.get('duration_suggested', '依個人進度')}")
                                st.markdown(f"**評價**：⭐ {course.get('rating', '0.0')}  ({course.get('review_count', 0)} 則)")
                            with col_c2:
                                st.warning(f"**🤔 戰略推薦原因 (Strategic Reason)：**\n\n{course.get('strategic_reason', '')}")
                            st.markdown("---")
                            
                    with st.expander("🛠️ 查看代理人生成的 Raw JSON (Debug)"):
                        st.json(result)
                else:
                    st.error("⚠️ Agent 返回的結構非預期，下方為原始輸出：")
                    st.json(result)
                    
            except Exception as e:
                st.error(f"生成期間發生錯誤：{str(e)}")
