import sys
from src.core.agent_engine.task_types import TaskType
from src.core.agent_engine.config import get_config_by_type

print("Testing RESUME_OPT retrieval...")
task_type = TaskType("resume_opt")
inputs = {"user_id": "demo"}

config = get_config_by_type(task_type, inputs)
if config is None:
    print("CONFIG IS NONE!")
else:
    print("CONFIG RETRIEVED SUCCESSFULLY!")
    print(config.keys())
