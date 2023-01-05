#!/usr/bin/env python
# main.py
def doubleit(val):
    import ipdb
    ipdb.set_trace()
    return val * 3

if __name__ == "__main__":
    print("doubleit 2: %d", doubleit(2))
    print("doubleit 4: %d", doubleit(4))
    print("doubleit 8: %d", doubleit(8))
