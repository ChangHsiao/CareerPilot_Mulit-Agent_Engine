# 職涯領航員：整合型專案資料夾設計規劃

本規劃結合了 `CAREER_AGENT_INTEGRATION_ARCH.md` 的核心引擎架構，以及 `專題crewai試做.ipynb` 與現有系統中的業務模組（課程匹配、職缺媒合等），旨在建立一個高內聚、低耦合的專業開發結構。

---

## 1. 專案整體資料夾結構

```text
AIPE02_01_CrewAI_Career/
├── src/
│   ├── core/                           # 【核心引擎層】
│   │   ├── agent_engine/
│   │   │   ├── __init__.py
│   │   │   ├── task_types.py           # 任務類型定義 (Enum)
│   │   │   ├── config.py               # 中央廚房配置 (食譜)
│   │   │   └── manager.py              # Crew 執行管理 (主廚與 QA)
│   │   └── database/                   # 資料庫底層封裝
│   │       ├── __init__.py
│   │       ├── supabase_client.py      # Supabase 連接與基礎操作
│   │       └── qdrant_client.py        # Qdrant 向量資料庫連接
│   │
│   ├── features/                       # 【業務特徵層】各功能獨立模組
│   │   ├── analysis/                   # 職涯與技術分析報告
│   │   │   ├── __init__.py
│   │   │   ├── schemas.py              # CareerReport, SkillAnalysis 模型
│   │   │   ├── tools.py                # 技術評估與算分工具
│   │   │   ├── calculator.py           # 六維能力向量計算邏輯
│   │   │   └── prompts.py              # 技術/心理/策略分析 Prompts
│   │   │
│   │   ├── resume/                     # 履歷診斷與優化
│   │   │   ├── __init__.py
│   │   │   ├── schemas.py              # ResumeAnalysis, ResumeOptimization 模型
│   │   │   ├── tools.py                # 履歷抓取與解析工具
│   │   │   └── prompts.py              # 診斷/優化/求職信 Prompts
│   │   │
│   │   ├── matching/                   # 職缺匹配與過濾
│   │   │   ├── __init__.py
│   │   │   ├── schemas.py              # JobMatch, JobItem 模型
│   │   │   ├── tools.py                # 職缺搜尋與推薦工具
│   │   │   ├── fetch_filter_jobs.py    # 職缺抓取與硬過濾邏輯
│   │   │   └── matcher.py              # 匹配分數計算邏輯
│   │   │
│   │   ├── course/                     # 課程推薦與路徑規劃
│   │   │   ├── __init__.py
│   │   │   ├── schemas.py              # CourseRecommendation 模型
│   │   │   ├── tools.py                # 課程檢索工具
│   │   │   └── course_matching.py      # 課程匹配算法
│   │   │
│   │   └── projects/                   # Side Project 推薦
│   │       ├── __init__.py
│   │       ├── schemas.py              # SideProject, ProjectPhase 模型
│   │       └── prompts.py              # 專案設計與規劃 Prompts
│   │
│   └── common/                         # 【通用輔助層】
│       ├── __init__.py
│       ├── utils.py                    # 時間格式化、JSON 修復等公用函式
│       └── constants.py                # 系統常數 (職位清單、標準職級)
│
├── index/                              # 索引建立與資料初始化腳本
│   ├── setup_qdrant_index.py           # 職缺向量索引初始化
│   └── setup_resume_index.py           # 履歷向量索引初始化
│
├── test/                               # 自動化測試與除錯腳本
│   ├── test_agent_flow.py              # 整合流程測試
│   ├── test_resume_critique.py         # 履歷診斷單元測試
│   └── ...
│
├── .env                                # 環境變數
├── README.md                           # 專案說明
├── requirements.txt                    # 依賴套件
└── CAREER_AGENT_INTEGRATION_ARCH.md    # 架構設計文件 (已存在)
```

---

## 2. 設計邏輯說明

### 2.1 模組化業務 (Features)
每個業務模組（如 `resume`, `matching`）都是自給自足的，包含其專屬的：
*   **Schemas**: 確保 Agent 輸出的資料結構正確。
*   **Tools**: 提供 Agent 執行任務所需的特殊能力（如算分、抓取資料）。
*   **Prompts**: 集中管理複雜的角色扮演與任務描述，方便後期微調。

### 2.2 中央廚房 (Core Engine)
*   **`task_types.py`**：統一管理系統支援的任務清單，例如 `RESUME_CRITIQUE`, `JOB_MATCHING`, `CAREER_REPORT`。
*   **`config.py`**：根據 `TaskType` 從 `features/` 各模組中挑選合適的「食材」（Tools, Prompts, Schemas）並組合成「食譜」。
*   **`manager.py`**：負責執行 CrewAI 流程。它不關心具體的業務邏輯，只負責將 Worker 的產出交給 QA Agent 進行最終的 Pydantic 校驗與格式化。

### 2.3 資料庫底層封裝 (Core Database)
將 Supabase 與 Qdrant 的操作從業務代碼中抽離，統一放在 `src/core/database/`。這樣當未來需要更換資料庫或調整連接方式時，只需修改此處。

---

## 3. 保留與遷移路徑

1.  **原 `src/report/`**：遷移至 `src/features/analysis/`。
2.  **原 `src/features/matching/`**：遷移並整合至 `src/features/matching/`。
3.  **原 `src/course/`**：遷移至 `src/features/course/`。
4.  **原 `src/Multi_Agent/`**：其核心邏輯已演化為 `src/core/agent_engine/`。
5.  **原 `src/job_matching/`**：整合進 `src/features/matching/` 工具層。

---

## 4. 預期效益
*   **代碼複用**：QA Agent 與 Manager 邏輯只需寫一次，所有功能共用。
*   **維護容易**：想要修改課程推薦的邏輯？只需看 `src/features/course/`。
*   **穩定性高**：QA Agent 強制執行 Pydantic 轉換，解決了開發中常見的 JSON 解析錯誤。
