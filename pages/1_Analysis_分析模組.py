import streamlit as st
import json
import logging
import pandas as pd

# ==========================================
# 0. Mock Data Templates (預設範本)
# ==========================================
# (1) 資深 AI 應用工程師範本
EXPERIENCED_RESUME = {
  "skills": [
    {
      "name": "JavaScript",
      "level": 3
    },
    {
      "name": "HTML/CSS",
      "level": 4
    },
    {
      "name": "React",
      "level": 2
    }
  ],
  "privacy": "private",
  "summary": "2025 年畢業生，無正式工作經驗。自學前端約 6 個月，做過幾個練習專案。積極求職中。",
  "projects": [
    "練習: Todo App",
    "練習: 氣象 API 串接",
    "畢業專題: 線上問卷系統 (前端部分)"
  ],
  "education": [
    {
      "details": "國立台灣大學 資工系 學士 2025 畢業"
    }
  ],
  "experience": [],
  "personal_info": {
    "name": "劉家豪 (David Liu)",
    "email": "demo_user@test.com",
    "github": "https://github.com/david-liu-remote",
    "location": "Remote (Taoyuan)"
  }
}

EXPERIENCED_SURVEY = {
    "questionnaire_response": {
    "module_a": {
    "q5_devops": "paas_only",
    "q8_domain": "Online Survey Systems",
    "q3_backend": "unfamiliar",
    "q6_ai_data": "api_consumer",
    "q2_frontend": "basic_html_css",
    "q4_database": [
      "rdbms_sql"
    ],
    "q7_security": "framework_default",
    "q1_languages": [
      {
        "name": "JavaScript",
        "score": 3
      },
      {
        "name": "HTML/CSS",
        "score": 4
      }
    ]
    },
    "module_b": {
    "q14_process": "waterfall_none",
    "q15_english": "slow_reading",
    "q13_learning": "hoarding",
    "q10_tech_choice": "popularity",
    "q12_code_review": "formality",
    "q9_troubleshoot": "log_search",
    "q11_communication": "comply"
    },
    "module_c": {
    "q18_industry": "software_house",
    "q17_target_role": "frontend",
    "q16_current_level": "entry_level",
    "q19_search_status": "active_urgent"
    },
    "module_d": {
    "q21_pressure": "accept_immediately",
    "q20_values_top3": [
      "financial_reward",
      "technical_growth",
      "team_culture"
    ],
    "q22_career_type": "generalist",
    "q23_learning_style": [
      "video_courses",
      "hands_on_projects"
    ]
    }
    }
}

EXPERIENCED_TRAIT = {
  "trait_created_at": "2026-03-04 11:09:00Z",
  "trait_raw_scores": {
    "decision": 3,
    "learning": 3,
    "transfer": 5,
    "ambiguity": 2,
    "structure": 8
  },
  "primary_archetype": "STRUCTURE_ARCHITECT",
  "secondary_archetypes": [
    "CROSS_DOMAIN_INTEGRATOR"
  ],
  "trait_normalized_scores": {
    "decision": 57,
    "learning": 50,
    "transfer": 86,
    "ambiguity": 57,
    "structure": 80
  }
}

# (2) 無經驗/白紙轉職者範本
ENTRY_LEVEL_RESUME = {
  "name": "吳宜蓁",
  "email": "ycwu@example.com",
  "phone": "0956-789-012",
  "github": "https://github.com/test-designer-wu",
  "skills": {
    "tools": [
      "Figma",
      "Adobe Illustrator",
      "Zeplin",
      "VS Code（自學中）"
    ],
    "domain": [
      "UI/UX 設計",
      "Design System",
      "Prototype",
      "用戶研究"
    ],
    "programming": [
      "CSS（基礎）",
      "JavaScript（入門）"
    ]
  },
  "summary": "實踐大學視覺傳達設計系畢業，現任 UI 設計師 1 年，熟悉 Figma，對 CSS 與 JavaScript 有入門概念，目標打通設計到實作的完整能力鏈，轉型全端工程師。",
  "linkedin": "null",
  "projects": [
    {
      "name": "設計系統建置（工作中）",
      "tools": [
        "Figma",
        "Storybook（學習中）"
      ],
      "description": "主導公司設計系統建置，定義 Color Token、Typography 規範、Component Library，與工程師共同維護"
    },
    {
      "name": "個人網頁作品集（進行中）",
      "tools": [
        "HTML",
        "CSS",
        "JavaScript"
      ],
      "description": "以 HTML/CSS/JavaScript 建立個人設計作品集網站，自學 DOM 操作與基礎動效"
    }
  ],
  "education": [
    {
      "degree": "學士",
      "school": "實踐大學",
      "department": "視覺傳達設計系",
      "graduation_year": "2024"
    }
  ],
  "experience": [
    {
      "title": "UI 設計師",
      "company": "某設計工作室",
      "duration": "2024/07 – 現在（約1年）",
      "description": [
        "負責 App 與網頁 UI 介面設計，交付高保真 Figma 原型",
        "與前端工程師協作，提供 Design Token 與切版規範文件",
        "參與用戶訪談與可用性測試，迭代優化設計方案"
      ]
    }
  ],
  "autobiography": "我是吳宜蓁，一年的 UI 設計師工作讓我深刻體會設計與工程之間的鴻溝。我希望成為能同時掌握設計美感與技術實作的全端工程師，讓好的設計不再因工程限制而妥協。"
}

ENTRY_LEVEL_SURVEY = {
    "questionnaire_response": {
    "module_a": {
    "q5_devops": "ftp_git_pull",
    "q8_domain": "生命科學／生物醫學",
    "q3_backend": "script_only",
    "q6_ai_data": "api_only",
    "q2_frontend": "no_experience",
    "q4_database": [],
    "q7_security": "framework_default",
    "q1_languages": []
    },
    "module_b": {
    "q14_process": "no_process",
    "q15_english": "translate_dependent",
    "q13_learning": "wait_for_project",
    "q10_tech_choice": "just_learned",
    "q12_code_review": "formalism",
    "q9_troubleshoot": "restart",
    "q11_communication": "passive_follow"
    },
    "module_c": {
    "q18_industry": "big_tech",
    "q17_target_role": "data_scientist",
    "q16_current_level": "entry_level",
    "q19_search_status": "active_urgent"
    },
    "module_d": {
    "q21_pressure": "consider_short_term",
    "q20_values_top3": [
      "technical_growth",
      "financial_reward",
      "work_life_balance"
    ],
    "q22_career_type": "specialist",
    "q23_learning_style": [
      "video_courses",
      "hands_on_projects"
    ]
    }
    }
}

ENTRY_LEVEL_TRAIT = {
  "trait_created_at": "2026-03-04T09:00:00Z",
  "trait_raw_scores": {
    "decision": 2,
    "learning": 3,
    "transfer": 5,
    "ambiguity": 0,
    "structure": 10
  },
  "primary_archetype": "STRUCTURE_ARCHITECT",
  "secondary_archetypes": [
    "CROSS_DOMAIN_INTEGRATOR"
  ],
  "trait_normalized_scores": {
    "decision": 43,
    "learning": 50,
    "transfer": 86,
    "ambiguity": 29,
    "structure": 100
  }
}

# ==========================================
# 1. 阻止資料庫讀取與寫入 (Monkey Patching)
# ==========================================
import src.core.database.supabase_client as db_client

def _mock_get_latest_resume(user_id: str):
    # 直接回傳存在 session_state 內的最新履歷字串 (代表從 Text Area 攔截)
    return st.session_state.get("mock_resume_text", "")

db_client.get_latest_resume = _mock_get_latest_resume

import src.core.agent_engine.result_handlers as handlers
class MockHandler:
    def process(self, data, **kwargs):
        pass # 不寫入真實的資料庫

original_get_handler = handlers.HandlerRegistry.get_handler
def _mock_get_handler(self, task_type):
    return MockHandler()
handlers.HandlerRegistry.get_handler = _mock_get_handler

# 引入核心控制器
from src.core.agent_engine.manager import CareerAgentManager

# ==========================================
# 2. 頁面 UI 與狀態管理
# ==========================================
st.set_page_config(page_title="AI 面試火力展示：分析模組", page_icon="🧠", layout="wide")
st.title("🧠 職涯診斷分析模組 (Data-Driven 面試展示版)")
st.markdown("本頁面專為展示 **複雜 JSON 結構接軌**、**動態自動路由** 與 **Agent 協作** 所設計。完全隔離真實資料庫，讓您可以在面試時向主考官展示系統處理多維度數據的能力。")

# 初始化 session state 中的表單預設內容
if "form_survey_json" not in st.session_state:
    st.session_state.form_survey_json = json.dumps(EXPERIENCED_SURVEY, ensure_ascii=False, indent=2)
if "form_trait_json" not in st.session_state:
    st.session_state.form_trait_json = json.dumps(EXPERIENCED_TRAIT, ensure_ascii=False, indent=2)
if "form_resume_text" not in st.session_state:
    st.session_state.form_resume_text = EXPERIENCED_RESUME

st.subheader("一鍵注入測試場景 (Mock Data Injectors)")
col_mock1, col_mock2, _ = st.columns([1, 1, 2])
with col_mock1:
    if st.button("🚀 載入【資深 AI 工程師】測試包"):
        st.session_state.form_survey_json = json.dumps(EXPERIENCED_SURVEY, ensure_ascii=False, indent=2)
        st.session_state.form_trait_json = json.dumps(EXPERIENCED_TRAIT, ensure_ascii=False, indent=2)
        st.session_state.form_resume_text = EXPERIENCED_RESUME
        st.rerun()
with col_mock2:
    if st.button("🌱 載入【白紙轉職者】測試包"):
        st.session_state.form_survey_json = json.dumps(ENTRY_LEVEL_SURVEY, ensure_ascii=False, indent=2)
        st.session_state.form_trait_json = json.dumps(ENTRY_LEVEL_TRAIT, ensure_ascii=False, indent=2)
        st.session_state.form_resume_text = ENTRY_LEVEL_RESUME
        st.rerun()

st.markdown("---")

st.subheader("Raw Data 編輯區 (Payload Inspector)")
st.markdown("在此區域，您可以任意修改送給後端 CrewAI 的 Payload 結構，觀察系統的容錯與動態抓取邏輯。")

with st.form("analysis_form"):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**1. Raw JSON (職能與特質問卷)**")
        input_survey = st.text_area("Survey JSON:", value=st.session_state.form_survey_json, height=200)
        input_trait = st.text_area("Trait JSON:", value=st.session_state.form_trait_json, height=200)
    with col2:
        st.markdown("**2. Raw Text (個人原始履歷內容)**")
        input_resume = st.text_area("Resume Content:", value=st.session_state.form_resume_text, height=450)
        
    submitted = st.form_submit_button("⚡ 啟動 CrewAI 分析邏輯 (Execute Pipeline)")

# 即時顯示動態解析結果
if input_survey:
    try:
        parsed_survey = json.loads(input_survey)
        survey_data = parsed_survey.get("questionnaire_response", parsed_survey)
        target_role = survey_data.get("module_c", {}).get("q17_target_role", "未知名稱")
        
        # 模擬後端的有經驗判斷邏輯
        q1_langs = survey_data.get("module_a", {}).get("q1_languages", [])
        has_experience = False
        if isinstance(q1_langs, list):
            for lang in q1_langs:
                if isinstance(lang, dict) and lang.get("score") not in [None, 0, "0", 0.0, ""]:
                    has_experience = True
                    break
        
        route_msg = "🚨 `career_analysis_experienced` (準備啟動技術查核)" if has_experience else "🌱 `career_analysis_entry_level` (準備啟動技能轉譯)"
        
        st.info(f"**系統即時解析 (Dynamic Parser)**：\n- 🎯 偵測到的目標職缺：`{target_role}`\n- 🔀 後台任務路由預測：{route_msg}")
    except Exception as e:
        st.warning("⚠️ JSON 格式有誤，請檢查雙引號或是括號。")

# ==========================================
# 3. 處理表單送出邏輯與圖表渲染
# ==========================================
if submitted:
    # 保存給 Monkey patch 工具讀取
    st.session_state["mock_resume_text"] = input_resume
    
    # 建立輸入物件
    user_input_dict = {
        "user_id": "demo_user",
        "survey_json": input_survey,
        "trait_json": input_trait,
        "current_timestamp": "2024-10-01T12:00:00Z", # Mock 預設
        "report_version": "1.0",
        "STANDARD_ROLES": [
            "前端工程師", "後端工程師", "全端工程師", 
            "資料科學家/數據分析師", "AI 工程師", "DevOps/SRE 工程師"
        ]
    }

    manager = CareerAgentManager()
    
    with st.spinner("🤖 CrewAI 代理人兵團正在分析上述的 JSON 與履歷，請稍等 (約需 1 - 2 分鐘，請耐心等候)..."):
        try:
            # 觸發核心邏輯：career_analysis，它會在 manager 內部根據 survey 自動分流
            result = manager.run_task("career_analysis", user_input_dict)
            st.success("🎉 分析報告生成成功！")
            
            # --- 渲染結果 (Report Rendering) ---
            if isinstance(result, dict) and "preliminary_summary" in result:
                st.markdown("## 📊 職涯診斷與落差分析報告")
                
                # 1. 核心洞察 (Core Insight)
                st.markdown("### 💡 顧問核心洞察 (Core Insight)")
                insight = result.get("preliminary_summary", {}).get("core_insight", "")
                st.info(insight)
                
                st.markdown("---")
                
                # 2. 目前狀態與目標落差
                col_gap1, col_gap2 = st.columns(2)
                gap_analysis = result.get("gap_analysis", {})
                current = gap_analysis.get("current_status", {})
                target = gap_analysis.get("target_position", {})
                
                with col_gap1:
                    st.markdown(f"**👨‍💻 目前職級**：{current.get('actual_level', '未知')}")
                    st.markdown(f"**🎯 目標職位**：{target.get('role', '未知')}")
                    st.markdown(f"**📈 綜合匹配度**：{target.get('match_score', '未知')}")
                
                with col_gap2:
                    st.markdown("**⚠️ 認知落差警告**")
                    st.write(current.get("cognitive_bias", ""))
                
                # 3. SWOT 深度落差
                with st.expander("🔍 深度落差分析 (SWOT)", expanded=True):
                    st.markdown(target.get("gap_description", "").replace("\n", "\n\n"))
                
                # 4. 雷達圖分析 (使用 Streamlit 原生的 bar chart 代替)
                st.markdown("### 🕸️ 六維能力評估分數")
                radar = result.get("radar_chart", {}).get("dimensions", [])
                
                if radar:
                    try:
                        df = pd.DataFrame(radar)
                        df.set_index("axis", inplace=True)
                        st.bar_chart(df)
                    except Exception:
                        for row in radar:
                            st.write(f"- {row.get('axis')}: {row.get('score')}")
                
                # 5. 行動計畫
                st.markdown("### 🗺️ 短中長期行動計畫 (Action Plan)")
                action_plan = result.get("action_plan", {})
                st.markdown(f"**【短期計畫 (1-3個月)】**\n\n{action_plan.get('short_term', '')}")
                st.markdown(f"**【中期計畫 (3-6個月)】**\n\n{action_plan.get('mid_term', '')}")
                st.markdown(f"**【長期計畫 (6個月以上)】**\n\n{action_plan.get('long_term', '')}")
                
                # 提供 Raw JSON 查看
                with st.expander("🛠️ 查看代理人生成的最終 Raw JSON (驗證格式用)"):
                    st.json(result)
            else:
                # 容錯：若回傳格式不是完整的 dict
                st.markdown("### ⚠️ Agent 返回的結構非預期")
                st.json(result)
                
        except Exception as e:
            st.error(f"分析期間系統發生錯誤：{str(e)}")
