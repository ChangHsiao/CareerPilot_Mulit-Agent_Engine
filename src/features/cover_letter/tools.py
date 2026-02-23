from crewai.tools import BaseTool
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class SearchRecommendJobTool(BaseTool):
    name: str = "SearchRecommendJob"
    description: str = "獲取推薦職缺的詳細資訊 (JD)，包含 job_title, job_description, requirements。Input: job_id"
    
    def _run(self, job_id: str) -> str:
        """
        到 Supabase 抓取職缺資料，進行推薦信生成。
        """
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not SUPABASE_URL or not SUPABASE_KEY:
            return "錯誤: 遺漏 Supabase 設定，無法抓取職缺資料。"
            
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

        try:
            # 採用括號包裹的方式進行鏈式呼叫，避免縮進與反斜線問題
            response = (
                supabase.table("job_posting")
                .select("job_id, job_title, job_description, requirements")
                .eq("job_id", job_id)
                .single()
                .execute()
            )

            if not response.data:
                return f"錯誤: 找不到 ID 為 {job_id} 的職缺資料。"

            return str(response.data)

        except Exception as e:
            return f"資料庫抓取失敗: {str(e)}"
