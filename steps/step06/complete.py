"""Recipe 06: checked, runnable cumulative code checkpoint.
The implementation lives in the shared app package to avoid 15 diverging copies.
"""
import json
from app.lesson import run

if __name__ == "__main__":
    print(json.dumps(run(6), ensure_ascii=False, indent=2))
