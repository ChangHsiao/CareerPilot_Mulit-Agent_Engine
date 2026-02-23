# 求職推薦信生成模組：建構紀錄與功能說明手冊

本文件詳盡紀錄了「求職推薦信生成模組 (Cover Letter Module)」的設計理念、技術架構與建構流程。本模組完全遵循系統統一的「標準化 Multi-Agent」開發規範。

---

## 1. 模組設計哲學

### 1.1 從「罐頭訊息」轉向「對標價值」
傳統 AI 生成的求職信往往充斥著「我很努力」、「我非常有興趣」等空泛詞彙。本模組的設計核心在於**「精準對標」**：
- **獵頭視角**：模擬資深獵頭，優先找出職缺描述 (JD) 中的痛點。
- **證據驅動**：從優化後的履歷中提取具備數據或實績的 STAR 案例進行回擊。
- **文化適配**：根據目標公司類型（新創 vs. 大型外商）自動切換溝通語調。

---

## 2. 檔案架構與職責 (Feature Architecture)

模組存放於 `src/features/cover_letter/`：

| 檔案名稱 | 職責與關鍵技術 |
| :--- | :--- |
| `schemas.py` | 定義 `CoverLetter` 模型。包含 `subject` (高點擊率主旨) 與 `content` (正文)。 |
| `tools.py` | 實作 `SearchRecommendJobTool`。透過 `job_id` 從 Supabase 抓取職務需求 (JD)。 |
| `agents.py` | 定義 **Cover Letter Strategist**。設定其具備招募心理學與外商獵頭背景。 |
| `tasks.py` | 實作 `get_cover_letter_task`。定義了：職位理解、價值主張、行動呼籲三大撰寫支柱。 |
| `prompts.py` | **模組對接窗口**。整合 Agent、Task 與 Tool，提供配置給核心引擎調度。 |

---

## 3. 建構流程紀錄 (Construction Log)

1.  **結構化定義 (2026-02-23)**：
    - 根據 `初版.ipynb` 提取 Pydantic 模型，確保主旨與內容能被前端穩定渲染。
2.  **工具開發與測試**：
    - 實作資料庫查詢工具，解決了 Python 鏈式呼叫在換行縮進時的 `IndentationError`。
    - 採用括號 `()` 包裹方式優化了 `supabase-py` 的呼叫語法。
3.  **Agent 性格建模**：
    - 導入「資深外商獵頭」背景，強調「不使用空泛形容詞」的嚴格準則。
4.  **系統引擎註冊**：
    - 在 `src/core/agent_engine/config.py` 中新增 `TaskType.COVER_LETTER` 路由。
    - 實現了「控制權反轉」，由 `manager.py` 統一發送任務指令。

---

## 4. 運作原理與 API 規範

### 4.1 輸入參數 (Inputs)
- `optimize_resume`: 經過優化後的結構化履歷內容。
- `job_id`: 目標職缺在系統中的編號。

### 4.2 執行路徑
1.  **Tool Call**：Agent 首先呼叫 `SearchRecommendJob` 獲取該 `job_id` 的 JD。
2.  **Analysis**：比對履歷技能與 JD 需求。
3.  **Drafting**：按照獵頭邏輯撰寫主旨與三段式內容。
4.  **QA Validation**：由系統通用 QA Agent 進行最終結構化輸出。

---

## 5. 測試驗證方式

### 5.1 自動化測試
執行以下指令可運行針對該模組的整合測試：
```bash
python -m test.test_cover_letter
```

### 5.2 測試重點
- **結構完整性**：輸出必須包含 `subject` 與 `content`。
- **內容準確性**：信中提到的技術棧必須與 `optimize_resume` 內容相符，嚴禁捏造。
- **工具聯動**：確保能正確識別 `job_id` 並抓取對應的職位資訊。

---

**紀錄日期**: 2026-02-23
**架構版本**: v2.0 (Standardized Multi-Agent Flow)
