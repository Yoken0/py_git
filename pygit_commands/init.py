import os

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
