# 求職信推薦生成模組建構計畫 (Cover Letter Module Plan)

本模組旨在透過資深獵頭視角的 AI 代理人，根據使用者優化後的履歷與目標職缺資訊，生成具備高說服力的求職信 (Cover Letter)。本計畫遵循系統統一的「高內聚、低耦合」標準架構。

---

## 1. 運作原理 (Workflow)

本模組採用 **「資料驅動 + 雙層把關」** 的運作邏輯：

1.  **資料獲取 (Tool Interaction)**: 
    - 系統接收 `job_id`，透過內建工具從資料庫抓取該職缺的詳細描述 (JD) 與需求 (Requirements)。
2.  **核心撰寫 (Worker Stage)**:
    - **Agent**: `CoverLetterStrategist` (資深獵頭)。
    - **邏輯**: 比對 `optimize_resume` 與 `JD` 的核心痛點，提取 2-3 個「關鍵成就對標」，避免空泛的形容詞。
3.  **品質保證 (QA Stage)**:
    - **Agent**: `Core QA Lead` (由系統引擎自動載入)。
    - **邏輯**: 確保語氣符合該公司文化（新創 vs. 外商），檢查格式是否符合 Pydantic 模型。

---

## 2. 介面定義 (API Specification)

### 2.1 輸入參數 (Inputs)
```python
user_input = {
    "optimize_resume": { ... }, # 優化後的履歷 JSON
    "job_id": 46                # 目標職缺 ID
}
```

### 2.2 輸出結構 (Outputs - CoverLetter Schema)
- `subject`: 包含職位名稱與核心賣點的專業主旨。
- `content`: 完整求職信文字內容。

---

## 3. 檔案架構配置 (Standardized Architecture)

模組路徑：`src/features/cover_letter/`

| 檔案名稱 | 功能說明 |
| :--- | :--- |
| `schemas.py` | 定義 `CoverLetter` Pydantic 模型。 |
| `agents.py` | 定義 `CoverLetterStrategist`。包含其招募心理學的性格設定 (Backstory)。 |
| `tasks.py` | 定義 `write_cover_letter_task`。指令包含：職位理解、價值主張、STAR 實績、行動呼籲。 |
| `tools.py` | 實作 `SearchRecommendJobTool`。用於根據 `job_id` 到 Supabase 抓取職缺資料。 |
| `prompts.py` | **模組分發窗口**。實作 `get_cover_letter_config` 函式，整合 Agent、Task 與 Tool。 |

---

## 4. 整合與路由計畫 (Integration)

為了讓模組順利運行，必須在 `src/core/agent_engine/` 中進行以下註冊：

1.  **TaskType 註冊**: 確認 `task_types.py` 已包含 `COVER_LETTER = "cover_letter"`。
2.  **路由註冊**: 在 `config.py` 中新增分支：
    ```python
    elif task_type == TaskType.COVER_LETTER:
        from src.features.cover_letter.prompts import get_cover_letter_config
        return get_cover_letter_config(task_type, inputs)
    ```

---

## 5. 實作檢查清單 (Checklist)

1.  [ ] **建立 Feature 資料夾**: `mkdir -p src/features/cover_letter`。
2.  [ ] **實作 Schema**: 定義輸出模型。
3.  [ ] **開發工具**: 建立可連接資料庫的職缺查詢工具。
4.  [ ] **配置 Agent & Task**: 遷移 Notebook 中的資深獵頭提示詞。
5.  [ ] **對接測試**: 使用 Mock 履歷數據與真實 `job_id` 進行端到端測試。

---
**核准日期**: 2026-02-23
**架構版本**: v2.0 (Standardized Multi-Agent Flow)
