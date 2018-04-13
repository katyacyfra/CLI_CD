import os, sys
import subprocess

class Parser:
    """Parses string to the list of arguments"""
    def __init__(self, s):
        self.s = s
        self.result = []
        self.index = 0
        self.end = len(s)
        self.main_parse()

    def main_parse(self):
        res=""
        tokens=[]
        while self.index < self.end:
            if self.s[self.index] == ' ':
                self.index = self.index + 1
                if res != "":
                    tokens.append(res)
                res = ""

            elif self.s[self.index] == "'":
                self.index = self.index + 1
                try:
                    res = self.parse_q_strong()
                    tokens.append(res)
                    res=""
                except:
                    self.index = self.end #stop parsing
                    res = ""
                    tokens = []
                    break

            elif self.s[self.index] == '"':
                self.index = self.index + 1
                try:
                    res = self.parse_q_weak()
                    tokens.append(res)
                    res=""
                except:
                    self.index = self.end #stop parsing
                    res = ""
                    tokens = []
                    break

            elif self.s[self.index] == '$':
                self.index = self.index + 1
                if res !="":
                    res = ""
                    tokens.append(res)
                res = self.parse_var()
                tokens.append(res)
                res =""

            elif self.s[self.index] == '=':
                self.index = self.index + 1
                tokens.append("EQ")
                if res != "":
                    tokens.append(res)
                var = self.parse_assign(res)
                tokens.append(var)
                res = ""

            elif self.s[self.index] == '|':
                self.index = self.index + 1
                if res != "":
                    tokens.append(res)
                res = ""
                self.result.append(tokens)
                tokens = []
            else:
                res+=self.s[self.index]
                self.index = self.index + 1
        if res != "":
            tokens.append(res)
        if tokens: self.result.append(tokens)

    def parse_assign(self, last):
        """ Parses assignment FILE=example.txt """
        var = ""
        if self.s[self.index] == '"':
            self.index = self.index + 1
            var = self.parse_q_weak()
        elif self.s[self.index] == "'":
            self.index = self.index + 1
            var = self.parse_q_strong()
        else:
            while self.index < self.end and self.s[self.index] != ' ':
                var+=self.s[self.index]
                self.index = self.index + 1
            self.index = self.index + 1
        return var
        #CManager.env_variables[last] = var

    def parse_var(self):
        """ Parses $VAR """
        var = ""
        result = ['VAR']
        while self.index < self.end and (self.s[self.index]).isalnum():
            var+=self.s[self.index]
            self.index = self.index + 1
        result.append(var)
        return result

    def parse_q_strong(self):
        """Parses strong quoting"""
        res = []
        in_ordinary = ""
        while self.index < self.end and self.s[self.index] != "'":
            in_ordinary+=self.s[self.index]
            self.index = self.index + 1

        if self.index == self.end and self.s[self.index-1] != "'":
            print('No closing quote!')
            raise ValueError('No closing quote!')
        else:
            self.index = self.index + 1
            res.append(in_ordinary)
            return res

    def parse_q_weak(self):
        """Parses weak quoting"""
        res = []
        in_double = ""
        while self.index < self.end and self.s[self.index] != '"':
            if self.s[self.index] == '$':
                self.index = self.index + 1
                var = self.parse_var()
                if in_double!="":
                    res.append(in_double)
                res.append(var)
                in_double = ""
            else:
                in_double+= self.s[self.index]
                self.index = self.index + 1
        if self.index == self.end and self.s[self.index-1] != '"':
             raise ValueError('No closing quote!')
        else:
            self.index = self.index + 1
        res.append(in_double)
        return res

class CManager:
    """Prepares commands and arguments for execution"""
    env_variables = {}
    def __init__(self):
        pass

    def get_args_number(self, method):
        try:
            return Executor.count_args[method]
        except:
            print('No such method in parameters dictionary - return 0')
            return 0

    def get_command(self, command):
        if hasattr(OrdinaryEx, '_'+command):
            obj = OrdinaryEx()
            method = getattr(obj,'_'+command )
            obj.count_args = self.get_args_number(method.__name__)
        elif hasattr(OneCommand,'_'+command):
            obj = OneCommand()
            method = getattr(obj,'_'+command )
            obj.count_args = self.get_args_number(method.__name__)
        elif hasattr(Environment,'_'+command):
            obj = Environment()
            method = getattr(obj,'_'+command )
            obj.count_args = self.get_args_number(method.__name__)
        else:
            obj = JustString(command)
        return obj

    def process_input(self, input):
        result = JustString()
        if not isinstance(input, list):
            return JustString(input)
        #pipe
        if all(isinstance(el, list) for el in input) and len(input):
            arg = None
            for i in input:
                if arg:
                    i.append(arg)
                arg=i
            input = input[-1]
        i = 0
        while (i < len(input)):
            if isinstance(input[i], list):
                result = self.process_input(input[i])
            else:
                obj = self.get_command(input[i])
                if isinstance(obj, JustString):
                    if i == 0 and len(input) > 1:#unknown command
                        i = i + 1
                        while i < len(input):
                            if input[i] == 'EQ':#come back to binary op
                                input[i] = input[i+1]
                                input[i+1] = '='
                                i = i+1
                            i = i + 1
                        try:
                            obj = ProcessEx(input)
                        except FileNotFoundError:
                            print("Unknown command")
                            obj = ErrorExecution()
                        except:
                            print("Process error:", sys.exc_info()[0])
                            obj = ErrorExecution()
                    return obj
                if isinstance(obj, ErrorExecution):
                    result = obj
                    break
                else:
                    method = getattr(obj,'_' + input[i])
                    end = i + obj.count_args
                    args = []
                    i = i+1
                    if end >= len(input):
                        try:
                            raise ValueError()
                        except:
                            print('Not enough arguments for', method.__name__[1:])
                            result = ErrorExecution()
                            break
                    if end == -1: end = len(input) - 1
                    while i <=end:
                        args.append(self.process_input(input[i]))
                        i = i+1
                    try:
                        method(args)
                        result = obj
                        if isinstance(obj, Environment):
                            result = self.process_input([obj.output])
                    except KeyError:
                        print("No such variable ", args[0], " in environment")
                        result = ErrorExecution()
                        break
                    except FileNotFoundError:
                        print("No such file or directory: ", args[0].output)
                        result = ErrorExecution()
                        break
            i = i+1
        return result

class Executor:
    #args number dictionary, -1 - takes all args in list
    count_args = {'_echo': -1,
                  '_cat': 1,
                  '_EQ': 2,
                  '_VAR': 1,
                  '_pwd': 0,
                  '_ls': 0,
                  '_cd': 1,
                  '_wc': 1,
                  '_exit': 0}
    def __init__(self):
        self.output = ""

    def print_o(self):
        print(self.output)

class OrdinaryEx(Executor):
    def __init__(self):
        self.count_args = 1
        self.output = ""
    def _echo(self, arg):
        for i in arg:
            self.output+=i.output+' '
        self.output = self.output[:-1]
    def _cat(self, arg):
        if isinstance(arg[0], JustString):#read file
            with open(arg[0].output) as f:
                for line in f:
                   self.output+=line+'\n '
        else:#read stdin
            self.output = arg[0].output
    def _wc(self, arg):
        def count_all(l):
            counts = []
            counts.append(len(l))
            words = sum([len(line.split()) for line in l])
            counts.append(words)
            return counts

        if isinstance(arg[0], JustString):#read file
            with open(arg[0].output, 'r') as fi:
                lw = count_all(list(fi))
            size = os.path.getsize(arg[0].output)
            self.output = "%d %d %d" % (lw[0], lw[1], size)
        else:#read from stdin
            size = 0
            cont = []
            input = arg[0].output.splitlines()
            for line in list(input):
                if line != ' ':
                    size += len(line.encode("utf8"))
                    cont.append(line)
            lw = count_all(cont)
            self.output = "%d %d %d" % (lw[0], lw[1], size)
    def _EQ(self,arg):
        CManager.env_variables[arg[0].output] = arg[1].output

    def _cd(self, arg):
        """
        Changes the directory of shell to the passed relative directory.

        :param arg: expected to have one argument which is target directory.
        """
        dir = arg[0].output
        os.chdir(dir)
        self.output = ""


class Environment(Executor):
    def __init__(self):
        pass
    def _VAR(self, arg):
        try:
            self.output = CManager.env_variables[arg[0].output]
        except:
            raise KeyError

class OneCommand(Executor):
    def __init__(self):
        self.output = ""
    def _exit(self, arg):
        print("CLI will be closed...Bye!")
        sys.exit()
    def _pwd(self, arg):
        self.output = os.getcwd()

    def _ls(self, arg):
        self.output = '\n'.join(os.listdir())

class JustString(Executor):
    """String behavior"""
    def __init__(self, value=""):
        self.output = value
    def concat(self, value):
        self.output += value

class ErrorExecution(Executor):
    """Smth went wrong"""
    def __init__(self):
        self.output = ''

class ProcessEx:
    """Input to shell"""
    def __init__(self,input):
        out = subprocess.Popen(input, stdout=subprocess.PIPE)
        self.output = out.communicate()[0]
        try:
            self.output =  self.output.decode('utf-8')
        except UnicodeDecodeError:
            pass

def main():
    cm = CManager()
    while True:
        st = input("Enter the command: ")
        p = Parser(st)
        res = cm.process_input(p.result)
        if isinstance(res, JustString): #try to call shell
            try:
                res = ProcessEx(p.result[0])
            except FileNotFoundError:
                print("Unknown command")
                res.output = ''
            except:
                print("Unknown command", sys.exc_info()[0])
                res.output = ''
        print(res.output)

if __name__ == '__main__':
    main()
