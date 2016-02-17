import os
import sys
from novaclient import client as novaclient

hostname = sys.argv[1]
hostname = hostname[0:hostname.find(".novalocal")]

nova = novaclient.Client(2,os.environ['OS_USERNAME'],os.environ['OS_PASSWORD'],os.environ['OS_TENANT_NAME'],os.environ['OS_AUTH_URL'],True)
server = nova.servers.find(name=hostname)
enc_metas = [enc_meta for enc_key,enc_meta in server.metadata.items() if "enc" in enc_key]
print "---\nclasses:\n  " + "\n  ".join("".join(enc_metas).split("\n"))
