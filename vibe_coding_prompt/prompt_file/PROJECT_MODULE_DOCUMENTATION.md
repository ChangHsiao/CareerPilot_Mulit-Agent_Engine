# Side Project 推薦模組：建構紀錄與功能說明手冊

本文件記錄了 Side Project 推薦模組從規劃到實作的完整過程，並說明其核心架構、設計哲學以及與系統引擎的對接規範。

---

## 1. 建構背景與邏輯演進

### 1.1 早期架構 (v1.0)
在初期構想中，Side Project 模組被設計為單一執行檔案（`recommendation.py`），直接將 Agent 性格與任務指令寫在 Prompt 中。這種做法雖能快速運作，但存在以下缺點：
- **維護困難**：Prompt 過長，且 Agent 性格與任務邏輯耦合嚴重。
- **擴充性低**：無法輕易讓其他 Agent 協作或複用同一 Agent。
- **邏輯不一致**：與後來開發的「履歷優化模組」採用了不同的設計標準。

### 1.2 標準化演進 (v2.0)
為了確保整個系統的 Multi-Agent 架構邏輯通順與統一，我們決定將 Side Project 模組的建構邏輯與 **Resume 模組完全對齊**。
- **標準化 Feature 架構**：拆分為 `agents.py`, `tasks.py`, `schemas.py`, `prompts.py`。
- **控制權解耦**：不再讓模組自行決定執行流程，而是透過 `prompts.py` 向 `core/agent_engine` 提供配置。

---

## 2. 功能說明 (Functional Specifications)

### 2.1 核心目標 (Mission)
本模組旨在根據「職涯缺口分析」的結果，為使用者量身打造具備「職場可解釋性」的實作專案。其產出的計畫書必須能直接轉化為履歷上的競爭優勢。

### 2.2 關鍵規則 (Execution Rules)
- **禁止玩具專案**：避開 To-do List 或氣象 App，專注於解決真實商業痛點（如 RAG 系統、工控嵌入式系統、高併發後端）。
- **階段化實踐**：專案必須拆解為 3–5 個階段，確保使用者能循序漸進。
- **履歷價值化 (Resume Value)**：每一階段的任務完成後，必須提供一段符合 STAR 原則、可直接填入履歷的專業敘述。

---

## 3. 檔案架構與職責分配

模組存放於 `src/features/projects/`：

| 檔案名稱 | 職責說明 |
| :--- | :--- |
| `schemas.py` | 定義 `SideProject` 與 `ProjectPhase` 的 Pydantic 模型。負責結構化輸出的校準。 |
| `agents.py` | 定義 **Project Architect** (設計者) 與 **Industry QA** (技術審核者) 的背景與目標。 |
| `tasks.py` | 定義具體的任務 Prompt。包含「專案設計任務」與「品質優化任務」。 |
| `prompts.py` | **模組對接窗口**。負責組合 Agent 與 Task，回傳系統配置給 Core Engine。 |
| `tools.py` | (預留) 用於串接資料庫或外部 API 的技術工具（如 FetchSkillGap）。 |

---

## 4. Multi-Agent 執行流程 (Workflow)

本模組採用 **Sequential Process (順序執行)**，共包含三層把關：

1.  **第一層：專案設計 (Project Architect)**
    - 分析 `skill_gap_result` 中的弱項。
    - 選定市場主流技術棧。
    - 規劃 MVP 起步的實作路徑。
2.  **第二層：技術優化 (Industry QA)**
    - 審核技術細節的合理性。
    - 修潤 `resume_value` 的專業術語。
    - 確保階段目標 (Goal) 具備職場說服力。
3.  **第三層：系統把關 (Core QA Lead)**
    - 由 `manager.py` 自動掛載，負責最後的 JSON 結構驗證與 Metadata 注入。

---

## 5. 核心引擎對接 (Core Integration)

為了讓 `manager.py` 能夠呼叫此模組，我們在 `src/core/agent_engine/config.py` 中進行了以下調整：

```python
# src/core/agent_engine/config.py

elif task_type == TaskType.PROJECT_REC:
    from src.features.projects.prompts import get_project_config
    return get_project_config(task_type, inputs)
```

這種設計模式確保了：
- **引擎保持純粹**：不需要知道模組內部的 Prompt 內容。
- **配置式擴充**：未來加入新模組時，只需在 `config.py` 註冊一條路由即可。

---

## 6. 測試與驗證

我們建立了 `test/test_project_recommendation.py` 作為整合測試入口。
- **測試方式**：模擬真實的缺口分析資料（Mock Data）。
- **驗證指標**：
    - 是否成功產出 3 個以上的 Phase。
    - 輸出的 JSON 是否包含所有的 Pydantic 欄位。
    - 技術棧是否精準命中 weaknesses。

---

**紀錄日期**: 2026-02-23
**架構版本**: v2.0 (Standardized Multi-Agent Flow)
