from typing import List, Dict, Any
import math
from supabase import create_client
from dotenv import load_dotenv
import os

# =========================
# Supabase 初始化
# =========================
load_dotenv()
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------------------------------------------------
# 基礎設定與權重表
# ---------------------------------------------------------

# 課程等級定義
COURSE_LEVEL_MAP = {
    "Beginner": 1,
    "Intermediate": 2,
    "Advanced": 3
}

# 政策權重分佈 (Policy Distribution)
# 每一級的總和不需為1，這是「增益係數」
# 用途：決定「大方向」，例如 Level 2 主要看 Beginner/Intermediate，絕不看 Advanced
USER_TO_COURSE_DISTRIBUTION = {
    1: {1: 1.0, 2: 0.0, 3: 0.0},  # 新手：專注基礎
    2: {1: 0.9, 2: 0.6, 3: 0.0},  # 關鍵級別：開放 60% 的窗口給中階，讓 40分的人有機會
    3: {1: 0.5, 2: 1.0, 3: 0.4},  # 中階：向下複習，向上探索
    4: {1: 0.0, 2: 0.7, 3: 0.9},  # 中高階：強度提升
    5: {1: 0.0, 2: 0.0, 3: 1.0},  # 專家：只看難的
}

# =========================
# 新增：職級字串與系統 Level 的映射字典
# =========================
ACTUAL_LEVEL_MAP = {
    "entry_level": 1,     # 轉職中/學習中
    "junior": 2,          # 初階工程師
    "mid_level": 3,       # 中階工程師
    "senior": 4,          # 資深工程師
    "lead_architect": 5   # 技術主管/架構師
}

# =========================
# Step 1：撈使用者缺口分析
# =========================
def fetch_user_gap(user_id: str) -> Dict:
    resp = (
        supabase
        .table("user_skill_gap")
        .select("job_category, actual_level")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    return resp.data[0]

# =========================
# Step 2：匹配分數 → 使用者等級
# =========================
def parse_actual_level(actual_level_str: str) -> int:
    """
    【代碼意圖】將報告分析出的文字職級，精準轉為 1~5 級的整數。
    【為什麼這樣寫】使用 .get() 方法，並預設回傳 1。這是防呆機制 (Fail-safe)，
                  如果前端傳來預期外的字串，系統會安全地把它當作新手處理，而不會當機崩潰。
    """
    return ACTUAL_LEVEL_MAP.get(actual_level_str, 1)


# =========================
# Step 3：撈課程
# =========================
def fetch_candidate_courses(job_category: str) -> List[Dict]:
    resp = (
        supabase
        .table("course")
        .select("course_id, course_name, url, rating, review_count, level, course_type, duration_suggested")
        # .eq("job_category", job_category)
        .execute()
    )
    return resp.data

# =========================
# Step 4：中文字難易度 → 數值難易度
# =========================
def normalize_course_difficulty(courses: List[Dict]) -> List[Dict]:
    result = []

    for c in courses:
        level = COURSE_LEVEL_MAP.get(c.get("level"))
        if level is None:
            continue

        c["course_level"] = level
        result.append(c)

    return result

# =========================
# Step 5：Priority Score 計算 (政策等級 → 能力游標 (1.0 ~ 3.0))
# =========================
def compute_ability_cursor_from_level(user_level: int) -> float:
    """
    【代碼意圖】將 1~5 級的絕對職級，線性映射到 1.0~3.0 的課程難度空間。
    【數學公式解析】$Cursor = 1.0 + (user_level - 1) \times 0.5$
      - Level 1 (新手) -> 1.0 (Beginner 課程)
      - Level 2 (初階) -> 1.5 (介於 Beginner 與 Intermediate 之間)
      - Level 3 (中階) -> 2.0 (Intermediate 課程)
      - Level 4 (資深) -> 2.5 (介於 Intermediate 與 Advanced 之間)
      - Level 5 (主管) -> 3.0 (Advanced 課程)
    【應用場景】算出這個小數點游標後，才能跟課程本身的難度 (1, 2, 3) 算「幾何距離」。
    """
    return 1.0 + (user_level - 1) * 0.5

def compute_priority_score(
    course_level: int,
    ability_position: float,
    user_level: int
) -> float:
    """
    計算單一課程的推薦分數
    """
    # A. 距離分數 (Distance Score) - 連續性
    # 課程等級與使用者游標越近，分數越高
    # 使用高斯函數概念或簡單倒數： 1 / (1 + 距離平方) 讓接近的權重放大
    distance = abs(course_level - ability_position)
    distance_score = 1 / (1 + distance ** 2)

    # B. 政策權重 (Policy Weight) - 離散性
    # 查表確認該等級使用者是否適合此難度
    level_weight = USER_TO_COURSE_DISTRIBUTION[user_level].get(
        course_level, 0
    )

    return distance_score * level_weight

def rank_courses(
    courses: List[Dict],
    user_level: int # 這裡改為直接接收 1~5 的 user_level
) -> List[Dict]:

    # 1. 將 1~5 級轉換為 1.0~3.0 的游標
    ability_position = compute_ability_cursor_from_level(user_level)

    for c in courses:
        # 2. 計算雙軌分數 (距離分數 * 政策權重)
        c["priority_score"] = compute_priority_score(
            c["course_level"],
            ability_position,
            user_level
        )

        # 3. 課程品質分數不變
        c["quality_score"] = (
            (c.get("rating", 0) / 5 * 0.7) +
            (min(c.get("review_count") or 0, 1000) / 1000 * 0.3)
        )

    # 4. 排序：優先看適合度 (priority)，再看品質 (quality)
    return sorted(
        courses,
        key=lambda x: (x["priority_score"], x["quality_score"]),
        reverse=True
    )

# =========================
# Step 6：最終推薦流程（整合版）
# =========================
def recommend_courses(
    target_dimension: str,     # 你想補強的技能維度 (如 D1_frontend)
    actual_level_str: str,     # 從報告來的職級字串 (如 "mid_level")
    top_k: int = 5
) -> List[Dict]:

    # 1. 轉換字串為 1~5 等級
    user_level = parse_actual_level(actual_level_str)

    # 2. 從資料庫撈出該維度的課程並正規化 (假定你已經把 D1~D6 欄位設計好了)
    courses = fetch_candidate_courses(target_dimension)
    courses = normalize_course_difficulty(courses)

    # 3. 將計算好的 user_level 丟進去排序
    ranked = rank_courses(courses, user_level)

    return ranked[:top_k]