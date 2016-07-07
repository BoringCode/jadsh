# jadsh

import os
import sys
import importlib
import re
import shlex
from jadsh.prompt import Prompt
import jadsh.constants as constants

class Shell():
 
    def __init__(self, prompt = Prompt(), status = constants.SHELL_STATUS_RUN):
        self.status = status
        self.prompt = prompt
        self.builtins = {}
        self.history = []
        self.environment = {}

        self.loop()

    def loop(self):
        while self.status == constants.SHELL_STATUS_RUN:
            self.title("jadsh " + os.getcwd())

            # Draw the prompt
            self.prompt.draw()

            # Grab user input
            try:
                user_input = sys.stdin.readline()
            except KeyboardInterrupt:
                sys.stdout.write("\n")
                continue
            except IOError:
                user_input = "exit"

            if not user_input:
                user_input = "exit"
           
            # Allow commands to be split (so user can enter multiple commands at once)
            commands = re.split('[;]+', user_input)
            for cmd in commands:
                # Help the user
                if self.syntax_check(cmd) == False:
                    continue

                # Get tokens from user input
                tokens = self.tokenize(cmd)

                # Execute command
                try:
                    self.status = self.execute(tokens)
                except OSError as e:
                    self.message("jadsh error", str(e))
                    return
                except KeyboardInterrupt:
                    continue

    def execute(self, tokens):
        if len(tokens) == 0: return constants.SHELL_STATUS_RUN

        command = tokens[0]
        args = tokens[1:]

        # Check if builtin command
        if self.builtin(command):
            return self.builtins[command].execute(*args)
       
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
        return constants.SHELL_STATUS_RUN

    def builtin(self, command):
        if command in self.builtins: return True
        try:
            mod = importlib.import_module("jadsh.builtins." + command)
            obj = getattr(mod, command)(self)
            self.builtins[command] = obj
            return True
        except ImportError:
            return False
    
    def tokenize(self, command):
        tokens = shlex.split(command)
        return tokens

    def message(self, title, message, status = False):
        sys.stdout.write(self.hilite(title + ": ", status))
        sys.stdout.write(message)
        sys.stdout.write("\n")

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
            self.message("jadsh error", "Unsupported use of &&. In jadsh, please use 'COMMAND; and COMMAND'")
            return False
        if user_input[0] == "$":
            self.message("jadsh error", "Unsupported use of $VARIABLE. In jadsh, variables cannot be used directly. Use 'eval $VARIABLE' instead.")
            return False

    def title(self, title):
        sys.stdout.write("\x1b]2;" + title + "\x07")