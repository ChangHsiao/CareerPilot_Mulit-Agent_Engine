from enum import Enum

class TaskType(Enum):
    """定義系統支援的所有任務類型"""
    CAREER_ANALYSIS_EXPERIENCED = "career_analysis_experienced" # 有經驗者分析
    CAREER_ANALYSIS_ENTRY_LEVEL = "career_analysis_entry_level" # 無經驗者/轉職分析
    JOB_MATCHING = "job_matching" # 職缺匹配
    RESUME_CRITIQUE = "resume_critique"               # 履歷深度診斷
    RESUME_GENERATION = "resume_generation"           # 履歷優化與生成
    RESUME_ANALYSIS = "resume_analysis"               # 履歷分析 (Jupyter 版邏輯)
    RESUME_OPTIMIZATION = "resume_optimization"       # 履歷優化 (Jupyter 版邏輯)
    PROJECT_REC = "project_rec" # 專案推薦
    COVER_LETTER = "cover_letter" # 求職信
