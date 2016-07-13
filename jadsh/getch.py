import sys
import jadsh.constants as constants

class Getch():
    """
    Gets a single character from standard input

    Returns the char code and handles special terminal input (escape sequences)
    """
    def __init__(self):
        #try:
        #    self.read = _GetchWindows()
        #except ImportError:
        self.read = _GetchUnix()

    def __call__(self):
        char = ord(self.read())     
        while True:
            if char == constants.ESC:
                # Grab a sequence of 2 characters
                try:
                    seq = [self.read(), self.read()]
                except:
                    return constants.ESC
                # ESC [ sequences
                if seq[0] == '[':
                    if seq[1] >= '0' and seq[1] <= '9':
                        try:
                            seq.append(self.read())
                        except:
                            return constants.ESC
                        if seq[2] == '~':
                            if seq[1] == '3': 
                                return constants.DEL_KEY
                            elif seq[1] == '5': 
                                return constants.PAGE_UP
                            elif seq[1] == '6': 
                                return constants.PAGE_DOWN
                    else:
                        if seq[1] == 'A': 
                            return constants.ARROW_UP
                        elif seq[1] == 'B': 
                            return constants.ARROW_DOWN
                        elif seq[1] == 'C': 
                            return constants.ARROW_RIGHT
                        elif seq[1] == 'D': 
                            return constants.ARROW_LEFT
                        elif seq[1] == 'H':
                            return constants.HOME_KEY
                        elif seq[1] == 'F':
                            return constants.END_KEY
                # Escape 0 sequences
                elif seq[0] == '0':
                    if seq[1] == 'H':
                        return constants.HOME_KEY
                    elif seq[1] == 'F':
                        return constants.END_KEY
                else:
                    return constants.ESC
            # Default
            else:
                return char
        

class _GetchUnix():
    def __init__(self):
        import tty, sys

    def __call__(self, returnImmediately = False):
        import sys, tty, fcntl, os, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        old_flags = fcntl.fcntl(fd, fcntl.F_GETFL)
        try:
            if returnImmediately:
                fcntl.fcntl(fd, fcntl.F_SETFL, old_flags | os.O_NONBLOCK)
            tty.setraw(fd)
            if returnImmediately:
                ch = sys.stdin.buffer.raw.read(1)
            else:
                ch = sys.stdin.read(1)
        finally:
            if returnImmediately:
                fcntl.fcntl(fd, fcntl.F_SETFL, old_flags)
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

class _GetchWindows():
    def __init__(self):
        import msvcrt
    def __call__(self):
        import msvcrt
        return msvcrt.getch()