# test_user_fetch.py
import os
import json
from dotenv import load_dotenv

# 1. 載入環境變數
load_dotenv()

# 2. 匯入現有的資料庫工具
from src.core.database.supabase_client import get_latest_resume

def test_fetch_user_one():
    user_id = "1"
    print(f"--- 測試抓取 user_id: {user_id} 的履歷 ---")
    
    # 執行抓取
    result = get_latest_resume(user_id)
    
    # 輸出結果
    if "❌" in result or "Error" in result:
        print(f"抓取失敗: {result}")
    else:
        try:
            # 格式化輸出 JSON
            data = json.loads(result)
            print("抓取成功！內容如下：")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        except json.JSONDecodeError:
            print("抓取成功，但內容非標準 JSON：")
            print(result)

if __name__ == "__main__":
    test_fetch_user_one()
