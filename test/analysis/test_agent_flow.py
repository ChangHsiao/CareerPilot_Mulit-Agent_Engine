import json
import os
from dotenv import load_dotenv
from src.core.agent_engine.manager import CareerAgentManager

load_dotenv()

def test_experienced_analysis():
    print("\n\n====== TEST CASE: EXPERIENCED ANALYSIS ======")
    manager = CareerAgentManager()

    INPUT_CAREER_DATA = {
    "module_a": {
        "q1_languages": [{"name": "Python", "score": 5}, {"name": "SQL", "score": 4}, {"name": "Git", "score": 4}],
        "q2_frontend": "unfamiliar",
        "q3_backend": "distributed_system",
        "q4_database": ["rdbms_sql", "key_value_cache"],
        "q5_devops": "k8s_cicd",
        "q6_ai_data": "api_consumer",
        "q7_security": "framework_default",
        "q8_domain": "電子商務"
    },
    "module_b": {
        "q9_troubleshoot": "incident_analysis",
        "q10_tech_choice": "tradeoff_analysis",
        "q11_communication": "alternative_solution",
        "q12_code_review": "architecture_solid",
        "q13_learning": "deep_dive_sharing",
        "q14_process": "process_optimization",
        "q15_english": "global_comm"
    },
    "module_c": {
        "q16_current_level": "senior",
        "q17_target_role": "backend",
        "q18_industry": "product_company",
        "q19_search_status": "passive_open"
    },
    "module_d": {
        "q20_values_top3": ["technical_growth", "social_impact", "financial_reward"],
        "q21_pressure": "consider_short_term",
        "q22_career_type": "specialist",
        "q23_learning_style": ["official_docs", "hands_on_projects"]
    }
    }

    INPUT_TRAIT_DATA = {
    "user_id": "1", # Assuming same user
    "trait_raw_responses": {"Q1": "C", "Q2": "A", "Q3": "B", "Q4": "C", "Q5": "A", "Q6": "B", "Q7": "B", "Q8": "A", "Q9": "A", "Q10": "A"},
    "trait_calculation_debug": {"structure_raw": 10, "ambiguity_raw": 0, "decision_raw": 2, "learning_raw": 4, "transfer_raw": 5},
    "trait_normalized_scores": {
        "structure": 95,
        "ambiguity": 35,
        "decision": 50,
        "learning": 60,
        "transfer": 85
    },
    "primary_archetype": "STRUCTURE_ARCHITECT",
    "secondary_archetypes": ["CROSS_DOMAIN_INTEGRATOR"],
    "trait_created_at": "2026-02-15T10:00:00Z"
    }

    RESUME_DATA = {
    "basics": {
    "name": "陳浩宇",
    "summary": "擁有 5 年經驗的後端工程師，專精於 Python 與高流量電商系統開發..."
    },
    "skills": {
    "languages": ["Python (Expert)", "SQL (Advanced)"],
    "frameworks": ["Django", "Flask", "FastAPI"],
    "infrastructure": ["Docker (Basic)", "AWS EC2/S3"] # 履歷顯示 K8s 經驗確實較少
    },
    "work": [
    {
      "company": "PChome 網路家庭",
      "position": "資深後端工程師",
      "highlights": ["主導雙11購物節高併發流量優化", "Redis 快取", "重構為微服務"]
    }
    ]
    }

    user_input = {
        "survey_json": json.dumps(INPUT_CAREER_DATA),
        "trait_json": json.dumps(INPUT_TRAIT_DATA),
        "resume_json": json.dumps(RESUME_DATA),
        "user_id": "user_123"
    }

    result = manager.run_task("career_analysis_experienced", user_input)
    print("\n🎉 Analysis Result:")
    print(json.dumps(result, indent=2, ensure_ascii=False))

def test_entry_level_analysis():
    print("\n\n====== TEST CASE: ENTRY LEVEL ANALYSIS (No DB Save) ======")
    manager = CareerAgentManager()

    # 1. 定義無經驗者的虛擬問卷資料 (Module A & B 前半部皆為 0 或空值)
    INPUT_CAREER_DATA = {
        "module_a": {
            # Q1~Q8 未填寫，由前端帶入 0 或空值
            "q1_languages": "", 
            "q2_frontend": 0,
            "q3_backend": 0,
            "q4_database": "",
            "q5_devops": 0,
            "q6_ai_data": 0,
            "q7_security": 0,
            "q8_domain": ""
        },
        "module_b": {
            # Q9~Q14 未填寫，由前端帶入 0 或空值
            "q9_troubleshoot": 0,
            "q10_tech_choice": 0,
            "q11_communication": 0,
            "q12_code_review": 0,
            "q13_learning": 0,
            "q14_process": 0,
            
            # 只有 Q15_english 因為非技術職位也可能填寫，我們給個正常值
            "q15_english": "fluent_reading"
        },
        "module_c": {
            "q16_current_level": "entry_level",
            "q17_target_role": "frontend",
            "q18_industry": "agency",
            "q19_search_status": "urgent_active"
        },
        "module_d": {
            "q20_values_top3": ["work_life_balance", "social_support", "good_management"],
            "q21_pressure": "avoid_if_possible",
            "q22_career_type": "generalist",
            "q23_learning_style": ["video_tutorials", "mentorship"]
        }
    }

    # 2. 定義人格特質問卷結果 (隨意一組假資料)
    INPUT_TRAIT_DATA = {
        "user_id": "test_entry_001",
        "trait_raw_responses": {"Q1": "A", "Q2": "B", "Q3": "A", "Q4": "A", "Q5": "B", "Q6": "A", "Q7": "C", "Q8": "B", "Q9": "B", "Q10": "A"},
        "trait_calculation_debug": {"structure_raw": 5, "ambiguity_raw": 8, "decision_raw": 6, "learning_raw": 7, "transfer_raw": 4},
        "trait_normalized_scores": {
            "structure": 50,
            "ambiguity": 80,
            "decision": 60,
            "learning": 70,
            "transfer": 40
        },
        "primary_archetype": "ADAPTIVE_PIONEER",
        "secondary_archetypes": ["AGILE_LEARNER"],
        "trait_created_at": "2026-03-04T12:00:00Z"
    }

    # 3. 定義一組完全沒有軟體相關經驗的履歷
    RESUME_DATA = {
        "basics": {
            "name": "王小明",
            "summary": "之前在餐飲業擔任店長 3 年，擅長與人溝通及處理突發狀況，對程式開發產生濃厚興趣，目前正在自學 Python 與網頁前端技術，希望能成功轉職為軟體工程師。"
        },
        "skills": {
            "languages": ["自學 Python (初學)", "自學 HTML/CSS (初學)"],
            "frameworks": [],
            "infrastructure": []
        },
        "work": [
            {
                "company": "美味早午餐",
                "position": "店長",
                "highlights": [
                    "負責店鋪日常營運，帶領 5 人團隊",
                    "處理客訴與突發狀況，提升顧客滿意度 15%",
                    "優化排班與備料流程，降低 10% 食材浪費"
                ]
            }
        ]
    }

    user_input = {
        "survey_json": json.dumps(INPUT_CAREER_DATA),
        "trait_json": json.dumps(INPUT_TRAIT_DATA),
        "resume_json": json.dumps(RESUME_DATA),
        "user_id": "test_entry_001"
    }

    # 注意：我們傳入 "career_analysis" 讓 manager.py 啟動自動分流機制
    # 預期它會因為 q1_languages 分數皆為0/null，而自動切換為 career_analysis_entry_level
    print(f"🚀 啟動任務... 將測試無經驗者分流機制。")
    
    # 為了避免存入資料庫，我們暫時攔截或不使用包含存庫邏輯的 user_id
    # 若 Manager.py 中有 DB 儲存，我們就不提供真實存在的 supabase uuid，此測試會在儲存時 try-except 報錯但仍會回傳結果。
    result = manager.run_task("career_analysis", user_input)
    
    print("\n🎉 Analysis Result (顯示於終端機):")
    print(json.dumps(result, indent=2, ensure_ascii=False))

def test_analysis_with_db_resume():
    """
    實測：Agent 從 DB 撈取履歷 + 配合虛擬問卷資料 + 自動儲存報告。
    符合：GAP_ANALYSIS_STORAGE_PLAN.md 規範。
    """
    print("\n\n====== 實測：自動化流程 (DB 履歷 + 虛擬資料 + 自動儲存) ======")
    from src.core.database.supabase_client import get_supabase_client
    
    user_id = "1" # 指定測試 User ID
    manager = CareerAgentManager()
    supabase = get_supabase_client()

    # 1. 定義虛擬資料 (模擬前端傳入的問卷與心理測驗結果)
    INPUT_CAREER_DATA = {
        "module_a": {
        "q1_languages": [{"name": "Python", "score": 5}, {"name": "SQL", "score": 4}, {"name": "Git", "score": 4}],
        "q2_frontend": "unfamiliar",
        "q3_backend": "distributed_system",
        "q4_database": ["rdbms_sql", "key_value_cache"],
        "q5_devops": "k8s_cicd",
        "q6_ai_data": "api_consumer",
        "q7_security": "framework_default",
        "q8_domain": "電子商務"
    },
    "module_b": {
        "q9_troubleshoot": "incident_analysis",
        "q10_tech_choice": "tradeoff_analysis",
        "q11_communication": "alternative_solution",
        "q12_code_review": "architecture_solid",
        "q13_learning": "deep_dive_sharing",
        "q14_process": "process_optimization",
        "q15_english": "global_comm"
    },
    "module_c": {
        "q16_current_level": "senior",
        "q17_target_role": "backend",
        "q18_industry": "product_company",
        "q19_search_status": "passive_open"
    },
    "module_d": {
        "q20_values_top3": ["technical_growth", "social_impact", "financial_reward"],
        "q21_pressure": "consider_short_term",
        "q22_career_type": "specialist",
        "q23_learning_style": ["official_docs", "hands_on_projects"]
    }
    }
    INPUT_TRAIT_DATA = {
        "user_id": "1", # Assuming same user
    "trait_raw_responses": {"Q1": "C", "Q2": "A", "Q3": "B", "Q4": "C", "Q5": "A", "Q6": "B", "Q7": "B", "Q8": "A", "Q9": "A", "Q10": "A"},
    "trait_calculation_debug": {"structure_raw": 10, "ambiguity_raw": 0, "decision_raw": 2, "learning_raw": 4, "transfer_raw": 5},
    "trait_normalized_scores": {
        "structure": 95,
        "ambiguity": 35,
        "decision": 50,
        "learning": 60,
        "transfer": 85
    },
    "primary_archetype": "STRUCTURE_ARCHITECT",
    "secondary_archetypes": ["CROSS_DOMAIN_INTEGRATOR"],
    "trait_created_at": "2026-02-15T10:00:00Z"
    }

    # 注意：這裡「不提供」resume_json，強迫 Agent 去撈資料庫裡的 user_id=1 履歷
    user_input = {
        "user_id": user_id,
        "survey_json": INPUT_CAREER_DATA,
        "trait_json": INPUT_TRAIT_DATA
    }

    # 2. 執行任務
    print(f"🚀 啟動任務... Agent 將自主撈取 User {user_id} 的履歷內容並進行分析。")
    result = manager.run_task("career_analysis_experienced", user_input)
    
    print("\n🎉 分析完成！")

    # 3. 驗證資料庫儲存 (這是關鍵驗證點)
    print(f"🧪 驗證點：正在檢查 Supabase 中的 career_analysis_report 表...")
    try:
        # 查詢最新的一筆紀錄，確認是否為剛剛存入的
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
            print("❌ 失敗：資料庫中找不到剛剛存入的報告。請檢查 Handler 邏輯。")
    except Exception as e:
        print(f"❌ 驗證過程中發生錯誤: {e}")

def test_resume_analysis():
    print("\n\n====== TEST CASE: RESUME CRITIQUE ======")
    manager = CareerAgentManager(model_name="o3-mini")

    user_input = {
        "user_id": "user_123",
        "resume_content": "我是一個有五年經驗的工程師，我會寫程式，也喜歡學習新技術。",
        "target_role": "資深後端工程師"
    }

    result = manager.run_task("resume_analysis", user_input)
    print("\n🎉 Analysis Result:")
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    # 這裡可以選擇要跑哪個測試
    
    # 新增的無經驗者邏輯測試
    test_entry_level_analysis()
    
    # 以下為原有測試，先註解掉以專注測試新分支
    # test_analysis_with_db_resume()
    # test_experienced_analysis()
    # test_resume_critique()
