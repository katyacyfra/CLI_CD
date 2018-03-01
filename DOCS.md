# Documentation

CLI.py - simple command line interpreter.

## Classes and methods

Parser: parses input string to the list of commands.
Examples:
"echo Hello" -> [['echo', 'Hello' ]]
"echo 123| cat" -> [['echo', '123'], ['cat']]
"x=test" -> [['EQ', 'x', 'test']]
"$x" -> [[]]
See more examples in tests.py

CManager: takes parsed input and executes it by calling methods from chid classes of Executor whith proper number of arguments. Also contains dictionary with environment variables. It controls exceptions via printing error cause and ending execution of current commands. 

Executor: contains output of child classes commands and information about required number of arguments for all methods

Child classes of Executor:

OrdinaryEx: implements commands whith arguments:cat, wc, echo, assignment of variable (_EQ).
OneCommand: implements commands with no arguments: exit, pwd.
Environment: takes value of variable from environment (method _VAR)
JustString: implements string behaviour for non-command arguments
ProcessEx: if command is unknown tries to get output from system via Process
ErrorExecution: returns itself in case of execution errors