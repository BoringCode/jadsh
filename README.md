# jadsh 

[![Build Status](https://travis-ci.org/BoringCode/jadsh.svg?branch=master)](https://travis-ci.org/BoringCode/jadsh)

> Just Another Dumb SHell

Experiments with making a really dumb, slow shell in Python. This will never be usable. Heck you probably shouldn't even look at it. But, I'm making it.

Zero dependencies. Built entirely using Python stdlib and escape sequences.

## Requirements

- Python 2.7+
- setuptools
- Unix terminal with ANSI escape code support

## Setup

Install the shell on your machine.

```bash
python setup.py install
```

Launch the shell.

```bash
jadsh
```

## Development

Setting up your development environment requires a few extra steps. 

```bash
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
python setup.py develop
```

Now the application is installed locally and you can continue to make changes without reinstalling.

Launch the shell.

```bash
jadsh
```

Alternatively you can launch the shell as a direct module: `python -m jadsh`

## Tests

Testing is an important part of ensuring program stability. Individual tests are located in the `jadsh/tests/` directory.

Run all tests:

```bash
python -m unittest discover
```

Run an individual test suite (for example test_shell.py):

```bash
python -m unittest jadsh.tests.test_shell
```

## Learning jadsh

When you start jadsh, you should see this:

```
Welcome to jadsh, Just Another Dumb SHell
Type help for instructions on how to use jadsh
you@hostname:~:$ 
```

Shells work by giving them commands. Using jadsh is no different.

A command is executed by typing the name of the command, then a set of arguments to pass to the command.

For example:

```
echo "hello world"
```

This calls the `echo` command and passes the argument `"hello world"`. The result is the text `"hello world"` being output to the screen. All commands in jadsh follow this simple syntax.

Any program on your computer can be executed this way. As long as it exists in the `PATH`, you can call it.

Some examples include:

- ls - list the files and directories in your current working directory
- cd - change the current working directory of jadsh
- echo - output a set of arguments to the shell
- mv - move or rename a set of files

Go to the [wiki](https://github.com/BoringCode/jadsh/wiki) for additional documentation.

## OS Support

Tested on Ubuntu 16.04. Should support any unix terminal with ANSI escape code support.

## License

&copy; Bradley Rosenfeld

Licensed under the [MIT license](https://github.com/BoringCode/jadsh/blob/master/LICENSE)
