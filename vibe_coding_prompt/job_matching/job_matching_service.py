# job_matching_service.py
from qdrant_client import QdrantClient
import json
# 將兩個採購員匯入廚房
from src.features.matching.qdrant_retriever import JobMatchRetriever, UserProfileRetriever
from src.features.analysis.calculator import JobMatcher
from src.features.analysis.llm_advisor import CareerLLMAdvisor
import concurrent.futures # 🌟 新增這行：用來開啟多執行緒
from openai import OpenAI
from dotenv import load_dotenv

class CareerMatchingService:
    """
    職缺匹配模組的核心入口。
    負責協調資料庫讀取，並執行商業邏輯 (混合計分演算法)。
    重構為前端標準 JSON。
    """
    def __init__(self, qdrant_client: QdrantClient, supabase_client, openai_api_key: str):
        # 1. 初始化時，同時接收 Qdrant 與 Supabase 兩個客戶端
        self.qdrant_client = qdrant_client
        self.supabase_client = supabase_client

        self.resume_retriever = UserProfileRetriever(qdrant_client, "resume_vectors")
        self.job_retriever = JobMatchRetriever(qdrant_client, "job_vectors")
        # 實例化 AI 顧問
        self.llm_advisor = CareerLLMAdvisor(api_key=openai_api_key)

    def find_best_jobs(self, user_id: int, filters: dict, user_6d_profile: dict) -> list[dict]:
        """
        這就是您未來的模組總入口！
        """
        try:
            # ==========================================
            # Phase 1: Qdrant 混合召回 (撈取 Top 50 候選名單)
            # ==========================================
            # 1. 拿鑰匙 (提取履歷向量)
            print(f"正在提取 User {user_id} 的履歷向量...")
            resume_vector = self.resume_retriever.get_resume_vector(user_id)

            # 2. 找保險箱 (Qdrant 混合檢索，完成 0.3 文本相似度與硬篩選)
            print("正在進行第一階段候選名單檢索...")
            primary_candidates = self.job_retriever.search_hybrid_jobs(
                query_vector=resume_vector,
                filters=filters,
                limit=50
            )

            if not primary_candidates:
                print("⚠️ 找不到任何符合硬篩選條件的職缺。")
                return []


            # ==========================================
            # Phase 1.5 Supabase 批量查詢 (Batch Query)
            # ==========================================
            print("正在向 Supabase 提取候選職缺的六維能力分數...")
            
            # 1. 整理出所有要查詢的 Job ID 陣列 (例如: [101, 105, 203])
            job_ids = [job['job_id'] for job in primary_candidates]

            # 2. 一次性向 Supabase 發送請求 (避免 N+1 查詢問題)。使用 company_id 進行關聯，
            response_jobs = self.supabase_client.table('job_posting') \
                .select('job_id, job_title, job_description, requirements, full_address, source_url, company_id, d1_frontend, d2_backend, d3_devops, d4_ai_data, d5_quality, d6_soft_skills') \
                .in_('job_id', job_ids) \
                .execute()
            job_data_list = response_jobs.data

            # 抽出所有的 company_id，準備去 company_info 查公司名稱與產業
            company_ids = list(set([job['company_id'] for job in job_data_list if job.get('company_id')]))

            # 查詢 company_info
            response_companies = self.supabase_client.table('company_info') \
                .select('company_id, company_name, industry') \
                .in_('company_id', company_ids) \
                .execute()
            company_lookup = {row['company_id']: row for row in response_companies.data}

            # 4. 將職缺與公司資訊合併為一個超級大字典 (O(1) 查找)
            job_full_lookup = {}
            for job_row in job_data_list:
                comp_info = company_lookup.get(job_row.get('company_id'), {})
                job_full_lookup[job_row['job_id']] = {
                    **job_row, 
                    'company_name': comp_info.get('company_name', '未提供'),
                    'industry': comp_info.get('industry', '未提供')
                }

            # ==========================================
            # Phase 2: Python 0.7 歐幾里得距離重排序 (Re-ranking)
            # ==========================================
            print("正在進行第二階段：六維能力差距分析與重新計分...")
            final_results = []
            
            for job in primary_candidates:
                job_id = job['job_id']
                job_details = job_full_lookup.get(job_id, {})
                if not job_details: continue # 防呆：如果 Supabase 沒資料就跳過

                # 1. 取得 Qdrant 的文本相似度分數 (佔 0.3)
                score_text = max(0.0, job.get('score_text', 0.0))
                score_6d = JobMatcher.calculate_dynamic_job_gap(user_6d_profile, job_details)
                final_score = (0.7 * score_6d) + (0.3 * score_text)
                
                # 將計算結果存回
                job['score_6d'] = score_6d
                job['final_score'] = final_score
                job['job_details'] = job_details # 把完整資料塞進去備用
                final_results.append(job)

            # 根據最終總分由高到低重新排序，並截取前 10 名
            final_results.sort(key=lambda x: x['final_score'], reverse=True)
            top_10_jobs = final_results[:10]

            # # 排序與截取完成後，再把它們的數值轉成百分比字串
            # for job in top_10_jobs:
            #     # 取得原本的小數
            #     raw_final = job['final_score']
            #     raw_6d = job['score_6d']
            #     raw_text = job.get('score_text', 0.0)

            #     # 覆蓋為帶有 % 的字串 (例如 "85.2%")
            #     job['final_score'] = f"{raw_final:.1%}"
            #     job['score_6d'] = f"{raw_6d:.1%}"
            #     job['score_text'] = f"{raw_text:.1%}"
                
            #     # (選擇性防呆) 如果您怕前端未來還是需要拿原始數字來做條件判斷 (例如 > 0.8 才亮綠燈)
            #     # 可以偷偷保留一個原始數值欄位給他們
            #     job['raw_scores'] = {
            #         "final": raw_final,
            #         "score_6d": raw_6d,
            #         "score_text": raw_text
            #     }

          # ==========================================
            # 🌟 Phase 3: AI 顧問深度分析 (Top 10 平行運算版)
            # ==========================================
            print("正在為 Top 10 職缺生成專屬 AI 分析報告 (啟動 10 股平行運算)...")
            
            # 定義一個「單一職缺處理小幫手」函數
            def process_job_to_frontend_json(job):
                try:
                    details = job['job_details']
                    
                    # 1. 準備格式化百分比分數
                    f_final = f"{job['final_score']:.1%}"
                    # f_6d = f"{job['score_6d']:.1%}"
                    # f_text = f"{job.get('score_text', 0.0):.1%}"

                    # 🌟 調整 2：清理 Requirements 字串
                    raw_req = str(details.get('requirements', ''))
                    # 步驟 A：依換行符號 (\n) 切開字串，並去除每一行頭尾的多餘空白
                    req_lines = [line.strip() for line in raw_req.split('\n') if line.strip()]
                    # 步驟 B：移除重複項目 (例如消除連兩次的 "提升英文能力")，並保持原本的順序
                    req_lines = list(dict.fromkeys(req_lines))
                    # 步驟 C：用 " | " 把這些乾淨的條件重新串起來，變成美觀的單行字串
                    clean_requirements = " | ".join(req_lines)
                    
                    # 2. 呼叫 LLM 顧問 (傳入職稱進行分析)
                    ai_insights = self.llm_advisor.generate_job_insights(
                        job_title=details.get('job_title', '未知職缺'),
                        user_6d=user_6d_profile,
                        job_6d=details, # details 裡面包含了 d1~d6 的分數
                        match_score=f_final
                    )
                    
                    # 🌟 3. 重組為前端需要的完美 JSON 結構 (完全對應您的圖片規格)
                    return {
                        "job_id": str(details.get('job_id', '')),
                        "job_title": str(details.get('job_title', '')),
                        "job_description": str(details.get('job_description', '')),
                        "requirements": clean_requirements,  # 👈 放入清理過的美觀字串
                        "company_name": str(details.get('company_name', '')),
                        "industry": str(details.get('industry', '')),
                        "full_address": str(details.get('full_address', '')),
                        "source_url": str(details.get('source_url', '')),
                        "final_score": f_final,              # 👈 扁平化，直接給最終分數
                        "ai_analysis": ai_insights
                    }
                except Exception as e:
                    print(f"⚠️ 單筆資料處理失敗: {e}")
                    return None

            # 🚀 平行運算處理並組裝 JSON
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                frontend_json_list = list(executor.map(process_job_to_frontend_json, top_10_jobs))
                
            # 過濾掉可能因為錯誤而變成 None 的資料
            return [j for j in frontend_json_list if j is not None]

        except Exception as e:
            print(f"❌ 匹配服務發生錯誤: {e}")
            raise e

if __name__ == "__main__":
    import os
    import json
    from dotenv import load_dotenv
    from supabase import create_client, Client
    from qdrant_client import QdrantClient
    
    print("==================================================")
    print("🚀 啟動完整職缺匹配系統 (本地端測試模式)")
    print("==================================================")
    
    load_dotenv()
    
    # 這裡開始了 try 區塊
    try:
        # 1. 建立連線與檢查金鑰
        qdrant_client = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"))
        
        supabase_url: str = os.getenv("SUPABASE_URL")
        supabase_key: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        supabase_client: Client = create_client(supabase_url, supabase_key)
        
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("找不到 OPENAI_API_KEY，無法啟動 AI 顧問！")
            
        # 2. 啟動服務
        service = CareerMatchingService(qdrant_client, supabase_client, openai_api_key)
        
        # 3. 測試條件
        TEST_USER_ID = 1
        filters = {
            "city": ["台北市"], 
            "salary_min": 50000,
            "salary_max": 100000
        }
        
        chen_6d_profile = {
            "D1": 2.5, "D2": 4.5, "D3": 3.0, 
            "D4": 2.0, "D5": 3.5, "D6": 4.0
        }
        
        print(f"\n🔍 正在為 User {TEST_USER_ID} 尋找並計算最佳職缺...")
        final_frontend_data = service.find_best_jobs(user_id=TEST_USER_ID, filters=filters, user_6d_profile=chen_6d_profile)
        
        # 4. 印出結果
        print("\n🏆 ================= 終極排行榜 Top 10 ================= 🏆\n")
        if final_frontend_data:
            print("\n✅ 成功生成前端格式！以下為第一名職缺的 JSON 結構預覽：\n")
            # indent=4 讓 JSON 漂亮排版，ensure_ascii=False 確保中文字正常顯示
            print(json.dumps(final_frontend_data[0], indent=4, ensure_ascii=False))
            print(f"\n🎯 總共成功產出 {len(final_frontend_data)} 筆結構化職缺。")
        else:
            print("⚠️ 未產生任何結果。")
            
    except Exception as e:
        print(f"\n❌ 測試過程中發生錯誤：{e}")