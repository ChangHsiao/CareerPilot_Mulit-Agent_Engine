# Side Project 推薦模組建構計畫 (Project Recommendation Plan)

本計畫旨在透過 Multi-Agent 協作，為使用者生成具備「職涯銜接價值」的專案計畫。本模組遵循系統統一的「高內聚、低耦合」架構，與履歷分析模組（Resume Module）採用相同的邏輯設計。

## 1. 核心任務定義 (PROJECT_REC)

### 1.1 任務目標
- **缺口補齊**：根據職涯分析（Career Analysis）中產出的 `weaknesses`，設計精準的實作專案。
- **履歷價值化**：每個實作階段（Phase）都必須提供對應的「履歷描述建議」，確保專案具備職場說服力。
- **難度分級**：根據使用者的現有實力（strengths），調整專案的複雜度與技術棧。

### 1.2 關鍵規則
- **商務邏輯導向**：禁止生成「玩具專案」（如簡易計數器），優先考慮 RAG、微服務或真實數據處理場景。
- **階段化實踐**：專案必須包含 3-5 個具備明確里程碑（Milestones）的階段。
- **技術棧一致性**：建議的技術必須符合目前目標市場的主流需求。

---

## 2. 檔案資料夾結構與功能分配 (Standardized Feature Architecture)

為確保擴充性與可維護性，本模組捨棄單一檔案設計，採用與 `resume` 模組一致的拆分架構。

### `src/features/projects/` (功能核心)
- **`schemas.py`** (結構定義)
    - 定義 `SideProject` 與 `ProjectPhase` 的 Pydantic 模型，確保輸出 JSON 的穩定性。
- **`agents.py`** (Agent 定義)
    - `ProjectArchitect`: 職涯專案架構師。負責分析技能缺口並設計技術方案。
    - `IndustryQA`: 產業專家 Agent。負責審核專案計畫的商業價值與技術可行性。
- **`tasks.py`** (Task 定義)
    - `project_design_task`: 定義專案設計的具體 prompt、輸入變數與預期結構。
- **`tools.py`** (工具功能)
    - `FetchSkillGapTool`: 用於抓取前序步驟（Career Analysis）產出的分析結果。
- **`prompts.py`** (配置分發器)
    - **`get_project_config` 函式**：這是與核心引擎對接的唯一窗口。它負責將上述 Agent 與 Task 實例化，並回傳配置 Dict。

### `src/core/agent_engine/` (通用引擎對接)
- **`config.py`**: 新增 `TaskType.PROJECT_REC` 分支，動態路由至 `src.features.projects.prompts.get_project_config`。
- **`manager.py`**: 無須變動。透過 `get_config_by_type` 取得配置後，自動執行 Crew 流程。

---

## 3. Multi-Agent 流程設計 (Standardized Flow)

本模組採用 **Sequential Process (順序執行)**：

1.  **階段一：專案設計 (Design Stage)**
    - **執行者**：`ProjectArchitect`
    - **輸出**：初步的專案藍圖（包含技術棧、實作路徑）。
2.  **階段二：品質優化 (QA & Refinement Stage)**
    - **執行者**：`IndustryQA` (參考階段一的輸出)
    - **目標**：確保 Phase 中包含具體的 Resume Value 描述，並校正難度。
    - **輸出**：結構化的 `SideProject` Pydantic 物件。

---

## 4. 實作檢查清單 (Implementation Checklist)

1.  [ ] **Schema 遷移**：在 `projects/schemas.py` 中定義輸出模型。
2.  [ ] **Agent/Task 定義**：將 Notebook 中的提示詞遷移至 `agents.py` 與 `tasks.py`。
3.  [ ] **配置註冊**：在 `src/core/agent_engine/config.py` 中新增 `PROJECT_REC` 路由。
4.  [ ] **對接測試**：確保 `manager.py` 能成功呼叫 `PROJECT_REC` 並獲得結構化回應。

---
**核准日期**: 2026-02-23
**架構版本**: v2.0 (Standardized Architecture)
