import json
import os
from dotenv import load_dotenv
from src.core.agent_engine.manager import CareerAgentManager

load_dotenv()

# ==========================================
# 假資料定義區 (Mock Data)
# ==========================================

def get_experienced_mock_data():
    """回傳有經驗者的問卷與特質假資料 (履歷將由 Manager 透過 user_id 從 DB 撈取)"""
    survey_data = {
    "module_a": {
    "q5_devops": "cloud_manual",
    "q8_domain": "B2B SaaS, Agile Management",
    "q3_backend": "db_auth_testing",
    "q6_ai_data": "pandas_numpy",
    "q2_frontend": "optimization_ssr",
    "q4_database": [
      "rdbms_sql",
      "nosql_document",
      "key_value_cache"
    ],
    "q7_security": "auth_rbac",
    "q1_languages": [
      {
        "name": "JavaScript",
        "score": 5
      },
      {
        "name": "TypeScript",
        "score": 5
      },
      {
        "name": "SQL",
        "score": 4
      }
    ]
    },
    "module_b": {
    "q14_process": "process_optimization",
    "q15_english": "global_comm",
    "q13_learning": "deep_dive_sharing",
    "q10_tech_choice": "tradeoff_analysis",
    "q12_code_review": "architecture_solid",
    "q9_troubleshoot": "incident_analysis",
    "q11_communication": "value_driven"
    },
    "module_c": {
    "q18_industry": "product_company",
    "q17_target_role": "fullstack",
    "q16_current_level": "lead_architect",
    "q19_search_status": "passive_open"
    },
    "module_d": {
    "q21_pressure": "consider_short_term",
    "q20_values_top3": [
      "technical_growth",
      "financial_reward",
      "team_culture"
    ],
    "q22_career_type": "manager",
    "q23_learning_style": [
      "official_docs",
      "hands_on_projects",
      "mentorship_community"
    ]
    }
    }

    trait_data = {
    "trait_created_at": "2026-03-04 11:06:00Z",
    "trait_raw_scores": {
    "decision": 2,
    "learning": 3,
    "transfer": 5,
    "ambiguity": 2,
    "structure": 9
    },
    "primary_archetype": "STRUCTURE_ARCHITECT",
    "trait_raw_responses": {
    "Q1": "C",
    "Q2": "A",
    "Q3": "A",
    "Q4": "B",
    "Q5": "A",
    "Q6": "B",
    "Q7": "B",
    "Q8": "A",
    "Q9": "A",
    "Q10": "A"
    },
    "secondary_archetypes": [
    "CROSS_DOMAIN_INTEGRATOR"
    ],
    "trait_normalized_scores": {
    "decision": 43,
    "learning": 50,
    "transfer": 86,
    "ambiguity": 57,
    "structure": 90
    }
    }
    
    return survey_data, trait_data


def get_entry_level_mock_data():
    """回傳無經驗者的問卷與特質假資料 (履歷將由 Manager 透過 user_id 從 DB 撈取)"""
    survey_data = {
    "module_a": {
    "q5_devops": "ftp_git_pull",
    "q8_domain": "行銷／消費者行為",
    "q3_backend": "script_only",
    "q6_ai_data": "api_only",
    "q2_frontend": "no_experience",
    "q4_database": [],
    "q7_security": "framework_default",
    "q1_languages": []
    },
    "module_b": {
    "q14_process": "no_process",
    "q15_english": "slow_reading",
    "q13_learning": "hoarding",
    "q10_tech_choice": "just_learned",
    "q12_code_review": "formalism",
    "q9_troubleshoot": "restart",
    "q11_communication": "passive_follow"
    },
    "module_c": {
    "q18_industry": "startup",
    "q17_target_role": "frontend",
    "q16_current_level": "entry_level",
    "q19_search_status": "passive_observing"
    },
    "module_d": {
    "q21_pressure": "tend_to_decline",
    "q20_values_top3": [
      "work_life_balance",
      "culture_fit",
      "technical_growth"
    ],
    "q22_career_type": "generalist",
    "q23_learning_style": [
      "video_courses",
      "documentation"
    ]
    }
    }

    trait_data = {
    "trait_created_at": "2026-03-04T09:05:00Z",
    "trait_raw_scores": {
    "decision": 3,
    "learning": 5,
    "transfer": 3,
    "ambiguity": 3,
    "structure": 0
    },
    "primary_archetype": "LEARNING_ACCELERATOR",
    "trait_raw_responses": {
    "Q1": "B",
    "Q2": "D",
    "Q3": "B",
    "Q4": "A",
    "Q5": "B",
    "Q6": "A",
    "Q7": "A",
    "Q8": "B",
    "Q9": "A",
    "Q10": "C"
    },
    "secondary_archetypes": [],
    "trait_normalized_scores": {
    "decision": 57,
    "learning": 70,
    "transfer": 57,
    "ambiguity": 71,
    "structure": 0
    }
    }

    return survey_data, trait_data


# ==========================================
# 測試情境區 (Test Cases)
# ==========================================

def verify_db_save(user_id: str):
    """驗證是否成功將生成的報告寫入 Supabase 資料庫"""
    from src.core.database.supabase_client import get_supabase_client
    supabase = get_supabase_client()
    
    print(f"\n🧪 驗證點：正在檢查 Supabase 中的 career_analysis_report 表 (user_id={user_id})...")
    try:
        response = supabase.table("career_analysis_report") \
            .select("*") \
            .eq("user_id", user_id) \
            .order("generated_at", desc=True) \
            .limit(1) \
            .execute()
        
        if response.data:
            record = response.data[0]
            print(f"✅ 成功！已從資料庫撈到最新生成的報告紀錄。")
            print(f"   - 紀錄 ID: {record.get('id')}")
            print(f"   - 報告版本: {record.get('report_version')}")
            print(f"   - 存入時間: {record.get('generated_at')}")
            print(f"   - 目標職位: {record.get('target_position')}")
        else:
            print("❌ 失敗：資料庫中找不到剛剛存入的報告。請檢查 DB 儲存邏輯。")
    except Exception as e:
        print(f"❌ 驗證過程中發生錯誤: {e}")


def test_experienced_analysis():
    """1. 帶入有經驗者假資料，並從 DB 撈取其履歷進行測試"""
    print("\n\n====== TEST CASE 1: EXPERIENCED ANALYSIS (Mock Data + DB Resume) ======")
    user_id = "7" # 強迫 Agent 去撈資料庫裡的該 user_id 的履歷
    manager = CareerAgentManager()
    survey_data, trait_data = get_experienced_mock_data()
    trait_data["user_id"] = user_id

    user_input = {
        "user_id": user_id,
        "survey_json": json.dumps(survey_data),
        "trait_json": json.dumps(trait_data)
    }

    print(f"🚀 啟動任務... Agent 將自主撈取 DB 中 User {user_id} 的履歷，並與【有經驗者假資料】進行分析。")
    result = manager.run_task("career_analysis", user_input)
    
    print("\n🎉 分析結果 (Analysis Result):")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    verify_db_save(user_id)
    print("\n💡 提示：您可以前往檢查 `logs/crewai_outputs/task_audit_trail.log`，看看 Agent 是否有留下稽核蹤跡！")
    print("🧠 進階提示：另外有紀錄 Agent 思考過程的 `logs/crewai_outputs/agent_thoughts_trail.log` 可以檢視！")


def test_entry_level_analysis():
    """2. 帶入無經驗者假資料，並從 DB 撈取其履歷進行測試"""
    print("\n\n====== TEST CASE 2: ENTRY LEVEL ANALYSIS (Mock Data + DB Resume) ======")
    user_id = "38" # 強迫 Agent 去撈資料庫裡的該 user_id 的履歷
    manager = CareerAgentManager()
    survey_data, trait_data = get_entry_level_mock_data()
    trait_data["user_id"] = user_id

    user_input = {
        "user_id": user_id,
        "survey_json": json.dumps(survey_data),
        "trait_json": json.dumps(trait_data)
    }

    print(f"🚀 啟動任務... Agent 將自主撈取 DB 中 User {user_id} 的履歷，並透過分流機制處理【無經驗/轉職者】分析。")
    result = manager.run_task("career_analysis", user_input)
    
    print("\n🎉 分析結果 (Analysis Result):")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    verify_db_save(user_id)
    print("\n💡 提示：您可以前往檢查 `logs/crewai_outputs/task_audit_trail.log`，看看 Agent 是否有留下稽核蹤跡！")
    print("🧠 進階提示：另外有紀錄 Agent 思考過程的 `logs/crewai_outputs/agent_thoughts_trail.log` 可以檢視！")


def test_analysis_with_db_survey():
    """3. 透過 user_id 從 DB 同時撈取履歷與問卷資料 (career_survey 表) 進行測試"""
    print("\n\n====== TEST CASE 3: DB SURVEY & DB RESUME ======")
    user_id = input("請輸入要測試的 user_id (可以直接 Enter 預設為 4): ").strip()
    if not user_id:
        user_id = "5"

    from src.core.database.supabase_client import get_supabase_client
    supabase = get_supabase_client()
    
    print(f"🔍 正在從資料庫 fetch user_id={user_id} 的 career_survey 資料...")
    try:
        response = supabase.table("career_survey").select("questionnaire_response, personality").eq("user_id", user_id).execute()
        
        if not response.data:
            print(f"❌ 找不到 user_id={user_id} 的 career_survey 資料！請確認該 user_id 有填寫問卷。")
            return
            
        record = response.data[0]
        survey_data = record.get("questionnaire_response", {})
        trait_data = record.get("personality", {})
        
        if isinstance(trait_data, dict):
             trait_data["user_id"] = user_id
             
        print("✅ 成功取得問卷與特質資料！")
    except Exception as e:
        print(f"❌ 撈取資料失敗: {e}")
        return

    manager = CareerAgentManager()
    
    user_input = {
        "user_id": user_id,
        "survey_json": json.dumps(survey_data) if isinstance(survey_data, dict) else survey_data,
        "trait_json": json.dumps(trait_data) if isinstance(trait_data, dict) else trait_data
    }

    print(f"🚀 啟動任務... Agent 將自主撈取 DB 中 User {user_id} 的履歷，並使用 DB 問卷資料進行分析。")
    result = manager.run_task("career_analysis", user_input)
    
    print("\n🎉 分析結果 (Analysis Result):")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    verify_db_save(user_id)
    print("\n💡 提示：您可以前往檢查 `logs/crewai_outputs/task_audit_trail.log`，看看 Agent 是否有留下稽核蹤跡！")
    print("🧠 進階提示：另外有紀錄 Agent 思考過程的 `logs/crewai_outputs/agent_thoughts_trail.log` 可以檢視！")


if __name__ == "__main__":
    print("請選擇你要執行的測試項目：")
    print("==========================")
    print("1: 測試有經驗者 (假資料 + 透過 user_id 從 DB 撈取履歷 + DB 儲存)")
    print("2: 測試無經驗者/轉職者 (假資料 + 透過 user_id 從 DB 撈取履歷 + DB 儲存)")
    print("3: 測試從 DB 撈取問卷與履歷 (全真實資料 + DB 儲存)")
    
    test_experienced_analysis()
    # test_entry_level_analysis()
    # test_analysis_with_db_survey()
