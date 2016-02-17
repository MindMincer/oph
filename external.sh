#!/bin/bash
source /openrc
/usr/bin/python /etc/puppetlabs/python/get_classes.py $1 2> /dev/null | sed "s/'true'/true/g;s/'false'/false/g"
