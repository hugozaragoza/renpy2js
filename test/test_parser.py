import pytest
import renpy_parser.parser as parse_factory
from renpy_parser.renpyClasses import Character
from renpy_parser.utils import debug


@pytest.mark.parametrize("source,des", [
    # basic with extra lines
    ("""\
label start:
    # comment
    # comment
    "blah # blah"
    # check that ignore code words can be used as keywords:
    jump nvl
# end
""", """\
start
  label_tree
    label_line	start
    say_line	"blah # blah"
    jump_line	nvl
"""),
    # Characters
    ("""\
define char1 = Character("Hugo",color=1)

define char2 = Character("Nat",image=1)
label one:
    "Hello [char2]!"
    jump end
""",
     # I don't know why pretty print generates empty lines after defines? //TODO
     """\
start
  code_line_def\tchar1 = Character("Hugo",color=1)
  code_line_def\tchar2 = Character("Nat",image=1)
  label_tree
    label_line	one
    say_line	"Hello [char2]!"
    jump_line	end
"""),

    # ------------------------------------------------------
    # TEST THAT IT PASSES:
    ("""\
define J = Character('Nat', image='bg.jpg')
label start:
    $ a = 2
    "It's 6AM, you are still in bed in your pyjammas."     
    menu:
        "You wait and see":
            $ a = 2
            jump waitAndSee
    #:menu
""", None),
    # -----------------------
    ("""\
label menu1:
    "Blah"
    menu: 
        "You say"
        "choice0":
            "response 0"
            jump end
        "choice1":
            "response 0"
            jump end
    #:menu 
""", None),
    # -----------------------
    ("""\
label menu2:
    "Blah"
    menu:
        "menu 0"
        "choice0":
            jump end
        "choice1":
            menu:
                "choice 11":
                    "header"
                    jump end
                "choice 12":
                    "header"
                    jump end
            #:menu
    #:menu
    """, None),
    # -----------------------
    ("""\
# comment and code
$ a = 2
label start:
    H "line 1"
    Hugo "line 2"
    "line 3"
    jump j1
label basic_choice:
    menu:
    
        "menu header"
        "choice 1_1":
            "answer to 1_1"
            jump after1_1
    #:menu
label second_choice:
    "line 2"
    jump end
""", None),
    # -----------------------
    ("""\
define J = Character('Nat', image='bg.jpg')

# Credits: https://commons.wikimedia.org/wiki/File:Blue_background.jpg

label start:
    "hello"
    jump end
"""
     , None),
])
def test_parse(source, des):
    parser = parse_factory.build_parser()
    res = parser.parse(source).pretty()
    if des is not None:
        print(len(res))
        assert res == des


@pytest.mark.parametrize(
    "source,des_transformed_tree, des_chars",
    [
        # -----------------------
        ("""\
label simplest:
    "Hello"
    jump end
label s2:
    "Hello2"
    jump end2
""",
         [('label_tree', ('simplest', [('say_line', ('', 'Hello')), ('jump_line', 'end')])),
          ('label_tree', ('s2', [('say_line', ('', 'Hello2')), ('jump_line', 'end2')]))]
         , {},),

        # -----------------------
        ("""\
label simpleIF:
    "Hello1"
    if a == 1:
        "Sentence"
    #:if
    if a == 1:
        "Hello2"
        jump one
    else:    
        "Hello3"
        jump two
    #:if
    jump __none
""",
         [('label_tree', ('simpleIF', [('say_line', ('', 'Hello1')), (
                 'if_tree', [('if_start', "(window.context.get('a')||0)==1", [('say_line', ('', 'Sentence'))])]),
                                       ('if_tree', [
                                           ('if_start', "(window.context.get('a')||0)==1",
                                            [('say_line', ('', 'Hello2')), ('jump_line', 'one')]),
                                           ('if_else', [('say_line', ('', 'Hello3')), ('jump_line', 'two')])]), ()]))]
         , {},),

        ("""\
label complexIF:
    "Hello1"
    if a == 1:
        "Hello2"
        jump one
    #:if
    if b == 2:            
        "Hello3"
        jump two
    else:
        jump three
    #:if
    jump __none
""",
         [('label_tree', ('complexIF', [('say_line', ('', 'Hello1')), ('if_tree', [
             ('if_start', "(window.context.get('a')||0)==1", [('say_line', ('', 'Hello2')), ('jump_line', 'one')])]), (
                                                'if_tree', [('if_start', "(window.context.get('b')||0)==2",
                                                             [('say_line', ('', 'Hello3')), ('jump_line', 'two')]),
                                                            ('if_else', [('jump_line', 'three')])]), ()]))]
         , {},
         ),

        # -----------------------
        ("""\
label simple_menu:
    menu:
        "say1":
            "first response"
            jump end
        "say2":
            "something here"
            jump end   
    #:menu
""",
         [('label_tree',
           ('simple_menu',
            [('menu_tree',
              [('menu_choice',
                ('choice_label__say1_0',
                 'say1 (MISSING)',
                 [('say_line', ('', 'first response')), ('jump_line', 'end')])),
               ('menu_choice',
                ('choice_label__say2_0',
                 'say2 (MISSING)',
                 [('say_line', ('', 'something here')), ('jump_line', 'end')]))])]))],
         {},
         ),

        # -----------------------
        ("""\
label simple_menu2:
    menu:
        "say1":
            "first response"
            jump end
        "say2":
            jump end   
    #:menu
""",
         [('label_tree',
           ('simple_menu2',
            [('menu_tree',
              [('menu_choice',
                ('choice_label__say1_0',
                 'say1 (MISSING)',
                 [('say_line', ('', 'first response')), ('jump_line', 'end')])),
               ('menu_choice',
                ('choice_label__say2_0',
                 'say2 (MISSING)',
                 [('jump_line', 'end')]))])]))],
         {},
         ),

        # -----------------------
        ("""\
define hugo = Character("Hugo", image="blah")
$ a_var = 2
label start:
    $ b_var = 3
    $ a_var += 10
    $ c_var += b_var
    hugo "Hello [hugo]"
    jump end
""",
         [('code_line', '// hugo = Character("Hugo", image="blah")'),
          ('code_line', "window.context.set('a_var',2)"),
          ('label_tree', ('start', [
              ('code_line', "window.context.set('b_var',3)"),
              ('code_line', "window.context.set('a_var',(window.context.get('a_var')||0) + 10)"),
              ('code_line',
               "window.context.set('c_var',(window.context.get('c_var')||0) + (window.context.get('b_var')||0))"),
              ('say_line', ('Hugo', 'Hello Hugo')), ('jump_line', 'end')]))]
         ,
         {"hugo": Character("Hugo", image="blah")},
         ),
        # -----------------------
        ("""\
label start:
"Hello"
$ a = 1
if a==1:
    "IF 1"
    jump two
#:if
jump __END

label two:
"Label two reached"
jump __END
        """,

         [('label_tree', ('start', [
             ('say_line', ('', 'Hello')),
             ('code_line', "window.context.set('a',1)"),
             ('if_tree', [
                 ('if_start', "(window.context.get('a')||0)==1", [
                     ('say_line', ('', 'IF 1')), ('jump_line', 'two')]
                  )]),
             ('jump_line', '__END')])),
          ('label_tree', ('two', [('say_line', ('', 'Label two reached')), ('jump_line', '__END')]))]

         ,
         {},
         ),
        ("""\
label start:
if a == 1:
    "say if 1"
    menu:
        "choice 1":
            jump end
    #:menu
#:if
jump end
""",
         [('label_tree', ('start', [
             ('if_tree', [
                 ('if_start', "(window.context.get('a')||0)==1", [
                     ('menu_tree',
                      [('say_line', ('', 'say if 1')),
                       ('menu_choice', (
                               'choice_label__choice_1_0',
                               'choice 1 (MISSING)',
                               [('jump_line', 'end')]))]
                      )])]),
             ('jump_line', 'end')]))]

         ,
         {},
         ),
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
    ])
def test_parse_and_transform(source, des_transformed_tree, des_chars):
    all = parse_factory.parse_renpy(source)
    assert all, "Failed to parse!"
    tree = all[1][2]
    seq = all[1][-1]
    print(seq)
    assert seq == des_transformed_tree
    assert tree.objs == des_chars
