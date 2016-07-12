# jadsh

import sys
import os
import importlib
import re
import shlex
from jadsh.getch import Getch
from jadsh.prompt import Prompt
import jadsh.constants as constants

class Shell(): 
    def __init__(self, prompt = Prompt(), status = constants.SHELL_STATUS_RUN):
        self.status = status
        self.prompt = prompt
        self.builtins = {}
        self.history = []
        self.environment = {}

        self.getch = Getch()

        self.loop()

    def loop(self):
        current_command = ""
        current_char = ""
        char_code = -1
        cursor_position = 0
        execute = False
        redraw = True
        while self.status == constants.SHELL_STATUS_RUN:
            # Reset cursor position if current command is empty
            if len(current_command) == 0 or cursor_position < 0: cursor_position = 0
            if cursor_position > len(current_command): cursor_position = len(current_command)

            # Only redraw if necessary
            if redraw:
                # Clear the current line and redraw
                sys.stdout.write("\x1b[2K\r")

                sys.stdout.write(str(cursor_position) + " ")
                sys.stdout.write(str(len(current_command)) + " ")
                if len(current_char) == 1: sys.stdout.write(str(ord(current_char)) + " ")

                # Draw the prompt
                self.prompt.draw()

                # Output what the user has entered so far
                sys.stdout.write(current_command[:cursor_position])
                sys.stdout.write(current_command[cursor_position:])
                sys.stdout.flush()
            # Only write current character if user is just typing text
            else:
                sys.stdout.write(current_char)
                sys.stdout.flush()
                sys.stdout.write(current_command[cursor_position:])
                redraw = True

            # Grab user input
            char_code = self.getch()

            # Escape sequence, handle appropriately
            if char_code >= constants.ARROW_UP:
                print("Esc sequence")
                continue

            current_char = chr(char_code)

            # Error checking
            if len(current_char) == 0:
                continue

            # Backspace
            if char_code == constants.BACKSPACE:
                current_command = current_command[:-1]
                if cursor_position > 0: cursor_position -= 1
            # End of line
            elif char_code == constants.CTRL_C:
                current_command = ""
                sys.stdout.write("\r")
            # End of input
            elif char_code == constants.CTRL_D:
                current_command = "exit"
                execute = True
            # Enter, input command
            elif char_code == constants.ENTER:
                execute = True
                sys.stdout.write("\n")
            # Ignore these keys
            elif char_code == constants.ESC:
                continue
            # Regular input
            else:
                cursor_position += 1
                current_command = current_command[:cursor_position] + current_char + current_command[cursor_position:]
                #redraw = False

            
            # Execute flag has been set, send the current user input to be parsed
            if execute:
                self.parse(current_command)
                current_command = ""
                execute = False

    def parse(self, string):
        # Allow commands to be split (so user can enter multiple commands at once)
        commands = re.split('[;]+', string)
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
                return

    def execute(self, tokens):
        if len(tokens) == 0: return constants.SHELL_STATUS_RUN

        command = tokens[0]
        args = tokens[1:]

        # Check if builtin command
        if self.builtin(command):
            return self.builtins[command].execute(*args)
       
        # Fork to child process
        pid = os.fork()

        # 0 means that I am the child, so I should replace myself with the new program
        if pid == 0:
            os.execvp(command, tokens)
        # I am the parent
        elif pid > 0:
            # Wait for the child to complete before continuing
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
        if not user_input: return True
        if "&&" in user_input:
            self.message("jadsh error", "Unsupported use of &&. In jadsh, please use 'COMMAND; and COMMAND'")
            return False
        if user_input[0] == "$":
            self.message("jadsh error", "Unsupported use of $VARIABLE. In jadsh, variables cannot be used directly. Use 'eval $VARIABLE' instead.")
            return False