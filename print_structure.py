import os

def print_tree(start_path, prefix="", level=3):
    if level < 0:
        return
    files = sorted(os.listdir(start_path))
    for file in files:
        if file in ['__pycache__', 'venv', 'env', '.git']:
            continue
        full_path = os.path.join(start_path, file)
        print(prefix + "|-- " + file)
        if os.path.isdir(full_path):
            print_tree(full_path, prefix + "|   ", level - 1)

print_tree(".", level=3)
