""" ebssh.bin._ebssh
"""

import os
from argparse import ArgumentParser

from fabric.colors import red

from ebssh import config
from ebssh.fabric_commands import run, put, get
from ebssh import version

_help = (
    'The ebssh commandline utility requires all of the '
    'following environment variables to be set: '
    'AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_DEFAULT_REGION, '
    'EB_APP, EB_ENV.  Optionally, you can set EB_USER '
    '(defaults to ec2-user)')

def get_parser():
    """ build the default parser """
    parser = ArgumentParser()
    # parser.set_conflict_handler("resolve")
    parser.add_argument(
        "-v", '--version', default=False, dest='version',
        action='store_true',
        help=("show version information"))
    subparsers = parser.add_subparsers(help='commands')
    help_parser = subparsers.add_parser('help', help='show help info')
    help_parser.set_defaults(subcommand='help')

    rparser = subparsers.add_parser('run', help='execute remote command')
    rparser.add_argument(
        'remote_cmd', type=unicode, help='remote command to execute')

    gparser = subparsers.add_parser('get', help='get file from remote')
    gparser.add_argument('remote_path', help='remote file')
    gparser.add_argument(
        'local_path', nargs='?', default='.', help='local file')

    pparser = subparsers.add_parser('put', help='put file to remote')
    pparser.add_argument('local_path', help='remote file')
    pparser.add_argument(
        'remote_path', nargs='?', default='~', help='local file')

    pparser.set_defaults(subcommand='put')
    gparser.set_defaults(subcommand='get')
    rparser.set_defaults(subcommand='run')
    return parser


def configure():
    _vars = 'AWS_ACCESS_KEY AWS_SECRET_KEY AWS_DEFAULT_REGION EB_APP EB_ENV'
    _vars = _vars.split()
    for v in _vars:
        try:
            config.update({v: os.environ[v]})
        except KeyError:
            print  # warnings clutter the startup, make sure error is visible
            print red('ERROR: environment variable {0} should be set'.format(v))
            raise SystemExit(1)
    USER = os.environ.get('EB_USER', 'ec2-user')
    config.update({'USER': USER})


def entry():
    parser = get_parser()
    args = parser.parse_args()
    if args.subcommand in ['version', 'help']:
        if args.subcommand == 'version':
            print version.__version__
        if args.subcommand == 'help':
            parser.print_help()
        raise SystemExit()
    configure()
    if args.subcommand == 'run':
        remote_cmd = args.remote_cmd
        result = run(remote_cmd)
        # TODO: return status code?
        return
    elif args.subcommand == 'get':
        remote_path = args.remote_path
        local_path = args.local_path
        get(remote_path, local_path)
    elif args.subcommand == 'put':
        remote_path = args.remote_path
        local_path = args.local_path
        put(local_path, remote_path)
    else:
        raise SystemExit("unrecognized subcommand")
