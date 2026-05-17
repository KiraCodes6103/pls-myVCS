# commands/cmd_log.py
from core import commit
from core.repository import Repository


def run(args):
    repo = Repository.find()
    commit.log(repo)
