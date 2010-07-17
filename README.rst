================
git-remote-couch
================

Relax your source code
----------------------

:Author: `Filip Noetzel <http://filip.noetzel.co.uk/>`_
:Version: v0.1a
:Web: http://github.com/peritus/git-remote-couch/
:Git: ``git clone git://github.com/peritus/git-remote-couch.git``
  (`browse source <http://github.com/peritus/git-remote-couch/>`_)
:Download: `Downloads page on GitHub <https://github.com/peritus/git-remote-couch/downloads>`_
:Abstract: `git-remote-couch` is a `git-remote-helper
  <http://www.kernel.org/pub/software/scm/git/docs/git-remote-helpers.html>`_
  that allows you to push source code into a `CouchDB
  <http://couchdb.apache.org/>`_ (you can then fetch a clone from it, of course).

.. warning::

  This software is very slow and a three headed monkey will eat your data!  It
  should not be used to save valuable production source code!  **ALWAYS** keep
  at least a second copy using other backup mechanisms.

.. note::

  This is a fun project for me to learn some git and CouchDB internals. Also, I
  want to write `CouchApps <http://github.com/couchapp/couchapp>`_ that handle
  source code. Patches welcome.


Installation and Usage
++++++++++++++++++++++

First, install `git-remote-couch` via your favorite Python package installing mechanism, like so::

  easy_install -U git-remote-couch

Then, you can start cloning a repository::

  git remote add couch http+couch://localhost:5984/testrepo/
  git push origin master

You can now browse your repository with CouchDB's web interface at
`http://localhost:5984/_utils/database.html?testrepo
<http://localhost:5984/_utils/database.html?testrepo>`_ or clone that
repository::

  git clone http+couch://localhost:5984/testrepo/ a_copy
