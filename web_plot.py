#!/usr/bin/env python
# -*- coding: us-ascii -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab
#
# web_plot.py - Serve SVGs of json plots from https://github.com/clach04/sbc_temperature_monitor/
# Copyright (C) 2020  Chris Clark
"""Serve SVG of json plots

Uses WSGI, see http://docs.python.org/library/wsgiref.html

Python 2 or Python 3
"""

import cgi
import os
import logging
import mimetypes
from pprint import pprint

import socket
import struct
import sys
from wsgiref.simple_server import make_server

import glob
import json

import stress_plot


log = logging.getLogger(__name__)
logging.basicConfig()
log.setLevel(level=logging.DEBUG)


def to_bytes(in_str):
    # could choose to only encode for Python 3+
    return in_str.encode('utf-8')

def not_found(environ, start_response):
    """serves 404s."""
    #start_response('404 NOT FOUND', [('Content-Type', 'text/plain')])
    #return ['Not Found']
    start_response('404 NOT FOUND', [('Content-Type', 'text/html')])
    return [to_bytes('''<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
<html><head>
<title>404 Not Found</title>
</head><body>
<h1>Not Found</h1>
<p>The requested URL /??????? was not found on this server.</p>
</body></html>''')]


def determine_local_ipaddr():
    local_address = None

    # Most portable (for modern versions of Python)
    if hasattr(socket, 'gethostbyname_ex'):
        for ip in socket.gethostbyname_ex(socket.gethostname())[2]:
            if not ip.startswith('127.'):
                local_address = ip
                break
    # may be none still (nokia) http://www.skweezer.com/s.aspx/-/pypi~python~org/pypi/netifaces/0~4 http://www.skweezer.com/s.aspx?q=http://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib has alonger one

    if sys.platform.startswith('linux'):
        import fcntl

        def get_ip_address(ifname):
            ifname = ifname.encode('latin1')
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            return socket.inet_ntoa(fcntl.ioctl(
                s.fileno(),
                0x8915,  # SIOCGIFADDR
                struct.pack('256s', ifname[:15])
            )[20:24])

        if not local_address:
            for devname in os.listdir('/sys/class/net/'):
                try:
                    ip = get_ip_address(devname)
                    if not ip.startswith('127.'):
                        local_address = ip
                        break
                except IOError:
                    pass

    # Jython / Java approach
    if not local_address and InetAddress:
        addr = InetAddress.getLocalHost()
        hostname = addr.getHostName()
        for ip_addr in InetAddress.getAllByName(hostname):
            if not ip_addr.isLoopbackAddress():
                local_address = ip_addr.getHostAddress()
                break

    if not local_address:
        # really? Oh well lets connect to a remote socket (Google DNS server)
        # and see what IP we use them
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 53))
        ip = s.getsockname()[0]
        s.close()
        if not ip.startswith('127.'):
            local_address = ip

    return local_address


# A relatively simple WSGI application.
# ignore URL send SVG back :-)
def simple_app(environ, start_response):
    status = '200 OK'
    #headers = [('Content-type', 'text/plain')]
    headers = [('Content-type', 'image/svg+xml;charset=utf-8')]
    result = []

    t_chart = stress_plot. generate_pygal_chart()

    start_response(status, headers)
    result.append(t_chart.render())
    #result.append(to_bytes('hello'))
    return result


server_port = 8000
server_port = 8080
server_port = 8777

httpd = make_server('', server_port, simple_app)
print("Serving on port %d..." % server_port)
local_ip = determine_local_ipaddr()
log.info('Starting server: %r', (local_ip, server_port))
log.info('Starting server: http://%s:%d', local_ip, server_port)
httpd.serve_forever()

