# 分析報告模組結構對齊計畫 (Analysis Module Structure Alignment Plan)

本計畫旨在將 `src/features/analysis` 模組的檔案結構與專案中其他成熟模組（如 `resume`, `cover_letter`）對齊。這將提升代碼的一致性、可讀性，並方便未來的單元測試與功能擴充。

---

## 1. 現狀分析與差異對比

目前 `analysis` 模組雖然功能完整，但在 CrewAI 物件（Agents, Tasks）的定義上過度依賴 `prompts.py` 中的字典配置，缺乏像其他模組一樣的獨立定義文件。

### 1.1 結構對比表

| 檔案名稱 | `analysis` (現狀) | 其他標準模組 (如 `resume`) | 說明 |
| :--- | :---: | :---: | :--- |
| `agents.py` | ❌ 缺失 | ✅ 存在 | 負責定義 `create_agent` 函數 |
| `tasks.py` | ❌ 缺失 | ✅ 存在 | 負責定義 `create_task` 函數 |
| `prompts.py` | ✅ 存在 | ✅ 存在 | `analysis` 內包含過多配置邏輯，標準應僅存提示詞 |
| `schemas.py` | ✅ 存在 | ✅ 存在 | 定義 Pydantic 輸出模型 (一致) |
| `tools.py` | ✅ 存在 | ✅ 存在 | 定義工具類別 (一致) |
| `calculator.py` | ✅ 存在 | ❌ 不適用 | 存儲核心算分邏輯 (領域特定) |

---

## 2. 結構更新目標

在**不更改任何現有分數運算與輸出結構**的前提下，進行以下調整：

1.  **解耦配置與提示詞**：將 `prompts.py` 中的原始提示詞字串提取為獨立常數。
2.  **標準化物件定義**：新增 `agents.py` 與 `tasks.py`，封裝 CrewAI 物件的建立邏輯。
3.  **保持相容性**：確保 `get_analysis_config` 仍然有效，以維持與 `CareerAgentManager` 的對接。

---

## 3. 具體更新路徑

### 3.1 檔案新增計畫

#### `src/features/analysis/agents.py` (新增)
- 實作 `create_tech_lead_agent(llm)`
- 實作 `create_psychologist_agent(llm)`
- 實作 `create_career_advisor_agent(llm)`
- 實作 `create_discovery_mentor_agent(llm)`

#### `src/features/analysis/tasks.py` (新增)
- 實作 `create_tech_verification_task(agent, inputs)`
- 實作 `create_trait_analysis_task(agent, inputs)`
- 實作 `create_final_report_task(agent, inputs, context)`
- 實作 `create_discovery_mentor_task(agent, inputs)`

### 3.2 檔案重構計畫

#### `src/features/analysis/prompts.py` (重構)
- 將 `get_analysis_config` 中的角色、目標、背景故事、任務描述提取為頂層常數 (如 `TECH_LEAD_ROLE`, `TECH_LEAD_BACKSTORY`)。
- `get_analysis_config` 內部將引用這些常數，減少字典中的硬編碼內容。

#### `src/features/analysis/calculator.py` (保留)
- **絕對不修改任何邏輯**。
- 此檔案將繼續作為 `tools.py` 的底層支撐。

---

## 4. 預期效益

1.  **開發體驗一致性**：開發者在不同模組間切換時，能快速定位 Agent 與 Task 的定義。
2.  **測試友善**：可以針對單一 Agent 或 Task 進行單元測試，而不需要透過複雜的 `manager.py` 配置。
3.  **邏輯清晰**：`prompts.py` 回歸純粹的內容管理，不再混雜過多的組裝邏輯。

---

## 5. 執行驗證

更新完成後，將執行 `test/test_agent_flow.py` 中的 `test_experienced_analysis()`，確保：
1.  報告輸出結構（JSON）與更新前完全一致。
2.  D1-D6 分數計算正確性未受影響。
3.  AI 的分析語氣與深度維持水準。
