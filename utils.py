
import os
import json
from datetime import datetime

LOGFILE = "logs.json"

def log_request(tool):
    today = datetime.today().strftime("%Y-%m-%d")
    if os.path.exists(LOGFILE):
        with open(LOGFILE, "r") as f:
            logs = json.load(f)
    else:
        logs = {}

    if today not in logs:
        logs[today] = {"diamond": 0, "paintbynumbers": 0}

    if tool in logs[today]:
        logs[today][tool] += 1

    with open(LOGFILE, "w") as f:
        json.dump(logs, f)

def get_logs():
    if os.path.exists(LOGFILE):
        with open(LOGFILE, "r") as f:
            return json.load(f)
    return {}

def clear_generated_files():
    count = 0
    for fname in os.listdir("static"):
        if fname.endswith(".png") and (
            fname.startswith("canvas_") or
            fname.startswith("painted_") or
            fname.startswith("diamond_")
        ):
            try:
                os.remove(os.path.join("static", fname))
                count += 1
            except Exception:
                pass
    return count
