git-remote-couch
================

Preparations
------------

To fetch, we first need a couch

>>> from git_remote_couch.tests import CouchDBLayer
>>> couch = CouchDBLayer('couch')
>>> couch.setUp()

>>> import os
>>> import sys
>>> from subprocess import Popen, STDOUT, PIPE
>>> from shlex import split
>>> def system(cmd):
...     process = Popen(split(cmd), stderr=STDOUT, stdout=PIPE)
...     # from http://stackoverflow.com/questions/1388753/how-to-get-output-from-subprocess-popen
...     while True:
...         out = process.stdout.read(1)
...         if out == '' and process.poll() != None:
...             break
...         if out != '':
...             sys.stdout.write(out)
...             sys.stdout.flush()

>>> os.environ['PATH'] = os.path.join(os.getcwd(), '..', '..', 'bin') + ':' + os.environ['PATH']

--------

So, we clone a couch:

>>> system('git clone http+couch://localhost:5984/testrepo1')
Initialized empty Git repository in /Users/filip/workspace/git-remote-couch/parts/test/testrepo1/.git/
Got arguments ('http://localhost:5984/testrepo1', 'http://localhost:5984/testrepo1')
Got command 'capabilities' with args ''
out: connect
out: fetch
out: option
out: push
out: 
Got command 'connect' with args 'git-upload-pack'
out: fallback
Got command 'list' with args ''
out: 7aeaa2fc0abbf439534769e15b3a59a5814cc3d1 refs/heads/master
out: @refs/heads/master HEAD
out: 
Got command 'connect' with args 'git-upload-pack'
out: fallback
Got command 'option' with args 'progress false'
out: unsupported
Got command 'option' with args 'verbosity 1'
out: unsupported
Got command 'fetch' with args '7aeaa2fc0abbf439534769e15b3a59a5814cc3d1 refs/heads/master'
ERROR: Unknown command, fetch

Turn off the couch then:

>>> couch.tearDown()
