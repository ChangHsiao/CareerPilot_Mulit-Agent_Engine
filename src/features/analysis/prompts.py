from typing import Dict, Any, Optional
from src.core.agent_engine.task_types import TaskType
from .schemas import CareerReport
from .tools import CareerAnalysisTools

# ==========================================
# 1. 核心規則與 Mapping 常數 (不變動邏輯)
# ==========================================

STANDARD_ROLES_STR = "前端工程師, 後端工程師, 全端工程師, 資料科學家, AI 工程師, DevOps/SRE 工程師"

MAPPING_INSTRUCTION = """
**Radar Chart Mapping Rules (Strictly Follow)**:
請將工具計算出的 D1-D6 分數映射為以下中文名稱：
- D1 -> "前端開發"
- D2 -> "後端開發"
- D3 -> "運維部署"
- D4 -> "AI與數據"
- D5 -> "工程品質"
- D6 -> "軟實力"

注意：
- 如果輸入資料是 Entry Level (無經驗)，Technical dimensions (前四項) 請直接使用 0.5。
- 請確保 `radar_chart.dimensions` 陣列中剛好包含這 6 個項目，順序不拘。
"""

CAREER_STAGE_MAPPING = """
**Career Stage Mapping Rules (Strictly Follow)**:
請將問卷的 q16_current_level 以及你評估的實際職級，嚴格轉譯為以下五種標準格式之一：
- entry_level -> "轉職中/學習中 (Entry Level)"
- junior -> "初階工程師 (Junior)"
- mid_level -> "中階工程師 (Mid Level)"
- senior -> "資深工程師 (Senior)"
- lead_architect -> "技術主管/架構師 (Lead Architect)"
"""

# ==========================================
# 2. Agent 定義常數
# ==========================================

# Tech Lead
TECH_LEAD_ROLE = "資深技術評估專家 (Tech Lead)"
TECH_LEAD_GOAL = "精準計算技術分數、計算與目標職位的匹配度並驗證履歷真實性"
TECH_LEAD_BACKSTORY = """你是一位嚴格的技術面試官，擅長從履歷細節中識破膨風或發掘潛力。
你的核心職職職責：
1. **算分**：使用工具計算 D1-D6 分數。
2. **匹配**：根據算出的分數與使用者的目標職位，計算匹配百分比。
3. **驗證 (Fact Check)**：比對「問卷分數」與「履歷內容 (Resume)」。
- 例如：如果 D2 (後端) 分數很高，檢查履歷是否有「高併發」、「微服務」等關鍵字支持。
- 如果 D3 (運維) 分數低，檢查履歷是否真的缺乏 CI/CD 或 Cloud 經驗。
- **若履歷內容比問卷更強，請在分析中註明「潛力被低估」。**
"""

# Psychologist
PSYCHOLOGIST_ROLE = "認知心理學家 (Psychologist)"
PSYCHOLOGIST_GOAL = "分析使用者特質並預測其在團隊中的行為模式"
PSYCHOLOGIST_BACKSTORY = """你是一位專精於「認知負載理論」與「軟體工程心理學」的專家。
你擁有一套分析框架，能將抽象的心理測驗分數映射到具體的程式開發場景。

**你的核心分析理論 (Cognitive Framework)**:
1. **Structure (架構力)**: 高分者擅長處理複雜的後端邏輯；低分者則適合彈性的前端互動。
2. **Ambiguity (模糊耐受度)**: 高分者適合 DevOps/SRE，能處理未知的 Error；低分者在維護型專案中表現更好。
3. **Decision (決策力)**: 高分者具備 Tech Lead 潛力。
4. **Transfer (敘事遷移)**: 高分者能將舊經驗快速映射到新技能。
"""

# Career Advisor
ADVISOR_ROLE = "職涯策略顧問 (Career Advisor)"
ADVISOR_GOAL = "綜合技術與心理分析，撰寫深度職涯報告草稿"
ADVISOR_BACKSTORY = """你是麥肯錫等級的顧問，擅長撰寫邏輯縝密、行動導向的建議書。
你的報告特色是「具體且有憑有據」。每一份報告都必須是「客製化的深度文章」。
你的寫作標準：由淺入深、結構化敘事、行動導向、嚴格遵守格式、使用流暢繁體中文。
"""

# Discovery Mentor (Entry Level)
MENTOR_ROLE = "轉職潛力挖掘導師 (Discovery Mentor)"
MENTOR_GOAL = "將非技術背景的舊經驗轉譯為軟體工程潛力"
MENTOR_BACKSTORY = """你是一位專精於「跨領域轉職」的導師，擅長使用「概念橋接」技術。
你認為「沒有白走的路」，所有的行政、行銷、業務經驗，都能對應到軟體工程的某個面向。
你的風格：拒絕空泛（Excel = SQL 雛形）、具象化比喻、極度詳盡。
"""

# ==========================================
# 3. Task 描述常數
# ==========================================

TECH_VERIFICATION_DESCRIPTION = """計算技術分數與目標職位匹配度，並驗證履歷真實性。
[問卷資料]: {survey_json}
[履歷資料]: {resume_json}
請依序執行：
1. 使用「問卷資料」呼叫工具計算 D1-D6 技術分數。
2. 根據算出的 D1-D6 分數與問卷中的目標職位 (target_role)，呼叫工具計算『匹配分數 (Match Score)』。
3. 對比「履歷資料」內容進行真實性驗證，若履歷證據與問卷分數不符，請註明落差。"""

TRAIT_ANALYSIS_DESCRIPTION = """分析人格特質。
資料: {trait_json}
根據使用者的分數，對照「認知分析理論」，評估其職位適配性。"""

FINAL_REPORT_DESCRIPTION = f"""綜合技術與心理分析，生成最終的 CareerReport JSON。
{MAPPING_INSTRUCTION}
{CAREER_STAGE_MAPPING}

**寫作重點**:
1. 結合特質分析。
2. 針對「硬實力」落差提供補強建議。
3. Gap Analysis 中必須點出具體技術缺口 (如 K8s)。
4. 行動計畫應包含具體工具與實作建議。
"""

ENTRY_LEVEL_TRANSITION_DESCRIPTION = f"""分析履歷中的非技術經驗，進行『技能轉譯』。
資料: {{resume_json}}

**核心任務**：
1. **Skill Translation (技能轉譯)**: 找出至少 3 個具體行為並對照程式概念。
2. **Role Recommendation (職位推薦)**: 從標準清單中推薦職位並說明理由。標準清單：[{STANDARD_ROLES_STR}]。
"""

ENTRY_LEVEL_FINAL_DESCRIPTION = f"""根據轉譯結果與特質，推薦職位並規劃學習路徑。
{MAPPING_INSTRUCTION}
{CAREER_STAGE_MAPPING}

**寫作風格**:
1. Preliminary Summary: 100 字左右，結合特質與潛力。
2. Gap Analysis: **必須完整擴寫『技能轉譯』內容**。
3. Action Plan: 具體的工具 (Python, SQL) 與實作建議。
4. Target Role: 必須符合格式 "領航員分析您適合的職類為 - [職位名稱]"。
"""

# ==========================================
# 4. Config Dispatcher (保持 Manager 相容性)
# ==========================================

def get_analysis_config(task_type: TaskType, inputs: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    提供 Manager 呼叫的配置字典。
    """
    # === 設定 1: 有經驗者職涯分析 ===
    if task_type == TaskType.CAREER_ANALYSIS_EXPERIENCED:
        return {
            "output_model": CareerReport,
            "qa_extra_instructions": f"""
               - **report_metadata (必須包含此物件)**: 
                 - `user_id`: 必須填入 "{inputs.get('user_id', 'unknown')}"。
                 - `timestamp`: 必須填入 "{inputs.get('current_timestamp', 'unknown')}"。
                 - `version`: 必須填入 "{inputs.get('report_version', '1.0')}"。
               - **職位與職級**:
                 - `role` 與 `actual_level` 等欄位，**必須完全匹配** Schema 描述中提供的標準清單。
            """,
            "agents": [
                {
                    "role": TECH_LEAD_ROLE,
                    "goal": TECH_LEAD_GOAL,
                    "backstory": TECH_LEAD_BACKSTORY,
                    "tools": [
                        CareerAnalysisTools.calculate_tech_vectors, 
                        CareerAnalysisTools.calculate_match_score
                    ]
                },
                {
                    "role": PSYCHOLOGIST_ROLE,
                    "goal": PSYCHOLOGIST_GOAL,
                    "backstory": PSYCHOLOGIST_BACKSTORY,
                    "tools": []
                },
                {
                    "role": ADVISOR_ROLE,
                    "goal": ADVISOR_GOAL,
                    "backstory": ADVISOR_BACKSTORY,
                    "tools": []
                }
            ],
            "tasks": [
                {
                    "description": TECH_VERIFICATION_DESCRIPTION,
                    "expected_output": "技術評估備忘錄 (包含 D1-D6 分數與驗證結果)"
                },
                {
                    "description": TRAIT_ANALYSIS_DESCRIPTION,
                    "expected_output": "一份關於使用者學習潛力與認知特質的分析報告。"
                },
                {
                    "description": FINAL_REPORT_DESCRIPTION,
                    "expected_output": "CareerReport JSON"
                }
            ]
        }

    # === 設定 2: 無經驗/轉職者分析 ===
    elif task_type == TaskType.CAREER_ANALYSIS_ENTRY_LEVEL:
        return {
            "output_model": CareerReport,
            "qa_extra_instructions": f"""
               - **report_metadata (必須包含此物件)**: 
                 - `user_id`: 必須填入 "{inputs.get('user_id', 'unknown')}"。
                 - `timestamp`: 必須填入 "{inputs.get('current_timestamp', 'unknown')}"。
                 - `version`: 必須填入 "{inputs.get('report_version', '1.0')}"。
               - **職位與職級**:
                 - `role` 與 `actual_level` 等欄位，**必須完全匹配** Schema 描述中提供的標準清單。
            """,
            "agents": [
                {
                    "role": MENTOR_ROLE,
                    "goal": MENTOR_GOAL,
                    "backstory": MENTOR_BACKSTORY,
                    "tools": []
                },
                {
                    "role": ADVISOR_ROLE,
                    "goal": ADVISOR_GOAL,
                    "backstory": ADVISOR_BACKSTORY,
                    "tools": []
                }
            ],
            "tasks": [
                {
                    "description": ENTRY_LEVEL_TRANSITION_DESCRIPTION,
                    "expected_output": "一份包含『技能轉譯對照表』與『職位推薦理由』的詳細備忘錄。"
                },
                {
                    "description": ENTRY_LEVEL_FINAL_DESCRIPTION,
                    "expected_output": "轉職建議 CareerReport JSON"
                }
            ]
        }
    
    return None
