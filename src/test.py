from CLI import Parser, CManager
import unittest
import os
from unittest import mock

class TestParser(unittest.TestCase):
  def test_dquotes(self):
      p = Parser('echo "Hello, world"')
      self.assertEqual(p.result, [['echo', ['Hello, world']]])

  def test_squotes(self):
      p = Parser("echo   'Hello '")
      self.assertEqual(p.result, [['echo', ['Hello ']]])

  def test_assign(self):
      p = Parser("FILE=example.txt")
      self.assertEqual(p.result, [["EQ","FILE", "example.txt"]])

  def test_subst(self):
      p = Parser("cat $FILE")
      self.assertEqual(p.result, [['cat', ['VAR', 'FILE']]])

  def test_subst_string(self):
      p = Parser('echo "  $HELLO, world"')
      self.assertEqual(p.result, [['echo', ['  ', ['VAR', 'HELLO'], ', world']]])

  def test_subst_string_no_var(self):
      p = Parser('echo " __ $R, world"')
      self.assertEqual(p.result, [['echo', [' __ ', ['VAR', 'R'], ', world']]])

  def test_pipe(self):
      p = Parser('cat x.txt | wc| cat example.txt|wc  ')
      self.assertEqual(p.result, [['cat', 'x.txt'], ['wc'], ['cat', 'example.txt'], ['wc']])

  def test_assign_q(self):
      p = Parser("FILE='example.txt'")
      self.assertEqual(p.result, [['EQ', 'FILE', ['example.txt']]])


class TestAll(unittest.TestCase):
  def setUp(self):
      self.cm = CManager()

  def test_echo(self):
      p = Parser('echo "Hello, world!"')
      res = self.cm.process_input(p.result)
      self.assertEqual(res.output, "Hello, world!")

  def test_assignment(self):
      p = Parser('FILE=example.txt')
      res = self.cm.process_input(p.result)
      self.assertEqual(self.cm.env_variables['FILE'], "example.txt" )# added to environment variables
      self.assertEqual(res.output, '')

  def test_pwd(self):
      p = Parser('pwd')
      res = self.cm.process_input(p.result)
      self.assertEqual(res.output, os.getcwd())

  ls_files_mock = ["file1", "file2", "file3"]

  @mock.patch("os.listdir", return_value=ls_files_mock)
  def test_ls(self, listdir_mock: mock.Mock):
      p = Parser("ls")
      res = self.cm.process_input(p.result)

      self.assertEqual(res.output, '\n'.join(TestAll.ls_files_mock))

  @mock.patch("os.chdir")
  def test_cd(self, chdir_mock: mock.Mock):
      p = Parser("cd directory")
      self.cm.process_input(p.result)

      chdir_mock.assert_called_once_with("directory")

  def test_cat_subst(self):
      p = Parser('cat $FILE')
      res = self.cm.process_input(p.result)
      self.assertEqual(res.output, 'text test\n ')

  def test_cat_no_file(self):
      p = Parser('cat no_such_file.txt|cat')
      res = self.cm.process_input(p.result)
      self.assertEqual(res.output, '')

  def test_wc(self):
      p = Parser('wc example.txt')
      res = self.cm.process_input(p.result)
      self.assertEqual(res.output, '1 2 9')

  def test_wc_file(self):
      p = Parser('cat example.txt | wc')
      res = self.cm.process_input(p.result)
      self.assertEqual(res.output, '1 2 9')

  def test_wc_input(self):
      p = Parser('echo 123 | wc')
      res = self.cm.process_input(p.result)
      self.assertEqual(res.output, '1 1 3')

  def test_big_pipe(self):
      p = Parser('echo "Hello"| cat|cat')
      res = self.cm.process_input(p.result)
      self.assertEqual(res.output, "Hello")

  def test_var_command(self):
      p = Parser('x=pwd')
      res = self.cm.process_input(p.result)
      p = Parser('$x')
      res = self.cm.process_input(p.result)
      self.assertEqual(res.output, os.getcwd())

  def test_var_command_arg(self):
      p = Parser('y=echo')
      res = self.cm.process_input(p.result)
      p = Parser('$y 123')
      res = self.cm.process_input(p.result)
      self.assertEqual(res.output, '123')

  def test_calling_shell(self):
      p = Parser('ping -W 2 -c 1 192.168.1.70')
      res = self.cm.process_input(p.result)
      print(res.output)

if __name__ == '__main__':
    unittest.main()

