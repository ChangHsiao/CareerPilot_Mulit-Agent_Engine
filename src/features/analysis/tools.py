# tools.py
import json
import ast
import re
from crewai.tools import tool
# 假設這是你的原始模組
from src.features.analysis.calculator import CareerAnalyzer
from src.features.matching.matcher import JobMatcher
from src.core.database.supabase_client import get_latest_resume

def parse_input_to_dict(input_str: str):
    """
    輔助函式：將輸入字串解析為 dict。
    支援標準 JSON (雙引號) 與 Python Literal (單引號)。
    """
    if isinstance(input_str, dict):
        return input_str
        
    if not isinstance(input_str, str):
        return input_str

    # 移除字串前後可能的空白或 Markdown 標籤
    clean_str = input_str.strip().replace("```json", "").replace("```", "").strip()

    try:
        # 1. 嘗試標準 JSON
        return json.loads(clean_str)
    except json.JSONDecodeError:
        try:
            # 2. 嘗試 Python literal_eval (處理單引號的情況)
            return ast.literal_eval(clean_str)
        except (ValueError, SyntaxError):
            # 3. 如果兩者都失敗，嘗試使用正則表達式提取第一個 JSON 對象 {...}
            match = re.search(r'\{.*\}', clean_str, re.DOTALL)
            if match:
                extracted = match.group(0)
                try:
                    return json.loads(extracted)
                except:
                    try:
                        return ast.literal_eval(extracted)
                    except:
                        pass
            return clean_str # 降級處理：如果解析失敗，回傳原始字串

class CareerAnalysisTools:
    
    @tool("Fetch Resume From Database")
    def fetch_resume_from_db(user_id: str):
        """
        根據 user_id 從資料庫中獲取該使用者最新的履歷內容 (JSON 格式字串)。
        """
        try:
            # 魯棒性處理：LLM 有時會傳入 {"user_id": "1"} 或帶引號的 "1"
            parsed_val = parse_input_to_dict(user_id)
            
            clean_id = user_id
            if isinstance(parsed_val, dict):
                clean_id = parsed_val.get("user_id") or parsed_val.get("id") or list(parsed_val.values())[0]
            else:
                clean_id = str(parsed_val).strip().strip("'").strip('"')
            
            print(f"DEBUG: fetch_resume_from_db 原始輸入: {user_id} -> 解析為: {clean_id}")
            return get_latest_resume(str(clean_id))
        except Exception as e:
            return f"Error fetching resume: {str(e)}"

    @tool("Calculate Technical Vectors")
    def calculate_tech_vectors(user_json_str: str):
        """
        接收使用者職涯問卷的 JSON 字串，計算 D1-D6 六維能力分數。
        """
        # 定義預設分數 (Entry Level Baseline)
        default_scores = {
            "D1": 0.5, "D2": 0.5, "D3": 0.5, 
            "D4": 0.5, "D5": 1.0, "D6": 1.0 
        }

        try:
            user_data = parse_input_to_dict(user_json_str)

            # 檢查是否為無經驗者 (如果沒有 module_a 或是 q1_languages 為空)
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
            # 發生任何錯誤都回傳預設值
            return f"Error (using defaults): {str(default_scores)}. Details: {str(e)}"

    @tool("Calculate Job Match Score")
    def calculate_match_score(vectors_str: str, target_role: str):
        """
        計算使用者能力向量與目標職位的匹配分數 (0-100)。
        """
        try:
            # 使用輔助函式解析，確保支援單/雙引號
            vectors = parse_input_to_dict(vectors_str)
            score = JobMatcher.calculate_match_score(vectors, target_role)
            return str(score)
        except Exception as e:
            return f"Error calculating match score: {str(e)}"