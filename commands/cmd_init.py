# commands/cmd_init.py
import os
from core.repository import Repository

def run(args):
    path = os.getcwd()
    Repository.init(path)
