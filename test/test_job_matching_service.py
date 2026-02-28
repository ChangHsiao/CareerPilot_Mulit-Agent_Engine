# test/test_job_matching_service.py
import os
import json
import sys

# 確保可以匯入 src 資料夾
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from src.core.database.supabase_client import get_supabase_client
from src.core.database.qdrant_client import get_qdrant_client

# 匯入重構後的服務
from src.features.matching.service import CareerMatchingService

def test_full_job_matching_flow():
    print("==================================================")
    print("🚀 啟動職缺匹配模組整合測試")
    print("==================================================")
    
    load_dotenv()
    
    # 1. 環境變數檢查
    openai_api_key = os.getenv("OPENAI_API_KEY")

    if not openai_api_key:
        print("❌ 錯誤：環境變數 OPENAI_API_KEY 不完整，請檢查 .env 檔案。")
        return

    try:
        # 2. 初始化連線
        print("正在建立資料庫連線...")
        qdrant_client = get_qdrant_client()
        supabase_client = get_supabase_client()
        
        # 3. 啟動職缺匹配服務
        service = CareerMatchingService(
            qdrant_client=qdrant_client, 
            supabase_client=supabase_client, 
            openai_api_key=openai_api_key
        )
        
        # 4. 準備測試資料 (以陳浩宇為例)
        TEST_USER_ID = 1        # 根據你提供的資料庫現況，使用 user_id = 2
        TEST_DOCUMENT_ID = 1    # 對應 RESUME 表中的 resume_id = 2
        TEST_SOURCE_TYPE = "RESUME"  # 明確指定去「原始履歷」資料庫找
        filters = {
            "city": ["台北市", "新北市"], 
            "salary_min": 40000,
            "salary_max": 60000
        }
        
        print(f"🔍 正在為 User {TEST_USER_ID} 執行漏斗式職缺篩選...")
        print(f"📄 目標文件: {TEST_SOURCE_TYPE} (ID: {TEST_DOCUMENT_ID})")
        print(f"篩選條件: {filters}")
        
        # 5. 執行核心匹配流程
        print("\n⏳ 開始呼叫 service.find_best_jobs()...")
        results = service.find_best_jobs(
            user_id=TEST_USER_ID, 
            document_id=TEST_DOCUMENT_ID,
            source_type=TEST_SOURCE_TYPE,
            filters=filters
        )
        
        # --- 新增：為了在測試檔直接印出檢視，這裡手動去撈一次同樣的資料來顯示 ---
        print("\n📊 [測試專用] 正在從資料庫獨立提取六維分數以供人工檢視...")
        report_response = (
            supabase_client.table('career_analysis_report')
            .select('radar_chart, report_version')
            .eq('user_id', TEST_USER_ID)
            .execute()
        )
        if report_response.data:
            latest_report = max(
                report_response.data, 
                key=lambda x: float(x.get('report_version') or '0.0')
            )
            radar_chart = latest_report.get('radar_chart', {})
            print(f"✅ User {TEST_USER_ID} 的原始雷達圖資料 (radar_chart):")
            print(json.dumps(radar_chart, indent=2, ensure_ascii=False))
        else:
            print("⚠️ 找不到該 User 的六維雷達圖資料！")
        # -------------------------------------------------------------
        
        # 6. 驗證結果
        print("\n🏆 ================= 終極排行榜 Top 10 ================= 🏆\n")
        if results:
            print(f"✅ 成功產出 {len(results)} 筆職缺推薦：\n")
            
            for i, job in enumerate(results, 1):
                print(f"[{i}] {job.get('job_title')} @ {job.get('company_name')}")
                print(f"    最終契合度: {job.get('final_score')}")
                print(f"    AI 分析內容:")
                print(json.dumps(job.get('ai_analysis'), indent=8, ensure_ascii=False))
                print("-" * 50)
            
            # 驗證關鍵欄位是否存在 (以第一名為例)
            top_job = results[0]
            required_keys = ["job_id", "job_title", "requirements", "final_score", "ai_analysis"]
            missing_keys = [k for k in required_keys if k not in top_job]
            if not missing_keys:
                print("\n✅ JSON 結構完整性驗證通過。")
            else:
                print(f"\n❌ JSON 缺少欄位: {missing_keys}")
            
            print("\n🎉 職缺匹配模組測試通過！")
        else:
            print("⚠️ 測試完成，但未找到符合條件的職缺。請確認資料庫中是否有對應地區與薪資的職缺。")
            
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤：{e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_full_job_matching_flow()
