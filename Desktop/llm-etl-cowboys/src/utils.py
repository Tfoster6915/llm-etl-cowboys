import os

def ensure_dir(d: str):
    if not os.path.exists(d):
        os.makedirs(d, exist_ok=True)
