import os
import hashlib
import zlib
import argparse
import sys

def init(args):
    """
    Initializes a new PyGit repository.
    Creates the .pygit directory and its subdirectories.
    """
    repo_path = os.path.join(os.getcwd(), '.pygit')
    if os.path.exists(repo_path):
        print("PyGit repository already initialized.")
        return

    os.makedirs(repo_path)
    os.makedirs(os.path.join(repo_path, 'objects'))
    os.makedirs(os.path.join(repo_path, 'refs', 'heads'))

    with open(os.path.join(repo_path, 'HEAD'), 'w') as f:
        f.write('ref: refs/heads/main\n')

    print(f"Initialized empty PyGit repository in {repo_path}")

def hash_object(data, obj_type='blob'):
    """
    Hashes the data and stores it in the object database.
    Returns the hash of the object.
    """
    header = f"{obj_type} {len(data)}\0".encode()
    full_data = header + data
    sha1 = hashlib.sha1(full_data).hexdigest()

    repo_path = find_repo()
    if not repo_path:
        raise Exception("Not a PyGit repository.")

    obj_path = os.path.join(repo_path, 'objects', sha1[:2])
    if not os.path.exists(obj_path):
        os.makedirs(obj_path)
    
    compressed_data = zlib.compress(full_data)
    with open(os.path.join(obj_path, sha1[2:]), 'wb') as f:
        f.write(compressed_data)
    
    return sha1

def find_repo(path='.'):
    """
    Finds the root of the PyGit repository.
    """
    path = os.path.abspath(path)
    pygit_dir = os.path.join(path, '.pygit')
    if os.path.isdir(pygit_dir):
        return pygit_dir
    parent = os.path.dirname(path)
    if parent == path:
        return None
    return find_repo(parent)

def rm(args):
    """
    Removes files from the index.
    """
    repo_path = find_repo()
    if not repo_path:
        print("fatal: not a git repository (or any of the parent directories): .pygit")
        return

    index_path = os.path.join(repo_path, 'index')
    if not os.path.exists(index_path):
        print("fatal: no index file found.")
        return

    index = {}
    with open(index_path, 'r') as f:
        for line in f:
            mode, sha1, path = line.strip().split()
            index[path] = (mode, sha1)

    for file_path in args.files:
        if file_path in index:
            del index[file_path]
            print(f"Removed '{file_path}' from the index.")
            os.remove(file_path)
        else:
            print(f"fatal: pathspec '{file_path}' did not match any files in the index")

    with open(index_path, 'w') as f:
        for path, (mode, sha1) in sorted(index.items()):
            f.write(f"{mode} {sha1} {path}\n")


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


def write_tree():
    """
    Writes the current index as a tree object.
    """
    repo_path = find_repo()
    index_path = os.path.join(repo_path, 'index')
    tree_entries = b''
    with open(index_path, 'r') as f:
        for line in f:
            mode, sha1, path = line.strip().split()
            # For simplicity, we are not handling nested directories here.
            # A full implementation would build a tree of trees.
            tree_entries += f'{mode} {path}\0'.encode() + bytes.fromhex(sha1)

    return hash_object(tree_entries, 'tree')

def get_head_ref():
    """ Gets the current HEAD reference. """
    repo_path = find_repo()
    head_path = os.path.join(repo_path, 'HEAD')
    with open(head_path, 'r') as f:
        head_ref = f.read().strip()
    
    if head_ref.startswith('ref: '):
        return os.path.join(repo_path, *head_ref.split(' ')[1].split('/'))
    return None

def get_parent_commit():
    """ Gets the parent commit SHA1 from the current HEAD. """
    ref_path = get_head_ref()
    if ref_path and os.path.exists(ref_path):
        with open(ref_path, 'r') as f:
            return f.read().strip()
    return None


def commit(args):
    """
    Creates a new commit object.
    """
    repo_path = find_repo()
    if not repo_path:
        print("fatal: not a git repository.")
        return

    tree_sha = write_tree()
    parent_commit = get_parent_commit()
    
    commit_data = f"tree {tree_sha}\n"
    if parent_commit:
        commit_data += f"parent {parent_commit}\n"
    
    # For simplicity, we are not including author and committer information.
    commit_data += f"\n{args.message}\n"
    
    commit_sha = hash_object(commit_data.encode(), 'commit')
    
    ref_path = get_head_ref()
    with open(ref_path, 'w') as f:
        f.write(commit_sha)
        
    print(f"Committed to main: {commit_sha}")

def cat_file(args):
    """
    Provides content or type and size information for repository objects
    """
    repo_path = find_repo()
    if not repo_path:
        print("fatal: not a git repository.")
        return

    obj_sha = args.object
    obj_dir = os.path.join(repo_path, 'objects', obj_sha[:2])
    obj_file = os.path.join(obj_dir, obj_sha[2:])

    if not os.path.exists(obj_file):
        print(f"fatal: Not a valid object name {obj_sha}")
        return

    with open(obj_file, 'rb') as f:
        compressed_data = f.read()
    
    decompressed_data = zlib.decompress(compressed_data)
    
    if args.p:
        header_end = decompressed_data.find(b'\0')
        content = decompressed_data[header_end+1:]
        sys.stdout.buffer.write(content)


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

    current_commit_sha = get_parent_commit()
    while current_commit_sha:
        current_commit_sha = print_commit(current_commit_sha)


def main():
    parser = argparse.ArgumentParser(description="A simple git implementation in Python.")
    subparsers = parser.add_subparsers(dest='command')
    subparsers.required = True

    # init command
    parser_init = subparsers.add_parser('init', help='Initialize a new, empty repository.')
    parser_init.set_defaults(func=init)

    # add command
    parser_add = subparsers.add_parser('add', help='Add file contents to the index.')
    parser_add.add_argument('files', nargs='+', help='Files to add')
    parser_add.set_defaults(func=add)

    # commit command
    parser_commit = subparsers.add_parser('commit', help='Record changes to the repository.')
    parser_commit.add_argument('-m', '--message', required=True, help='Commit message')
    parser_commit.set_defaults(func=commit)
    
    # cat-file command
    parser_cat_file = subparsers.add_parser('cat-file', help='Provide content for repository objects')
    parser_cat_file.add_argument('-p', action='store_true', help='Pretty-print the contents of <object>')
    parser_cat_file.add_argument('object', help='The object to display')
    parser_cat_file.set_defaults(func=cat_file)

    # logs command
    parser_logs = subparsers.add_parser('logs', help='Show commit logs.')
    parser_logs.set_defaults(func=logs)

    # remove command
    parser_rm = subparsers.add_parser('rm', help='Remove files from the index.')
    parser_rm.add_argument('files', nargs='+', help='Files to remove')
    parser_rm.set_defaults(func=rm)



    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
