PyGit: A Simple Git Clone in Python
PyGit is a custom version control system built from the ground up in Python. It was created as a learning exercise to understand the internal data structures and core concepts that power modern VCS tools like Git.

This project demystifies Git by recreating its fundamental object model and commands, showing how commits, trees, and blobs work together to track the history of a project.

Features
PyGit currently supports the essential commands needed to track changes in a project:

init: Initialize a new, empty repository.

add: Stage file changes for the next commit.

commit: Record a snapshot of the staged changes to the project's history.

log: View the history of commits.

cat-file: Inspect the contents of Git objects from the internal database.

Quick Start
Here is a simple walkthrough of how to use PyGit to version control a new project.

1. Initialize a Repository
First, create a new directory for your project and initialize a PyGit repository within it.

mkdir my-project
cd my-project
pygit init

This will create a hidden .pygit directory, which is the "database" for your repository.

2. Create a File and Add It
Create a new file and then use the add command to stage it. Staging a file tells PyGit that you want to include its changes in the next commit.

echo "Hello, PyGit!" > hello.txt
pygit add hello.txt

3. Commit Your Changes
Use the commit command to save the staged changes as a new snapshot in the history. Every commit requires a message describing the changes.

pygit commit -m "Initial commit"

4. Check the Log
You can now view the commit you just made using the log command.

pygit log

This will display the unique commit hash and the message you provided.

How It Works
PyGit simulates the core components of Git's object database:

Blobs: Store the contents of files.

Trees: Represent the contents of a directory, referencing blobs and other trees.

Commits: A snapshot of the project's root tree at a specific point in time, linked to a parent commit to form a history.

All objects are compressed with zlib and identified by a SHA-1 hash of their contents, ensuring data integrity.
