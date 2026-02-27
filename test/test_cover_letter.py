import os
import json
import pytest
from src.core.agent_engine.manager import CareerAgentManager
from src.core.agent_engine.task_types import TaskType

def test_cover_letter_flow():
    """
    測試求職推薦信模組的完整執行流程。
    模擬前端傳入 user_id=1 與 optimization_id=5，讓 Agent 自動透過工具從資料庫撈取資料。
    """
    manager = CareerAgentManager()
    
    # 模擬前端傳入的參數
    user_id = "2"
    task_type_str = "cover_letter"
    
    # 使用指定的 optimization_id 與 job_id
    user_input = {
        "optimization_id": "7", 
        "job_id": 60 # 假設 job_id 為 60 (iOS / Mac / tvOS App 軟體研發工程師)
    }
    
    print(f">>> 啟動 Cover Letter 推薦測試...")
    print(f">>> 模擬前端傳入 - User ID: {user_id}, Optimization ID: {user_input['optimization_id']}")
    print(f">>> 職缺 ID: {user_input['job_id']}")
    
    try:
        # 執行任務：Manager 會根據 task_type "cover_letter" 調用對應配置
        # 並讓 Agent 使用工具從 Supabase 抓取資料
        final_result = manager.run_task(
            task_type_str=task_type_str,
            user_id=user_id,
            user_input=user_input,
        )
        
        # 驗證生成結果結構
        assert "subject" in final_result, "回傳結果應包含主旨 (subject)"
        assert "content" in final_result, "回傳結果應包含正文 (content)"
        
        print("\n" + "="*50)
        print("[測試成功] 求職信生成成功！")
        print(f"[主旨]: {final_result['subject']}")
        print("-" * 30)
        print("[正文內容]:")
        print(final_result["content"])
        print("="*50 + "\n")
        
    except Exception as e:
        print(f"\n❌ [測試失敗] 流程執行出現錯誤: {e}")
        # 如果資料庫找不到對應 ID，請確認 Supabase 中是否存在 ID=5 的優化履歷
        pytest.fail(f"Cover Letter 流程執行失敗: {e}")

if __name__ == "__main__":
    test_cover_letter_flow()
