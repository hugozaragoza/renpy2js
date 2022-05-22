import pytest

from renpy_parser import utils


@pytest.mark.parametrize("input,des", [
    ([], []),
    ([1], [1]),
    (["1", [1]], ["1", 1]),
    (["1", [1], [[3, 4]]], ["1", 1, 3, 4]),
    (["1", (2, 3)], ["1", 2, 3]),
])
def test_flatten(input, des):
    assert utils.flatten(input) == des
