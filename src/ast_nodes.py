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
