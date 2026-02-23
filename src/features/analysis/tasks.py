from crewai import Task
from .prompts import (
    TECH_VERIFICATION_DESCRIPTION,
    TRAIT_ANALYSIS_DESCRIPTION,
    FINAL_REPORT_DESCRIPTION,
    ENTRY_LEVEL_TRANSITION_DESCRIPTION,
    ENTRY_LEVEL_FINAL_DESCRIPTION
)

def create_tech_verification_task(agent, survey_json: str, resume_json: str):
    """建立技術驗證任務"""
    return Task(
        description=TECH_VERIFICATION_DESCRIPTION.format(
            survey_json=survey_json,
            resume_json=resume_json
        ),
        expected_output="技術評估備忘錄 (包含 D1-D6 分數與驗證結果)",
        agent=agent
    )

def create_trait_analysis_task(agent, trait_json: str):
    """建立人格特質分析任務"""
    return Task(
        description=TRAIT_ANALYSIS_DESCRIPTION.format(
            trait_json=trait_json
        ),
        expected_output="一份關於使用者學習潛力與認知特質的分析報告。",
        agent=agent
    )

def create_final_report_task(agent, context: list):
    """建立最終綜合報告任務 (Experienced 用)"""
    return Task(
        description=FINAL_REPORT_DESCRIPTION,
        expected_output="CareerReport JSON",
        agent=agent,
        context=context
    )

def create_discovery_mentor_task(agent, resume_json: str):
    """建立技能轉譯任務 (Entry Level 用)"""
    return Task(
        description=ENTRY_LEVEL_TRANSITION_DESCRIPTION.format(
            resume_json=resume_json
        ),
        expected_output="一份包含『技能轉譯對照表』與『職位推薦理由』的詳細備忘錄。",
        agent=agent
    )

def create_entry_level_final_task(agent, context: list):
    """建立最終綜合報告任務 (Entry Level 用)"""
    return Task(
        description=ENTRY_LEVEL_FINAL_DESCRIPTION,
        expected_output="轉職建議 CareerReport JSON",
        agent=agent,
        context=context
    )
