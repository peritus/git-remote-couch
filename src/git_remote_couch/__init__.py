#!/usr/bin/env

import sys
from couchdb import Server
from couchdb.http import ResourceConflict, ResourceNotFound
from urlparse import urlparse
from subprocess import Popen, STDOUT, PIPE
from shlex import split
from json import loads, dumps

# Whether or not to show debug messages
DEBUG = True

def system(cmd):
    process = Popen(split(cmd), stderr=STDOUT, stdout=PIPE)
    # from http://stackoverflow.com/questions/1388753/how-to-get-output-from-subprocess-popen
    value = ""
    while True:
        read = process.stdout.read(1)
        value += read
        if read == '' and process.poll() != None:
            return value

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

    DESIGN_DOCUMENT = {
       "_id": "_design/git_remote_couch",
       "views": {
           "refs": {
               "map": "function(doc){ if (doc._id.match(/^refs/)){emit(doc._id, doc.content)}}"
           }
       }
    }

    def do_capabilities(self, line):
        stdout("connect")
        stdout("fetch")
        stdout("list")
        stdout("option")
        stdout("push")
        stdout()

    def do_list(self, line):
        """Lists all the refs"""

        for row in self.couch.view('git_remote_couch/refs'):
            stdout("%s %s" % (row['value'].strip("\n"), row['key']))

        stdout()

    def do_connect(self, line):
        """Connects to the Couch"""

        parsed = urlparse(self.url)
        db_name = parsed.path.lstrip("/")

        try:
            self.server = Server('%s://%s/' % (parsed.scheme, parsed.netloc))
            self.couch = self.server[db_name]
        except ResourceNotFound:
            self.couch = self.server.create(db_name)
        except:
            die("Can't connect")

        # install / update design document
        def add_design_document():
            try:
                self.couch['_design/git_remote_couch'] = self.DESIGN_DOCUMENT
            except:
                die("Can't connect")

        try:
            got = self.couch['_design/git_remote_couch']
        except ResourceNotFound:
            add_design_document()

        stdout("fallback")

    def do_push(self, line):
        src, dst = line[0].split(":")
        rev_list = system("git rev-list --objects %s" % src)
        for obj in rev_list.split('\n'):
            obj = obj.split()
            if obj:
                hash = obj[0]
                content = system("git cat-file -p %s" % hash)
                try:
                    self.couch[hash] = {'content': content}
                except ResourceConflict, e:
                    pass # ignore, must be the same then

        self.couch[dst] = {'content': system("git rev-parse %s" % src)}

        stdout("ok %s" % dst)

    def do_option(self, line):
        stdout("unsupported")

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

        func = getattr(self, "do_%s" % cmd)

        if func == None:
            die("Unknown command, %s", cmd)

        func(cmdline)
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
