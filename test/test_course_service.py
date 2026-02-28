import os
import json
from dotenv import load_dotenv
from src.features.course.course_matching import CourseRecommendationService

# 載入環境變數 (確保能連到 Supabase)
load_dotenv()

def test_course_recommendation():
    print("====== 正在測試課程推薦服務 (CourseRecommendationService) ======")
    
    # 1. 初始化服務
    service = CourseRecommendationService()
    
    # 2. 測試用 user_id
    test_user_id = "1" 
    
    print(f"測試使用者 ID: {test_user_id}")
    
    try:
        # 由於新架構直接回傳 List[Dict]，不再有外層的 response wrapping
        recommendations = service.get_recommendations(test_user_id, top_k=3)
        
        print("✅ 推薦結果獲取成功！")
        print(f"獲取推薦課程數量: {len(recommendations)}")
        print("==========================================================")
        
        for i, course in enumerate(recommendations, 1):
            print(f"[{i}] 課程名稱: {course.get('course_name')}")
            print(f"    - ID: {course.get('course_id')} | 語言難度: {course.get('level')} | 等級值: {course.get('course_level')}")
            print(f"    - 時長: {course.get('duration_suggested')} | 類型: {course.get('course_type')}")
            print(f"    - 評分 (Rating): {course.get('rating')} | 評論數: {course.get('review_count')}")
            print(f"    - 優先分數 (Priority): {course.get('priority_score', 0):.4f}")
            print(f"    - 品質分數 (Quality): {course.get('quality_score', 0):.4f}")
            print(f"    - 連結: {course.get('url')}")
            print("----------------------------------------------------------")

    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {e}")

if __name__ == "__main__":
    test_course_recommendation()
