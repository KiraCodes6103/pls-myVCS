import sys
from core import objects
from core.repository import Repository


def run(args):
    repo = Repository.find()
    obj_type, content = objects.read_object(args.sha, repo.path)

    if args.type_only:
        print(obj_type)
    elif args.size_only:
        print(len(content))
    else:
        sys.stdout.buffer.write(content)
