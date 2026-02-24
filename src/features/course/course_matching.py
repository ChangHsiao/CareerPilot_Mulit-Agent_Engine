from typing import List, Dict, Any, Optional
import math
import os
from .schemas import CourseItem, CourseRecommendationResponse
from src.core.database.supabase_client import get_supabase_client

# =========================
# 基礎設定與權重表
# =========================
COURSE_LEVEL_MAP = {
    "Beginner": 1,
    "Intermediate": 2,
    "Advanced": 3
}

# 政策權重分佈 (Policy Distribution)
# 決定不同 User Level 與 Course Level 間的推薦強弱
USER_TO_COURSE_DISTRIBUTION = {
    1: {1: 1.0, 2: 0.0, 3: 0.0},  # 新手：專注基礎
    2: {1: 0.9, 2: 0.6, 3: 0.0},  # 關鍵級別：主要基礎，部分中階
    3: {1: 0.5, 2: 1.0, 3: 0.4},  # 中階：向下複習，向上探索
    4: {1: 0.0, 2: 0.7, 3: 0.9},  # 中高階：強度提升
    5: {1: 0.0, 2: 0.0, 3: 1.0},  # 專家：只看難的
}

class CourseRecommendationService:
    """
    課程推薦服務，負責根據使用者的技能缺口分析結果提供課程建議。
    """
    def __init__(self, supabase_client=None):
        self.supabase = supabase_client or get_supabase_client()

    def fetch_user_gap(self, user_id: str) -> Optional[Dict]:
        """
        從 Supabase 撈取該使用者的最新技能缺口分析結果。
        """
        try:
            resp = (
                self.supabase
                .table("user_skill_gap")
                .select("job_category, match_score")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )
            return resp.data[0] if resp.data else None
        except Exception as e:
            print(f"⚠️ 獲取使用者缺口分析失敗: {e}")
            return None

    def fetch_candidate_courses(self, job_category: str) -> List[Dict]:
        """
        從 Supabase 撈取與職位類別相關的候選課程清單。
        """
        try:
            # 目前初步以全體課程為準，未來可依 job_category 篩選
            resp = (
                self.supabase
                .table("course")
                .select("course_id, course_name, url, rating, review_count, level, course_type, duration_suggested")
                .execute()
            )
            return resp.data
        except Exception as e:
            print(f"⚠️ 獲取候選課程失敗: {e}")
            return []

    @staticmethod
    def score_to_user_level(match_score: int) -> int:
        """
        將 0-100 的 match_score 映射到 1-5 等級。
        """
        if match_score <= 20: return 1
        elif match_score <= 40: return 2
        elif match_score <= 60: return 3
        elif match_score <= 80: return 4
        return 5

    @staticmethod
    def compute_user_ability_position(match_score: int) -> float:
        """
        將 0-100 的 match_score 映射到課程難度空間 (1.0-3.0)。
        """
        return round(1.0 + (match_score / 100) * 2.0, 3)

    def calculate_scores(self, courses: List[Dict], match_score: int, user_level: int) -> List[Dict]:
        """
        計算每一門課程的推薦分數。
        """
        ability_position = self.compute_user_ability_position(match_score)
        processed_courses = []

        for c in courses:
            level_val = COURSE_LEVEL_MAP.get(c.get("level"))
            if level_val is None:
                continue

            # 1. Priority Score (基於距離與政策權重)
            distance = abs(level_val - ability_position)
            distance_score = 1 / (1 + distance ** 2)
            policy_weight = USER_TO_COURSE_DISTRIBUTION[user_level].get(level_val, 0)
            priority_score = distance_score * policy_weight

            # 2. Quality Score (基於評價與評論數)
            rating = c.get("rating", 0) or 0
            reviews = c.get("review_count", 0) or 0
            quality_score = (rating / 5 * 0.7) + (min(reviews, 1000) / 1000 * 0.3)

            # 更新課程資訊
            c["course_level_val"] = level_val
            c["priority_score"] = priority_score
            c["quality_score"] = quality_score
            processed_courses.append(c)

        return processed_courses

    def get_recommendations(self, user_id: str, top_k: int = 5) -> CourseRecommendationResponse:
        """
        主推薦流程入口。
        """
        # 1. 獲取使用者狀態
        user_gap = self.fetch_user_gap(user_id)
        if not user_gap:
            # 默認值
            match_score = 40
            job_category = "backend"
        else:
            match_score = user_gap["match_score"]
            job_category = user_gap["job_category"]

        user_level = self.score_to_user_level(match_score)

        # 2. 獲取並處理課程
        courses = self.fetch_candidate_courses(job_category)
        scored_courses = self.calculate_scores(courses, match_score, user_level)

        # 3. 排序
        ranked = sorted(
            scored_courses,
            key=lambda x: (x["priority_score"], x["quality_score"]),
            reverse=True
        )

        # 4. 封裝回傳
        recommendations = []
        for r in ranked[:top_k]:
            recommendations.append(CourseItem(
                course_id=str(r["course_id"]),
                course_name=r["course_name"],
                url=r["url"],
                level=r["level"],
                course_type=r.get("course_type"),
                priority_score=r["priority_score"],
                quality_score=r["quality_score"]
            ))

        return CourseRecommendationResponse(
            user_id=user_id,
            user_level=user_level,
            match_score=match_score,
            recommendations=recommendations
        )
