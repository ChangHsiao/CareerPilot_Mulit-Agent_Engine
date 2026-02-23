# test/test_multi_agent_flow.py
import json
import os
import sys
from dotenv import load_dotenv

# 將專案根目錄加入路徑，確保能正確 import src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.Multi_Agent.manager import CareerAgentManager

def test_career_analysis():
    load_dotenv()
    
    # 1. 初始化總代理 (預設使用 o3-mini)
    # 注意：請確保環境變數中已有 OPENAI_API_KEY
    manager = CareerAgentManager(model_name="o3-mini")

    # 2. 準備模擬資料 (Mock Data)
    mock_survey = {
        "user_id": "test_user_001",
        "module_a": {
            "q1_languages": [{"name": "Python", "score": 5}, {"name": "SQL", "score": 4}],
            "q2_frontend": "unfamiliar",
            "q3_backend": "distributed_system",
            "q5_devops": "docker_basic",
            "q6_ai_data": "pandas_numpy",
            "q7_security": "owasp_basic",
            "q4_database": ["rdbms_sql", "nosql_document"]
        },
        "module_b": {
            "q9_troubleshoot": "log_search",
            "q10_tech_choice": "team_familiarity",
            "q11_communication": "alternative_solution",
            "q12_code_review": "logic_safety",
            "q13_learning": "consistent_input",
            "q14_process": "agile_scrum",
            "q15_english": "fluent_reading"
        },
        "module_c": {"q16_current_level": "senior", "q17_target_role": "backend"}
    }
    
    mock_trait = {
        "user_id": "test_user_001",
        "trait_normalized_scores": {
            "structure": 95,
            "ambiguity": 35,
            "decision": 50,
            "learning": 60,
            "transfer": 85
        },
        "primary_archetype": "STRUCTURE_ARCHITECT"
    }
    
    mock_resume = {
        "basics": {
            "name": "測試工程師", 
            "summary": "擁有 5 年經驗的後端開發者，專精於 Python 與高流量電商系統開發。"
        },
        "skills": {
            "languages": ["Python (Expert)", "SQL (Advanced)"],
            "infrastructure": ["Docker (Basic)"]
        }
    }

    user_input = {
        "survey_json": json.dumps(mock_survey),
        "trait_json": json.dumps(mock_trait),
        "resume_json": json.dumps(mock_resume),
        "target_role": "backend",
        "learning_style": "Hands-on Projects"
    }

    # 3. 測試：有經驗者流程
    print("\n" + "="*50)
    print("🚀 測試任務：有經驗者職涯分析 (CAREER_ANALYSIS_EXPERIENCED)")
    print("="*50)
    
    try:
        # 使用 TaskType 字串，manager 內部會轉換
        result_exp = manager.run_task("career_analysis_experienced", user_input)
        print("\n✅ 執行成功！產出的報告摘要：")
        print(f"核心洞察: {result_exp.get('preliminary_summary', {}).get('core_insight')}")
        print(f"評估職級: {result_exp.get('gap_analysis', {}).get('current_status', {}).get('actual_level')}")
        print(f"目標職位: {result_exp.get('gap_analysis', {}).get('target_position', {}).get('role')}")
        
        # 存檔供檢查
        with open("test_result_experienced.json", "w", encoding="utf-8") as f:
            json.dump(result_exp, f, indent=2, ensure_ascii=False)
        print("\n📝 詳細結果已存至 test_result_experienced.json")
        
    except Exception as e:
        print(f"❌ 執行失敗: {str(e)}")

    # 4. 測試：無經驗者流程
    print("\n" + "="*50)
    print("🚀 測試任務：無經驗/轉職者分析 (CAREER_ANALYSIS_ENTRY_LEVEL)")
    print("="*50)
    
    # 修改資料模擬無經驗
    mock_survey_entry = {
        "user_id": "test_user_entry",
        "module_c": {"q16_current_level": "entry_level"}
    }
    mock_resume_entry = {
        "basics": {"name": "Alex", "summary": "行政專員，擅長 Excel 與流程管理。"},
        "skills": {"tools": ["Excel VLOOKUP", "Project Management"]}
    }
    
    user_input_entry = {
        "survey_json": json.dumps(mock_survey_entry),
        "trait_json": json.dumps(mock_trait), # 延用特質
        "resume_json": json.dumps(mock_resume_entry),
        "target_role": None,
        "learning_style": "Video Courses"
    }
    
    try:
        result_entry = manager.run_task("career_analysis_entry_level", user_input_entry)
        print("\n✅ 執行成功！產出的報告摘要：")
        print(f"核心洞察: {result_entry.get('preliminary_summary', {}).get('core_insight')}")
        print(f"推薦職位: {result_entry.get('gap_analysis', {}).get('target_position', {}).get('role')}")
        
        # 存檔供檢查
        with open("test_result_entry.json", "w", encoding="utf-8") as f:
            json.dump(result_entry, f, indent=2, ensure_ascii=False)
        print("\n📝 詳細結果已存至 test_result_entry.json")
        
    except Exception as e:
        print(f"❌ 執行失敗: {str(e)}")

if __name__ == "__main__":
    test_career_analysis()
