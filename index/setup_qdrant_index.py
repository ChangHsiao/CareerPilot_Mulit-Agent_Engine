# fix_qdrant_index.py
import os
import sys

# 確保可以匯入 src 資料夾 (環境路徑設定)
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = current_dir # 如果這支檔案放在根目錄，就直接用 current_dir
sys.path.append(project_root)

from dotenv import load_dotenv
from qdrant_client.http import models
from src.core.database.qdrant_client import get_qdrant_client

def fix_indices():
    """
    一次性維護腳本：為 Qdrant 建立缺少的 Payload Index
    """
    load_dotenv()
    
    try:
        # 1. 取得 Qdrant 連線
        client = get_qdrant_client()
        print("連線到 Qdrant 成功。正在為 'optimized_resume_vectors' 集合建立索引...")
        
        # 2. 為 optimization_id 建立整數型別 (INTEGER) 的索引 (這就是報錯缺少的那個)
        client.create_payload_index(
            collection_name="optimized_resume_vectors",
            field_name="optimization_id",
            field_schema=models.PayloadSchemaType.INTEGER,
        )
        print("🎉 成功建立 'optimization_id' 索引！")

        # 3. 順便為 user_id 也建立索引 (作為雙重防護)
        client.create_payload_index(
            collection_name="optimized_resume_vectors",
            field_name="user_id",
            field_schema=models.PayloadSchemaType.INTEGER,
        )
        print("🎉 成功建立 'user_id' 索引！")

    except Exception as e:
        print(f"❌ 建立索引時發生錯誤 (如果顯示 already exists 代表已經建過了): {e}")

if __name__ == "__main__":
    fix_indices()