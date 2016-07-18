import sys
import os
import re

from jadsh.parser import Parser
from jadsh.runner import Runner
from jadsh.getch import Getch
from jadsh.prompt import Prompt
import jadsh.constants as constants

class Shell():
    """
    jadsh, Just Another Dumb SHell
    """
    def __init__(self, prompt = Prompt(), stdin = sys.stdin, stdout = sys.stdout, status = constants.SHELL_STATUS_RUN):
        """
        Expects a new Prompt object and the status the shell should start with

        Prompt objects allow easy customization of the prompt
        """
        self.status = status
        self.prompt = prompt
        self.stdin = stdin
        self.stdout = stdout

        self.runner = Runner(stdin = self.stdin, stdout = self.stdout)
        self.parser = Parser(self.runner)

        self.history = []
        self.history_position = 0

        # The screen object
        self.screenObject = ""

        # Grab individual characters from standard input
        self.getch = Getch(self.stdin)

        # Output welcome message
        self.welcome()

        # Start the main program loop
        self.loop()

    def welcome(self):
        self.stdout.write("Welcome to jadsh, Just Another Dumb SHell\n")
        self.stdout.write("Type %s for instructions on how to use jadsh\n" % self.hilite("help", True))
        self.stdout.flush()

    def screenAppend(self, string):
        """
        Append new strings to the screen object
        """
        self.screenObject += str(string)

    def drawScreen(self):
        """
        Draw the terminal so the user can see it
        """
        if self.stdout.isatty():
            # Reset cursor to previous position
            # TODO: Handle edge case when current line is at the bottom of the terminal
            self.screenAppend("\x1b8")

            # Hide the cursor
            self.screenAppend("\x1b[?25l");

            # Clear everything after the current line
            self.screenAppend("\x1b[J\r")

            # Save the current cursor position
            self.screenAppend("\x1b7")

            # Set the terminal title
            title = self.prompt.title("jadsh %s" % os.getcwd())
            self.screenAppend(title)

        # Generate the prompt
        prompt = self.prompt.generate()
        self.screenAppend(prompt)

        # Display the current input (what the user is typing)
        self.screenAppend(self.user_input)

        if self.stdout.isatty():
            self.screenAppend("\x1b[?25h") # Show cursor

            # Calculate cursor position and place at correct spot
            # TODO: Handle edge case when user input goes to more than 1 line
            position = len(self.user_input) - self.cursor_position
            if position > 0:
                # Move cursor backwards
                self.screenAppend("\x1b[%sD" % str(position))

        if not self.stdout.isatty():
            self.screenAppend("\n")

        # Output everything to the screen
        self.stdout.write(self.screenObject)
        self.stdout.flush()
        self.screenObject = ""

    def loop(self):
        """
        The main program loop

        Draws terminal screen, gets keyboard input, and executes programs as necessary
        """
        self.user_input = ""
        self.cursor_position = 0
        self.saveCursor()
        while self.status == constants.SHELL_STATUS_RUN:
            # Reset cursor position if current command is empty
            if len(self.user_input) == 0 or self.cursor_position < 0: self.cursor_position = 0
            if self.cursor_position > len(self.user_input): self.cursor_position = len(self.user_input)

            # Draw the screen
            self.drawScreen()

            # Keyboard input
            execute = self.keyboardInput()
            
            # Execute flag has been set, send the current user input to be parsed
            if execute:
                self.parse(self.user_input)
                self.cursor_position = 0
                self.user_input = ""
                self.saveCursor()

    def keyboardInput(self):
        """
        Grab keyboard input from the terminal and evaluate it as necessary

        @return Boolean
        """
        char_code = -1
        current_char = ""
        execute = False

        # Grab user input (1 character at a time)
        # This method returns the ASCII code of the character, not the actual character
        char_code = self.getch()

        # Error checking
        if char_code is False:
            self.status = constants.SHELL_STATUS_STOP
            # Attempt to execute whatever is left
            execute = self.user_input != ""
            return execute

        # Escape sequence, handle appropriately
        if char_code >= constants.ARROW_UP:
            if char_code == constants.ARROW_LEFT:
                if self.cursor_position > 0:
                    self.cursor_position -= 1
            elif char_code == constants.ARROW_RIGHT:
                if self.cursor_position < len(self.user_input):
                    self.cursor_position += 1
            # Move by words, rather than characters
            elif char_code == constants.CTRL_ARROW_LEFT:
                if self.cursor_position > 0:
                    # Grab the string before the current cursor
                    past_string = self.user_input[:self.cursor_position]
                    # Get a list of all the words in the string
                    words = past_string.split()
                    # Decrement the cursor by the length of the past string minus the last occurrence of the last word
                    # This handles unknown spaces that were stripped out by the split
                    self.cursor_position -= len(past_string) - past_string.rfind(words[-1])
            elif char_code == constants.CTRL_ARROW_RIGHT:
                if self.cursor_position < len(self.user_input):
                    # Grab the string after the current cursor
                    forward_string = self.user_input[self.cursor_position:]
                    # Get a list of all the words
                    words = forward_string.split()
                    # Increment the cursor position by the index of the found word plus its length
                    # Have to do this because of spaces (I don't know if there is a space in front of the word)
                    self.cursor_position += forward_string.find(words[0]) + len(words[0])
            # History
            elif char_code == constants.ARROW_UP:
                if self.history_position < len(self.history):
                    self.history_position += 1
                    self.user_input = self.history[-self.history_position]["input"]
                    self.cursor_position = len(self.user_input)
            elif char_code == constants.ARROW_DOWN:
                if self.history_position > 1:
                    self.history_position -= 1
                    self.user_input = self.history[-self.history_position]["input"]
                    self.cursor_position = len(self.user_input)
                else:
                    self.history_position = 0
                    self.user_input = ""
                    self.cursor_position = 0
            # Delete key
            elif char_code == constants.DEL_KEY:
                if len(self.user_input) > 0:
                    # Reforms user input string based upon cursor position
                    self.user_input = self.user_input[:self.cursor_position] + self.user_input[self.cursor_position + 1:]
            # Move cursor to end of line
            elif char_code == constants.END_KEY:
                self.cursor_position = len(self.user_input)
            # Move cursor to beginning of line
            elif char_code == constants.HOME_KEY:
                self.cursor_position = 0
            return execute

        # Convert ASCII code to actual character
        current_char = chr(char_code)

        # Error checking
        if len(current_char) == 0:
            execute = False

        # Backspace
        if char_code == constants.BACKSPACE:
            if len(self.user_input) > 0:
                self.user_input = self.user_input[:self.cursor_position - 1] + self.user_input[self.cursor_position:]
                if self.cursor_position > 0: self.cursor_position -= 1
        # End of line
        elif char_code == constants.CTRL_C:
            self.cursor_position = 0
            self.user_input = ""
        # End of input
        elif char_code == constants.CTRL_D:
            self.user_input = "exit"
            execute = True
        # Enter, execute the user input as a command
        elif char_code == constants.ENTER or char_code == constants.NEWLINE:
            execute = True
            self.stdout.write("\n")
            self.saveCursor()
            self.stdout.flush()
        elif char_code == constants.TAB:
            # Ignore tabs for now, eventually we will do tab completion
            execute = False
        # Ignore these keys
        elif char_code == constants.ESC:
            execute = False
        # Regular input, add it to the user input at the cursor position
        else:
            self.user_input = self.user_input[:self.cursor_position] + current_char + self.user_input[self.cursor_position:]
            self.cursor_position += 1

        return execute

    def parse(self, string):
        """
        Parse new commands from the user and then pass the commands to be executed
        """
        # Allow commands to be split (so user can enter multiple commands at once)
        try:
            commands = self.parser.parse(string)
        except Exception as e:
            self.message("jadsh error", str(e))
            return

        for cmd in commands:
            # Execute command
            try:
                self.status = self.execute(cmd)
                if self.status == constants.SHELL_STATUS_STOP:
                    break
            except OSError as e:
                # Failed status
                os.environ["status"] = str(constants.EXIT_CODE_NOT_FOUND)
                self.message(cmd[0], "command not found")
                return
            except KeyboardInterrupt:
                continue

    def execute(self, tokens):
        """
        Execute commands from the user

        @return int (a shell status code)
        """
        if len(tokens) == 0: return constants.SHELL_STATUS_RUN

        # Dumb history tracking
        # TODO: Build function and output to history file
        self.history.append({ "command": tokens[0], "args": tokens[1:], "input": self.user_input })

        results = self.runner.execute(tokens)

        self.saveCursor()

        # Export status to shell
        os.environ["status"] = str(results["status"])

        # Builtins have the power to change the status of the shell
        if results["builtin"]:
            return results["status"]

        # Assume all went well, continue
        return constants.SHELL_STATUS_RUN

    def message(self, title, message, status = False):
        """
        Display message in the terminal
        """
        self.stdout.write(self.hilite("%s: " % str(title), status))
        self.stdout.write("%s\n" % str(message))
        self.stdout.flush()
        self.saveCursor()

    def saveCursor(self):
        if self.stdout.isatty():
            self.stdout.write("\x1b7")

    def resetCursor(self):
        if self.stdout.isatty():
            self.stdout.write("\x1b8")

    def hilite(self, string, status = False, bold = False):
        """
        Generate bold, or colored string using ANSI escape codes

        @return String
        """
        if not self.stdout.isatty(): return string
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