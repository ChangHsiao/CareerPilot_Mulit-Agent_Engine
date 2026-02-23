import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient, models
from src.features.matching.qdrant_retriever import JobMatchRetriever

def run_real_data_test():
    """
    [整體意圖]
    這是一個純唯讀 (Read-Only) 的測試腳本。
    它會連線到您的真實 Qdrant 資料庫，並嘗試用硬篩選條件撈出職缺。
    """
    # 1. 載入 .env 檔案中的環境變數
    load_dotenv()
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")
    
    if not qdrant_url or not qdrant_api_key:
        raise ValueError("請確認 .env 檔案中已設定 QDRANT_URL 與 QDRANT_API_KEY")

    # 2. 建立真實的遠端連線
    print(f"正在連線至真實資料庫: {qdrant_url}...")
    client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)

# ==========================================
# ⚠️ 【關鍵設定】：請輸入您真實的 Collection 名稱
# ==========================================
    REAL_COLLECTION_NAME = "job_vectors"

    # 確認 Collection 是否存在
    if not client.collection_exists(REAL_COLLECTION_NAME):
        raise ValueError(f"找不到 Collection: {REAL_COLLECTION_NAME}，請檢查名稱是否正確！")

    # 3. 實例化檢索模組 (綁定真實的 Collection)
    retriever = JobMatchRetriever(client=client, collection_name=REAL_COLLECTION_NAME)

    # 4. 設定陳浩宇的測試條件
    # 💡 [顧問提示] 為了應對真實資料的不確定性，location 可以多寫幾個同義詞
    filters = {
        "city": ["台北市"], 
        "salary_min": 50000,
        "salary_max": 100000
    }
    
    print(f"\n--- 啟動真實資料庫【唯讀】過濾測試 ---")
    print(f"目標 Collection: {REAL_COLLECTION_NAME}")
    print(f"篩選條件: {filters}\n")
    
    # 5. 執行純硬篩選 (使用 scroll，不耗費昂貴的向量運算資源)
    # 我們先 limit=5 看前 5 筆就好，確認 Payload 結構對不對
    try:
        results = retriever.filter_jobs_only(filters=filters, limit=50)

    # 6. 驗證與印出結果
        if len(results) == 0:
            print("⚠️ 找不到任何符合條件的職缺！可能原因：")
            print("1. 真的沒有符合條件的職缺。")
            print("2. 您 Payload 裡面的欄位名稱可能不是 'location' 或 'salary'，請檢查當初爬蟲存入時的 Key 名稱。")
        else:
            print(f"✅ 成功撈取 {len(results)} 筆符合條件的真實職缺：\n")
            for res in results:
                print(f"- Job ID: {res['job_id']}")
                # 只印出我們關心的幾個欄位，避免畫面被龐大的 JD 塞滿
                payload = res['payload']
                loc = payload.get('city', '未標示')
                sal_min = payload.get('salary_min', '未標示')
                sal_max = payload.get('salary_max', '未標示')
                title = payload.get('job_title', payload.get('title', '未標示'))
                print(f"  職缺名稱: {title} | 地點: {loc} | 薪資: {sal_min}~{sal_max}")
                
    except Exception as e:
        print(f"❌ 查詢失敗，錯誤訊息：{e}")

if __name__ == "__main__":
    run_real_data_test()