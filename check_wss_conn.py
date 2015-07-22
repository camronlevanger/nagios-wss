#!/usr/bin/python
import json
import sys
import argparse
import threading
from twisted.python import log
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks

from autobahn.twisted.wamp import ApplicationSession

"""
Setup constants
"""
EXIT_CODE_NORMAL = 0
EXIT_CODE_WARNING = 1
EXIT_CODE_CRITICAL = 2
EXIT_CODE_UNKNOWN = 3


exit_code = EXIT_CODE_UNKNOWN
exit_message = 'UNKNOWN - Unable to get info for socket connections'
topic = 'notifications.1'


class Component(ApplicationSession):

    """
    An application component that subscribes and receives events,
    and stop after having received 5 events.
    """

    @inlineCallbacks
    def onJoin(self, details):
        global exit_code
        global exit_message
        global topic
        exit_code = EXIT_CODE_CRITICAL
        exit_message = 'CRITICAL - Connected, but no messages received'

        def onEvent(msg, options=None):
            global exit_code
            global exit_message

            print("Got event: {}".format(msg))

            exit_code = EXIT_CODE_NORMAL
            exit_message = 'OK - Socket session fully established'
            reactor.stop() # We can exit now.

        try:
            yield self.subscribe(onEvent, topic)
            print "Subscribed, waiting for event..."
        except Exception:
            exit_code = EXIT_CODE_CRITICAL
            exit_message = 'CRITICAL - Connected, but no subscription made'

    def onLeave(self, details):
        """
        There is a bug in authobahn.wamp.protocol.py that always calls
        disconnect() even if there is no longer a transport, so let's just
        override it. This way Nagios doesn't get 'Unhandled Error' as the
        exit message.
        """
        if self._transport:
            self.disconnect()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='A Nagios plugin to monitor WAMP servers'
    )

    parser.add_argument('-H', '--host')
    parser.add_argument('-R', '--realm')
    parser.add_argument('-T', '--topic')
    parser.add_argument('--debug', action="store_true")
    parser.add_argument('-t', '--timeout', type=int)
    args = parser.parse_args()

    host = 'wss://localhost:8080/ws'
    if args.host is not None:
        host = str(args.host)

    realm = 'realm1'
    if args.realm is not None:
        realm = args.realm

    topic = 'notifications.1'
    if args.topic is not None:
        topic = args.topic

    debug = False
    if args.debug is not None:
        debug = args.debug

    timeout = 7 * 60 # 7 minutes
    if args.timeout is not None:
        timeout = args.timeout

    def timeoutError():
        print "Timed out!"
        reactor.stop() # This causes the runner.run() function to return.

    timeoutTimer = threading.Timer(timeout, timeoutError)
    timeoutTimer.start()

    try:
        if debug:
            log.startLogging(sys.stdout)

        from autobahn.twisted.wamp import ApplicationRunner
        runner = ApplicationRunner(host, realm)
        runner.run(Component)

    except KeyboardInterrupt:
        print "Shutdown requested...exiting"
    except Exception:
        exit_code = EXIT_CODE_CRITICAL
        exit_message = "CRITICAL - Unable to connect to socket server"

    timeoutTimer.cancel()
    print exit_message
    sys.exit(exit_code)
