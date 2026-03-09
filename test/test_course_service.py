import os
import json
from dotenv import load_dotenv
from src.features.course.course_matching import CourseRecommendationService
from src.common.logger import setup_logger

# 載入環境變數 (確保能連到 Supabase)
load_dotenv()

# 加入 Logger
logger = setup_logger()

def test_course_recommendation():
    print("====== 正在測試課程推薦服務 (CourseRecommendationService) ======")
    
    # 1. 初始化服務
    service = CourseRecommendationService()
    
    # 2. 測試用 user_id
    test_user_id = "37" 
    
    print(f"測試使用者 ID: {test_user_id}")
    
    try:
        # 新架構會交由 Agent 處理，回傳的是 Pydantic schema (CareerRoadmap) 轉換的 Dict
        # 也有可能是發生錯誤的回傳 {"status": "error", "message": "..."}
        result = service.get_recommendations(test_user_id, top_k=3)
        
        if result.get("status") == "error":
            error_msg = result.get('message')
            logger.error(f"服務回傳錯誤狀態: {error_msg}")
            print(f"❌ 測試無法進行，發生錯誤: {error_msg}")
            return
            
        # 從 AI 回傳的結構中，提取我們需要的欄位
        courses = result.get("learning_pathway", [])
        
        print("✅ 推薦結果獲取成功！")
        print(f"🎯 戰略分析: \n{result.get('overall_strategy')}\n")
        print(f"獲取推薦課程數量: {len(courses)}")
        print("==========================================================")
        
        for i, course in enumerate(courses, 1):
            print(f"[{i}] 課程名稱: {course.get('course_name')}")
            print(f"    - ID: {course.get('course_id')} | 語言難度: {course.get('level')}")
            print(f"    - 時長: {course.get('duration_suggested')} | 類型: {course.get('course_type')}")
            print(f"    - 評分 (Rating): {course.get('rating')} | 評論數: {course.get('review_count')}")
            print(f"    - 戰略原因: {course.get('strategic_reason')}")
            print(f"    - 連結: {course.get('url')}")
            print("----------------------------------------------------------")

        print("\n💡 提示：您可以前往檢查 `logs/crewai_outputs/task_audit_trail.log`，看看 Agent 是否有留下稽核蹤跡！")

    except Exception as e:
        # [修復] 將原本單純的 print 改為 logger.error，這樣錯誤才會進 log
        logger.error(f"測試過程中發生錯誤: {e}", exc_info=True)
        print(f"❌ 測試過程中發生錯誤，詳細請見 logs: {e}")

if __name__ == "__main__":
    test_course_recommendation()
