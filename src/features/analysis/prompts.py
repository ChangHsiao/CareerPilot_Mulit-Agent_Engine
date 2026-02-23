from typing import Dict, Any, Optional
from src.core.agent_engine.task_types import TaskType
from .schemas import CareerReport
from .tools import CareerAnalysisTools

# ===============
# 職涯分析報告配置 (Recipe for Career Analysis)
# ===============

def get_analysis_config(task_type: TaskType, inputs: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    
    # 標準職位定義 (與 Schema 一致)
    STANDARD_ROLES_STR = "前端工程師, 後端工程師, 全端工程師, 資料科學家, AI 工程師, DevOps/SRE 工程師"
    
    # 雷達圖 Mapping 指令
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

    # === 設定 1: 有經驗者職涯分析 ===
    if task_type == TaskType.CAREER_ANALYSIS_EXPERIENCED:
        return {
            "output_model": CareerReport,
            "agents": [
                {
                    "role": "資深技術評估專家 (Tech Lead)",
                    "goal": "精準計算技術分數並驗證履歷真實性",
                    "backstory": """你是一位嚴格的技術面試官，擅長從履歷細節中識破膨風或發掘潛力。
                    你的核心職責：
                    1. **算分**：使用工具計算 D1-D6 分數。
                    2. **驗證 (Fact Check)**：比對「問卷分數」與「履歷內容 (Resume)」。
                    - 例如：如果 D2 (後端) 分數很高，檢查履歷是否有「高併發」、「微服務」等關鍵字支持。
                    - 如果 D3 (運維) 分數低，檢查履歷是否真的缺乏 CI/CD 或 Cloud 經驗。
                    - **若履歷內容比問卷更強，請在分析中註明「潛力被低估」。**
                    """,
                    "tools": [CareerAnalysisTools.calculate_tech_vectors]
                },
                {
                    "role": "認知心理學家 (Psychologist)",
                    "goal": "分析使用者特質並預測其在團隊中的行為模式",
                    "backstory": """你是一位專精於「認知負載理論」與「軟體工程心理學」的專家。
                    你擁有一套分析框架，能將抽象的心理測驗分數映射到具體的程式開發場景。
                    
                    **你的核心分析理論 (Cognitive Framework)**:
                    1. **Structure (架構力)**: 高分者擅長處理複雜的後端邏輯；低分者則適合彈性的前端互動。
                    2. **Ambiguity (模糊耐受度)**: 高分者適合 DevOps/SRE，能處理未知的 Error；低分者在維護型專案中表現更好。
                    3. **Decision (決策力)**: 高分者具備 Tech Lead 潛力。
                    4. **Transfer (敘事遷移)**: 高分者能將舊經驗快速映射到新技能。
                    """,
                    "tools": []
                },
                {
                    "role": "職涯策略顧問 (Career Advisor)",
                    "goal": "綜合技術與心理分析，撰寫深度職涯報告草稿",
                    "backstory": """你是麥肯錫等級的顧問，擅長撰寫邏輯縝密、行動導向的建議書。
                    你的報告特色是「具體且有憑有據」。每一份報告都必須是「客製化的深度文章」。
                    你的寫作標準：由淺入深、結構化敘事、行動導向、嚴格遵守格式、使用流暢繁體中文。
                    """,
                    "tools": []
                }
            ],
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
                    資料: {inputs.get('trait_json')}
                    根據使用者的分數，對照「認知分析理論」，評估其職位適配性。""",
                    "expected_output": "一份關於使用者學習潛力與認知特質的分析報告。"
                },
                {
                    "description": f"""綜合技術與心理分析，生成最終的 CareerReport JSON。
                    {MAPPING_INSTRUCTION}
                    {CAREER_STAGE_MAPPING}
                    
                    **寫作重點**:
                    1. 結合特質分析。
                    2. 針對「硬實力」落差提供補強建議。
                    3. Gap Analysis 中必須點出具體技術缺口 (如 K8s)。
                    4. 行動計畫應包含具體工具與實作建議。
                    """,
                    "expected_output": "CareerReport JSON"
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
                    "backstory": """你是一位專精於「跨領域轉職」的導師，擅長使用「概念橋接」技術。
                    你認為「沒有白走的路」，所有的行政、行銷、業務經驗，都能對應到軟體工程的某個面向。
                    你的風格：拒絕空泛（Excel = SQL 雛形）、具象化比喻、極度詳盡。
                    """,
                    "tools": []
                },
                {
                    "role": "職涯策略顧問 (Career Advisor)",
                    "goal": "為轉職者規劃具體的學習路徑與職位推薦",
                    "backstory": """你專精於協助非本科系學生成功轉職為工程師。
                    你負責綜合 Mentor 的「技能轉譯」與潛力分析，生成內容豐厚、語氣詳實的最終報告。
                    """,
                    "tools": []
                }
            ],
            "tasks": [
                {
                    "description": f"""分析履歷中的非技術經驗，進行『技能轉譯』。
                    資料: {inputs.get('resume_json')}
                    
                    **核心任務**：
                    1. **Skill Translation (技能轉譯)**: 找出至少 3 個具體行為並對照程式概念。
                    2. **Role Recommendation (職位推薦)**: 從標準清單中推薦職位並說明理由。標準清單：[{STANDARD_ROLES_STR}]。
                    """,
                    "expected_output": "一份包含『技能轉譯對照表』與『職位推薦理由』的詳細備忘錄。"
                },
                {
                    "description": f"""根據轉譯結果與特質，推薦職位並規劃學習路徑。
                    {MAPPING_INSTRUCTION}
                    {CAREER_STAGE_MAPPING}
                    
                    **寫作風格**:
                    1. Preliminary Summary: 80-100 字，結合特質與潛力。
                    2. Gap Analysis: **必須完整擴寫『技能轉譯』內容**。
                    3. Action Plan: 具體的工具 (Python, SQL) 與實作建議。
                    4. Target Role: 必須符合格式 "領航員分析您適合的職類為 - [職位名稱]"。
                    """,
                    "expected_output": "轉職建議 CareerReport JSON"
                }
            ]
        }
    
    return None
