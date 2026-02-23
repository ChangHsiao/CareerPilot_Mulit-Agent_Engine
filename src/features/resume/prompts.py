from typing import Dict, Any, Optional
from src.core.agent_engine.task_types import TaskType
from .schemas import ResumeAnalysis, ResumeOptimization
from .tools import FetchResumeTool

# ===============
# 履歷任務配置 (Recipe for Resume Tasks)
# ===============

def get_resume_config(task_type: TaskType, inputs: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    
    # === 設定 1: 履歷深度診斷 (Critique) ===
    if task_type == TaskType.RESUME_CRITIQUE:
        return {
            "output_model": ResumeAnalysis,
            "agents": [
                {
                    "role": "資深企業 HR 審查官 (Resume Auditor)",
                    "goal": "從企業與 ATS 篩選角度，精準找出履歷中的致命缺點與可優化空間",
                    "backstory": """你擁有 10 年技術招募經驗，擅長從企業 HR 與 ATS 的視角產出深度診斷。
                    你會特別關注缺乏量化證據、描述模糊、與目標職位不一致等問題。
                    """,
                    "tools": [FetchResumeTool()]
                }
            ],
            "tasks": [
                {
                    "description": f"""執行履歷深度診斷。
                    目標職位: {inputs.get('target_role', '後端工程師')}
                    [原始履歷內容]:
                    {inputs.get('resume_content', '請使用 FetchUserResume 工具獲取')}
                    
                    請針對履歷進行診斷，挑出關鍵問題、評估嚴重程度，並給予改進方向。""",
                    "expected_output": "一份結構化的履歷診斷報告草稿。"
                }
            ]
        }

    # === 設定 2: 履歷目標導向優化 (Optimization) ===
    elif task_type == TaskType.RESUME_GENERATION:
        return {
            "output_model": ResumeOptimization,
            "agents": [
                {
                    "role": "資深企業 HR 審查官 (Resume Auditor)",
                    "goal": "產出初步診斷建議",
                    "backstory": "你負責先找出履歷的問題點，為優化者提供依據。",
                    "tools": []
                },
                {
                    "role": "職涯文字修辭家 (Career Wordsmith)",
                    "goal": "根據診斷結果與 STAR 原則，優化履歷內容",
                    "backstory": """你擅長將平淡的描述轉化為具吸引力的專業術語。
                    確保產出符合台灣繁體中文職場習慣，並保留使用者原有語氣。
                    """,
                    "tools": []
                }
            ],
            "tasks": [
                {
                    "description": f"""先進行履歷診斷。
                    目標職位: {inputs.get('target_role', '後端工程師')}
                    履歷內容: {inputs.get('resume_content')}""",
                    "expected_output": "初步診斷備忘錄"
                },
                {
                    "description": """根據診斷結果，使用 STAR 原則與行業術語重寫履歷各個區塊。
                    確保專業度與真實性。""",
                    "expected_output": "優化後的履歷內容草稿"
                }
            ]
        }

    return None
