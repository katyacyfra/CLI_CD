from ast_nodes import AST, StringQNode, ResultNode, StringDQNode, CommandNode, GrepNode
import argparse


class ASTParser:
    """Parses string to the list of arguments"""

    def __init__(self, s):
        self.s = s
        self.result = []
        self.index = 0
        self.end = len(s)
        self.tree = AST()
        self.main_parse()

    def main_parse(self):
        res = ""
        tokens = []
        current_node = self.tree.root
        while self.index < self.end:

            if self.s[self.index] == ' ':
                self.index = self.index + 1
                res = res.replace(" ", "")
                if res != "":
                    if isinstance(current_node, CommandNode):
                        new_node = StringQNode(res)
                        current_node.children.append(new_node)
                    else:
                        if res == 'grep':
                            new_node = self.parse_grep(current_node)
                        else:
                            new_node = CommandNode(res)
                        current_node.children.append(new_node)
                        current_node = new_node
                res = ""

            elif self.s[self.index] == "'":
                self.index = self.index + 1
                try:
                    new_node = self.parse_q_strong()
                except:
                    raise ValueError("No closing quote!")
                if isinstance(current_node, CommandNode):
                    current_node.children.append(new_node)
                res = ""

            elif self.s[self.index] == '"':
                self.index = self.index + 1
                try:
                    new_node = self.parse_q_weak()
                    res = ""
                except:
                    raise ValueError("No closing quote!")
                if isinstance(current_node, CommandNode):
                    current_node.children.append(new_node)
                res = ""

            elif self.s[self.index] == '$':
                self.index = self.index + 1
                new_node = self.parse_var()
                current_node.children.append(new_node)
                if isinstance(current_node, ResultNode):
                    current_node = new_node
                res = ""

            elif self.s[self.index] == '=':
                self.index = self.index + 1
                value = self.parse_assign()
                new_node = CommandNode('EQ')
                new_node.children.append(StringQNode(res))
                new_node.children.append(value)
                current_node.children.append(new_node)
                res = ""

            elif self.s[self.index] == '|':
                self.index = self.index + 1
                if res != "":
                    if isinstance(current_node, ResultNode):
                        current_node.children.append(CommandNode(res))
                    else:
                        current_node.children.append(StringQNode(res))

                res = ""
                current_node = self.tree.root
            else:
                res += self.s[self.index]
                self.index = self.index + 1
        res = res.replace(" ", "")
        if res != "":
            if isinstance(current_node, CommandNode):
                new_node = StringQNode(res)
                current_node.children.append(new_node)
            else:
                new_node = CommandNode(res)
                current_node.children.append(new_node)
                current_node = new_node
        if len(self.tree.root.children) > 1:  # there is a pipe, let's transform tree
            children = self.tree.root.children
            self.tree.root.children = []
            current_node = self.tree.root
            while len(children) > 0:
                new_node = children.pop()
                current_node.children.append(new_node)
                current_node = new_node

    def parse_assign(self):
        """ Parses assignment FILE=example.txt """
        if self.s[self.index] == '"':
            self.index = self.index + 1
            var = self.parse_q_weak()
        elif self.s[self.index] == "'":
            self.index = self.index + 1
            var = self.parse_q_strong()
        else:
            var = ""
            while self.index < self.end and self.s[self.index] != ' ':
                var += self.s[self.index]
                self.index = self.index + 1
            var = StringQNode(var)
            self.index = self.index + 1
        return var
        # CManager.env_variables[last] = var

    def parse_var(self):
        """ Parses $VAR """
        var = ""
        result = CommandNode('VAR')
        while self.index < self.end and (self.s[self.index]).isalnum():
            var += self.s[self.index]
            self.index = self.index + 1
        result.children.append(StringQNode(var))
        return result

    def parse_q_strong(self):
        """Parses strong quoting"""
        res = ""
        in_ordinary = ""
        while self.index < self.end and self.s[self.index] != "'":
            in_ordinary += self.s[self.index]
            self.index = self.index + 1

        if self.index == self.end and self.s[self.index - 1] != "'":
            raise ValueError('No closing quote!')
        else:
            self.index = self.index + 1
            res += (in_ordinary)
            return StringQNode(res)

    def parse_q_weak(self):
        """Parses weak quoting"""
        res = StringDQNode("")
        in_double = ""
        while self.index < self.end and self.s[self.index] != '"':
            if self.s[self.index] == '$':
                self.index = self.index + 1
                if in_double != '':
                    res.children.append(StringQNode(in_double))
                    in_double = ""
                var = self.parse_var()
                res.children.append(var)
                in_double = ""
            else:
                in_double += self.s[self.index]
                self.index = self.index + 1
        if self.index == self.end and self.s[self.index - 1] != '"':
            raise ValueError('No closing quote!')
        else:
            self.index = self.index + 1
        if in_double != '':
            res.children.append(StringQNode(in_double))
        return res

    def parse_grep(self, current):
        parser = argparse.ArgumentParser()
        args = []
        res = ""
        if len(self.tree.root.children) == 0:
            read_from_stdin = False
        else:
            read_from_stdin = True

        while self.index < self.end and self.s[self.index] != '|':
            if self.s[self.index] == ' ':
                self.index = self.index + 1
                args.append(res)
                res = ""
            else:
                res += self.s[self.index]
                self.index = self.index + 1

        if self.index < self.end and self.s[self.index] == '|':
            self.index = self.index - 1
        res = res.replace(' ', '')
        if res != '':
            args.append(res)
        if read_from_stdin == False:
            parser.add_argument('-i', action="store_true", default=False)
            parser.add_argument('-w', action="store_true", default=False)
            parser.add_argument('-A', action="store", default=0, type=int)
            parser.add_argument("pattern", type=str, help="pattern")
            parser.add_argument("file", type=str, help="file")
        else:
            parser.add_argument('-i', action="store_true", default=False)
            parser.add_argument('-w', action="store_true", default=False)
            parser.add_argument('-A', action="store", default=0, type=int)
            parser.add_argument("pattern", type=str, help="pattern")
        namespace = parser.parse_args(args)
        node = GrepNode(namespace, read_from_stdin)
        return node
