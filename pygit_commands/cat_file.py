import os
import zlib
import sys
from .base import find_repo

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
