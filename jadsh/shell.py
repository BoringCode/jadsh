# jadsh

import os
import sys
import importlib
import re
import shlex
from jadsh.prompt import Prompt
from jadsh.constants import *

class Shell():
 
    def __init__(self, prompt = Prompt(), status = SHELL_STATUS_RUN):
        self.status = status
        self.prompt = prompt
        self.builtins = {}
        self.history = []
        
        self.loop()

    def loop(self):
        while self.status == SHELL_STATUS_RUN:
            self.title("jadsh " + os.getcwd())

            # Draw the prompt
            self.prompt.draw()

            # Grab user input
            try:
                user_input = sys.stdin.readline()
            except KeyboardInterrupt:
                user_input = "exit"

            # Help the user
            if self.syntax_check(user_input) == False:
                continue
           
            # Allow commands to be split (so user can enter multiple commands at once)
            commands = re.split('[;]+', user_input)
            for cmd in commands:
                # Get tokens from user input
                tokens = self.tokenize(cmd)

                # Execute command
                try:
                    self.status = self.execute(tokens)
                except OSError as e:
                    print(self.hilite("jadsh error: ") + str(e))
                    return

    def execute(self, tokens):
        if len(tokens) == 0: return SHELL_STATUS_RUN

        command = tokens[0]
        args = tokens[1:]

        # Check if builtin command
        if self.builtin(command):
            return self.builtins[command].execute(self, *args)
       
        # Fork to child process
        pid = os.fork()

        if pid == 0:
            os.execvp(command, tokens)
        elif pid > 0:
            while True:
                wpid, status = os.waitpid(pid, 0)

                if os.WIFEXITED(status) or os.WIFSIGNALED(status):
                    break
        
        self.history.append({ "command": command, "args": args })

        # Assume all went well, continue
        return SHELL_STATUS_RUN

    def builtin(self, command):
        if command in self.builtins: return True
        try:
            mod = importlib.import_module("jadsh.builtins." + command)
            obj = getattr(mod, command)()
            self.builtins[command] = obj
            return True
        except ImportError:
            return False
    
    def tokenize(self, command):
        return shlex.split(command)

    def hilite(self, string, status = False, bold = False):
        attr = []
        if status:
            # green
            attr.append('32')
        else:
            # red
            attr.append('31')
        if bold:
            attr.append('1')
        return '\x1b[%sm%s\x1b[0m' % (';'.join(attr), string)

    def syntax_check(self, user_input):
        if "&&" in user_input:
            print(self.hilite("Unsupported use of &&.") + " In jadsh, please use 'COMMAND; and COMMAND'")
            return False

    def title(self, title):
        sys.stdout.write("\x1b]2;" + title + "\x07")
