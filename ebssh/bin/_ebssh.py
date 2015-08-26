""" ebssh.bin._ebssh
"""

import os, sys

from fabric import api
from fabric.colors import red

from ebssh import config
from ebssh.decorators import using_eb_ssh_context
from ebssh.decorators import using_fabric_context
from ebssh.fabric_commands import run, put, get

_help = (
    'The ebssh commandline utility requires all of the '
    'following environment variables to be set: '
    'AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_DEFAULT_REGION, '
    'EB_APP, EB_ENV.  Optionally, you can set EB_USER '
    '(defaults to ec2-user)')

try:
    context = dict(
        ACCESS=os.environ['AWS_ACCESS_KEY'],
        SECRET=os.environ["AWS_SECRET_KEY"],
        REGION=os.environ['AWS_DEFAULT_REGION'],
        APP_NAME=os.environ['EB_APP'],
        ENV_NAME=os.environ['EB_ENV'],
        USER=os.environ.get(
            'EB_USER', 'ec2-user'))
except KeyError:
    print # warnings clutter the startup, make sure error is visible
    print red('ERROR: ')+_help
    raise SystemExit(1)

else:
    config.update(context)a

# clean namespace, some things should
# not be listed as fabric commands
del using_fabric_context
del using_eb_ssh_context

if __name__ == '__main__':

    # a neat hack that makes this file a "self-hosting" fabfile,
    # ie it is invoked directly but still gets all the fabric niceties
    # like real option parsing, including --help and -l (for listing
    # commands). note that as of fabric 1.10, the file for some reason
    # needs to end in .py, despite what the documentation says.  see:
    # http://docs.fabfile.org/en/1.4.2/usage/fabfiles.html#fabfile-discovery
    #
    # the .index() manipulation below should make this work regardless of
    # whether this is invoked from shell as "./foo.py" or "python foo.py"
    from fabric.main import main as fmain
    patched_argv = ['fab', '-f', __file__, ] + \
        sys.argv[sys.argv.index(__file__) + 1:]
    sys.argv = patched_argv
    fmain()
