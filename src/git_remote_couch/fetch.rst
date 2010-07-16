git-remote-couch
================

Preparations
------------

>>> import os
>>> import sys
>>> from subprocess import Popen, STDOUT, PIPE
>>> from shlex import split

>>> COUCHDB_PORT = 5984
>>> if 'COUCHDB_PORT' in os.environ: COUCHDB_PORT = int(os.environ['COUCHDB_PORT'])

>>> def system(cmd, env=None):
...     if env != None:
...         env.update(os.environ)
...     process = Popen(split(cmd), stderr=STDOUT, stdout=PIPE, env=env)
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
>>> system("git commit -m 'Initial commit'", env=dict(
...  GIT_AUTHOR_DATE="2005-04-07T22:13:13",
...  GIT_COMMITTER_DATE="2005-04-07T22:13:13"))
[master (root-commit) 36a81d6] Initial commit
 0 files changed, 0 insertions(+), 0 deletions(-)
 create mode 100644 foo.txt

>>> system("git remote add origin http+couch://localhost:%d/testrepo0" % COUCHDB_PORT)
>>> system("git push origin master:refs/heads/experimental")
Got arguments ('origin', 'http://localhost:.../testrepo0')
Got command 'capabilities' with args ''
out: fetch
out: list
out: option
out: push
out: 
Got command 'list' with args 'for-push'
out: 
Got command 'option' with args 'progress false'
out: unsupported
Got command 'option' with args 'verbosity 1'
out: unsupported
Got command 'push' with args 'refs/heads/master:refs/heads/experimental'
out: ok refs/heads/experimental

Then we push again (we don't need to upgrade the ref then)
>>> system("git push origin master:refs/heads/experimental")
Got arguments ('origin', 'http://localhost:.../testrepo0')
Got command 'capabilities' with args ''
out: fetch
out: list
out: option
out: push
out: 
Got command 'list' with args 'for-push'
out: 36a81d66f949805e7526b12419c61a0a4000bd47 refs/heads/experimental
out: @refs/heads/experimental HEAD
out: 
Everything up-to-date


>>> import livetest, json, pprint
>>> couch = livetest.TestApp('localhost:%d' % COUCHDB_PORT)
>>> pprint.pprint(json.loads(couch.get("/testrepo0/_all_docs").unicode_body))
{u'offset': 0,
 u'rows': [{u'id': u'09a13b897d3d0f528d487c704da540cb952d7606',
            u'key': u'09a13b897d3d0f528d487c704da540cb952d7606',
            u'value': {u'rev': u'1-...'}},
           {u'id': u'36a81d66f949805e7526b12419c61a0a4000bd47',
            u'key': u'36a81d66f949805e7526b12419c61a0a4000bd47',
            u'value': {u'rev': u'1-...'}},
           {u'id': u'_design/git_remote_couch',
            u'key': u'_design/git_remote_couch',
            u'value': {u'rev': u'1-...'}},
           {u'id': u'e69de29bb2d1d6434b8b29ae775ad8c2e48c5391',
            u'key': u'e69de29bb2d1d6434b8b29ae775ad8c2e48c5391',
            u'value': {u'rev': u'1-...'}},
           {u'id': u'refs/heads/experimental',
            u'key': u'refs/heads/experimental',
            u'value': {u'rev': u'1-...'}}],
 u'total_rows': 5}

>>> system("git ls-remote origin")
Got arguments ('origin', 'http://localhost:.../testrepo0')
Got command 'capabilities' with args ''
out: fetch
out: list
out: option
out: push
out: 
Got command 'list' with args ''
out: 36a81d66f949805e7526b12419c61a0a4000bd47 refs/heads/experimental
out: @refs/heads/experimental HEAD
out: 
36a81d66f949805e7526b12419c61a0a4000bd47	refs/heads/experimental
36a81d66f949805e7526b12419c61a0a4000bd47	HEAD

Now we create a second commit

>>> system('touch -t200504072213.12 bar.txt')
>>> system('git add bar.txt')

>>> system("git commit -m 'Second commit'", env=dict(
...  GIT_AUTHOR_DATE="2005-04-07T23:13:13",
...  GIT_COMMITTER_DATE="2005-04-07T23:13:13"))
[master c0993a2] Second commit
 0 files changed, 0 insertions(+), 0 deletions(-)
 create mode 100644 bar.txt

And then push again

>>> system("git push origin master:refs/heads/experimental")
Got arguments ('origin', 'http://localhost:.../testrepo0')
Got command 'capabilities' with args ''
out: fetch
out: list
out: option
out: push
out:
Got command 'list' with args 'for-push'
out: 36a81d66f949805e7526b12419c61a0a4000bd47 refs/heads/experimental
out: @refs/heads/experimental HEAD
out:
Got command 'option' with args 'progress false'
out: unsupported
Got command 'option' with args 'verbosity 1'
out: unsupported
Got command 'push' with args 'refs/heads/master:refs/heads/experimental'
out: ok refs/heads/experimental

>>> os.chdir('..')

>>> system("git clone http+couch://localhost:%d/testrepo0 testrepo0_clone" % COUCHDB_PORT)
Initialized empty Git repository in .../testrepo0_clone/.git/
Got arguments ('http://localhost:.../testrepo0', 'http://localhost:.../testrepo0')
Got command 'capabilities' with args ''
out: fetch
out: list
out: option
out: push
out: 
Got command 'list' with args ''
out: c0993a27450a2f77e9089f19ceeb62e5e2225fd9 refs/heads/experimental
out: @refs/heads/experimental HEAD
out: 
Got command 'option' with args 'progress false'
out: unsupported
Got command 'option' with args 'verbosity 1'
out: unsupported
Got command 'fetch' with args 'c0993a27450a2f77e9089f19ceeb62e5e2225fd9 refs/heads/experimental'
out: 

Now the two directories should be exact copies of the repository.

>>> os.path.exists("testrepo0_clone")
True

>>> os.chdir("testrepo0_clone")
>>> system("ls")
bar.txt
foo.txt
>>> system("git rev-list --objects --all")
c0993a27450a2f77e9089f19ceeb62e5e2225fd9
36a81d66f949805e7526b12419c61a0a4000bd47
00906ce530257852785a7149b8df0c6a75a48ad2
e69de29bb2d1d6434b8b29ae775ad8c2e48c5391 bar.txt
09a13b897d3d0f528d487c704da540cb952d7606
>>> system("git fsck --full")



