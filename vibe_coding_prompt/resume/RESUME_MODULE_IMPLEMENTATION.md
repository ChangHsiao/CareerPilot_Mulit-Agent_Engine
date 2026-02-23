# 履歷模組實作報告 (Resume Module Implementation Report)

本文件記錄了將 `專題crewai試做_初版.ipynb` 中的履歷分析與優化邏輯，遷移並整合至現有專案架構（`AIPE02_01_Project_re`）的完整實作流程。

## 1. 實作目標
- 將分散在 Notebook 中的 Agent 定義、Task 指令與 Pydantic 模型，依照「高內聚、低耦合」原則配置到功能模組中。
- 建立一個可串接的 Multi-Agent 流程：**先進行深度分析，再根據分析結果執行優化。**
- 確保新模組能與專案的 `CareerAgentManager` (Core Engine) 完美對接。

---

## 2. 修改與新建檔案清單

### A. 資料結構層 (Schema Layer)
- **修改 `src/features/resume/schemas.py`**
  - **內容**：新增 `ResumeIssue` (單項診斷)、`ResumeAnalysis` (完整分析報告) 與 `ResumeOptimization` (優化後履歷內容) 模型。
  - **目的**：確保 Agent 輸出的 JSON 格式具備強型別約束，便於前端與 API 呼叫。

### B. Agent 與 Task 定義層 (Feature Layer)
- **新建 `src/features/resume/agents.py`**
  - **內容**：定義「資深招募顧問 (Analysis)」與「履歷策略顧問 (Optimization)」的系統提示詞 (Backstory) 與性格設定。
- **新建 `src/features/resume/tasks.py`**
  - **內容**：定義具體的執行步驟（如分析清楚度、STAR 化處理等）。將 Notebook 中的指令遷移過來，並透過 `inputs` 動態注入資料。

### C. 核心引擎集成 (Core Integration)
- **修改 `src/core/agent_engine/task_types.py`**
  - **內容**：在 `TaskType` Enum 中新增 `RESUME_ANALYSIS` 與 `RESUME_OPTIMIZATION` 常數。
- **修改 `src/features/resume/prompts.py`**
  - **內容**：實作 `get_resume_config` 函式。這是與 Core Engine 的橋樑，負責根據 `TaskType` 領取對應的 Agent 與 Task 配置。
- **修改 `src/core/agent_engine/config.py`**
  - **內容**：在 `get_config_by_type` 路由中，將新的 `TaskType` 導向 `src/features/resume/prompts.py`。

### D. 測試與驗證 (Validation)
- **新建 `test/test_resume_notebook_logic.py`**
  - **內容**：包含 Notebook 中的 mock 資料，模擬完整的業務流程。
  - **測試路徑**：`Analysis -> 获取結果 -> Optimization (使用分析結果作為 context)`。

---

## 3. 業務邏輯流程 (Business Flow)

本模組支援順序執行流程：

1.  **用戶提交**：原始履歷 + 職涯偏好問卷。
2.  **執行分析** (`RESUME_ANALYSIS`)：
    - Agent：資深招募顧問。
    - 產出：結構化的診斷報告（包含優劣勢、風險與改善建議）。
3.  **執行優化** (`RESUME_OPTIMIZATION`)：
    - Agent：履歷策略顧問。
    - 輸入：原始履歷 + **步驟 2 的診斷報告**。
    - 產出：優化後的完整履歷全文。

---

## 4. 如何執行測試
在專案根目錄下執行以下指令，即可驗證模組是否正常運作：

```bash
python test/test_resume_notebook_logic.py
```

此測試會依序執行分析與優化，並在控制台輸出結果摘要與 JSON 內容。
