import os
import json
from dotenv import load_dotenv
from src.Multi_Agent.manager import CareerAgentManager, TaskType

# 載入環境變數 (確保 API Key 被讀取)
load_dotenv()

# 1. 準備模擬資料
MOCK_RESUME_CONTENT = """
姓名：張小明
目標職位：後端工程師
工作經歷：
- 2022-2024 ABC 科技 軟體工程師
  負責寫 API，維護資料庫，修復 Bug。使用 Python 和 Django。
- 2020-2022 XYZ 工作室 助理工程師
  協助主管處理雜事，寫一些簡單的網頁。
專案經驗：
- 個人部落格：用 Flask 寫的，可以留言。
技能：Python, Git, SQL (一點點)
"""

def test_resume_flow_with_manager():
    print("\n🚀 === 開始測試：總代理 (Manager) 履歷診斷流程 ===")
    
    # 2. 初始化總代理
    # 預設會使用 o3-mini 模型
    manager = CareerAgentManager()

    # 3. 設定任務參數
    user_input = {
        "user_id": "test_user_001",
        "target_role": "後端工程師",
        "resume_content": MOCK_RESUME_CONTENT
    }

    # 4. 執行任務 (指定任務類型為 resume_critique)
    # 此動作會根據 configs.py 啟動 Auditor (Worker) 與 QA Lead (品質監控)
    try:
        print(f"正在執行 [RESUME_CRITIQUE] 任務，請稍候...\n")
        result = manager.run_task("resume_critique", user_input)

        # 5. 驗證並呈現結果
        print("✅ 任務執行成功！")
        print("-" * 30)
        
        # 檢查 Metadata 是否被正確填充
        metadata = result.get("report_metadata", {})
        print(f"報告元數據:")
        print(f"  - User ID: {metadata.get('user_id')}")
        print(f"  - 生成時間: {metadata.get('timestamp')}")
        print(f"  - 版本: {metadata.get('version')}")
        print("-" * 30)

        print(f"候選人定位: {result.get('candidate_positioning')}")
        print(f"ATS 風險等級: {result.get('ats_risk_level')}")
        
        issues = result.get("critical_issues", [])
        print(f"\n發現 {len(issues)} 個關鍵問題：")
        for i, issue in enumerate(issues, 1):
            print(f"{i}. [{issue.get('section')}] {issue.get('issue_reason')[:80]}...")
            print(f"   建議改善方向: {', '.join(issue.get('improvement_direction', []))}")

        print("\n下一步行動建議：")
        for action in result.get("recommended_next_actions", []):
            print(f"- {action}")

    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_resume_flow_with_manager()
