#!/usr/bin/python3

import pickle
import subprocess as sub

from mitmproxy import ctx
from mitmproxy.proxy.protocol import TlsLayer
from mitmproxy.exceptions import TlsProtocolException

dataf = "output.log"

# TLS layer wrapper to detect failed connections.
class TlsDetectFail(TlsLayer):

    def _establish_tls_with_client(self):
        try:
            super()._establish_tls_with_client()
        except TlsProtocolException as e:
            addr, sni = self.server_conn.ip_address, self.server_conn.sni
            log_data((False, sni, addr), dataf)
            raise e

class Interceptor:

    def __init__(self):
        self.command = ""

    # When the addon is loaded adds a new option
    def load(self, loader):
        loader.add_option(
                name = "app",
                typespec = str,
                default = "com.android.chrome",
                help = "App to be examined",
        )

    # Configure the command when the app
    # option is modified.
    def configure(self, updated):
        if ctx.options.app:
            app = ctx.options.app
            self.command = "adb shell netstat -utpn | grep " + app + " | sort | uniq | tr -s ' ' | cut -d ' ' -f 4"

    # Replace next layer in client TLS
    # Handshake to detect failures.
    def next_layer(self, nlayer):
        if isinstance(nlayer, TlsLayer) and nlayer._client_tls:
            nlayer.__class__ = TlsDetectFail

    # For each request checks if it belongs to our app
    # and logs it if neccessary.
    def request(self, flow):
        port, host = conn_data(flow.client_conn, flow.request)
        if valid_conn(port, self.command):
            log_data((True, host, flow.request), dataf)

###########################################################################################################################
#                                                                                                                         #
#                                       Utils                                                                             #
#                                                                                                                         #
###########################################################################################################################

# Logs a an entry to a selected datafile
def log_data(entry, dataf):
    with open(dataf, "ab") as f:
        pickle.dump(entry, f)

# Checks if connection is from the specified app
def valid_conn(port, command):
    nets = call_sh(command).splitlines()
    ports = app_ports(nets)
    return port in ports

# Returns client port and server domain
# of a HTTP connection.
def conn_data(client, req):
    port = client.address[1]
    host = get_host(client, req)
    return (port, host)

# Gets host from SNI or header information.
def get_host(client, req):
    if client.sni:
        return client.sni
    elif "Host" in req.headers:
        return req.headers["Host"]
    elif "host" in req.headers:
        return req.headers["host"]
    else:
        return "unknown"

# Returns a list of every port of a connection
# of the selected app
def app_ports(ports):
    res = []
    for l in ports:
        port = int(l.split(":")[-1])
        res.append(port)
    return res

# Executes a command in a shell and returns its output
def call_sh(command):
    return sub.run(command, shell=True, stdout=sub.PIPE, stderr=sub.PIPE).stdout.decode("utf-8")

addons = [Interceptor()]
