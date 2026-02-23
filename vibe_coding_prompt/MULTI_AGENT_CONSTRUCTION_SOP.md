# 多代理系統 (Multi-Agent System) 建構專業 SOP 
## —— 從零到一：建設精神與實戰指南

本文件旨在指導如何建構一個專業、可擴充且高品質的多代理系統。這套流程是基於 `src/Multi_Agent` 的實作經驗總結而成。

---

## 1. 多代理系統的核心建設精神

建構多代理系統（MAS）不只是讓多個 AI 對話，其真正的精神在於：
1. **職責分離 (Separation of Concerns)**：每個 Agent 只專注於一件小事（例如：技術、心理、格式）。
2. **對抗性思考 (Adversarial Thinking)**：讓執行者與審核者分離，由審核者（QA）站在對立面檢查錯誤。
3. **數據驅動 (Data-Driven)**：將「業務邏輯（Prompt）」與「執行引擎（Manager）」完全解耦。

---

## 2. 專業建構 SOP (Step-by-Step)

### 第一步：定義任務藍圖 (The Blueprint)
**動作**：明確系統要解決哪些問題，並將其分類。
- **實作方式**：在 `manager.py` 中定義 `TaskType(Enum)`。
- **目的**：為每個請求建立唯一的標識符，方便路由。

### 第二步：角色設計與團隊選角 (The Casting)
**動作**：根據任務需求，設計「最適合」的專家。
- **實作方式**：在 `configs.py` 中定義 Agents 的 `role`, `goal`, `backstory`。
- **秘訣**：
    - 不要讓一個 Agent 做所有事。
    - 給予明確的性格背景（例如：冷峻的資深招募官 vs. 溫暖的職涯導師）。

### 第三步：定義任務流水線 (The Workflow)
**動作**：規劃 Agent 之間的執行順序與依賴關係。
- **實作方式**：定義 `Task` 清單，並利用 `context` 參數將上一步的結果傳給下一步。
- **模式**：通常採用 **Sequential (順序執行)**，確保後續專家能參考前人的分析結果。

### 第四步：建立品質控管層 (The Quality Gate) —— **關鍵步驟**
**動作**：設置一個專門的 **QA Agent**，負責最終的審核與格式化。
- **職責**：
    - 檢查是否有幻覺（Hallucination）。
    - 統一語氣（例如：確保繁體中文、嚴格禁止 Markdown）。
    - 強制轉換為 Pydantic 結構。
- **重要性**：這是解決 LLM 輸出不穩定（Non-deterministic）的最強手段。

### 第五步：封裝統一入口管理器 (The Facade)
**動作**：建立一個 `Manager` 類別，作為對外溝通的唯一窗口。
- **職責**：
    - 接收前端傳入的參數。
    - 根據 `TaskType` 調用配置工廠。
    - 啟動 `Crew` (團隊) 並執行。
    - 處理例外情況 (Exception Handling)。

### 第六步：驗證與自動化測試 (The Verification)
**動作**：建立測試腳本，模擬各種使用者輸入情境。
- **實作方式**：如 `test_multi_agent_flow.py`，驗證輸出是否符合 Pydantic 模型。

---

## 3. 必要的模組化設置 (Must-Have Modules)

建構專業多代理系統時，您的資料夾應包含以下功能組件：

1. **`manager.py` (大腦)**：
    - 負責「啟動」與「流程調度」。
    - 不寫具體的 Prompt，只寫執行邏輯。

2. **`configs.py` (知識庫)**：
    - 存放所有 Agent 的設定。
    - 這是系統最常變動的部分，將其抽離可確保大腦（Manager）的穩定。

3. **`schemas.py` (規格書)**：
    - 使用 Pydantic 定義每一種任務的輸出格式。
    - 沒有 Schema 的 Agent 產出只能算「文字草稿」，不能稱為「數據產出」。

4. **`tools.py` (手與腳)**：
    - 定義 Agent 可以調用的工具（如資料庫查詢、數學運算、網路搜尋）。

---

## 4. 專家建議：如何「學以致用」？

如果您今天要加入一個新功能（例如「面試模擬」）：
1. **不要** 在原有的程式碼中寫一大串 `if/else`。
2. **第一步**：在 `TaskType` 加入 `INTERVIEW_PREP`。
3. **第二步**：在 `configs.py` 中配置「面試官 Agent」與「面試評價 QA Agent」。
4. **第三步**：在 `schemas.py` 定義面試評分表。
5. **第四步**：直接呼叫 `manager.run_task("interview_prep", data)`。

**這就是架構化的力量 —— 新功能的開發只需要「配置」，不需要「重寫」。**
