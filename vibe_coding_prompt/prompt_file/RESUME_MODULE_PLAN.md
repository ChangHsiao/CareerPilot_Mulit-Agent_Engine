# 履歷模組配置計畫 (Resume Module Plan)

本計畫根據 `專題crewai試做_初版.ipynb` 的邏輯，將履歷功能拆解為「分析」與「優化」兩個階段，並整合至 Multi-Agent 架構中。

## 1. 核心任務定義

### A. 履歷分析 (Resume Analysis)
- **目標**：模擬企業 HR 進行 6-10 秒的快速掃描，找出履歷與目標職缺間的風險與落差。
- **輸入**：使用者原始履歷、職涯偏好問卷。
- **關鍵規則**：
    - **零推測原則**：僅針對白紙黑字的內容進行分析。
    - **風險標註**：明確指出空窗期、職涯跨度過大或技能不符。
    - **診斷面向**：清楚度、證據力（數據）、ATS 關鍵字、目標一致性。

### B. 履歷優化 (Resume Optimization)
- **目標**：根據分析報告，在不捏造事實的前提下，優化敘事方式與專業術語。
- **輸入**：使用者原始履歷、履歷分析報告。
- **關鍵規則**：
    - **風格建模**：模仿原作者語氣（條列或敘事），避免 AI 罐頭感。
    - **STAR 原則**：將經歷轉化為「情境、任務、行動、結果」。
    - **禁止捏造**：嚴禁新增未提及的技能、證照或專案。

---

## 2. 資料夾結構配置與功能分配

本模組遵循「高內聚、低耦合」原則，並採用優化後的「標準化 Feature 架構」。

> **設計理念說明 (Architecture Evolution)**：
> 異於早期模組（如 analysis）將 Agent 與 Task 定義全部擠在 `prompts.py` 的做法，履歷模組採用拆分設計。這樣做的好處是：
> 1. **提升可讀性**：避免單一檔案過長，便於快速定位 Agent 的性格設定或 Task 的執行細節。
> 2. **提升複用性**：未來其他功能（如模擬面試）若需引用相同的 Agent，可直接從 `agents.py` 導入。
> 3. **職責明確**：`prompts.py` 僅作為配置分發器，不參與具體的 Agent/Task 內容撰寫。

### `src/features/resume/` (功能核心)
- **`schemas.py`** (結構定義)
    - 定義 `ResumeAnalysis` 與 `ResumeOptimization` 的 Pydantic 模型。
- **`agents.py`** (新檔案 - Agent 定義)
    - `AnalysisConsultant`: 資深招募顧問 Agent（包含其 Backstory 與系統提示）。
    - `OptimizationStrategy`: 履歷策略顧問 Agent。
- **`tasks.py`** (新檔案 - Task 定義)
    - `analysis_task`: 定義分析履歷的具體步驟與預期輸出。
    - `optimization_task`: 定義優化履歷的具體步驟。
- **`tools.py`** (工具功能)
    - `FetchUserResume`, `FetchUserSurvey` 等資料存取工具。
- **`prompts.py`** (對接入口)
    - **`get_resume_config` 函式**：這是與 `core/agent_engine` 的關鍵橋樑。它會根據 `TaskType` 實例化 `agents.py` 中的 Agent 與 `tasks.py` 中的 Task，並封裝成 Dict 回傳給 Manager。

### `src/core/agent_engine/` (通用引擎)
- **`manager.py`**: 作為通用調度器，負責接收請求並啟動 Crew。它不包含 Resume 業務細節。
- **`config.py`**: 透過 `from src.features.resume.prompts import get_resume_config` 進行動態路由。
- **`task_types.py`**: 定義 `RESUME_ANALYSIS` 與 `RESUME_OPTIMIZATION` 的 Enum 常數。

---

## 3. Multi-Agent 流程設計 (Flow)

本模組採用 **Sequential Process (順序執行)**：

1.  **階段一：深度分析**
    - **執行者**：`AnalysisConsultant`
    - **審核者**：`ResumeQA`
    - **輸出**：結構化的 `ResumeAnalysis` JSON。
2.  **階段二：策略優化**
    - **執行者**：`OptimizationStrategy` (參考階段一的輸出)
    - **審核者**：`ResumeQA`
    - **輸出**：結構化的 `ResumeOptimization` JSON。

### 為什麼這樣配置？
- **職責分離**：招募顧問負責「挑毛病」，策略顧問負責「解決問題」，避免同一個 Agent 既當裁判又當球員，提高專業度。
- **QA 介入**：每個階段都有 QA 確保輸出的 JSON 格式正確，且內容沒有產生幻覺（例如憑空生出技能）。
- **結構化輸出**：強制輸出 Pydantic 模型，確保後端 API 能穩定對接到前端 UI。
