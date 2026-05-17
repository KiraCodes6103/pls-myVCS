from core import objects
from core.repository import Repository


def run(args):
    repo_path = Repository.find().path if args.write else '.'

    with open(args.file, 'rb') as f:
        data = f.read()

    sha = objects.hash_object(data, 'blob', repo_path, write=args.write)
    print(sha)
