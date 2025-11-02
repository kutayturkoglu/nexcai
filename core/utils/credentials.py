import os
import json

TOKEN_DIR = os.path.expanduser("~/.tokens")
os.makedirs(TOKEN_DIR, exist_ok=True)

def _token_path(service_name):
    return os.path.join(TOKEN_DIR, f"{service_name}.json")

def save_token(service_name, token_data):
    path = _token_path(service_name)
    with open(path, "w") as f:
        f.write(token_data)
    return path

def load_token(service_name):
    path = _token_path(service_name)
    if os.path.exists(path):
        with open(path, "r") as f:
            return f.read()
    return None
