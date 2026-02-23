from typing import Dict, Any, Optional
from src.core.agent_engine.task_types import TaskType
from .schemas import ResumeAnalysis, ResumeOptimization
from .agents import create_analysis_consultant, create_optimization_strategy_consultant
from .tasks import create_analysis_task, create_optimization_task

def get_resume_config(task_type: TaskType, inputs: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    獲取履歷模組的配置 (包含 Agents 與 Tasks)。
    """
    
    # 這裡的 llm 會由 Manager 傳入，但在目前的架構中，Manager 會處理實例化。
    # 由於 Manager 需要的是配置清單，我們回傳對應的結構。
    
    # === 1. 履歷分析 (RESUME_ANALYSIS) ===
    if task_type == TaskType.RESUME_ANALYSIS:
        # 在目前的 Manager 架構中，我們回傳的是用於建立 Agent/Task 的資料
        return {
            "output_model": ResumeAnalysis,
            "agents": [
                {
                    "role": "服務過跨國科技公司（FAANG 等級）的資深招募顧問",
                    "goal": "針對使用者的問卷與原始履歷進行「第一輪履歷篩選與風險評估」，找出影響進入面試的核心問題",
                    "backstory": """你是一位擁有多年頂尖科技公司招募經驗的專家，深知企業平均只花 6–10 秒掃描一份履歷。
                    你的視角極其專業且冷峻，專門從企業端尋找潛在風險。
                    你只評論「履歷中已出現的內容」，絕不推測或新增使用者未提供的經驗。
                    你的診斷標準包含：清楚度、證據力（數據化）、ATS 關鍵字完整度、以及與目標職涯的一致性。""",
                    "tools": []
                }
            ],
            "tasks": [
                {
                    "description": f"""
                    執行極其嚴苛的「第一輪履歷篩選與風險評估」。
                    [使用者問卷]: {inputs.get('survey_json')} 
                    [使用者履歷]: {inputs.get('resume_json')} 
                    
                    針對【清楚度、證據力、關鍵字、一致性】進行深度診斷。
                    規則：零推測、明確標註風險、提供具體改善建議。
                    """,
                    "expected_output": "診斷分析報告備忘錄 (包含風險警示與修改建議)"
                }
            ]
        }

    # === 2. 履歷優化 (RESUME_OPTIMIZATION) ===
    elif task_type == TaskType.RESUME_OPT:
        return {
            "output_model": ResumeOptimization,
            "agents": [
                {
                    "role": "服務獵頭與企業 HR 的資深履歷策略顧問",
                    "goal": "在不破壞使用者個人風格的前提下，根據診斷結果將履歷優化為「專業人士的表達方式」，產出一份完整的履歷。",
                    "backstory": """你是一位擅長微調職涯敘事的專家。你的核心思維不是「重寫」，而是「修飾」。
                    你具備精準模仿使用者語氣與句型的能力。你嚴格遵守 STAR 原則，絕不憑空捏造。""",
                    "tools": []
                }
            ],
            "tasks": [
                {
                    "description": f"""
                    將 [原始履歷內容]: {inputs.get('resume_json')} 
                    根據 [履歷診斷分析結果]: {inputs.get('analysis_result')} 進行優化。
                    
                    核心挑戰：優化後的內容必須「聽起來仍然像使用者自己寫的」。
                    規則：風格建模、STAR 化處理、專業術語轉化、嚴禁新增捏造事實。
                    """,
                    "expected_output": "優化後的完整履歷全文與風格定義。"
                }
            ]
        }
    
    return None
