import os
import sys
import json
from unittest.mock import patch
from dotenv import load_dotenv

# 確保可以匯入 src 資料夾
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.core.database.supabase_client import get_supabase_client
from src.core.agent_engine.manager import CareerAgentManager

def test_analysis_module(save_to_db: bool = False):
    print("==================================================")
    print(f"🚀 啟動 Analysis 模組優化測試 ({'寫入資料庫' if save_to_db else '不寫入資料庫'})")
    print("==================================================")
    
    load_dotenv()
    
    # 準備連線
    print("正在連接 Supabase 獲取測試使用者資料...")
    supabase = get_supabase_client()
    
    # 預設測試 user_id = 1 (若您的資料庫有其他 user_id，請依需求替換)
    TEST_USER_ID = 2
    TRAIT_JSON = {
  "trait_raw_responses": {
    "Q1": "C", 
    "Q2": "A", 
    "Q3": "B", 
    "Q4": "B", 
    "Q5": "A", 
    "Q6": "B", 
    "Q7": "B", 
    "Q8": "A", 
    "Q9": "A", 
    "Q10": "A"
  },
  "trait_raw_scores": {
    "structure": 9,
    "ambiguity": 0,
    "decision": 2,
    "learning": 4,
    "transfer": 5
  },
  "trait_normalized_scores": {
    "structure": 90,
    "ambiguity": 29,
    "decision": 43,
    "learning": 60,
    "transfer": 86
  },
  "primary_archetype": "STRUCTURE_ARCHITECT",
  "secondary_archetypes": [
    "CROSS_DOMAIN_INTEGRATOR"
  ],
  "trait_created_at": "2026-03-01T21:40:00Z"
}

    
    try:
        status_response = supabase.table("career_survey") \
            .select("questionnaire_response") \
            .eq("user_id", TEST_USER_ID) \
            .order("updated_at", desc=True) \
            .limit(1) \
            .execute()
            
        if not status_response.data:
            print(f"❌ 找不到 User ID {TEST_USER_ID} 的問卷資料")
            return
            
        survey_data = status_response.data[0]
        # 轉換為 json 字串供 Manager 讀取
        survey_json = json.dumps(survey_data, ensure_ascii=False)
        print(f"取得 {TEST_USER_ID} 的問卷資料，資料內容如下：{survey_json}")
        
    except Exception as e:
        print(f"❌ 從資料庫獲取問卷資料失敗: {e}")
        return
    
    user_input = {
        "user_id": TEST_USER_ID,
        "survey_json": survey_json,
        "trait_json": TRAIT_JSON
    }
    
    # 初始化 Manager
    print("\n⏳ 初始化 CareerAgentManager...")
    manager = CareerAgentManager()
    
    if save_to_db:
        print("\n⚠️ 注意：測試結果將寫入資料庫！")
    else:
        print("\n🛡️ 已屏蔽存檔機制，測試結果將【不會】寫入資料庫。")
    print(f"🧠 開始執行 analysis 分析任務 (這可能需要幾分鐘)...\n")
    
    try:
        if save_to_db:
            result = manager.run_task("career_analysis", user_input)
        else:
            # Patch handler_registry 的 get_handler 方法，使其回傳 None，從而跳過 handler.process(資料庫寫入)
            with patch.object(manager.handler_registry, 'get_handler', return_value=None):
                result = manager.run_task("career_analysis", user_input)
            
        print("\n🏆 ================= 分析結果 (Raw JSON) ================= 🏆\n")
        
        if isinstance(result, dict) and "status" in result and result.get("status") == "error":
            print("❌ 分析失敗:")
            print(result.get("message"))
            return
            
        # 印出完整 JSON 結果
        formatted_json = json.dumps(result, ensure_ascii=False, indent=2)
        print(formatted_json)
        
        print("\n🔍 =============== 優化重點欄位檢查 =============== \n")
        preliminary = result.get("preliminary_summary", {})
        print("💡 [core_insight (應包含產業洞察與個人總結)]:")
        print(preliminary.get("core_insight", "⚠️ 無資料"))
        print("-" * 50)
        
        gap = result.get("gap_analysis", {}).get("target_position", {})
        print("💡 [gap_description (應呈現 SWOT 標題與落差)]:")
        print(gap.get("gap_description", "⚠️ 無資料"))
        print("-" * 50)
        
        action = result.get("action_plan", {})
        print("💡 [action_plan.short_term (應包含具體工具與指標)]:")
        print(action.get("short_term", "⚠️ 無資料"))
        print("-" * 50)
        
        print("\n✅ 測試執行完畢！您可以從上方印出的資訊檢核優化格式是否正確。")
        
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤：{e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 若要寫入資料庫，可以使用 python test_analysis.py --save 執行
    # 或者直接修改下方為 test_analysis_module(save_to_db=True)
    save_to_db = "--save" in sys.argv
    test_analysis_module(save_to_db=save_to_db)
