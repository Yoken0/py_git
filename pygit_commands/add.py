import os
from .base import find_repo, hash_object

def add(args):
    """
    Adds file contents to the index.
    """
    repo_path = find_repo()
    if not repo_path:
        print("fatal: not a git repository (or any of the parent directories): .pygit")
        return

    index_path = os.path.join(repo_path, 'index')
    index = {}
    if os.path.exists(index_path):
        with open(index_path, 'r') as f:
            for line in f:
                mode, sha1, path = line.strip().split()
                index[path] = (mode, sha1)

    for file_path in args.files:
        if not os.path.exists(file_path):
            print(f"fatal: pathspec '{file_path}' did not match any files")
            continue
        
        with open(file_path, 'rb') as f:
            content = f.read()
        
        sha1 = hash_object(content)
        # For simplicity, we'll use a standard file mode.
        index[file_path] = ('100644', sha1)
        print(f"Added '{file_path}' to the index.")

    with open(index_path, 'w') as f:
        for path, (mode, sha1) in sorted(index.items()):
            f.write(f"{mode} {sha1} {path}\n")
