from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from .task_types import TaskType

class BaseResultHandler(ABC):
    """所有 Agent 結果處理器的基底類別"""
    def __init__(self, supabase_client):
        self.supabase = supabase_client

    @abstractmethod
    def process(self, pydantic_result: Any, **kwargs) -> Any:
        """
        處理並儲存結果的抽象方法
        :param pydantic_result: CrewAI 產出的 Pydantic 模型或 Dict
        :param kwargs: 包含 user_id, survey_id 等 metadata
        """
        pass

class GapAnalysisHandler(BaseResultHandler):
    """
    職涯缺口分析報告 (Gap Analysis) 儲存處理器
    對應資料表: career_analysis_report
    """
    def process(self, pydantic_result: Any, **kwargs) -> Any:
        # 1. 確保格式為字典 (相容 Pydantic v1/v2)
        if hasattr(pydantic_result, "model_dump"):
            data = pydantic_result.model_dump()
        elif hasattr(pydantic_result, "dict"):
            data = pydantic_result.dict()
        else:
            data = pydantic_result

        # 2. 身份識別：優先從 kwargs 拿，若無則從 metadata 提取
        user_id = kwargs.get("user_id") or data.get("report_metadata", {}).get("user_id")
        
        # 3. 欄位精準映射 (Mapping)
        # 根據資料表結構，將巢狀的 Pydantic 數據扁平化或存入 JSONB 欄位
        payload = {
            "user_id": user_id,
            "report_version": data.get("report_metadata", {}).get("version", "1.0"),
            "generated_at": data.get("report_metadata", {}).get("timestamp"),
            "target_position": data.get("gap_analysis", {}).get("target_position", {}).get("role"),
            
            # JSONB 區塊
            "preliminary_summary": data.get("preliminary_summary"),
            "radar_chart": data.get("radar_chart"),
            "gap_analysis": data.get("gap_analysis"),
            "action_plan": data.get("action_plan"),
            
            # 關聯鍵
            # "survey_id": kwargs.get("survey_id"),
            "resume_id": kwargs.get("resume_id")
        }

        # 4. 資料清洗：剔除 None 值
        payload = {k: v for k, v in payload.items() if v is not None}

        # 5. 執行寫入
        try:
            return self.supabase.table("career_analysis_report").insert(payload).execute()
        except Exception as e:
            print(f"❌ [GapAnalysisHandler] 寫入資料庫失敗: {e}")
            raise

class HandlerRegistry:
    """任務類型與處理器的註冊對照表"""
    def __init__(self, supabase_client):
        self._handlers = {
            # 這裡註冊不同 TaskType 對應的 Handler
            TaskType.CAREER_ANALYSIS_EXPERIENCED: GapAnalysisHandler(supabase_client),
            TaskType.CAREER_ANALYSIS_ENTRY_LEVEL: GapAnalysisHandler(supabase_client),
            # 未來可在這裡擴充其他模組的 Handler
        }

    def get_handler(self, task_type: TaskType) -> Optional[BaseResultHandler]:
        return self._handlers.get(task_type)
