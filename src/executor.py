import sys
import os
import subprocess
from config import cm, command_list
import re


class Executor:
    # args number dictionary, -1 - takes all args in list
    def __init__(self, command, args):
        self.output = ""
        self.command = "_" + command
        self.input = command
        self.args = args

        self.count_args = {'_echo': -1,
                           '_cat': 1,
                           '_EQ': 2,
                           '_VAR': 1,
                           '_pwd': 0,
                           '_wc': 1,
                           '_exit': 0,
                           '_grep': 2}

    def run(self):
        if self.command in self.count_args.keys():
            if self.count_args[self.command] > len(self.args) and self.count_args[self.command] != -1:
                raise AttributeError("Argument number is wrong!")
            getattr(self, self.command)(self.args)
            if self.command == '_VAR' and self.output in command_list:
                cname = self.output
                self.output = ""
                self.args = self.args[1:]
                getattr(self, '_' + cname)(self.args)
        else:
            inp = [self.input] + self.args
            self.output = ProcessEx(" ".join(inp)).output
        return self.output

    def _exit(self, arg):
        print("CLI will be closed...Bye!")
        sys.exit()

    def _pwd(self, arg):
        self.output = os.getcwd()

    def _echo(self, arg):
        self.output = ' '.join(arg)

    def _cat(self, arg):
        try:  # read file
            with open(arg[0]) as f:
                for line in f:
                    self.output += line + '\n'
        except:  # read stdin
            self.output = arg[0]

    def _wc(self, arg):
        def count_all(l):
            counts = []
            counts.append(len(l))
            words = sum([len(line.split()) for line in l])
            counts.append(words)
            return counts

        try:  # read file
            with open(arg[0], 'r') as fi:
                lw = count_all(list(fi))
            size = os.path.getsize(arg[0])
            self.output = "%d %d %d" % (lw[0], lw[1], size)
        except:  # read from stdin
            size = 0
            cont = []
            input = arg[0].splitlines()
            for line in list(input):
                if line != ' ':
                    size += len(line.encode("utf8"))
                    cont.append(line)
            lw = count_all(cont)
            self.output = "%d %d %d" % (lw[0], lw[1], size)

    def _EQ(self, arg):
        cm.env_variables[arg[0]] = arg[1]

    def _VAR(self, arg):
        try:
            self.output = cm.env_variables[arg[0]]
        except:
            raise KeyError


class ProcessEx(Executor):
    """Input to shell"""

    def __init__(self, input):
        out = subprocess.Popen(input, stdout=subprocess.PIPE)
        self.output = out.communicate()[0]
        try:
            self.output = self.output.decode('utf-8')
        except UnicodeDecodeError:
            pass


class GrepEx(Executor):
    """ Grep execution"""

    def __init__(self, args):
        self.args = args
        self.output = ""

    def run(self):
        lines_after = self.args['A']
        whole_word = self.args['w']
        ignore_case = self.args['i']
        pattern = self.args['pattern']
        if 'file' in self.args:
            file = self.args['file']

        re_flags = 0
        if ignore_case:
            re_flags |= re.IGNORECASE
        if whole_word:
            pattern = '\\b{}\\b'.format(pattern)

        compiled_pattern = re.compile(pattern, re_flags)

        if 'contents' in self.args:  # from stdin
            lines = self.args['contents'].splitlines()
        else:
            f = open(file, 'r')
            lines = f.read().splitlines()
            f.close()
        for i, line in enumerate(lines):
            if re.search(compiled_pattern, line):
                for ln in lines[i:i + 1 + lines_after]:
                    if lines_after > 0:
                        self.output += ln + '\n'
                    else:
                        self.output += ln
                if lines_after == 0:
                    self.output += '\n'
        self.output = self.output[:-1]
        return self.output




