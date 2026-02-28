import os
import sys

# 將專案根目錄加到 sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(project_root)

from dotenv import load_dotenv
from src.core.database.qdrant_client import get_qdrant_client
from qdrant_client.http import models

def main():
    load_dotenv()
    try:
        client = get_qdrant_client()
        print("連線到 Qdrant 成功。正在為 'job_vectors' 集合的 'is_labeled' 建立索引...")
        
        client.create_payload_index(
            collection_name="job_vectors",
            field_name="is_labeled",
            field_schema=models.PayloadSchemaType.BOOL,
        )
        print("🎉 索引建立成功！")
    except Exception as e:
        print(f"❌ 建立索引時發生錯誤: {e}")

if __name__ == "__main__":
    main()
