import pytest

import renpy_parser.parser as parse_factory


@pytest.mark.parametrize(
    "source,des_transformed_tree, des_chars",
    [
        ("""\
label arthimetic:
    $ a = B + 1
    if B == a + 1:
        "yes"
    #:if
    jump end
""",
         [('label_tree', ('arthimetic', [('code_line', "window.context.set('a',(window.context.get('B')||0) + 1)"), (
                 'if_tree',
                 [('if_start', "(window.context.get('B')||0)==(window.context.get('a')||0) + 1",
                   [('say_line', ('', 'yes'))])]),
                                         ('jump_line', 'end')]))],
         {},
         ),

        ("""\
label arthimetic: 
    $ a = 1
    $ b = a + 2
    jump end
""",
         [('label_tree', ('arthimetic', [('code_line', "window.context.set('a',1)"),
                                         ('code_line', "window.context.set('b',(window.context.get('a')||0) + 2)"),
                                         ('jump_line', 'end')]))],
         {},
         ),

    ])
def test_parse_and_transform(source, des_transformed_tree, des_chars):
    all = parse_factory.parse_renpy(source)
    assert all, "Failed to parse!"
    tree = all[1][2]
    seq = all[1][-1]
    print(seq)
    assert seq == des_transformed_tree
    assert tree.objs == des_chars
