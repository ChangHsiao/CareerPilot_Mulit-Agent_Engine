# 職缺匹配與推薦模組建構計畫 (Job Matching Module Plan) - Final Version

本模組為「職涯領航員」的核心功能，採用「高效檢索、混合算分、AI 深度洞察」三位一體的設計結構。

---

## 1. 運行邏輯：高效三階段流程

### 階段一：Qdrant 混合召回 (Hybrid Recall)
- **職責**：執行「語意搜尋」與「硬篩選」。
- **邏輯**：
    - **向量比對**：計算使用者履歷與職缺描述的相似度 (佔總分 30%)。
    - **硬條件過濾**：
        - **地區 (City)**：精確匹配。
        - **薪資 (Salary)**：職缺上限需符合使用者下限 (`salary_max >= user_salary_min`)。
- **產出**：Top 50 候選職缺 ID 與初步語意分數。

### 階段二：精確重排序 (Mathematical Re-ranking)
- **職責**：執行「六維能力契合度」精算。
- **邏輯**：
    1. **批量補全**：向 Supabase 一次性讀取 50 筆職缺的完整資訊與 D1-D6 分數。
    2. **幾何距離 (70%)**：計算使用者六維能力向量與職缺要求向量的歐幾里得距離。
    3. **權重加總**：`Final = (0.7 * 6D契合度) + (0.3 * 語意相似度)`。
- **產出**：排序後的 Top 10 職缺清單。

### 階段三：AI 顧問與平行處理 (AI Analysis)
- **職責**：產出文字報告並優化效能。
- **邏輯**：
    - **平行運算**：啟動 `Threadpool` 同時對 Top 10 職缺進行 LLM 分析。
    - **內容產出**：由 AI 顧問產出推薦理由、強項、短版、面試技巧。
    - **資料清理**：自動清理 Requirements 換行符號，產出美觀的「|」分隔字串。

---

## 2. 檔案結構與對接規範 (src/features/matching/)

- `qdrant_retriever.py`：負責 `JobMatchRetriever` 與 `UserProfileRetriever`。
- `matcher.py`：(原 calculator.py) 負責 `JobMatcher` 數學邏輯。
- `service.py`：(原 job_matching_service.py) 負責 `CareerMatchingService` 核心流程。
- `advisor.py`：(原 llm_advisor.py) 負責 `CareerLLMAdvisor` 的分析與 Prompt 管理。

---

## 3. 系統優勢與設計考量

1.  **N+1 解決方案**：採用 SQL `IN` 查詢，大幅減少資料庫往返次數。
2.  **效能最佳化**：利用 Python 多執行緒技術，解決了串列呼叫 LLM 導致前端轉圈圈過久的問題。
3.  **資料防呆**：包含 `try-except` 與欄位清理（Requirements 清理），確保回傳前端的 JSON 格式完美一致。
4.  **解耦 Multi-Agent**：維持 Service 模式，但在未來需要 Agent 主動推薦時，可直接透過 API 呼叫此 Service。
