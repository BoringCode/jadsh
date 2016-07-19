import sys
import os
import re

from jadsh.screen import Screen
from jadsh.parser import Parser
from jadsh.runner import Runner
from jadsh.getch import Getch
from jadsh.prompt import Prompt
import jadsh.constants as constants

class Shell():
    """
    jadsh, Just Another Dumb SHell
    """
    def __init__(self, prompt = Prompt(), args = [], stdin = sys.stdin, stdout = sys.stdout, stderr = sys.stderr, status = constants.SHELL_STATUS_RUN):
        """
        Expects a new Prompt object and the status the shell should start with

        Prompt objects allow easy customization of the prompt
        """
        self.status = status
        self.prompt = prompt
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.args = args

        # Set debug mode
        self.debug = "--debug" in self.args

        self.runner = Runner(stdin = self.stdin, stdout = self.stdout, stderr = self.stderr)
        self.parser = Parser(self.runner)

        self.history = []
        self.history_position = 0

        self.last_status = -1

        # The screen object
        self.screen = Screen(stdin = self.stdin, stdout = self.stdout, stderr = self.stderr)

        # Grab individual characters from standard input
        self.getch = Getch(self.stdin)

        # Output welcome message
        self.welcome()

        # Catch any uncaught errors
        # Assume uncaught errors are bad, and reload the shell
        try:
            # Start the main program loop
            self.loop()
        except BaseException as e:
            self.stderr.write(str(e))
            self.screen.message("jadsh error", "Fatal error, attempting to reload the shell")
            if self.debug:
                self.screen.write(e)
            else:
                os.execvp("jadsh", ["jadsh"])

    def welcome(self):
        self.screen.write("Welcome to jadsh, Just Another Dumb SHell\n", flush = False)
        self.screen.write("Type %s for instructions on how to use jadsh\n" % self.screen.hilite("help", True))

    def loop(self):
        """
        The main program loop

        Draws terminal screen, gets keyboard input, and executes programs as necessary
        """
        self.user_input = ""
        self.screen.saveCursor()
        execute = False
        while self.status == constants.SHELL_STATUS_RUN:
            # Set the terminal title
            self.screen.title("jadsh %s" % os.getcwd())

            # Draw the screen
            self.screen(self.prompt.generate(), self.user_input)

            # Keyboard input
            execute = self.keyboardInput()
            
            # Execute flag has been set, send the current user input to be parsed
            if execute:
                self.parse(self.user_input)
                self.user_input = ""
                self.screen.saveCursor()

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
                self.screen.updateCursor(-1)
            elif char_code == constants.ARROW_RIGHT:
                self.screen.updateCursor(1)
            # Move by words, rather than characters
            elif char_code == constants.CTRL_ARROW_LEFT:
                if self.screen.getCursor(self.user_input) > 0:
                    # Grab the string before the current cursor
                    past_string = self.user_input[:self.screen.getCursor(self.user_input)]
                    # Get a list of all the words in the string
                    words = past_string.split()
                    # Decrement the cursor by the length of the past string minus the last occurrence of the last word
                    # This handles unknown spaces that were stripped out by the split
                    self.screen.updateCursor(-(len(past_string) - past_string.rfind(words[-1])))
            elif char_code == constants.CTRL_ARROW_RIGHT:
                if self.screen.getCursor(self.user_input) < len(self.user_input):
                    # Grab the string after the current cursor
                    forward_string = self.user_input[self.screen.getCursor(self.user_input):]
                    # Get a list of all the words
                    words = forward_string.split()
                    # Increment the cursor position by the index of the found word plus its length
                    # Have to do this because of spaces (I don't know if there is a space in front of the word)
                    self.screen.updateCursor(forward_string.find(words[0]) + len(words[0]))
            # History
            elif char_code == constants.ARROW_UP:
                if self.history_position < len(self.history):
                    self.history_position += 1
                    self.user_input = self.history[-self.history_position]["input"]
                    self.screen.cursor = len(self.user_input)
            elif char_code == constants.ARROW_DOWN:
                if self.history_position > 1:
                    self.history_position -= 1
                    self.user_input = self.history[-self.history_position]["input"]
                    self.screen.cursor = len(self.user_input)
                else:
                    self.history_position = 0
                    self.user_input = ""
            # Delete key
            elif char_code == constants.DEL_KEY:
                if len(self.user_input) > 0:
                    # Reforms user input string based upon cursor position
                    self.user_input = self.user_input[:self.screen.getCursor(self.user_input)] + self.user_input[self.screen.getCursor(self.user_input) + 1:]
            # Move cursor to end of line
            elif char_code == constants.END_KEY:
                self.screen.cursor = len(self.user_input)
            # Move cursor to beginning of line
            elif char_code == constants.HOME_KEY:
                self.screen.cursor = 0
            return execute

        # Convert ASCII code to actual character
        current_char = chr(char_code)

        # Error checking
        if len(current_char) == 0:
            execute = False

        # Backspace
        if char_code == constants.BACKSPACE:
            if len(self.user_input) > 0:
                self.user_input = self.user_input[:self.screen.getCursor(self.user_input) - 1] + self.user_input[self.screen.getCursor(self.user_input):]
                if self.screen.cursor > 0: self.screen.updateCursor(-1)
        # End of line
        elif char_code == constants.CTRL_C:
            self.user_input = ""
        # End of input
        elif char_code == constants.CTRL_D:
            self.user_input = "exit"
            execute = True
        # Enter, execute the user input as a command
        elif char_code == constants.ENTER or char_code == constants.NEWLINE:
            execute = True
            self.screen.write("\n")
            self.screen.saveCursor()
        elif char_code == constants.TAB:
            # Ignore tabs for now, eventually we will do tab completion
            execute = False
        # Ignore these keys
        elif char_code == constants.ESC:
            execute = False
        # Regular input, add it to the user input at the cursor position
        else:
            self.user_input = self.user_input[:self.screen.getCursor(self.user_input)] + current_char + self.user_input[self.screen.getCursor(self.user_input):]
            self.screen.updateCursor(1)

        return execute

    def parse(self, string):
        """
        Parse new commands from the user and then pass the commands to be executed
        """
        # Allow commands to be split (so user can enter multiple commands at once)
        try:
            commands = self.parser(string)
        except ValueError as e:
            self.screen.message("jadsh error", str(e))
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
                self.screen.message(cmd[0], "command not found")
            except KeyboardInterrupt:
                pass
            self.last_status = int(os.getenv("status", -1))

    def execute(self, tokens):
        """
        Execute commands from the user

        @return int (a shell status code)
        """
        if len(tokens) == 0: return constants.SHELL_STATUS_RUN

        # Dumb history tracking
        # TODO: Build function and output to history file
        self.history.append({ "command": tokens[0], "args": tokens[1:], "input": self.user_input })

        results = self.runner(tokens)

        self.screen.saveCursor()

        # Builtins have the power to change the status of the shell
        if results["builtin"]:
            return results["status"]

        # Assume all went well, continue
        return constants.SHELL_STATUS_RUN