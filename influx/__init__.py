import time
import socket
import logging

from contextlib import contextmanager

import decorator
import statsd

logger = logging.getLogger(__name__)

_hostname = 'unknown'
try:
    _hostname = socket.gethostname().replace('.', '-')
except Exception:
    pass

_telegraf_client = None

_statsd_influx_host = None
_statsd_influx_port = None
_project_name = ''


class MissingConfiguration(Exception):
    pass


def _get_client():
    global _telegraf_client

    if not _statsd_influx_host:
        raise MissingConfiguration('Missing STATSD_INFLUX_HOST setting')

    if not _statsd_influx_port:
        raise MissingConfiguration('Missing STATSD_INFLUX_PORT setting')

    if _telegraf_client is None:
        _telegraf_client = statsd.StatsClient(_statsd_influx_host, _statsd_influx_port)

    return _telegraf_client


def _get_default_tags():
    return [('host', _hostname)]


def _escape_tags(tag):
    return tag.replace(':', '_')


def _get_tags(custom_tags):
    tags = sorted(custom_tags.items(), key=lambda x: x[0]) + _get_default_tags()

    return ','.join('{0}={1}'.format(_escape_tags(k), _escape_tags(v)) for k, v in tags)


def configure(statsd_host, statsd_port, project_name):
    global _statsd_influx_host
    global _statsd_influx_port
    global _project_name

    _statsd_influx_host = statsd_host
    _statsd_influx_port = statsd_port
    _project_name = project_name


def timing(name, seconds, **tags):
    new_name = '{prefix}.{name},{tags}'.format(
        prefix=_project_name,
        source=_hostname,
        name=name,
        tags=_get_tags(tags),
    )
    _get_client().timing(new_name, int(seconds * 1000))


@contextmanager
def block_timer(name, **tags):
    start = time.time()
    yield
    timing(name, (time.time() - start), **tags)


def timer(name, **tags):
    def decorate(func):
        def wrapper(*args, **kwargs):
            with block_timer(name, **tags):
                result = func(*args, **kwargs)
            return result
        return decorator.decorate(func, wrapper)
    return decorate


def incr(name, count, **tags):
    _get_client().incr('{prefix}.{name},{tags}'.format(
        prefix=_project_name,
        name=name,
        tags=_get_tags(tags),
    ), count)


def gauge(name, value, **tags):
    _get_client().gauge('{prefix}.{name},{tags}'.format(
        prefix=_project_name,
        name=name,
        tags=_get_tags(tags),
    ), value)

try:
    from django.conf import settings
    configure(settings.STATSD_INFLUX_HOST, settings.STATSD_INFLUX_PORT, settings.PROJECT_NAME)
except:
    pass
