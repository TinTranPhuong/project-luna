import sys
import os
from pathlib import Path

# 1. Setup Path (Project Root)
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from server.src.core.prompts.manager import PromptManager
# We import the limit to verify against it
from server.src.config.settings import MAX_HISTORY_MESSAGES

def test_sliding_window():
    print("✂️ Testing Context Sliding Window...")
    print(f"   - Configured Limit: {MAX_HISTORY_MESSAGES} messages")

    manager = PromptManager()

    # 2. Generate 'Overflow' Data
    # We create 5 more messages than allowed to force a trim
    total_messages = MAX_HISTORY_MESSAGES + 5
    print(f"   - Generating {total_messages} dummy messages...")
    
    fake_history = []
    for i in range(total_messages):
        fake_history.append({
            "role": "user", 
            "content": f"Message #{i+1}" # e.g., "Message #1", "Message #2"...
        })

    # 3. Run the Logic
    final_output = manager.build_messages(fake_history)

    # 4. Verification Logic
    # Expected Length = Limit + 1 (The System Prompt)
    expected_len = MAX_HISTORY_MESSAGES + 1
    actual_len = len(final_output)

    print(f"\n📊 Results:")
    print(f"   - Input Count:  {len(fake_history)}")
    print(f"   - Output Count: {actual_len} (Should be {expected_len})")

    # Check 1: Did it trim correctly?
    if actual_len == expected_len:
        print("   - ✅ PASSED: List length is correct.")
    else:
        print(f"   - ❌ FAILED: Expected {expected_len}, got {actual_len}")

    # Check 2: Is System Prompt still first?
    if final_output[0]["role"] == "system":
        print("   - ✅ PASSED: System Prompt is locked at Index 0.")
    else:
        print("   - ❌ FAILED: System Prompt is missing!")

    # Check 3: Did we keep the NEWEST messages?
    # The last message in output must match the last message in input
    last_in = fake_history[-1]["content"]
    last_out = final_output[-1]["content"]
    if last_in == last_out:
        print(f"   - ✅ PASSED: Most recent message preserved ('{last_out}').")
    else:
        print(f"   - ❌ FAILED: Lost recent context. Got '{last_out}'")

    # Check 4: Did we drop the OLDEST messages?
    # If we kept 10, the first user message should be "Message #6" (Dropped 1-5)
    first_user_msg = final_output[1]["content"]
    print(f"   - ℹ️  Oldest kept message: '{first_user_msg}'")

if __name__ == "__main__":
    test_sliding_window()