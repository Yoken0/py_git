import os
import zlib
from .base import find_repo, get_head_commit_sha

def logs(args):
    """
    Shows the commit logs.
    """
    repo_path = find_repo()
    if not repo_path:
        print("fatal: not a git repository.")
        return

    def print_commit(sha):
        obj_dir = os.path.join(repo_path, 'objects', sha[:2])
        obj_file = os.path.join(obj_dir, sha[2:])
        
        with open(obj_file, 'rb') as f:
            compressed = f.read()
        
        decompressed = zlib.decompress(compressed)
        header_end = decompressed.find(b'\0')
        commit_raw = decompressed[header_end+1:]
        
        print(f"commit {sha}")
        
        lines = commit_raw.decode('utf-8').split('\n')
        parent = None
        for line in lines:
            if line.startswith('parent '):
                parent = line.split(' ')[1]
            print(f"    {line}")
        
        return parent

    current_commit_sha = get_head_commit_sha()
    while current_commit_sha:
        current_commit_sha = print_commit(current_commit_sha)
