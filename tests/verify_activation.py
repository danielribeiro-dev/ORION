import sys
import os
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.append(os.getcwd())

from infra.container import Container

def test_activation():
    print("Testing System Activation...")
    
    container = Container.get_instance()
    
    # 1. Test Chat Plugin via Executor
    print("\n[TEST] Chat Capability")
    chat_plan = [("chat", {"user_input": "Hello from Test"})]
    # Mock LLM to avoid API calls/Cost
    container.llm_service.generate = MagicMock(return_value="Hello! I am ORION.")
    res_chat = container.executor.execute(chat_plan)
    print(f"Chat Result: {res_chat}")
    assert "Hello! I am ORION." in res_chat
    
    # 2. Test Web Plugin via Executor
    print("\n[TEST] Web Capability")
    web_plan = [("web", {"user_input": "Python"})]
    res_web = container.executor.execute(web_plan)
    print(f"Web Result: {res_web}")
    assert "Search Results for 'Python'" in res_web
    
    # 3. Test Filesystem Plugin via Executor
    print("\n[TEST] FS Capability")
    fs_plan = [("fs", {"user_input": "list"})]
    res_fs = container.executor.execute(fs_plan)
    print(f"FS Result: {res_fs}")
    assert "Current Directory" in res_fs
    
    print("\n✅ All Capabilities Active and Functional.")

if __name__ == "__main__":
    test_activation()
