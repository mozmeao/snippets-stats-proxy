Snippets Stats Proxy
==========================

This software is part of an experiment to evaluate Google Analytics as a
platform to collect, process and display snippet metrics data.

It collects requests from snippet actions (impressions, clicks and other) and
proxies them to Google Analytics before redirecting the user to the current data
collection pipeline at snippets-stats.mozilla.org.


Why this is proxy needed?
------------------------

This proxy is came into existence to fulfill the following:

1. Allow us to collect data in Google Analytics without directly sending users
   to Google. Instead browsers hit Mozilla managed cloud servers that run this
   proxy which in turn submit to GA limited amount of data as described in
   [Data Collection Chapter](http://abouthome-snippets-service.readthedocs.io/en/latest/data_collection.html)
   of Snippets documentation.

2. Allow us to maintain the current data collection pipeline while evaluating
   Google Analytics. The proxy receives the metrics and queues it to send it
   up to Google and then redirects browsers to the current data collection
   endpoint at https://snippets-stats.mozilla.org. The redirection is
   necessary because the current data collection pipeline extracts location
   information from IP before discarding it, therefore the ping must be made
   from the user's browser.


Parameters
----------
 1. GOOGLE_ANALYTICS_ID

    Google Analytics ID to collect the data under. If unset no data gets send to GA.

 2. GOOGLE_ANALYTICS_URL

    Google Analytics endpoint URL. Defaults to https://ssl.google-analytics.com/collect

 3. MOZILLA_ANALYTICS_URL

    Mozilla Analytics endpoint URL. If unset return 200 OK instead of redirect.
    Defaults to https://snippets-stats.mozilla.org/foo.html

 4. STATSD_HOST, STATSD_PORT and STATSD_PREFIX

    Optional Statsd host, port and prefix to collect views and exception counts.
