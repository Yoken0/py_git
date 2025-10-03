import os
import hashlib
import zlib

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

def get_head_ref():
    """ Gets the current HEAD reference path. """
    repo_path = find_repo()
    head_path = os.path.join(repo_path, 'HEAD')
    with open(head_path, 'r') as f:
        head_ref = f.read().strip()
    
    if head_ref.startswith('ref: '):
        return os.path.join(repo_path, *head_ref.split(' ')[1].split('/'))
    return None

def get_head_commit_sha():
    """ Gets the commit SHA1 from the current HEAD. Returns None if HEAD is unborn."""
    ref_path = get_head_ref()
    if ref_path and os.path.exists(ref_path):
        with open(ref_path, 'r') as f:
            return f.read().strip()
    return None
