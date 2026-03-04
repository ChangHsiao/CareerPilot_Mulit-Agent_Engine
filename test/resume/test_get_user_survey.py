import os
import sys

# 將專案根目錄加入系統路徑，確保可以正確 import src 模組
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

from src.features.resume.tools import DatabaseTools

def test_fetch_survey():
    # 設定要測試的 user_id
    user_id = "1"
    print(f"開始測試獲取用戶問卷中的目標職位 (user_id = {user_id})...\n")
    
    try:
        # 呼叫已經修改好的 get_user_survey 方法
        target_role = DatabaseTools.get_user_survey(user_id)
        
        print("======== 測試結果 ========")
        print(f"目標職位 (target_role): {target_role}")
        print("==========================")
        
    except Exception as e:
        print(f"測試過程中發生錯誤: {e}")

if __name__ == "__main__":
    test_fetch_survey()
