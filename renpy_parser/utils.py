import sys
import warnings


def myassert(test, msg):
    if not test:
        print("\nFAIL: " + msg + "\n")
        sys.exit(1)


def mywarn(msg):
    print("WARNING: " + msg)


def debug(msg, title=None):
    print("===============" + (title if title else ''))
    print(msg)
    print("---------------")
