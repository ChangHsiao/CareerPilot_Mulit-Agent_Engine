# src/Multi_Agent/configs.py
from typing import Dict, Any, List
from .manager import TaskType

# 引用現有的 Pydantic Models
from src.features.analysis.schemas import CareerReport
from src.features.resume.schemas import ResumeAnalysis, ResumeOptimization
# 引用現有的 Tools
from src.report.tools import CareerAnalysisTools
from src.features.resume.tools import FetchResumeTool

# ===============
# 分析報告相關設定
# ===============
def get_config_by_type(task_type: TaskType, inputs: Dict[str, Any]) -> Dict[str, Any]:
    
    # === 設定 1: 有經驗者職涯分析 ===
    if task_type == TaskType.CAREER_ANALYSIS_EXPERIENCED:
        return {
            "output_model": CareerReport, # 指定最終輸出的 Pydantic 模型
            
            # 定義 Workers (順序很重要)
            "agents": [
                {
                    "role": "資深技術評估專家 (Tech Lead)",
                    "goal": "精準計算技術分數並驗證履歷真實性",
                    "backstory": "你是一位嚴格的技術面試官，擅長從履歷細節中識破膨風或發掘潛力。",
                    "tools": [CareerAnalysisTools.calculate_tech_vectors]
                },
                {
                    "role": "認知心理學家 (Psychologist)",
                    "goal": "分析使用者特質並預測其在團隊中的行為模式",
                    "backstory": "你擅長運用認知科學將抽象的測驗分數轉化為具體的職場行為預測。",
                    "tools": []
                },
                {
                    "role": "職涯策略顧問 (Career Advisor)",
                    "goal": "綜合技術與心理分析，撰寫深度職涯報告草稿",
                    "backstory": "你是麥肯錫等級的顧問，擅長撰寫邏輯縝密、行動導向的建議書。",
                    "tools": []
                }
            ],
            
            # 定義 Tasks (對應上面的 Agents)
            "tasks": [
                {
                    "description": f"""計算技術分數並驗證履歷。
[問卷資料]: {inputs.get('survey_json')}
[履歷資料]: {inputs.get('resume_json')}
請使用「問卷資料」來計算分數，並對比「履歷資料」進行真實性驗證。""",
                    "expected_output": "技術評估備忘錄 (包含 D1-D6 分數與驗證結果)"
                },
                {
                    "description": f"""分析人格特質。
資料: {inputs.get('trait_json')}""",
                    "expected_output": "一份關於使用者學習潛力與認知特質的分析報告。"
                },
                {
                    "description": "綜合前兩份報告，撰寫職涯建議草稿。重點：分析 Gap 並提出 Action Plan。",
                    "expected_output": "職涯報告草稿 (純文字)"
                }
            ]
        }

    # === 設定 2: 無經驗/轉職者分析 ===
    elif task_type == TaskType.CAREER_ANALYSIS_ENTRY_LEVEL:
        return {
            "output_model": CareerReport,
            
            "agents": [
                {
                    "role": "轉職潛力挖掘導師 (Discovery Mentor)",
                    "goal": "將非技術背景的舊經驗轉譯為軟體工程潛力",
                    "backstory": "你擅長『技能轉譯』，能看出行政、業務經驗背後的邏輯思維價值。",
                    "tools": []
                },
                {
                    "role": "職涯策略顧問 (Career Advisor)",
                    "goal": "為轉職者規劃具體的學習路徑與職位推薦",
                    "backstory": "你專精於協助非本科系學生成功轉職為工程師。",
                    "tools": []
                }
            ],
            
            "tasks": [
                {
                    "description": f"""分析履歷中的非技術經驗，進行『技能轉譯』。
資料: {inputs.get('resume_json')}""",
                    "expected_output": "一份包含『技能轉譯對照表』與『職位推薦理由』的詳細備忘錄 (Memo)。"
                },
                {
                    "description": "根據轉譯結果與特質，推薦適合的入門職位並規劃學習路徑。",
                    "expected_output": "轉職建議草稿"
                }
            ]
        }
    
    # === 設定 3: 履歷深度診斷 (Critique) ===
    elif task_type == TaskType.RESUME_CRITIQUE:
        return {
            "output_model": ResumeAnalysis,
            "agents": [
                {
                    "role": "資深企業 HR 審查官 (Resume Auditor)",
                    "goal": "從企業與 ATS 篩選角度，精準找出履歷中的致命缺點與可優化空間",
                    "backstory": "你擁有 10 年技術招募經驗，擅長從企業 HR 與 ATS 的視角產出深度診斷。你會特別關注缺乏量化證據、描述模糊、與目標職位不一致等問題。",
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

    # === 設定 4: 履歷目標導向優化 (Optimization) ===
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
                    "backstory": "你擅長將平淡的描述轉化為具吸引力的專業術語，並確保產出符合台灣繁體中文職場習慣，保留使用者原有語氣。",
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
                    "description": "根據診斷結果，使用 STAR 原則與行業術語重寫履歷各個區塊。確保專業度與真實性。",
                    "expected_output": "優化後的履歷內容草稿"
                }
            ]
        }

    return None
