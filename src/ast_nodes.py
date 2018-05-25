from executor import *
from config import command_list


class AST:
    def __init__(self):
        self.root = ResultNode("")

    def walk(self):
        pass


class Node:
    def __init__(self, value):
        self.value = value

    def execute(self):
        return self.value


class ResultNode(Node):
    def __init__(self, value):
        self.value = value
        self.children = []

    def execute(self):
        self.value = self.children[0].execute()
        return self.value


class StringQNode(Node):
    def __init__(self, value):
        self.value = value
        self.children = []

    def execute(self):
        return self.value


class StringDQNode(Node):
    def __init__(self, value):
        self.value = value
        self.children = []

    def execute(self):
        self.value = ""
        for i in self.children:
            self.value += i.execute()
        return self.value


class CommandNode(Node):
    def __init__(self, command):
        self.command = command
        self.children = []

    def execute(self):
        args = []
        for i in self.children:
            args.append(i.execute())
        return Executor(self.command, args).run()


class GrepNode(CommandNode):
    def __init__(self, nm, read_from_stdin):
        self.command = 'grep'
        self.children = []
        self.namespace = vars(nm)
        self.read_from_stdin = read_from_stdin

    def execute(self):
        arg = ""
        if self.read_from_stdin:
            for c in self.children:
                arg = c.execute()
            self.namespace['contents'] = arg
        return GrepEx(self.namespace).run()
