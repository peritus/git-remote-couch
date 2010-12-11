#!/usr/bin/env python

import sys
from couchdb import Server
from couchdb.http import ResourceConflict, ResourceNotFound
from urlparse import urlparse
from subprocess import Popen, STDOUT, PIPE
from shlex import split
from json import loads, dumps
from binascii import b2a_hex, a2b_hex
from cStringIO import StringIO

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

    @property
    def server(self):
        if self._server != None:
            return self._server

        parsed = urlparse(self.url)

        try:
            self._server = Server('%s://%s/' % (parsed.scheme, parsed.netloc))
            return self._server
        except Exception, e:
            debug(repr(e))
            die("Can't connect")

    @property
    def couch(self):
        """Creates the remote couch"""
        if self._couch != None:
            return self._couch

        parsed = urlparse(self.url)
        db_name = parsed.path.lstrip("/")

        try:
            self._couch = self.server[db_name]
        except ResourceNotFound:
            self._couch = self.server.create(db_name)

        return self._couch

    def __init__(self, _, alias, url):
        self._couch = None
        self._server = None

        sanitize = lambda value: value.replace('http+couch', 'http', 1)

        self.alias = sanitize(alias)
        self.url = sanitize(url)
        self.ls_remote = {}

        debug("Got arguments %s", (self.alias, self.url))

        more = True

        while (more):
            more = self.read_one_line()

    def do_capabilities(self, line):
        stdout("fetch")
        stdout("list")
        stdout("option")
        stdout("push")
        stdout()

    def do_list(self, line):
        """Lists all the refs"""

        head = None
        for row in self.view('refs'):
            key = row['key']
            value = row['value'].strip("\n")
            self.ls_remote[key] = value
            stdout("%s %s" % (value, key))
            head = key # update, last one is just the HEAD

        if head:
            stdout("@%s HEAD" % row['key'])

        stdout()

    def do_push(self, line):
        src, dst = line[0].split(":")
        rev_list = system("git rev-list --objects %s" % src)

        for obj in rev_list.split('\n'):
            obj = obj.split()
            if obj:
                doc = {}
                hash = obj[0]

                doc['type'] = system("git cat-file -t %s" % hash).strip("\n")
                doc['content'] = system("git cat-file %s %s" % (doc['type'], hash))

                # prepare doc
                if doc['type'] == 'tree':
                    tree_list = StringIO(doc['content'])
                    doc['content'] = []
                    ascii = ''

                    while True:
                        c = tree_list.read(1)
                        if c == '\x00':
                            sha = b2a_hex(tree_list.read(20))
                            mode, filename = ascii.split(" ")
                            ascii = ''
                            doc['content'].append([mode, filename, sha])
                        elif c == '':
                            break
                        else:
                            ascii += c

                elif doc['type'] == 'commit':
                    header, message = doc['content'].split("\n\n", 1)
                    for line in header.split("\n"):
                        name, value = line.split(" ", 1)
                        doc[name] = value
                    doc['content'] = message

                # upload doc
                try:
                    if doc['type'] in ('tree', 'commit',):
                        self.couch[hash] = doc
                    elif doc['type'] in ('blob',):
                        self.couch[hash] = {'type': doc['type']}
                        blobdoc = self.couch[hash]
                        self.couch.put_attachment(
                                doc = blobdoc,
                                content = doc['content'],
                                filename = 'blob',
                                content_type = 'application/octet-stream')
                except ResourceConflict, e:
                    pass # ignore, must be the same then

        try:
            dstref = self.couch[dst]
        except ResourceNotFound:
            dstref = {'content': None}

        localref = system("git rev-parse %s" % src)

        if dstref['content'] != localref:
            dstref['content'] = localref
            self.couch[dst] = dstref
        else:
            assert False, "this should not happen"

        stdout("ok %s" % dst)

    def do_fetch(self, line):
        initial, ref = line

        # read the terminating blank line
        assert not self._read_one_line()

        fetch = [initial]

        while fetch:
            hash = fetch.pop()

            doc = self.couch[hash]

            content = []

            if doc['type'] == 'commit':
                for key in ('tree', 'parent', 'author', 'committer'):
                    if key in doc:
                        if key in ('tree', 'parent'):
                            fetch.append(doc[key])
                        content.append('%s %s\n' % (key, doc[key]))
                content.append("\n%s" % doc['content'])
            elif doc['type'] == 'tree':
                for mode, filename, sha in doc['content']:
                    fetch.append(sha)
                    content.append("%s %s\x00" % (mode, filename))
                    content.append(a2b_hex(sha))
            elif doc['type'] == 'blob':
                blob = self.couch.get_attachment(doc, 'blob', None)
                if blob == None:
                    content.append('') # necessary ?
                else:
                    content.append(blob.read())
            else:
                content.append(doc['content'])

            cmd = str("git hash-object -t %s -w --stdin" % doc['type'])

            process = Popen(split(cmd),
                    stdin=PIPE, stdout=PIPE, stderr=STDOUT)

            for chunk in content:
                process.stdin.write(chunk)
            process.stdin.close()
            process.wait()

        system("git update-ref %s %s" % (ref, initial))

        stdout()

    def do_option(self, line):
        stdout("unsupported")

    def view(self, name, attempt=0):
        if attempt > 2:
            die("Too many attempts to install design document")

        try:
            result = self.couch.view('git_remote_couch/%s' % name)
            result._fetch() # force evaluation (to trigger 404)
            return result
        except ResourceNotFound:
            # install / update design document
            try:
                self.couch['_design/git_remote_couch'] = self.DESIGN_DOCUMENT
            except:
                die("Could not add design document to '_design/git_remote_couch'")

        return self.view(name, attempt+1)

    def _read_one_line(self):
        """Reads one command."""
        cmdline = sys.stdin.readline()

        if not cmdline:
            warn("Unexpected EOF")
            return False

        return cmdline.strip().split()

    def read_one_line(self):
        """Processes one command."""

        cmdline = self._read_one_line()

        if not cmdline:
            # Blank line means we're about to quit
            return False

        cmd = cmdline.pop(0)
        debug("Got command '%s' with args '%s'", cmd, ' '.join(cmdline))

        try:
            func = getattr(self, "do_%s" % cmd)
        except AttributeError, e:
            die("Unknown command: '%s'", cmd)

        func(cmdline)
        sys.stdout.flush()

        return True

def main():
    if len(sys.argv) != 3:
        die("Expecting exactly three arguments.")
        sys.exit(1)

    CouchRemote(*sys.argv)
