import sys


def flatten(S):
    ''' flatten recursively any lists or tuples'''

    def islis(lis):
        return isinstance(lis, list) or isinstance(lis, tuple)

    if isinstance(S, tuple):
        S = list(S)

    if len(S) == 0:
        return S
    if islis(S[0]):
        return flatten(S[0]) + flatten(S[1:])
    return S[:1] + flatten(S[1:])


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
