from lark import Lark
from lark.indenter import Indenter

# I tried to use parsing indentation method from [1] but failed to meet some cases, so I ended up forcing some block endings with #:BLOCK_NAME
# [1] https://lark-parser.readthedocs.io/en/latest/examples/indented_tree.html
from renpy_parser import transformer
from renpy_parser.utils import debug, mywarn


def build_parser():
    tree_grammar = r"""

start: _code_line* label_tree+

label_tree: label_line (_sayblock | menu_tree)

menu_tree: _code_or_line* _MENU_START _code_or_line* choice_tree+ _MENU_END

choice_tree: choice_line (_sayblock|menu_tree)

_sayblock : _code_or_line* jump_line

_code_or_line: _code_line | say_line | if_block

label_line    : "label" KEYWORD ":" _NL
choice_line   : QSTRING ":" _NL
say_line      : [KEYWORD] QSTRING _NL
jump_line     : "jump" KEYWORD _NL

if_block: if_start if_else? _if_end
if_start      : if_head (_sayblock | menu_tree | (_code_or_line+))
if_else      : "else" ":" _NL (_sayblock | menu_tree)
_if_end       : "#:if" _NL

if_head : "if" KEYWORD IF_OP /[^:]+/ ":" _NL
IF_OP : "=="|"=>"|"=<"|">"|"<"
_code_line    : code_line_def | code_line_var
code_line_def : "define" /[^\n]+/ _NL
code_line_var : "$" /[^\n]+/ _NL

_MENU_START   : "menu:" _NL
_MENU_END     : "#:menu" _NL

COMMENT       : /# [^\n]+/ _NL
QSTRING       : /["][^"]*["]/
KEYWORD       : /[a-zA-Z0-9_]+/

%ignore COMMENT

_NL: / *(\n[\t ]*)+/


%ignore WS_INLINE
%import common.WS_INLINE


"""

    parser = Lark(tree_grammar, parser='lalr')
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
    tt.end()
    debug = (parser, tree, tt, seq)

    # some checks:
    # todo = set()
    # for label in tt.jumps:
    #     if label not in tt.labels:
    #         todo.add(label)
    # if len(todo) > 0:
    #     print(f"\nWARNING: Jump to missing labels: [{', '.join(todo)}]\n")

    return tt.labels, debug
