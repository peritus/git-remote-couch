#!/usr/bin/env

import sys
from couchdb import Server
from urlparse import urlparse

# Whether or not to show debug messages
DEBUG = True

def notify(msg, *args):
    """Print a message to stderr."""
    print >> sys.stderr, msg % args
    sys.stderr.flush()

def debug (msg, *args):
    """Print a debug message to stderr when DEBUG is enabled."""
    if DEBUG:
        print >> sys.stderr, msg % args
    sys.stderr.flush()

def stdout(msg=None):
    if msg == None:
        msg = ""
    debug("out: %s" % msg)
    sys.stderr.flush()
    print msg
    sys.stdout.flush()

def error (msg, *args):
    """Print an error message to stderr."""
    print >> sys.stderr, "ERROR:", msg % args
    sys.stderr.flush()

def warn(msg, *args):
    """Print a warning message to stderr."""
    print >> sys.stderr, "warning:", msg % args
    sys.stderr.flush()

def die (msg, *args):
    """Print as error message to stderr and exit the program."""
    error(msg, *args)
    sys.exit(1)


class CouchRemote(object):
    def do_capabilities(self, line):
        stdout("connect")
        stdout("fetch")
        stdout("option")
        stdout("push")
        stdout()

    def do_list(self, line):
        """Lists all the refs"""

        stdout("7aeaa2fc0abbf439534769e15b3a59a5814cc3d1 refs/heads/master")
        stdout("@refs/heads/master HEAD")
        stdout()

    def do_connect(self, line):
        """Connects to the Couch"""

        parsed = urlparse(self.url)
        server = Server('%s://%s/' % (parsed.scheme, parsed.netloc))
        server[parsed.path.lstrip("/")]

        if False:
            die("Can't connect")

        stdout("fallback")

    def do_option(self, line):
        stdout("unsupported")

    COMMANDS = {
        'capabilities': do_capabilities,
        'connect': do_connect,
        'list': do_list,
        'option': do_option,
    }

    def sanitize(self, value):
        """Cleans up the url."""

        return value.replace('http+couch', 'http', 1)

    def read_one_line(self):
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

        if cmd not in self.COMMANDS:
            die("Unknown command, %s", cmd)

        func = self.COMMANDS[cmd]
        func(self, cmdline)
        sys.stdout.flush()

        return True

    def __init__(self, _, alias, url):

        self.alias = self.sanitize(alias)
        self.url = self.sanitize(url)

        debug("Got arguments %s", (self.alias, self.url))

        more = True

        while (more):
            more = self.read_one_line()

def main():
    if len(sys.argv) != 3:
        die("Expecting exactly three arguments.")
        sys.exit(1)

    CouchRemote(*sys.argv)
