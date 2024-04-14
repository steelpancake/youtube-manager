import main
import config

import sys


def printv(*args, **kwargs):
    if config.cmd_args.verbose:
        print(*args, **kwargs)


def printe(*args, **kwargs):
    if 'file' in kwargs:
        del kwargs['file']
    new_args = ("ERROR", *args)
    print(*new_args, file=sys.stderr, **kwargs)
