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
        self.assertEqual(res, 'text test\n ')


    def test_wc(self):
        p = ASTParser('wc example.txt')
        res = self.cm.process_input(p.tree)
        self.assertEqual(res, '1 2 9')

    def test_wc_file(self):
        p = ASTParser('cat example.txt | wc')
        res = self.cm.process_input(p.tree)
        self.assertEqual(res, '1 2 9')

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


if __name__ == '__main__':
    unittest.main()

