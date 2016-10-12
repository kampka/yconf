yconf
=====
|Travis|_

A wrapper for combining yaml configuration files and command line argument parsing.
It builds upon PyYAML_ for parsing yaml config files and argparse_ for handling command line arguments and adds the clue produce one unified program configuration.


Requirements
------------

 - Python 2.7+ or 3.2+
 - PyYAML >= 3.1

Configuration Environments
--------------------------

Because configuration often differs depending on the environment, e.g. production and testing settings, yconf allows you to define multiple environments in a single configuration.
The current supported environemts are `production`, `staging` and `development`. For convenience, yconf is able to merge environment configuration to reduce redundancy, meaning that if the environment is set to `staging`, the configuration will inherit all settings available in a `production` environment and override them with `staging` values where neseccary.

Example
```````

config.yml

::

    production:
      rundir: /var/run/example
      database: /var/lib/example/db.sqlite
      loglevel: warning

    staging:
      database: :memory:

    development:
      loglevel: debug

Configuration

::

    # production environment
    config.rundir: /var/run/example
    config.database: /var/lib/example/db.sqlite
    config.loglevel: warning

    # staging environment
    config.rundir: /var/run/example
    config.database: :memory:
    config.loglevel: warning

    # development environment
    config.rundir: /var/run/example
    config.database: :memory:
    config.loglevel: debug

Both `staging` and `development` environments are optional.

If a directory is specified instead of a configuration file, yconf will
look for configuration files by convention of <environment>.yml in that
directory and merge them accordingly if possible.


Command Line Arguments
----------------------

Extending the argument list supported by a configuration will require subclassing `yconf.BaseConfiguration` and overriding the `makeParser` method.

Example

::

  import sys
  from yconf import BaseConfiguration

  class MyConfig(BaseConfiguration):

    def makeParser(self):
      parser = super(MyConfig, self).makeParser()
      parser.add_argument("-f", "--foo", dest="foo")
      return parser


  config = MyConfig()
  config.parse(sys.argv[1:])


The following configuration arguments are already preset:

  - `-c` Path to configuration file or directory
  - `-e` The environment used for configuration (default: production)

When present, command line argument always take precedent over configuration settings. To override nested yaml values, a dotted destination path can be set for the argument.

config.yml

::

    logging:
      loglevel: debug

Argument

::

    parser.add_argument("--log-level", dest="logging.loglevel")


Accessing Configuration
-----------------------

Configuration can be accessed either by attribute or by key.

::

  config = MyConfig()
  config.parse(args)

  config.foo == config['foo']
  config.foo.bar == config['foo']['bar']



.. _PyYAML: http://pyyaml.org/
.. _argparse: http://pypi.python.org/pypi/argparse
.. |Travis| image:: https://travis-ci.org/kampka/yconf.png?branch=master
.. _Travis: https://travis-ci.org/kampka/yconf/jobs/167164716#
