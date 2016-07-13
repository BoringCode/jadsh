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
    """
    jadsh, Just A Dumb SHell
    """
    def __init__(self, prompt = Prompt(), status = constants.SHELL_STATUS_RUN):
        """
        Expects a new Prompt object and the status the shell should start with

        Prompt objects allow easy customization of the prompt
        """
        self.status = status
        self.prompt = prompt
        self.builtins = {}
        self.history = []
        self.environment = {}

        # The screen object
        self.ab = ""

        # Grab individual characters from standard input
        self.getch = Getch()

        # Start the main program loop
        self.loop()

    def abAppend(self, string):
        """
        Append new strings to the screen object
        """
        self.ab += str(string)

    def drawScreen(self):
        """
        Draw the terminal so the user can see it
        """
        self.abAppend("\x1b[?25l"); # Hide cursor.

        # Go to beginning of line
        self.abAppend("\x1b[2K\r")

        # Set the terminal title
        title = self.prompt.title("jadsh " + os.getcwd())
        self.abAppend(title)

        # Generate the prompt
        prompt = self.prompt.generate()
        self.abAppend(prompt)

        # Display the current command (what the user is typing)
        self.abAppend(self.current_command)

        self.abAppend("\x1b[?25h") # Show cursor

        # Calculate cursor position and place at correct spot
        position = len(self.current_command) - self.cursor_position
        if position > 0:
            # Move cursor backwards
            self.abAppend("\x1b[" + str(position) + "D")

        # Output everything to the screen
        sys.stdout.write(self.ab)
        sys.stdout.flush()
        self.ab = ""


    def loop(self):
        """
        The main program loop

        Draws terminal screen, gets keyboard input, and executes programs as necessary
        """
        self.current_command = ""
        self.cursor_position = 0
        while self.status == constants.SHELL_STATUS_RUN:
            # Reset cursor position if current command is empty
            if len(self.current_command) == 0 or self.cursor_position < 0: self.cursor_position = 0
            if self.cursor_position > len(self.current_command): self.cursor_position = len(self.current_command)

            # Draw the screen
            self.drawScreen()

            # Keyboard input
            execute = self.keyboardInput()
            
            # Execute flag has been set, send the current user input to be parsed
            if execute:
                self.parse(self.current_command)
                self.cursor_position = 0
                self.current_command = ""

    def keyboardInput(self):
        """
        Grab keyboard input from the terminal and evaluate it as necessary

        @return Boolean
        """
        char_code = -1
        current_char = ""
        execute = False

        # Grab user input
        char_code = self.getch()

        # Escape sequence, handle appropriately
        if char_code >= constants.ARROW_UP:
            if char_code == constants.ARROW_LEFT:
                if self.cursor_position > 0:
                    self.cursor_position -= 1
            elif char_code == constants.ARROW_RIGHT:
                if self.cursor_position < len(self.current_command):
                    self.cursor_position += 1
            # Delete key
            elif char_code == constants.DEL_KEY:
                self.current_command = self.current_command[:self.cursor_position] + self.current_command[self.cursor_position + 1:]
            # Move cursor to end of line
            elif char_code == constants.END_KEY:
                self.cursor_position = len(self.current_command)
            # Move cursor to beginning of line
            elif char_code == constants.HOME_KEY:
                self.cursor_position = 0
            return False

        current_char = chr(char_code)

        # Error checking
        if len(current_char) == 0:
            return False

        # Backspace
        if char_code == constants.BACKSPACE:
            self.current_command = self.current_command[:self.cursor_position - 1] + self.current_command[self.cursor_position:]
            if self.cursor_position > 0: self.cursor_position -= 1
        # End of line
        elif char_code == constants.CTRL_C:
            self.current_command = ""
            sys.stdout.write("\r")
        # End of input
        elif char_code == constants.CTRL_D:
            self.current_command = "exit"
            execute = True
        # Enter, input command
        elif char_code == constants.ENTER:
            execute = True
            sys.stdout.write("\n")
        # Ignore these keys
        elif char_code == constants.ESC:
            return False
        # Regular input
        else:
            self.current_command = self.current_command[:self.cursor_position] + current_char + self.current_command[self.cursor_position:]
            self.cursor_position += 1

        return execute

    def parse(self, string):
        """
        Parse new commands from the user and then pass the commands to be executed
        """
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
        """
        Execute commands from the user

        @return int (a shell status code)
        """
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
        """
        Check if a command is a builtin

        @return Boolean (is a builtin or not)
        """
        # Check if the command has already been loaded as a builtin
        if command in self.builtins: return True
        try:
            # Attempt to load this command as a module. If it doesn't exist, the function will return false
            mod = importlib.import_module("jadsh.builtins." + command)
            # Generate new builtin object (passing this shell as an argument)
            obj = getattr(mod, command)(self)
            self.builtins[command] = obj
            return True
        except ImportError:
            return False
    
    def tokenize(self, command):
        """
        Convert a text command into a list of tokens

        shlex handles special cases (like "multi word strings") that a simple split on spaces can't handle

        @return List
        """
        tokens = shlex.split(command)
        return tokens

    def message(self, title, message, status = False):
        """
        Display message in the terminal
        """
        sys.stdout.write(self.hilite(title + ": ", status))
        sys.stdout.write(message)
        sys.stdout.write("\n")

    def hilite(self, string, status = False, bold = False):
        """
        Generate bold, or colored string using ANSI escape codes

        @return String
        """
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
        """
        Check the syntax of a command from the user

        This is purely a helper function for users who are used to Bash or another shell

        @return Boolean
        """
        if not user_input: return True
        if "&&" in user_input:
            self.message("jadsh error", "Unsupported use of &&. In jadsh, please use 'COMMAND; and COMMAND'")
            return False
        if user_input[0] == "$":
            self.message("jadsh error", "Unsupported use of $VARIABLE. In jadsh, variables cannot be used directly. Use 'eval $VARIABLE' instead.")
            return False
        return True