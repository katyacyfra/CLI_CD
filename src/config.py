class CommandManager:
    """Prepares commands and arguments for execution"""
    env_variables = {}

    def __init__(self):
        pass

    def process_input(self, tree):
        return tree.root.execute()


cm = CommandManager()

command_list = ['echo', 'cat', 'pwd', 'wc', 'exit', 'VAR', 'EQ']

