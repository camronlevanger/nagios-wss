#!/usr/bin/python
import sys
import os
import traceback
import argparse

from twisted.python import log
from twisted.internet import reactor

from autobahn.websocket import connectWS
from autobahn.wamp import WampClientFactory
from autobahn.wamp import WampClientProtocol

exit_code = 3
exit_message = 'UNKNOWN - Unable to get info for socket connections'

class NagiosMonitor(WampClientProtocol):

    def onOpen(self):
        global exit_code
        global exit_message
        exit_code = 1
        exit_message = 'Warning - Welcome message recieved, but no session'

    def onSessionOpen(self):
        global exit_code
        global exit_message
        exit_code = 0
        exit_message = 'OK - Socket session fully established'
        self.dropConnection(self)
        reactor.stop()

    def clientConnectionFailed(self, connector, reason):
        global exit_code
        global exit_message
        exit_code = 2
        exit_message = "CRITICAL - Unable to connect to socket server"
        reactor.stop()    
      

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='A Nagios plugin to monitor WAMP servers')
    parser.add_argument('-H', '--host')
    parser.add_argument('--debug', action="store_true")
    parser.add_argument('-t', '--timeout', type=int)
    args = parser.parse_args()

    host = 'wss://localhost:8080'
    if args.host != None:
        host = args.host

    debug = False
    if args.debug != None:
        debug = args.debug

    timeout = 30
    if args.timeout != None:
        timeout = args.timeout


    try:
        if debug:
            log.startLogging(sys.stdout)

        factory = WampClientFactory(host, debugWamp=debug)
        factory.protocol = NagiosMonitor
        connectWS(factory, timeout = timeout)
        reactor.run()
    except KeyboardInterrupt:
        print "Shutdown requested...exiting"
    except Exception:
        traceback.print_exc(file=sys.stdout)

    print exit_message
    sys.exit(exit_code)
