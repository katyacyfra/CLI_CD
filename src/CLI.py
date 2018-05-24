import os, sys
import subprocess
from config import cm

from ast_parser import ASTParser
from ast_nodes import *


def main():
    while True:
        st = input("Enter the command: ")
        p = ASTParser(st)
        res = cm.process_input(p.tree)
        print(res)


if __name__ == '__main__':
    main()