import os
from supabase import create_client, Client
from dotenv import load_dotenv

# 自動載入 .env 檔案
load_dotenv()

def get_supabase_client() -> Client:
    """
    統一獲取 Supabase Client 的連線實例。
    從環境變數讀取 SUPABASE_URL 與 SUPABASE_SERVICE_ROLE_KEY (或 SUPABASE_KEY)。
    """
    url = os.getenv("SUPABASE_URL")
    # 優先使用 Service Role Key 以獲得更高的操作權限，若無則回退至一般 Key
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        raise ValueError("❌ 找不到 Supabase 連線資訊。請確認 .env 檔案中的 SUPABASE_URL 與 SUPABASE_SERVICE_ROLE_KEY 已設定。")
    
    return create_client(url, key)
