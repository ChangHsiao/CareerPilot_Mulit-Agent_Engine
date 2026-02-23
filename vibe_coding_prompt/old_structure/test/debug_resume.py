import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient

def run_diagnostic():
    """
    [整體意圖]
    這是一支診斷腳本 (Diagnostic Script)。
    目的是印出 resume_vectors 資料表前 5 筆資料的「真實 ID 型別」與「Payload 內容」，
    藉此比對我們傳入的 ID 是否與資料庫吻合。
    """
    load_dotenv()
    client = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"))
    
    # ⚠️ 請確認這個名稱與您存履歷的真實名稱一模一樣
    COLLECTION_NAME = "resume_vectors" 

    print(f"🔍 正在檢查 Collection: {COLLECTION_NAME} ...\n")

    if not client.collection_exists(COLLECTION_NAME):
        print(f"❌ 嚴重錯誤：根本找不到名為 {COLLECTION_NAME} 的 Collection！")
        return

    # 使用 scroll API，不帶任何條件，直接滾出前 5 筆資料
    records, _ = client.scroll(
        collection_name=COLLECTION_NAME,
        limit=5,
        with_payload=True,
        with_vectors=False # 為了版面乾淨，我們先不印出那 1536 維的向量數字
    )

    if len(records) == 0:
        print("⚠️ 警告：這個 Collection 裡面是空的！(沒有任何履歷資料)")
        return

    print(f"✅ 成功撈到資料！以下是前 {len(records)} 筆紀錄的長相：\n")
    
    for i, r in enumerate(records):
        print(f"--- 第 {i+1} 筆 ---")
        # [關鍵排錯點] 印出 Qdrant 真實的 Point ID 與它的 Python 型別
        print(f"▶ 真實 Qdrant ID : {r.id}")
        print(f"▶ ID 的資料型別  : {type(r.id)}")
        print(f"▶ Payload 內容   : {r.payload}")
        print("")

if __name__ == "__main__":
    run_diagnostic()