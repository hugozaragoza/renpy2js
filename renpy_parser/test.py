import re

check = re.compile(r'^(?P<n1>[0-9])(?P<n2>(?:[+-][0-9])*)$')

ss = ["1", "1+1", "1+1-2"]
for s in ss:
    m = check.match(s)
    assert m
    print(m.group("n1"))
    print(m.group("n2"))
    print("-")
print("OK")
