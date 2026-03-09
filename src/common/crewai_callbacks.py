import os
import json
from datetime import datetime
from src.common.logger import setup_logger

sys_logger = setup_logger()

def task_audit_callback(task_output):
    """
    CrewAI 專屬：當某個 Task 執行完畢時，自動觸發並傳入 TaskOutput 物件
    用以儲存 Agent 的最終原始輸出，方便除錯與 Prompt 調整。
    """
    audit_folder = "logs/crewai_outputs"
    
    # 1. 自動建立資料夾
    if not os.path.exists(audit_folder):
        os.makedirs(audit_folder)
        
    audit_file = os.path.join(audit_folder, "task_audit_trail.log")
    
    try:
        # 2. 安全萃取 Agent 名稱 (防呆設計)
        agent_name = "Unknown Agent"
        if hasattr(task_output, "agent") and task_output.agent:
            if hasattr(task_output.agent, "role"):
                agent_name = task_output.agent.role
            else:
                agent_name = str(task_output.agent)

        # 3. 從 TaskOutput 萃取有價值的高維度資訊
        audit_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "agent_name": agent_name,
            "task_description": getattr(task_output, "description", "No description"),
            "final_output": getattr(task_output, "raw", str(task_output))
        }
        
        # 4. 以格式化 JSON 附加模式寫入
        with open(audit_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(audit_data, ensure_ascii=False, indent=4) + "\n" + "="*50 + "\n")
            
        sys_logger.info(f"✅ 已成功稽核 Agent [{agent_name}] 的任務輸出。")
        
    except Exception as e:
        sys_logger.error(f"CrewAI 任務存檔失敗: {e}", exc_info=True)


# def agent_step_callback(step_output):
#     """
#     捕捉 Agent 的每一次「思考(Thought)」與「行動(Action)」
#     """
#     try:
#         # 1. 防禦性正規化：確保我們處理的一定是個 List (拆解郵筒)
#         if isinstance(step_output, list):
#             steps_to_process = step_output
#         else:
#             steps_to_process = [step_output] # 如果只是一封信，我們也把它裝進清單裡統一處理

#         # 2. 迭代處理每一個步驟
#         for step in steps_to_process:
#             # 判斷這封信是不是 Tuple (AgentAction, Observation)
#             if isinstance(step, tuple) and len(step) > 0:
#                 action_obj = step[0]
#             else:
#                 action_obj = step
                
#             # 3. 核心過濾：檢查是否有 'tool' 屬性
#             if hasattr(action_obj, 'tool'):
#                 thought_text = ""
#                 if hasattr(action_obj, 'log') and action_obj.log:
#                     thought_text = action_obj.log
#                 elif hasattr(action_obj, 'text') and action_obj.text:
#                     thought_text = action_obj.text
#                 else:
#                     thought_text = f"未偵測到標準屬性。原始物件片段: {str(action_obj)[:200]}"
                    
#                 action_data = {
#                     "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#                     "tool_name": getattr(action_obj, 'tool', '無工具'),
#                     "tool_input": getattr(action_obj, 'tool_input', '無輸入'),
#                     "thought_log": thought_text
#                 }
                
#                 # 寫入系統 INFO (供終端機查看)
#                 sys_logger.info(f"🧠 [Agent 思考中] 調用工具: {action_data['tool_name']} | 參數: {action_data['tool_input']}")
                
#                 # 寫入專屬檔案
#                 audit_folder = "logs/crewai_outputs"
#                 if not os.path.exists(audit_folder):
#                     os.makedirs(audit_folder)
                    
#                 audit_file = os.path.join(audit_folder, "agent_thoughts_trail.log")
#                 with open(audit_file, "a", encoding="utf-8") as f:
#                     f.write(json.dumps(action_data, ensure_ascii=False, indent=4) + "\n" + "-"*40 + "\n")
#             else:
#                 # 【架構師秘訣】當條件不符時，印出 Debug 訊息，打破「靜默失敗」！
#                 sys_logger.debug(f"⚠️ [Agent Step 忽略] 傳入的物件不包含 tool 屬性。物件型態: {type(action_obj)}")
                
#     except Exception as e:
#         sys_logger.error(f"解析 Agent 步驟時發生錯誤: {e}", exc_info=True)
