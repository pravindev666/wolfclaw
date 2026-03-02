import os

# Set desktop mode
os.environ["WOLFCLAW_ENVIRONMENT"] = "desktop"

from core import config
from core import local_db

# User from our earlier inspection
user_id = "0d6db272-2167-464e-b1d0-d7063cdba902"

try:
    print(f"Testing save key for user: {user_id}")
    config.set_key("openai", "sk-test-12345", user_id=user_id)
    print("✅ Key saved successfully!")
    
    keys = config.get_all_keys(user_id=user_id)
    print("All keys:", keys)
    if keys.get("openai_key") == "sk-test-12345":
        print("✅ Retrieval confirmed!")
    else:
        print("❌ Retrieval failed or unexpected value.")
        
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
