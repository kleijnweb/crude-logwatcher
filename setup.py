#!/usr/bin/env python3
import sys

from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand

install_requires = [
    'PyYAML>=3.11',
    'requests>=2.9.1',
    'typing>=3.6.1; python_version < "3.6"',
    'python-dateutil>=2.6.1'
]

tests_require = [
    'mock',
    'pytest',
    'pytest-cov'
]


class PyTest(TestCommand):
    user_options = [('cov-html=', None, 'Generate junit html report')]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.cov = None
        self.pytest_args = ['--cov', 'logwatcher', '--cov-report', 'term-missing', '-v']
        self.cov_html = False

    def finalize_options(self):
        TestCommand.finalize_options(self)
        if self.cov_html:
            self.pytest_args.extend(['--cov-report', 'html'])
        self.pytest_args.extend(['tests'])

    def run_tests(self):
        import pytest

        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


def readme():
    try:
        return open('README.rst', encoding='utf-8').read()
    except TypeError:
        return open('README.rst').read()


setup(
    name='logwatcher',
    packages=find_packages(),
    version='0.0.1',
    description='Crude Log Parser And Notification Utility',
    long_description=readme(),
    author='John Kleijn',
    author_email='john@kleijnweb.nl',
    url='https://github.com/zalando/logwatcher',
    keywords='log monitor slack',
    license='LGPL',
    setup_requires=['flake8'],
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={'tests': tests_require},
    cmdclass={'test': PyTest},
    test_suite='tests',
    classifiers=[
        'Programming Language :: Python :: 3 :: Only',
        'Intended Audience :: Information Technology',
        'Operating System :: POSIX :: Linux',
        'Topic :: Internet :: Log Analysis'
    ],
    #entry_points={'console_scripts': ['logwatcher = logwatcher.main']}
)
