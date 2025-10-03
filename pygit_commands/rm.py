import os
from .base import find_repo

def rm(args):
    """
    Removes files from the index and working directory.
    """
    repo_path = find_repo()
    if not repo_path:
        print("fatal: not a git repository (or any of the parent directories): .pygit")
        return

    index_path = os.path.join(repo_path, 'index')
    
    # Read the index file if it exists
    index = {}
    if os.path.exists(index_path):
        with open(index_path, 'r') as f:
            for line in f:
                mode, sha1, path = line.strip().split()
                index[path] = (mode, sha1)

    # Flag to check if we actually modified the index
    index_modified = False

    # Iterate through the files provided by the user
    for file_path in args.files:
        if file_path in index:
            # Remove from the in-memory index
            del index[file_path]
            index_modified = True
            
            # Also remove from the working directory if it exists
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except OSError as e:
                    print(f"Error removing file {file_path}: {e}")
                    # If we can't remove the file, we'll continue, leaving it untracked.
            
            print(f"rm '{file_path}'")
        else:
            print(f"fatal: pathspec '{file_path}' did not match any files")

    # If we made changes, write the new index back to the file
    if index_modified:
        with open(index_path, 'w') as f:
            for path, (mode, sha1) in sorted(index.items()):
                f.write(f"{mode} {sha1} {path}\n")
