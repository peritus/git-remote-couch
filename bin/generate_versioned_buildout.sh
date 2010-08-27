#!/bin/sh

COUCHDB_VERSION=$1

cat $0 | grep '^#couch' |grep $COUCHDB_VERSION|awk '{print "[buildout]\nextends = buildout.cfg\n[versions]\ncouchdb=" $2 "\n[couchdb]\nmd5sum=" $3}'

# HOW TO REPRODUCE THIS FILE
#

function generate_list() {
  for COUCHDB_VERSION in 0.10.0 0.10.1 0.10.2 0.11.0 0.11.1 1.0.0;
    do echo '#couch' $COUCHDB_VERSION `curl ftp://ftp.fu-berlin.de/unix/www/apache/couchdb/$COUCHDB_VERSION/apache-couchdb-$COUCHDB_VERSION.tar.gz|md5sum|awk '{print $1}'`;
  done
}

#couch 0.10.0 227886b5ecbb6bcbbdc538aac4592b0e
#couch 0.10.1 a34dae8bf402299e378d7e8c13b7ba46
#couch 0.10.2 d24aad80bea950ec6795f8a0cd378f3c
#couch 0.11.0 c1784e3850da01dc37dad20c5b1a85f8
#couch 0.11.1 5100ef96f332ab4449ba891a98abde87
#couch 0.11.2 076b2637dda91cb81fb9bd922ac2f112
#couch 1.0.0 71e89c4b21c62417f2f413d74a38f079
#couch 1.0.1 001cf286b72492617e9ffba271702a00
