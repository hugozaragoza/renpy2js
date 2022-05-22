import re

from lark.visitors import Transformer

from renpy_parser.utils import mywarn, myassert


class Character():
    def __init__(self, name, color=None, image=None):
        self.name = name

    def __str__(self):
        return self.name

    def __eq__(self, other):
        if not isinstance(other, Character):
            # don't attempt to compare against unrelated types
            return NotImplemented
        return self.name == other.name


def parseexp(exp):
    check = re.compile(r'^(?P<key>[^=+*/<> -]+) *(?P<exp>.+) *$')
    m = check.match(exp)
    myassert(m, f"Failed to parse code expression: [{exp}]")
    return m.group("key"), m.group("exp")


class Transformer_labels(Transformer):

    def __init__(self):
        self.labels = set()

    def label_tree(self, items):
        key = items[0][1]
        self.labels.add(key)
        return items

    def label_line(self, items):
        assert len(items) == 1
        return ("label_line", items[0])


class Transformer1(Transformer):
    '''Build data tree'''

    def __init__(self):
        '''
        We expect defined_labels so we can warn on unfinished menu choices
        '''
        self.labels = None
        self.objs = None
        self._defined_labels = None
        self.warnins = {}

    def end(self):
        for w in self.warnins.values():
            mywarn(w)

    def transform(self, tree):
        # get all defined labels:
        t = Transformer_labels()
        t.transform(tree)
        self._defined_labels = t.labels
        # transform:
        self.labels = {}
        self.objs = {}
        return super().transform(tree)

    def resolve_characters(self, line):
        regex1 = re.compile(r'(\[.+?\])')
        ss = regex1.findall(line)
        for s in ss:
            key = s[1:-1]
            if key in self.objs:
                line = line.replace(s, str(self.objs[key]))
        return line

    def resolve_vars(self, exp):
        # resolve variables
        rex = re.compile(r"\b([a-zA-Z_-][^ ]*)\b")
        exp = rex.sub("(window.context.get('\\1')||0)", exp)
        return exp

    def addtoObjs(self, param, param1):
        assert param not in self.objs, f"Repeated key (object): [{param}]"
        self.objs[param] = param1

    # node visitors:
    def start(self, items):
        return items

    def menu_tree(self, items):
        return "menu_tree", items

    def addtoLabels(self, key, tree):
        myassert(not key in self.labels, "REPEATED LABEL DEFINITION: " + key)
        self.labels[key] = tree

    def choice_tree(self, items):
        key, title, tree = (items[0][1], items[0][2], items[1:])
        title = self.resolve_characters(title)
        if not tree[-1]:  # remove jump __none => ()
            tree = tree[0:-1]
        if len(tree) and tree[-1][0] == "jump_line":
            if tree[-1][1] not in self._defined_labels:
                title += " (MISSING)"
        self.addtoLabels(key, tree)
        return "menu_choice", (key, title, tree)

    def get_choice_label(self, choice_msg):
        cnt = 0
        choice_label = "choice_label__" + re.sub("[^a-zA-Z0-9_-]", "_", choice_msg)
        while choice_label + "_" + str(cnt) in self.labels:
            cnt += 1
        return choice_label + "_" + str(cnt)

    def choice_line(self, items):
        assert len(items) == 1
        choice_msg = str(items[0])[1:-1]
        choice_label = self.get_choice_label(choice_msg)
        return "choice_line", choice_label, choice_msg

    def jump_line(self, items):
        assert len(items) == 1
        key = items[0]
        if key == "__none":
            return ()
        elif key not in self._defined_labels and key != "__END":
            self.warnins["jump_to_" + key] = f"Jumped to undefined label: [{key}]"
        return "jump_line", items[0]

    def if_block(self, items):
        return "if_tree", items

    def if_start(self, items):
        if_head, if_rest = items[0], items[1:]
        assert (if_head.data == "if_head")
        exp = "".join([str(x) for x in if_head.children])
        return "if_start", exp, items[1:]

    def if_else(self, items):
        return "if_else", items

    def KEYWORD(self, items):
        return str(items)

    def label_tree(self, items):
        key = items[0][1]
        tree = items[1:]
        self.addtoLabels(key, tree)
        return ("label_tree", (key, tree))

    def label_line(self, items):
        assert len(items) == 1
        return ("label_line", items[0])

    def say_line(self, items):
        character, sayline = ("", "")
        if len(items) == 1:
            sayline = str(items[0])[1:-1]
        elif len(items) == 2:
            character = str(items[0])
            if character in self.objs:
                character = str(self.objs[character])
            sayline = str(items[1])[1:-1]
        else:
            assert False, "Unkown say_line structure"
        sayline = self.resolve_characters(sayline)
        return ("say_line", (character, sayline))

    def code_line_def(self, token):
        assert (len(token) == 1)
        exp = str(token[0]).strip()

        # Some checks to limit code injection threats: TODO find safer way
        check = re.compile(r'^(?P<key>[^ ]+) = (?P<exp>Character\([^(;)]+\)) *$')
        m = check.search(exp)
        if m:
            key, val = m.group('key'), m.group('exp')
            if (val.startswith("Character(")):
                val = eval(val)
                self.addtoObjs(key, val)
                return "code_line", f"// {exp}"

        assert False, f"Cannot parse def code line: [{exp}]"

    def code_line_var(self, token):
        assert (len(token) == 1)
        exp = str(token[0]).strip()
        return "code_line", exp
