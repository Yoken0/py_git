import os
from .base import find_repo, hash_object, get_head_ref, get_head_commit_sha

def write_tree():
    """
    Writes the current index as a tree object.
    """
    repo_path = find_repo()
    index_path = os.path.join(repo_path, 'index')
    if not os.path.exists(index_path):
        return None # Return None if index doesn't exist

    tree_entries = b''
    with open(index_path, 'r') as f:
        for line in f:
            mode, sha1, path = line.strip().split()
            tree_entries += f'{mode} {path}\0'.encode() + bytes.fromhex(sha1)

    return hash_object(tree_entries, 'tree')

def commit(args):
    """
    Creates a new commit object.
    """
    repo_path = find_repo()
    if not repo_path:
        print("fatal: not a git repository.")
        return

    tree_sha = write_tree()
    if not tree_sha:
        print("Nothing to commit (index is empty)")
        return

    parent_commit = get_head_commit_sha()
    
    commit_data = f"tree {tree_sha}\n"
    if parent_commit:
        commit_data += f"parent {parent_commit}\n"
    
    commit_data += f"\n{args.message}\n"
    
    commit_sha = hash_object(commit_data.encode(), 'commit')
    
    ref_path = get_head_ref()
    with open(ref_path, 'w') as f:
        f.write(commit_sha)
        
    print(f"Committed to main: {commit_sha}")
