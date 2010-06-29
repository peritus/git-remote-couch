#!/usr/bin/env

import sys

# Whether or not to show debug messages
DEBUG = True

def notify(msg, *args):
    """Print a message to stderr."""
    print >> sys.stderr, msg % args

def debug (msg, *args):
    """Print a debug message to stderr when DEBUG is enabled."""
    if DEBUG:
        print >> sys.stderr, msg % args

def error (msg, *args):
    """Print an error message to stderr."""
    print >> sys.stderr, "ERROR:", msg % args

def warn(msg, *args):
    """Print a warning message to stderr."""
    print >> sys.stderr, "warning:", msg % args

def die (msg, *args):
    """Print as error message to stderr and exit the program."""
    error(msg, *args)
    sys.exit(1)

def do_capabilities(line):
    print "connect"
    print "fetch"
    print "option"
    print "push"
    print

def do_list(line):
    """Lists all the refs"""

    #debug("@refs/heads/master HEAD")
    #print "@refs/heads/master HEAD"

    print

def do_connect(line):
    """Connects to the Couch"""
    if False:
        die("Can't connect")
    print "fallback"
    print

def do_option(line):
    print "unsupported\n\n"

COMMANDS = {
    'capabilities': do_capabilities,
    'connect': do_connect,
    'list': do_list,
    'option': do_option,
}

def sanitize(value):
    """Cleans up the url."""

    return value.replace('http+couch', 'http', 1)

def read_one_line():
    """Reads and processes one command."""

    cmdline = sys.stdin.readline()

    if not cmdline:
        warn("Unexpected EOF")
        return False

    cmdline = cmdline.strip().split()
    if not cmdline:
        # Blank line means we're about to quit
        return False

    cmd = cmdline.pop(0)
    debug("Got command '%s' with args '%s'", cmd, ' '.join(cmdline))

    if cmd not in COMMANDS:
        die("Unknown command, %s", cmd)

    func = COMMANDS[cmd]
    func(cmdline)
    sys.stdout.flush()

    return True

def main():
    args = sys.argv

    if len(args) != 3:
        die("Expecting exactly three arguments.")
        sys.exit(1)

    alias = sanitize(args[1])
    url = sanitize(args[2])

    if not alias.isalnum():
        warn("non-alnum alias '%s'", alias)
        alias = "tmp"

    args[1] = alias
    args[2] = url

    debug("Got arguments %s", args[1:])

    more = True

    while (more):
        more = read_one_line()

