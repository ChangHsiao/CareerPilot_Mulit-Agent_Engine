import os
import sys

# 將專案根目錄加入系統路徑，以確保能正確 import src 模組
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.common.logger import setup_logger

def run_logger_test():
    """
    測試專案專用 Logger 的功能：
    1. 驗證 INFO 等級的日誌是否能正常印出在終端機 (Console)
    2. 驗證 ERROR 等級的日誌是否能同時印出在終端機，並寫入 logs/career_system_error.log
    """
    print("\n================== Logger 測試開始 ==================")
    
    # 這裡會初始化 logger，並在專案根目錄建立 logs/ 資料夾
    logger = setup_logger()
    
    # 測試 1: INFO 訊息 (只應顯示在終端機)
    logger.info("【測試】系統初始化成功。")
    logger.info("【測試】這行訊息應該*只會*出現在終端機上，不會寫入檔案。")

    # 測試 2: ERROR 訊息 (應顯示在終端機，並寫入檔案)
    try:
        # 故意製造一個除以零的錯誤
        result = 1 / 0
    except Exception as e:
        logger.error(f"【測試】發生嚴重錯誤: {e}。這行訊息與 Traceback 應該會顯示在終端機，並且被寫入 logs/career_system_error.log", exc_info=True)
        
    print("================== Logger 測試結束 ==================\n")
    print("👉 請檢查您的終端機輸出。")
    print("👉 請前往專案根目錄下的 `logs` 資料夾，打開 `career_system_error.log` 檔案。")
    print("   (該檔案內應該只有剛才的 ERROR 記錄與 Traceback，沒有 INFO 記錄)")

if __name__ == "__main__":
    run_logger_test()
