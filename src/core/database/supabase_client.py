import os
from supabase import create_client, Client
from dotenv import load_dotenv

# 自動載入 .env 檔案
load_dotenv()

def get_supabase_client() -> Client:
    """
    統一獲取 Supabase Client 的連線實例。
    從環境變數讀取 SUPABASE_URL 與 SUPABASE_SERVICE_ROLE_KEY (或 SUPABASE_KEY)。
    優先使用 Service Role Key 以獲得更高的操作權限（例如寫入權限）。
    """
    url = os.getenv("SUPABASE_URL")
    # 優先選擇 Service Role Key，若無則回退至 Anon Key
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        raise ValueError("❌ 找不到 Supabase 連線資訊。請確認 .env 檔案中的 SUPABASE_URL 與 SUPABASE_SERVICE_ROLE_KEY 已設定。")
    
    try:
        # 初始化連線
        client = create_client(url, key)
        return client
    except Exception as e:
        print(f"❌ Supabase 連線失敗: {e}")
        raise
