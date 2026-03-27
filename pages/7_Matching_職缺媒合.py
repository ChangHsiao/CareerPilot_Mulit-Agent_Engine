import streamlit as st
import json
import logging
import os
import pandas as pd

from src.core.database.qdrant_client import get_qdrant_client
from src.core.database.supabase_client import get_supabase_client
from src.features.matching.service import CareerMatchingService
from src.core.agent_engine.result_handlers import HandlerRegistry

# ==========================================
# 0. 阻止寫入資料庫：覆寫 HandlerRegistry
# ==========================================
class MockHandler:
    def process(self, data, **kwargs):
        pass # 確保分析結果不會污染寫回資料庫

original_get_handler = HandlerRegistry.get_handler
def _mock_get_handler(self, task_type):
    return MockHandler()

HandlerRegistry.get_handler = _mock_get_handler

# ==========================================
# 1. 頁面 UI 與雙模式設定
# ==========================================
st.set_page_config(page_title="職缺媒合與面試分析", page_icon="🎯", layout="wide")
st.title("🎯 職缺媒合與面試攻防模組 (Dual-Mode 雙擎架構)")
st.markdown("本模組是系統中最複雜的核心，結合了 **Qdrant 向量混合搜尋 (Hybrid Search)**、**Numpy 數學硬條件重排 (Re-ranking)** 以及 **CrewAI 十股平行運算的人工智慧審查**。")

# 模式切換
engine_mode = st.radio(
    "⚙️ 請選擇演示引擎模式：",
    options=["🔴 Live Database Engine (真實打入 Supabase 與 Qdrant 進行多階段檢索) [火力展示首選]", 
             "🟢 Full Mock Engine (完全無痕斷網/本地快速展示用預設假資料)"],
    index=0
)

st.markdown("---")

display_results = []

# ==========================================
# 2. Live 模式表單設計
# ==========================================
if "Live Database Engine" in engine_mode:
    st.subheader("真實資料庫檢索參數定錨 (Live DB Query Payload)")
    st.markdown("系統將透過下列身分去抓取您在資料庫中最新版本的「六維能力評估雷達圖」，接著去 Qdrant 抓該文件對應的 1536 維特徵矩陣！")
    
    col_mock1, col_mock2 = st.columns([1, 3])
    with col_mock1:
        if st.button("🚀 載入範例展示帳號 (Demo Test User)"):
            st.session_state["mock_user_id"] = 3
            st.session_state["mock_doc_id"] = 5
            st.session_state["mock_source"] = "OPTIMIZATION"
            st.rerun()
        
    with st.form("live_matching_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            input_user_id = st.number_input("使用者 ID (User ID)", value=st.session_state.get("mock_user_id", 3), step=1)
        with col2:
            input_source = st.radio("履歷來源表單路由 (Source Type)", options=["RESUME", "OPTIMIZATION"], index=1 if st.session_state.get("mock_source", "") == "OPTIMIZATION" else 0)
        with col3:
            input_doc_id = st.number_input("文件編號 (Document ID)", value=st.session_state.get("mock_doc_id", 5), step=1)
            
        st.markdown("**(Optional) Qdrant Payload 過濾條件**")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            salary_min = st.number_input("期望最低年薪 (最低底薪門檻過濾)", value=600000, step=50000)
        with col_f2:
            input_city = st.multiselect("地區過濾 (City)", options=["台北市", "新北市", "桃園市", "新竹市", "新竹縣", "台中市", "台南市", "高雄市"], default=[])
        
        submitted = st.form_submit_button("⚡ 啟動全鏈路即時混合檢索 (Execute Live Pipeline)")

    if submitted:
        # 實例化真實的服務
        qdrant_client = get_qdrant_client()
        supabase_client = get_supabase_client()
        openai_api_key = os.getenv("OPENAI_API_KEY", "")
        
        service = CareerMatchingService(
            qdrant_client=qdrant_client,
            supabase_client=supabase_client,
            openai_api_key=openai_api_key
        )
        
        filters = {
            "salary_min": salary_min,
            "city": input_city
        }
        
        st.info(f"🔄 **[日誌 Pipeline Logger]** 收到請求...\n1. 正在掃描並鎖定 User `{input_user_id}` 最高版本的 `career_analysis_report` 雷達圖...\n2. 準備前往 Qdrant 提取 `doc_id={input_doc_id}` 的履歷向量...")
        
        with st.spinner("🤖 pipeline 正在穿越向量海與 Supabase 關聯表格...並由 CrewAI 平行審查 Top 10 職缺 (約需 30-90 秒)"):
            try:
                # 執行真實調用
                results = service.find_best_jobs(
                    user_id=input_user_id,
                    document_id=input_doc_id,
                    source_type=input_source,
                    filters=filters
                )
                st.session_state["live_matching_results"] = results
                st.success(f"🎉 搜尋與 AI 分析完畢！這是一份結合混合檢索的精選求職清單。")
            except Exception as e:
                st.error(f"❌ 執行期間發生錯誤 (請確認此資料庫帳號具備雷達圖與履歷向量)：{str(e)}")
                
    # 取出暫存的結果準備渲染
    display_results = st.session_state.get("live_matching_results", [])

# ==========================================
# 3. Mock 模式表單設計
# ==========================================
else:
    st.subheader("斷網安全展示模式 (Full Mock Engine)")
    st.markdown("此模式完全不向外發送任何 API Request，直接讀取本機燒錄好的「完美 104 職缺體驗 JSON 架構」來快速展示畫面風格與排版。")
    
    if st.button("⚡ 立即載入精美假亂真報告 (Load Mock Output)"):
        # 隨便提供假的完美 JSON 
        mock_json = [
            {
                "job_id": "mock_101",
                "job_title": "資深後端軟體工程師 (Sr. Backend Engineer)",
                "company_name": "星際雲端科技股份有限公司",
                "industry": "全球互聯網業",
                "full_address": "台北市信義區信義路五段 7 號 (101 大樓)",
                "source_url": "https://www.104.com.tw/job/mock1",
                "final_score": "88.5%",
                "recommendation_reason": "從 Numpy 重排序結果看來，您的後端開發分數 (D2=5) 與系統架構分數 (D5=4) 完全符合此職缺對於高併發與大流量服務的招聘需求；語意相似度驗證了您過去有豐富的金融底層處理經驗。",
                "strengths": "✅ 精通 Python 與 FastAPI 等非同步架構。\n✅ 履歷中提及的 Docker / K8s 微服務部署經驗完美對接此職缺。\n✅ 量化的 SQL 優化成果非常吸睛。",
                "weaknesses": "⚠️ 職缺中要求具備『跨國遠端跨部門協作能力』，您的軟實力 D6 分數僅拿到 2.5 分，需特別留意面試官對溝通手腕的測試。",
                "interview_tips": "👉 請在面試第一關主動丟出自己主導設計『分散式 Message Queue』的系統架構圖草稿。\n👉 被問到弱勢溝通題時，用 STAR 原則說明自己是如何將難懂的資料庫正規化名詞向行銷部門解釋的過往案例。"
            },
            {
                "job_id": "mock_102",
                "job_title": "全端架構工程師 (Full Stack Architect)",
                "company_name": "人工智慧趨勢運算中心",
                "industry": "AI 人工智慧與巨量資料",
                "full_address": "新竹縣竹北市新竹科學園區",
                "source_url": "https://www.104.com.tw/job/mock2",
                "final_score": "82.0%",
                "recommendation_reason": "雖然該職缺名為全端，但根據語義檢索指出，其工作內容高達 80% 專注於後端的 AI API 與資料庫調校。您強大的 D4 (運算與資料) 可以作為敲門磚切入。",
                "strengths": "✅ D4 達到滿分，強烈展現能接手大規模數據集與 RAG 系統的實力。\n✅ 曾在前一份工作擔任過開發主力，這點正好補足新創公司沒人帶人的陣痛期。",
                "weaknesses": "⚠️ D1 前端分數落在 2 分，而職缺說明有提到需協助維護少量的 React 內部儀表板。",
                "interview_tips": "👉 面試官極有可能拿 React 生命週期或 JS 閉包考你。不要硬背，大膽承認前端較弱，並立刻轉守為攻說：「但我目前有自學並在做一個 Todo App，而我能確保後端的 REST API 提供得異常穩定，從根本減輕前端工作量。」"
            }
        ]
        st.session_state["mock_matching_results"] = mock_json
        
    display_results = st.session_state.get("mock_matching_results", [])

# ==========================================
# 4. 渲染職缺卡片
# ==========================================
if display_results:
    st.markdown("---")
    st.markdown(f"## 🏆 精選 CrewAI 職缺推薦榜單 (總計 {len(display_results)} 筆)")
    
    for idx, job in enumerate(display_results, 1):
        with st.container():
            st.markdown(f"### ✨ [Top {idx}] {job.get('job_title', '未知職缺')} "
                        f"| 總合匹配率：<span style='color:#e14c3c; font-weight:bold;'>{job.get('final_score', '0%')}</span>", 
                        unsafe_allow_html=True)
            st.markdown(f"**🏢 {job.get('company_name', '未知公司')}** · *{job.get('industry', '未分類產業')}*")
            st.markdown(f"📍 {job.get('full_address', '')} | 🔗 [前往原職缺招募連結]({job.get('source_url', '#')})")
            
            # 使用兩欄設計，左邊是 AI 洞察，右邊是優缺點
            c1, c2 = st.columns([1, 1])
            with c1:
                st.info(f"**🤖 AI 教練的推薦底層邏輯：**\n\n{job.get('recommendation_reason', '')}")
                st.warning(f"**💬 面試攻防破局策略 (Interview Tips)：**\n\n{job.get('interview_tips', '')}")
            with c2:
                st.success(f"**💪 履歷中的超級武器 (Strengths)：**\n\n{job.get('strengths', '')}")
                st.error(f"**⚠️ 企業眼中的潛在雷區 (Weaknesses)：**\n\n{job.get('weaknesses', '')}")
                
        st.markdown("---")

    with st.expander("🛠️ 查看最終產出的 Raw JSON (Debug / 開發者檢視用)"):
        st.json(display_results)

