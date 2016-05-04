#Django Statsd Influx Client

###Django settings

```python
PROJECT_NAME = 'my_project',
HOSTNAME = 'localhost',
STATSD_INFLUX_HOST = 'localhost',
STATSD_INFLUX_PORT = '8125',
```

###Statsd Metric Format
```python
PROJECT_NAME.{metric_name},host=HOSTNAME,tag=value
```

###Examples

```python
influx.incr('test.metric', 2, source='my_source', tag='tag1')


influx.gauge('test.metric', 'v', source='my_source', tag='tag1')


with influx.block_timer("test.metric", source='my_source', tag='tag1'):
    call()


@influx.timer("test.metric", source='my_source', tag='tag1')
def noop():
    pass
```
    
