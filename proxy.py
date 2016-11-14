#!/usr/bin/env python
import asyncio
import urllib
import uuid

import aiohttp
from aiohttp import web

import config


async def send_to_ga(data):
    snippet_id = data.get('snippet_name')
    if not snippet_id:
        # No snippet ID, nothing to do here.
        return

    snippet_name = data.get('snippet_full_name', '(not set)')
    metric = data.get('metric', 'impression')
    locale = data.get('locale', '(not set)')
    href = data.get('href', '(not set)')
    href_no_params = href.split('?')[0] if href else '(not set)'

    params = {
        'v': 1,
        'tid': config.GOOGLE_ANALYTICS_ID,
        'dh': config.GOOGLE_ANALYTICS_DOMAIN,
        'ds': 'about:home',
        'cid': uuid.uuid4().hex,
        'ul': locale,
        'geoid': data.get('country', 'xx'),  # If we don't mark a country, AWS gets the credit
        'ua': data.get('agent', ''),
        'dt': 'Snippet {}'.format(snippet_id),
        'dp': '/show/{}/'.format(snippet_id),
        't': 'event',
        'ec': metric,
        'ea': snippet_id,
        'el': href,
        'cd1': snippet_id,
        'cd2': snippet_name,
        'cd3': data.get('campaign', None),
        'cd4': href_no_params,
        'cd5': locale,
        'cm1': 1 if metric == 'impression' else 0,
        'cm2': 1 if metric == 'click' else 0,
        'cm3': 1 if metric == 'snippet-blocked' else 0,
    }

    try:
        async with aiohttp.get(config.GOOGLE_ANALYTICS_URL, params=params) as response:
            config.statsd.incr('process_request.ga.{}'.format(response.status))
    except (ConnectionRefusedError, aiohttp.errors.ClientError):
        config.statsd.incr('process_request.ga.exception')


def webserver():
    loop = asyncio.get_event_loop()

    def ok_view(request):
        return aiohttp.web.Response(body=b'OK', content_type='text/plain')

    def webhook(request):
        data = {
            'agent': request.headers['USER-AGENT'],
        }
        data.update(urllib.parse.parse_qsl(request.query_string))
        if config.GOOGLE_ANALYTICS_URL and config.GOOGLE_ANALYTICS_ID:
            loop.create_task(send_to_ga(data))
        config.statsd.incr('view.webhook')

        headers = {
            'Access-Control-Allow-Origin': 'null',
        }

        if config.MOZILLA_ANALYTICS_URL:
            return aiohttp.web.HTTPFound(
                '{}?{}'.format(config.MOZILLA_ANALYTICS_URL, request.query_string), headers=headers)

        return aiohttp.web.Response(body=b'OK', content_type='text/plain', headers=headers)

    app = web.Application()
    app.router.add_route('GET', '/', ok_view)
    app.router.add_route('GET', '/foo', webhook)
    return app

application = webserver()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    srv = loop.create_server(application.make_handler(), '0.0.0.0', config.PORT)
    loop.create_task(srv)
    print("Server started at {}...".format(config.PORT))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()
