# tools.py
import json
import ast
import re
from typing import Any, Union, Dict
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

from src.features.analysis.calculator import CareerAnalyzer
from src.features.matching.matcher import JobMatcher
from src.core.database.supabase_client import get_latest_resume
from src.common.logger import setup_logger

logger = setup_logger()

def safe_parse_json(input_data: Union[str, Dict, Any]) -> Dict:
    """Safely parse input string or dict into dict"""
    if isinstance(input_data, dict):
        return input_data
    if not isinstance(input_data, str):
        return {}
        
    clean_str = input_data.strip().replace("```json", "").replace("```", "").strip()
    try:
        # 1. 嘗試標準 JSON
        return json.loads(clean_str)
    except Exception:
        try:
            # 2. 嘗試 Python literal_eval (處理單引號的情況)
            return ast.literal_eval(clean_str)
        except Exception:
            return {}

# 1. Fetch Resume Tool
class FetchResumeInput(BaseModel):
    user_id: str = Field(description="目標使用者的唯一識別碼，必須為純文字字串")

class FetchResumeFromDBTool(BaseTool):
    name: str = "Fetch Resume From Database"
    description: str = "根據 user_id 從資料庫中獲取該使用者最新的履歷內容 (JSON 格式字串)。"
    args_schema: type[BaseModel] = FetchResumeInput
    
    def _run(self, user_id: str) -> str:
        try:
            # 確保提取出乾淨的字串 ID
            clean_id = str(user_id).strip().strip("'").strip('"')
            logger.info(f"開始從資料庫獲取履歷 (user_id: {clean_id})")
            return str(get_latest_resume(clean_id))
        except Exception as e:
            logger.error(f"從資料庫獲取履歷發生錯誤: {str(e)}", exc_info=True)
            return (
                f"SYSTEM ERROR: FetchResumeFromDBTool 發生致命錯誤 ({str(e)})。\n"
                "【最高指令 - 防幻覺守則】：\n"
                "1. 由於無法取得真實履歷，你絕對不可瞎編或猜測履歷內容。\n"
                "2. 請立即在最終報告中向使用者說明：『⚠️ 系統維護中，無法獲取您的履歷資料，履歷驗證分析暫停。』\n"
                "3. 停止針對履歷部分的任何分析。"
            )

# 2. Calculate Technical Vectors Tool
class CalculateTechVectorsInput(BaseModel):
    user_id: str = Field(description="使用者的 ID")

class CalculateTechVectorsTool(BaseTool):
    name: str = "Calculate Technical Vectors"
    description: str = "計算 D1-D6 六維能力分數。"
    args_schema: type[BaseModel] = CalculateTechVectorsInput
    
    # [額外屬性] 預先注入的資料字串，LLM 不需提供
    survey_json_str: str = Field(default="")
    
    def _run(self, user_id: str) -> str:
        logger.info(f"開始計算技術分數向量 (user_id: {user_id})")
        default_scores = {"D1": 0.5, "D2": 0.5, "D3": 0.5, "D4": 0.5, "D5": 1.0, "D6": 1.0}
        try:
            user_data_raw = safe_parse_json(self.survey_json_str)
            if not user_data_raw:
                return str(default_scores)

            # 若資料包在 questionnaire_response 裡 (例如直接從 DB 得到的格式)
            user_data = user_data_raw.get("questionnaire_response", user_data_raw)

            ma = user_data.get("module_a", {})
            if not ma or not ma.get("q1_languages"):
                return str(default_scores)

            # 正常計算流程
            if CareerAnalyzer:
                analyzer = CareerAnalyzer(user_data)
                analyzer.calculate_vectors()
                return str(analyzer.scores) 
            else:
                return str(default_scores)
        except Exception as e:
            logger.error(f"計算技術分數向量發生錯誤: {str(e)}", exc_info=True)
            return (
                f"SYSTEM ERROR: CalculateTechVectorsTool 發生致命錯誤 ({str(e)})。\n"
                "【最高指令 - 防幻覺守則】：\n"
                "你現在沒有六維分數可以參考。請立即終止分析並向使用者回報：『⚠️ 技術分數計算引擎暫時發生異常，無法產出能力雷達圖，請稍後重試。』"
            )

# 3. Calculate match score tool
class CalculateMatchScoreInput(BaseModel):
    vectors_str: str = Field(description="使用者能力向量 (D1-D6) 的 JSON 字串")
    target_role: str = Field(description="目標職位名稱")

class CalculateMatchScoreTool(BaseTool):
    name: str = "Calculate Job Match Score"
    description: str = "計算使用者能力向量與目標職位的匹配分數 (0-100)。"
    args_schema: type[BaseModel] = CalculateMatchScoreInput
    
    def _run(self, vectors_str: str, target_role: str) -> str:
        logger.info(f"開始計算目標職位匹配分數 (target_role: {target_role})")
        try:
            vectors = safe_parse_json(vectors_str)
            if not vectors:
                vectors = {"D1": 0.5, "D2": 0.5, "D3": 0.5, "D4": 0.5, "D5": 1.0, "D6": 1.0}
            
            score = JobMatcher.calculate_match_score(vectors, target_role)
            return str(score)
        except Exception as e:
            logger.error(f"計算目標職位匹配分數發生錯誤: {str(e)}", exc_info=True)
            return (
                f"SYSTEM ERROR: CalculateMatchScoreTool 發生致命錯誤 ({str(e)})。\n"
                "【最高指令 - 防幻覺守則】：\n"
                "由於計算引擎錯誤，你無法得知雙方匹配度分數。請不要編造分數，並向使用者回報：『⚠️ 匹配度計算異常，本篇報告將跳過契合度數值驗證。』"
            )
