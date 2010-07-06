import unittest
import doctest
from lovely.testlayers.server import ServerLayer

import os

class CouchDBLayer(ServerLayer):

    """A layer that starts and stops CouchDB,
    executable needs to be in the path"""

    __bases__ = ()

    LOCAL_INI_TEMPLATE = '''\
[couchdb]
database_dir = %(store_dir)s
view_index_dir = %(store_dir)s
delayed_commits = false

[httpd]
port = %(port)s

[log]
level = info
'''

    COMMAND = 'couchdb -a ./local.ini'

    def __init__(self, name, port=5984, connections=10):
        self.port = port

        local_ini = open("./local.ini", "w")

        local_ini.write(self.LOCAL_INI_TEMPLATE % {
            'store_dir': os.path.abspath("."),
            'port': port,
            })
        local_ini.close()

        start_cmd = self.COMMAND

        super(CouchDBLayer, self).__init__(
            name, servers=['localhost:%s' % port],
            start_cmd=start_cmd)

def test_suite():
    os.environ['PATH'] = (
       ":" + os.path.join(os.path.dirname(__file__), '../../parts/couchdb/bin/') +
       ":" + os.path.join(os.path.dirname(__file__), '../../bin') +
       ':' + os.environ['PATH']
    )
    suite = unittest.TestSuite(
        doctest.DocFileSuite('fetch.rst',
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
    )
    suite.layer = CouchDBLayer('couch')
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
