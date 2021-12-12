from lark import Lark
from lark.indenter import Indenter

# parsing indentation method from: https://lark-parser.readthedocs.io/en/latest/examples/indented_tree.html
from renpy_parser import transformer
from renpy_parser.utils import debug, warn


def build_parser():
    tree_grammar = r"""
        
        ?start: _NL* _tree+
    
        _tree: (CODE_LINE|label_tree|menu_tree)
        
        label_tree: label_line _INDENT (menu_tree|_sayblock) _DEDENT
        menu_tree: say_line* _menu_start _INDENT (CODE_LINE|say_line)* menu_choice_tree+ _DEDENT
        menu_choice_tree: choice_line _INDENT (_sayblock|menu_tree)+ _DEDENT

        _sayblock : CODE_LINE* say_line* jump_line

        choice_line : ESCAPED_STRING ":" _NL 
        say_line : [KEYWORD] ESCAPED_STRING _NL
        
        _menu_start.102 : "menu" ":" _NL
        label_line.101  : "label" KEYWORD ":" _NL
        jump_line.100   : "jump" KEYWORD _NL
        
        _NL.9000 : /(\n[\t ]*)+/
                         
        KEYWORD.10 : /[a-zA-Z0-9_]+/        

        CODE_LINE.998   : ("define"|"$") /[^\n]+\n+/
        
        COMMENT.999 : / *#[^\n]*(\n)+/
        %ignore COMMENT
        %ignore WS_INLINE
        
        %declare _INDENT _DEDENT

        %import common.WS_INLINE
        %import common.ESCAPED_STRING

        


    """

    class TreeIndenter(Indenter):
        NL_type = '_NL'
        OPEN_PAREN_types = []
        CLOSE_PAREN_types = []
        INDENT_type = '_INDENT'
        DEDENT_type = '_DEDENT'
        tab_len = 8

    parser = Lark(tree_grammar, parser='lalr', postlex=TreeIndenter())
    return parser


def parse_error(e):
    print("----------------------------------------")
    print("PARSER FAILURE:")
    print(e)
    print("----------------------------------------")
    return False


def parse_renpy(renpy_script):
    parser = build_parser()
    try:
        tree = parser.parse(renpy_script, on_error=parse_error)
    except:
        return None
    tt = transformer.Transformer1()
    seq = tt.transform(tree)
    debug = (parser, tree, tt, seq)

    # some checks:
    todo = set()
    for label in tt.jumps:
        if label not in tt.labels:
            todo.add(label)
    if len(todo) > 0:
        print(f"\nWARNING: Jump to missing labels: [{', '.join(todo)}]\n")

    return tt.labels, debug
