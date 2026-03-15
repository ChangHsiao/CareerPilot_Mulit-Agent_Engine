# 🤖 AI Career Platform — 智慧職涯規劃平台

> **畢業專題 | AIPE02-01**  
> 以大型語言模型 (LLM) 與多智能體 (Multi-Agent) 框架為核心，打造一站式、個人化的 AI 職涯輔助系統。

---

## 📌 專案簡介

本專案是一套以 **CrewAI + OpenAI GPT-4o** 驅動的多智能體職涯平台。  
系統能依據使用者填寫的職涯問卷、上傳的履歷，自動化地執行以下工作：

- 📊 六維能力評估與職涯分析報告生成  
- 📝 履歷診斷與 AI 優化  
- 🔍 智慧職缺媒合（語意向量 + 六維能力混合計分）  
- 💌 客製化求職信生成  
- 📚 個人化課程學習路徑規劃  
- 💡 Side Project 推薦

---

## 🏗️ 系統架構

### 分層設計（Domain-Driven Design）

```
src/
├── core/                          # 核心基礎設施層
│   ├── agent_engine/              # Multi-Agent 執行引擎
│   │   ├── manager.py             # CareerAgentManager (Facade Pattern)
│   │   ├── config.py              # 配置分發器 (Configuration Dispatcher)
│   │   ├── task_types.py          # TaskType 枚舉定義
│   │   └── result_handlers.py     # 結果處理與資料庫回存
│   └── database/
│       └── supabase_client.py     # Supabase 連線管理
│
├── features/                      # 功能領域層 (Bounded Contexts)
│   ├── analysis/                  # 領域：職涯分析
│   │   ├── agents.py              # Agent 角色定義
│   │   ├── tasks.py               # Task 任務設計
│   │   ├── prompts.py             # Prompt 工程
│   │   ├── schemas.py             # Pydantic 輸出結構定義
│   │   ├── calculator.py          # 六維分數計算引擎
│   │   └── tools.py               # CrewAI 工具
│   ├── matching/                  # 領域：職缺媒合
│   │   ├── service.py             # CareerMatchingService
│   │   ├── matcher.py             # 六維差距精算
│   │   ├── qdrant_retriever.py    # 向量資料庫檢索
│   │   └── advisor.py             # LLM AI 顧問分析
│   ├── resume/                    # 領域：履歷優化
│   ├── cover_letter/              # 領域：求職信生成
│   ├── course/                    # 領域：課程推薦
│   └── projects/                  # 領域：Side Project 推薦
│
└── common/                        # 通用工具層
    ├── logger.py
    ├── constants.py
    └── utils.py
```

### Multi-Agent 管線（Agent Pipeline）

系統採用 **Facade Pattern** 統一入口，依 `TaskType` 動態組裝 Agent 陣列，並以 QA Agent 進行最終輸出驗證：

```
使用者請求
    │
    ▼
CareerAgentManager.run_task()
    │
    ├─ 自動分流 (Auto-Dispatch)
    │     ├─ career_analysis_experienced  → [Tech Lead → Psychologist → Career Advisor → QA]
    │     └─ career_analysis_entry_level  → [Discovery Mentor → Psychologist → Career Advisor → QA]
    │
    ├─ Worker Agents (專業執行)
    │     ├─ 資深技術評估專家 (Tech Lead)
    │     ├─ 認知心理學家 (Psychologist)
    │     ├─ 職涯策略顧問 (Career Advisor)
    │     └─ 轉職潛力挖掘導師 (Discovery Mentor)
    │
    └─ QA Agent (品質把關)
          └─ 格式驗證 → Pydantic 結構化輸出 → 自動回存 Supabase
```

### 職缺媒合三階段流程

```
Phase 0   │ 載入使用者六維能力分數 (from Supabase)
Phase 0.5 │ 擷取履歷文字摘要 (RAG Context)
Phase 1   │ Qdrant 語意向量混合召回 (Top 50)
Phase 2   │ 六維差距精算重排序 (Re-ranking → Top 10)
           │   final_score = 0.7 × score_6d + 0.3 × score_text
Phase 3   │ 10 執行緒平行 AI 分析 + JSON 格式化輸出
```

---

## 🛠️ 技術棧

| 類別 | 技術 |
|------|------|
| **LLM 框架** | CrewAI, LangChain |
| **語言模型** | OpenAI GPT-4o |
| **關聯式資料庫** | Supabase (PostgreSQL) |
| **向量資料庫** | Qdrant |
| **資料驗證** | Pydantic v2 |
| **數值計算** | NumPy, FAISS |
| **資料處理** | Pandas |
| **環境管理** | python-dotenv |
| **程式語言** | Python 3.10+ |

---

## ⚙️ 環境設定

### 1. 複製專案並建立虛擬環境

```bash
git clone https://github.com/<your-username>/AIPE02_01_Project_re.git
cd AIPE02_01_Project_re

python -m venv Career_venv
# Windows
Career_venv\Scripts\activate
# macOS / Linux
source Career_venv/bin/activate
```

### 2. 安裝相依套件

```bash
pip install -r requirements.txt
```

### 3. 設定環境變數

複製範例檔並填入您的 API 金鑰：

```bash
cp .env.example .env
```

編輯 `.env`：

```env
# OpenAI
OPENAI_API_KEY="sk-..."

# Supabase
SUPABASE_URL="https://your-project-ref.supabase.co"
SUPABASE_KEY="your_anon_key"
SUPABASE_SERVICE_ROLE_KEY="your_service_role_key"

# Qdrant
QDRANT_URL="your_qdrant_url"
QDRANT_API_KEY="your_qdrant_api_key"
QDRANT_JOB_COLLECTION_NAME="job_vectors"
QDRANT_RESUMES_COLLECTION_NAME="resume_vectors"
QDRANT_RESUMES_OPTIMIZATION_COLLECTION_NAME="optimized_resume_vectors"
```

---

## 🚀 使用方式

### 執行職涯分析

```python
from src.core.agent_engine.manager import CareerAgentManager

manager = CareerAgentManager(model_name="gpt-4o", temp=0.5)

result = manager.run_task(
    task_type_str="career_analysis",
    user_input={
        "user_id": "user_123",
        "survey_json": '{"module_a": {"q1_languages": [{"name": "Python", "score": 4}]}}',
        "resume_json": '{"experience": "3 years backend development..."}'
    }
)

print(result)
```

### 執行職缺媒合

```python
from src.features.matching.service import CareerMatchingService

service = CareerMatchingService(
    qdrant_client=qdrant_client,
    supabase_client=supabase_client,
    openai_api_key="sk-..."
)

jobs = service.find_best_jobs(
    user_id=123,
    document_id=456,
    source_type="RESUME",   # 或 "OPTIMIZATION"
    filters={"location": "台北"}
)
```

---

## 🤖 AI Agents 一覽

| Agent | 領域 | 職責 |
|-------|------|------|
| **Tech Lead** (資深技術評估專家) | Analysis | 計算 D1–D6 六維技術分數、履歷真實性驗證 |
| **Psychologist** (認知心理學家) | Analysis | 分析使用者認知特質、預測開發場景適配度 |
| **Career Advisor** (職涯策略顧問) | Analysis | 整合技術 + 心理分析，產出 SWOT 職涯報告 |
| **Discovery Mentor** (轉職潛力挖掘導師) | Analysis | 協助轉職者將舊經驗橋接至軟體工程潛力 |
| **Analysis Consultant** (資深招募顧問) | Resume | 履歷深度診斷，指出問題與改進點 |
| **Optimization Consultant** (履歷策略顧問) | Resume | 依業界標準重寫並優化履歷內容 |
| **Career LLM Advisor** (職涯 AI 顧問) | Matching | 生成每筆職缺的個人化匹配原因與面試建議 |
| **Career Strategist** (職涯發展戰略家) | Course | 規劃個人化學習路徑 |
| **Learning Designer** (教學系統設計專家) | Course | 設計課程結構與里程碑 |
| **Project Architect** (職涯專案架構師) | Projects | 推薦最具職涯價值的 Side Project |
| **Industry QA** (產業技術監控官) | Projects | 驗證專案推薦的市場對齊度 |
| **Cover Letter Strategist** (求職信專家) | Cover Letter | 生成針對特定職缺的個人化求職信 |
| **QA Lead** (品質與格式監控官) | Core | 跨所有模組的最終輸出驗證與格式化 |

---

## 📊 六維能力模型（6-Dimension Profile）

系統透過問卷與履歷分析，為每位使用者建立個人化的六維能力雷達圖：

| 維度 | 代碼 | 說明 |
|------|------|------|
| 前端開發 | D1 | HTML/CSS/JS、框架熟悉度 |
| 後端開發 | D2 | API 設計、資料庫、系統架構 |
| 運維部署 | D3 | CI/CD、Cloud、容器化 |
| AI 與數據 | D4 | 機器學習、資料分析、LLM |
| 工程品質 | D5 | 測試、程式碼品質、文件 |
| 軟實力   | D6 | 溝通、協作、問題解決 |

---

## 📁 其他目錄說明

| 目錄 | 說明 |
|------|------|
| `index/` | 向量索引相關資源 |
| `logs/` | 系統執行日誌 |
| `test/` | 測試腳本 |

---

## 🔒 安全性注意事項

- **請勿將 `.env` 檔案提交至版本控制系統**（已在 `.gitignore` 中排除）
- API 金鑰請使用環境變數管理，切勿寫死在程式碼中
- Supabase 的 `SERVICE_ROLE_KEY` 擁有完整存取權限，請妥善保管

---

## 📄 授權

本專案為學術用途之畢業專題，未設定開放授權。如需引用或使用，請先聯繫作者。

---

<div align="center">

**Built with ❤️ using CrewAI × GPT-4o × Supabase × Qdrant**

</div>
