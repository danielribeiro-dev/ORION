import sys
import os
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.append(os.getcwd())

from main import main
from infra.ui import ConsoleUI

def test_loop():
    print("Testing Main Loop...")
    
    # Mock inputs: "hello", "exit"
    inputs = iter(["hello", "exit"])
    
    def mock_input(prompt):
        try:
            val = next(inputs)
            print(f"[TEST INPUT] {val}")
            return val
        except StopIteration:
            return "exit"

    # Patch ConsoleUI.input_user AND Router to simulate intents
    with patch.object(ConsoleUI, 'input_user', side_effect=mock_input):
        # We simulate that the first input "hello" is CHAT (Allowed)
        # The second input "exit" triggers break before route
        with patch('routing.router.Router.route', return_value={"intent": "CHAT", "confidence": 0.99}):
            try:
                main()
            except SystemExit:
                print("System Exit caught (Expected).")
            
    # Verify Memory
    if os.path.exists("memory/profile.json"):
        print("✅ Profile Memory created.")
    else:
        print("❌ Profile Memory MISSING.")

    if os.path.exists("memory/history.jsonl"):
        print("✅ History Memory created.")
    else:
        print("❌ History Memory MISSING.")

if __name__ == "__main__":
    test_loop()
