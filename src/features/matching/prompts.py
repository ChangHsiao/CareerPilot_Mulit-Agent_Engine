# src/features/matching/prompts.py
"""
職缺匹配 AI 洞察分析的 CrewAI 配置工廠。
此函數的回傳格式必須與 manager.py 期待的 config dict 結構一致：
{
    "output_model": PydanticClass,
    "qa_extra_instructions": str,   (可選)
    "agents": [ {role, goal, backstory, tools, step_callback}, ... ],
    "tasks":  [ {description, expected_output, callback, tools}, ... ]
}
"""

from typing import Dict, Any, Optional
from src.core.agent_engine.task_types import TaskType
from .schemas import JobInsightResult


def get_matching_config(task_type: TaskType, inputs: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    提供 Manager 呼叫的配置字典。
    inputs 包含：job_title, user_6d, job_6d, match_score,
               job_description, job_requirements, resume_summary
    """
    if task_type == TaskType.JOB_MATCHING:

        # ============================================================
        # Agent 角色定義
        # ============================================================
        job_insight_agent_cfg = {
            "role": "資深職涯媒合顧問 (Job Matching Advisor)",
            "goal": (
                "根據候選人履歷、六維能力分數與職缺條件，"
                "產出客觀、具體且個人化的職缺落差分析報告。"
            ),
            "backstory": (
                "你是一位擁有 10 年獵頭經驗的資深職涯顧問，"
                "擅長透過量化數據與履歷文字，精準找出候選人與職缺之間的契合點與落差。"
                "你的建議必須具體、有針對性，絕對不能使用空洞的泛化語言，"
                "並且必須引用候選人履歷中的實際技能或經歷作為依據。"
            ),
            "tools": [],
            "step_callback": None,
        }

        # ============================================================
        # Task 描述
        # ============================================================
        # 從 inputs 中取出所有需要的資料
        job_title = inputs.get("job_title", "未知職缺")
        match_score = inputs.get("match_score", "N/A")
        resume_summary = inputs.get("resume_summary", "（無履歷內容）")
        job_description = inputs.get("job_description", "（無職缺描述）")
        job_requirements = inputs.get("job_requirements", "（無職缺條件）")
        user_6d = inputs.get("user_6d", {})
        job_6d = inputs.get("job_6d", {})

        task_description = f"""
你正在分析候選人與以下職缺的適配性：

【目標職缺】: {job_title}
【系統演算契合度】: {match_score}

【候選人履歷摘要】:
{resume_summary}

【職缺描述摘要】:
{job_description}

【職缺要求條件】:
{job_requirements}

【候選人六維能力分數 (滿分 5 分)】:
{user_6d}

【職缺六維能力要求 (滿分 5 分)】:
{job_6d}

請根據以上資訊，完成以下四項分析：
1. **recommendation_reason**：推薦此職缺給候選人的核心理由，需結合候選人的具體背景（約 60 字）
2. **strengths**：候選人應徵此職缺的最大優勢，需引用履歷中的具體技能或經驗（約 60 字）
3. **weaknesses**：候選人較缺乏、需要補足的部分，需對應職缺的具體要求（約 60 字）
4. **interview_tips**：針對落差給予一項具體的面試準備建議，需提到具體技術或技能名稱（約 60 字）
"""

        task_expected_output = (
            "包含 recommendation_reason, strengths, weaknesses, interview_tips "
            "四個欄位的 JSON 物件，每個欄位值為繁體中文字串。"
        )

        # ============================================================
        # 回傳標準 config dict（與其他模組完全相同的格式）
        # ============================================================
        return {
            "output_model": JobInsightResult,
            "qa_extra_instructions": (
                "請確保輸出的四個欄位（recommendation_reason, strengths, "
                "weaknesses, interview_tips）都是繁體中文字串，"
                "且每個欄位都必須有實質內容，不可為空字串或 '無'。"
            ),
            "agents": [job_insight_agent_cfg],
            "tasks": [
                {
                    "description": task_description,
                    "expected_output": task_expected_output,
                    "callback": None,
                    "tools": [],
                }
            ],
        }

    return None