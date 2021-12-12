from collections import defaultdict


def find_two(arr, k):
    if len(arr) < 2:
        return []
    val_to_pos = defaultdict(lambda: [])
    for i, el in enumerate(arr):
        val_to_pos[el].append(i)

    for i, el in enumerate(arr):
        div = k / el
        _len = len(val_to_pos[div])
        if div == el:
            _len -= 1
        if _len > 0:
            second_el = arr[(val_to_pos[div])[0]]
            return [el, second_el]
    return []


assert (find_two([1, 2, 10, 5], 10) == [1, 10])
assert (find_two([1, 2, 10, 5], 4) == [])
