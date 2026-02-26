import os
import json
from dotenv import load_dotenv
from src.core.database.supabase_client import get_supabase_client
from src.core.agent_engine.result_handlers import GapAnalysisHandler

# 1. 載入環境變數
load_dotenv()

def test_manual_storage():
    """
    手動測試：將 Agent 生成的報告結果存入資料庫，
    用以驗證 GapAnalysisHandler 的映射邏輯與資料庫 Schema 是否匹配。
    """
    print("\n🚀 開始測試：職涯分析報告手動存入流程...")
    
    # 初始化 Supabase 與 Handler
    supabase = get_supabase_client()
    handler = GapAnalysisHandler(supabase)

    # 2. 測試資料 (您提供的 Agent 生成結果)
    REPORT_DATA = {
        "report_metadata": {
            "user_id": "1",
            "timestamp": "2026-02-26T05:41:09.527Z",
            "version": "1.0"
        },
        "preliminary_summary": {
            "core_insight": "候選人展現出卓越的後端開發實力與扎實的系統架構能力，具備強大的知識遷移與跨領域整合潛能；雖然在前端與AI數據應用上顯示出技術缺口，但透過針對性培訓，未來有望彌補不足並提升領導能力。"
        },
        "radar_chart": {
            "dimensions": [
                {"axis": "前端開發", "score": 1.0},
                {"axis": "後端開發", "score": 3.7},
                {"axis": "運維部署", "score": 4.5},
                {"axis": "AI與數據", "score": 0.5},
                {"axis": "工程品質", "score": 3.7},
                {"axis": "軟實力", "score": 4.8}
            ]
        },
        "gap_analysis": {
            "current_status": {
                "self_assessment": "中階工程師 (Mid Level)",
                "actual_level": "中階工程師 (Mid Level)",
                "cognitive_bias": "候選人自評為中階工程師，然而履歷與實際操作經驗顯示，在程式語言、工具應用及數據視覺化上存在落差，認知偏差明顯。建議透過進階培訓與實案演練，協助調整自評與實力間的矛盾，進一步增強決策與領導潛能。"
            },
            "target_position": {
                "role": "後端工程師",
                "match_score": "82%",
                "gap_description": "候選人在前端開發與AI數據應用上存在技術盲點，顯示自評與履歷間的落差，需透過相關培訓進行技能彌補，進一步提升全盤技術整合與競爭力。"
            }
        },
        "action_plan": {
            "short_term": "參加進階Python與Git培訓，並學習基本的現代前端框架，以釐清自評與實際能力間的差距。",
            "mid_term": "進修機器學習與數據科學課程，並著手建立數據視覺化專案，加強AI與數據應用能力。",
            "long_term": "持續跨領域整合實踐，參與DevOps與CI/CD進階應用，進一步培養技術領導與決策能力。"
        }
    }

    # 3. 執行存入
    try:
        print(f"📦 正在調用 Handler.process()...")
        # 模擬 Manager 呼叫 Handler 的方式
        handler.process(REPORT_DATA, user_id="1")
        print(f"✅ Handler 執行成功！")
        
        # 4. 從資料庫驗證
        print(f"🧪 驗證點：檢查資料庫內容...")
        response = (
            supabase.table("career_analysis_report")
            .select("*")
            .eq("user_id", "1")
            .order("generated_at", desc=True)
            .limit(1)
            .execute()
        )
        
        if response.data:
            record = response.data[0]
            print(f"🎊 驗證成功！")
            print(f"   - 報告 ID: {record.get('id')}")
            print(f"   - 存入的時間 (generated_at): {record.get('generated_at')}")
            print(f"   - 映射的目標職位: {record.get('target_position')}")
        else:
            print("❌ 驗證失敗：資料庫中找不到紀錄。")

    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {e}")

if __name__ == "__main__":
    test_manual_storage()
