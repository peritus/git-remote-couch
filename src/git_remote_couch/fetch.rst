git-remote-couch
================

Preparations
------------

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

--------

So, we create a repo:
>>> system('rm -rf testrepo0')
>>> system('mkdir testrepo0')
>>> os.chdir('testrepo0')
>>> system('git init .')
Initialized empty Git repository in .../testrepo0/.git/

>>> system('git config user.name "Test User"')
>>> system('git config user.email "test@example.com"')

>>> system('touch -t200504072213.12 foo.txt')
>>> system('git add foo.txt')
>>> system("git commit -m 'Initial commit' --date=2005-04-07T22:13:13")
[master (root-commit) ...] Initial commit
 0 files changed, 0 insertions(+), 0 deletions(-)
 create mode 100644 foo.txt

>>> system("git remote add origin http+couch://localhost:5984/testrepo0")
>>> system("git push origin master:refs/heads/experimental")
Got arguments ('origin', 'http://localhost:5984/testrepo0')
Got command 'capabilities' with args ''
out: connect
out: fetch
out: option
out: push
out: 
Got command 'connect' with args 'git-receive-pack'
out: fallback
Got command 'list' with args 'for-push'
out: 
Got command 'connect' with args 'git-receive-pack'
out: fallback
Got command 'option' with args 'progress false'
out: unsupported
Got command 'option' with args 'verbosity 1'
out: unsupported
Got command 'push' with args 'refs/heads/master:refs/heads/experimental'
out: ok refs/heads/experimental

>>> os.chdir('..')

