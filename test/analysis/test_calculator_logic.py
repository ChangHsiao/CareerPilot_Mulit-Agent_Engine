import sys
import os
import json

# 加入專案根目錄到 sys.path，以確保能夠正確引用 src 模組
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.features.analysis.calculator import CareerAnalyzer

def main():
    # 這是您提供的測試資料 (Payload)
    test_payload = {
      "user_id": "test_user_9527",
      "timestamp": "2026-03-05T15:00:00.000Z",
      "module_a": {
        "q1_languages": [
          {"name": "JavaScript", "score": 4},
          {"name": "Go", "score": 4},
          {"name": "Python", "score": 3}
        ],
        "q2_frontend": "framework_spa",
        "q3_backend": "db_auth_testing",
        "q4_database": ["rdbms_sql", "key_value_cache", "vector_db"],
        "q5_devops": "docker_basic",
        "q6_ai_data": "pandas_numpy",
        "q7_security": "auth_rbac",
        "q8_domain": "FinTech"
      },
      "module_b": {
        "q9_troubleshoot": "rollback",
        "q10_tech_choice": "team_familiarity",
        "q11_communication": "alternative_solution",
        "q12_code_review": "logic_safety",
        "q13_learning": "consistent_input",
        "q14_process": "agile_scrum",
        "q15_english": "fluent_reading"
      }
    }

    print("=== 初始化 CareerAnalyzer ===")
    analyzer = CareerAnalyzer(test_payload)
    
    print("=== 執行向量分數計算 ===")
    analyzer.calculate_vectors()
    
    print("\n=== 新計算邏輯的結果 (能力六維度分數) ===")
    print(json.dumps(analyzer.scores, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
