import argparse
from pygit_commands import init, add, commit, logs, cat_file, rm

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