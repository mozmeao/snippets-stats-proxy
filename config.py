import socket
import struct

from statsd import StatsClient
from decouple import config

PORT = config('PORT', default=8000)

GOOGLE_ANALYTICS_ID = config('GOOGLE_ANALYTICS_ID')
GOOGLE_ANALYTICS_DOMAIN = config('GOOGLE_ANALYTICS_DOMAIN', default='snippets.mozilla.com')
GOOGLE_ANALYTICS_URL = config('GOOGLE_ANALYTICS_URL', default='https://ssl.google-analytics.com/collect')
MOZILLA_ANALYTICS_URL = config('MOZILLA_ANALYTICS_URL', default='https://snippets-stats.mozilla.org/foo.html')

# via http://stackoverflow.com/a/6556951/107114
def get_default_gateway_linux():
    """Read the default gateway directly from /proc."""
    try:
        with open("/proc/net/route") as fh:
            for line in fh:
                fields = line.strip().split()
                if fields[1] != '00000000' or not int(fields[3], 16) & 2:
                    continue

                return socket.inet_ntoa(struct.pack("<L", int(fields[2], 16)))
    except IOError:
        return 'localhost'


STATSD_HOST = config('STATSD_HOST', get_default_gateway_linux())
STATSD_PORT = config('STATSD_PORT', 8125, cast=int)
STATSD_PREFIX = config('STATSD_PREFIX', default='snippets_proxy')
statsd = StatsClient(STATSD_HOST, STATSD_PORT, prefix=STATSD_PREFIX)
