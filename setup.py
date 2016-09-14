from setuptools import setup
from setuptools.command.test import test as TestCommand
import sys


class Tox(TestCommand):
    user_options = [('tox-args=', 'a', "Arguments to pass to tox")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.tox_args = None

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import tox
        import shlex
        args = self.tox_args
        if args:
            args = shlex.split(self.tox_args)
        errno = tox.cmdline(args=args)
        sys.exit(errno)


setup(
    name='django-statsd-influx',
    packages=['influx'],
    version='0.1',
    description='Django Statsd Influx Client ',
    author='Jure Ham, Zemanta',
    author_email='jure.ham@zemanta.com',
    url='https://github.com/Zemanta/django-statsd-influx',
    download_url='https://github.com/Zemanta/django-statsd-influx/tarball/0.1',
    keywords=['statsd', 'influx', 'influxdb', 'django'],
    install_requires=[
        'statsd==3.2.1',
    ],
    tests_require=['tox', 'virtualenv', 'statsd==3.2.1', 'Django>=1.8.4'],
    cmdclass={'test': Tox},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
    ],
)
