#!/usr/bin/python3
def s(*argv, **kargv):
    print("  STAT ", *argv, **kargv)


def ss(*argv, **kargv):
    print("  STAT ", *argv, **kargv)


def sm(*argv, **kargv):
    print(*argv, **kargv)


def se(*argv, **kargv):
    print(*argv, **kargv)


def d(*argv, **kargv):
    print("  DEBUG ", *argv, **kargv)


def ds(*argv, **kargv):
    print("  DEBUG ", *argv, **kargv)


def dm(*argv, **kargv):
    print(*argv, **kargv)


def de(*argv, **kargv):
    print(*argv, **kargv)
