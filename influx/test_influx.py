from unittest import TestCase

import influx

influx.configure(
    project_name='my_project',
    statsd_host='localhost',
    statsd_port='8125',
)



class MockStatsd:

    def incr():
        pass

    def gauge():
        pass

    def timing():
        pass


class InfluxHelperTestCase(TestCase):

    def setUp(self):
        influx._telegraf_client = MockStatsd()

    def test_tag_none(self):
        influx._hostname = 'test_host'
        tags = {
            'tag1': 'v1',
            'tag2': '',
            'tag3': None,
        }
        result = influx._get_tags(tags)
        self.assertEqual(result, 'tag1=v1,host=test_host')

    def test_influx_incr(self):
        res = {}

        def incr(n, v):
            res['metric_name'] = n
            res['metric_value'] = v

        influx._telegraf_client.incr = incr
        influx._hostname = "my_host"

        influx.incr('test.metric', 2, source='my_source', tag='tag1')

        self.assertEqual(res, {
            'metric_name': 'my_project.test.metric,source=my_source,tag=tag1,host=my_host',
            'metric_value': 2,
        })

    def test_influx_gauge(self):
        res = {}

        def gauge(n, v):
            res['metric_name'] = n
            res['metric_value'] = v

        influx._telegraf_client.gauge = gauge
        influx._hostname = "h"

        influx.gauge('test.metric', 'v', source='my_source', tag='tag1')

        self.assertEqual(res, {
            'metric_name': 'my_project.test.metric,source=my_source,tag=tag1,host=h',
            'metric_value': 'v',
        })

    def test_influx_timing(self):
        res = {}

        def timing(n, v):
            res['metric_name'] = n
            res['metric_value'] = v

        influx._telegraf_client.timing = timing
        influx._hostname = "h"

        influx.timing("test.metric", 1.3, source='my_source', tag='tag1')

        self.assertEqual(res['metric_name'], 'my_project.test.metric,source=my_source,tag=tag1,host=h')
        self.assertEqual(res['metric_value'], 1300)

    def test_influx_block_timer(self):
        res = {}

        def timing(n, v):
            res['metric_name'] = n
            res['metric_value'] = v

        influx._telegraf_client.timing = timing
        influx._hostname = "h"

        with influx.block_timer("test.metric", source='my_source', tag='tag1'):
            pass

        self.assertEqual(res['metric_name'], 'my_project.test.metric,source=my_source,tag=tag1,host=h')

    def test_influx_decorator(self):
        res = {}

        def timing(n, v):
            res['metric_name'] = n
            res['metric_value'] = v

        influx._telegraf_client.timing = timing
        influx._hostname = "h"

        @influx.timer("test.metric", source='my_source', tag='tag1')
        def noop():
            pass

        noop()

        self.assertEqual(res['metric_name'], 'my_project.test.metric,source=my_source,tag=tag1,host=h')
