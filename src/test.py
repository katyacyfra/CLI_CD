import unittest
import os
import CLI
from config import cm
from ast_parser import ASTParser


class TestAll(unittest.TestCase):
    def setUp(self):
        self.cm = cm

    def test_echo(self):
        p = ASTParser('echo "Hello, world!"')
        res = self.cm.process_input(p.tree)
        self.assertEqual("Hello, world!", res)

    def test_assignment(self):
        p = ASTParser('FILE=example.txt')
        res = self.cm.process_input(p.tree)
        self.assertEqual(self.cm.env_variables['FILE'], "example.txt")  # added to environment variables
        self.assertEqual(res, '')

    def test_pwd(self):
        p = ASTParser('pwd')
        res = self.cm.process_input(p.tree)
        self.assertEqual(res, os.getcwd())

    def test_cat_subst(self):
        p = ASTParser('FILE=example.txt')
        res = self.cm.process_input(p.tree)
        p = ASTParser('cat $FILE')
        res = self.cm.process_input(p.tree)
        self.assertEqual('text test\n\nHello, world\n\nPython rules test\n\nhell\n\nhahe\n', res)


    def test_wc(self):
        p = ASTParser('wc example.txt')
        res = self.cm.process_input(p.tree)
        self.assertEqual('5 9 54', res)

    def test_wc_file(self):
        p = ASTParser('cat example.txt | wc')
        res = self.cm.process_input(p.tree)
        self.assertEqual('9 9 46', res)

    def test_wc_input(self):
        p = ASTParser('echo 123 | wc')
        res = self.cm.process_input(p.tree)
        self.assertEqual(res, '1 1 3')

    def test_big_pipe(self):
        p = ASTParser('echo "Hello"| cat|cat')
        res = self.cm.process_input(p.tree)
        self.assertEqual(res, "Hello")

    def test_var_command(self):
        p = ASTParser('x=pwd')
        res = self.cm.process_input(p.tree)
        p = ASTParser('$x')
        res = self.cm.process_input(p.tree)
        self.assertEqual(os.getcwd(), res)

    def test_var_command_arg(self):
        p = ASTParser('y=echo')
        res = self.cm.process_input(p.tree)
        p = ASTParser('$y 123')
        res = self.cm.process_input(p.tree)
        self.assertEqual('123', res)

    def test_calling_shell(self):
        p = ASTParser('ping -W 2 -c 1 192.168.1.70')
        res = self.cm.process_input(p.tree)
        print(res)

    def test_echo_quotes(self):
        p = ASTParser('x=1')
        res = self.cm.process_input(p.tree)
        p = ASTParser('echo "$x"')
        res = self.cm.process_input(p.tree)
        self.assertEquals('1', res)

    def test_echo_quotes_again(self):
        p = ASTParser('x=1')
        res = self.cm.process_input(p.tree)
        p = ASTParser('echo "1$x"')
        res = self.cm.process_input(p.tree)
        self.assertEquals('11', res)


class TestASTParser(unittest.TestCase):
    def test_ast_simple(self):
        p = ASTParser('echo 1 2')
        self.assertEqual('1', p.tree.root.children[0].children[0].value)
        self.assertEqual('2', p.tree.root.children[0].children[1].value)

    def test_ast_single_quotes(self):
        p = ASTParser("echo 'test just test'")
        self.assertEqual('test just test', p.tree.root.children[0].children[0].value)

    def test_ast_var(self):
        p = ASTParser("echo $x")
        self.assertEqual('VAR', p.tree.root.children[0].children[0].command)
        self.assertEqual('x', p.tree.root.children[0].children[0].children[0].value)

    def test_ast_assign(self):
        p = ASTParser("x=6")
        self.assertEqual('EQ', p.tree.root.children[0].command)
        self.assertEqual('x', p.tree.root.children[0].children[0].value)
        self.assertEqual('6', p.tree.root.children[0].children[1].value)

        p = ASTParser("x='file.txt'")
        self.assertEqual('file.txt', p.tree.root.children[0].children[1].value)

    def test_ast_double_quotes(self):
        p = ASTParser('echo "x"')
        self.assertEqual('x', p.tree.root.children[0].children[0].children[0].value)

        p = ASTParser('echo "$x"')
        self.assertEqual('VAR', p.tree.root.children[0].children[0].children[0].command)
        self.assertEqual('x', p.tree.root.children[0].children[0].children[0].children[0].value)

        p = ASTParser('echo "1$x"')
        self.assertEqual(2, len(p.tree.root.children[0].children[0].children))
        self.assertEqual('1', p.tree.root.children[0].children[0].children[0].value)
        self.assertEqual('VAR', p.tree.root.children[0].children[0].children[1].command)
        self.assertEqual('x', p.tree.root.children[0].children[0].children[1].children[0].value)

    def test_ast_pipe(self):
        p = ASTParser('cat x.txt|wc|cat example.txt|wc  ')
        self.assertEqual('wc', p.tree.root.children[0].command)
        self.assertEqual('example.txt', p.tree.root.children[0].children[0].children[0].value)


class TestGrep(unittest.TestCase):
    def setUp(self):
        self.cm = cm

    def test_ast_grep(self):
        p = ASTParser('grep -i -A 3 test test.txt')
        self.assertEqual('grep', p.tree.root.children[0].command)
        self.assertEqual(3, p.tree.root.children[0].namespace['A'])
        self.assertEqual('test', p.tree.root.children[0].namespace['pattern'])

        p = ASTParser('grep test test.txt')
        self.assertEqual(0, p.tree.root.children[0].namespace['A'])
        self.assertEqual(False, p.tree.root.children[0].namespace['i'])

    def test_simple_grep(self):
        p = ASTParser('grep text example.txt')
        res = self.cm.process_input(p.tree)
        self.assertEqual("text test", res)

    def test_multiple_strings(self):
        p = ASTParser('grep test example.txt')
        res = self.cm.process_input(p.tree)
        self.assertEqual("text test\nPython rules test", res)

    def test_ignore_case(self):
        p = ASTParser('grep -i hello example.txt')
        res = self.cm.process_input(p.tree)
        self.assertEqual("Hello, world", res)

    def test_whole_word(self):
        p = ASTParser('grep -i hell example.txt')
        res = self.cm.process_input(p.tree)
        self.assertEqual("Hello, world\nhell", res)

        p = ASTParser('grep -i -w hell example.txt')
        res = self.cm.process_input(p.tree)
        self.assertEqual("hell", res)

    def test_lines_after(self):
        p = ASTParser('grep world -A 2 example.txt')
        res = self.cm.process_input(p.tree)
        self.assertEqual("Hello, world\nPython rules test\nhell", res)

    def test_regexp(self):
        p = ASTParser('grep -i he example.txt')
        res = self.cm.process_input(p.tree)
        self.assertEqual("Hello, world\nhell\nhahe", res)

        p = ASTParser('grep -i ^he example.txt')
        res = self.cm.process_input(p.tree)
        self.assertEqual("Hello, world\nhell", res)

    def test_pipe(self):
        p = ASTParser('cat example.txt|grep -i he')
        res = self.cm.process_input(p.tree)
        self.assertEqual("Hello, world\nhell\nhahe", res)

        p = ASTParser('cat example.txt|grep -i he|grep ha')
        res = self.cm.process_input(p.tree)
        self.assertEqual("hahe", res)


if __name__ == '__main__':
    unittest.main()

