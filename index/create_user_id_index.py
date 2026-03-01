from qdrant_client import QdrantClient
from qdrant_client.http import models
import os
from dotenv import load_dotenv

load_dotenv()

def create_index():
    client = QdrantClient(
        url=os.getenv("QDRANT_URL"),
        api_key=os.getenv("QDRANT_API_KEY")
    )

    collection_name = "resumes"  # 請確認您的 Collection 名稱

    print(f"正在為 {collection_name} 建立 user_id 索引...")

    client.create_payload_index(
        collection_name=collection_name,
        field_name="user_id",
        field_schema=models.PayloadSchemaType.INTEGER, # 如果您的 user_id 是整數
    )
    print("✅ 索引建立完成！")

if __name__ == "__main__":
    create_index()