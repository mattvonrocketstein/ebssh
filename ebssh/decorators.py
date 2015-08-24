""" ebssh.decorators
"""
import contextlib

import mock
import ebcli

from fabric import api

from ebcli.objects import exceptions as _exceptions
from ebcli.operations.commonops import get_instance_ids as _oget_instance_ids
from ebcli.operations.sshops import _get_ssh_file


from ebssh import config

DEFAULT_USER = 'ec2-user'

def using_eb_context(fxn):
    """ this is a decorator that allows functions to run in a similar
        context to what the eb command line client expects after it
        is fully bootstrapped.  the problem is that while the awsebcli
        source is easy to read, it's often the case that it's not at all
        reusable because of the complex bootstrapping the command line
        utility requires (reading configuration files, potentially overriding
        that config with environment variables, etc etc).

        this code uses a context manager to patch "just enough" for
        code-reuse to be a realistic possibility.  i don't think there's
        another option here but be warned: this is a very dirty approach,
        and won't necessarily work with versions of awsebcli!=3.5.  on the
        bright side, patching with mock does make this a contextmanager
        proper.. there will be no sideffects outside of the decorated
        function call.
    """

    def newf(*args, **kargs):
        managers = [
            mock.patch('ebcli.lib.aws._region_name', new=config.REGION),
            mock.patch('ebcli.lib.aws._id', new=config.ACCESS),
            mock.patch('ebcli.lib.aws._key', new=config.SECRET),
            ]
        with contextlib.nested(*managers):
            return fxn(*args, **kargs)
    return newf


@using_eb_context
def _get_instance_ids():
    return _oget_instance_ids(config.APP_NAME, config.ENV_NAME)

# very similar to ebcli's `ssh_into_instance`, except that
#  1) logging has been hijacked
#  2) the given function will be called once ssh has been enabled
@using_eb_context
def beanstalk_ssh_wrapper(fxn, *args, **kargs):
    instance_id = kargs.pop('instance_id', None)
    force_open = kargs.pop('force_open', False)
    assert fxn and instance_id
    fxn_args = args
    fxn_kargs = kargs
    print 'INFO: defaulting to instance-id', instance_id
    instance = ebcli.lib.ec2.describe_instance(instance_id)
    try:
        keypair_name = instance['KeyName']
    except KeyError:
        raise _exceptions.NoKeypairError()
    try:
        ip = instance['PublicIpAddress']
    except KeyError:
        raise _exceptions.NotFoundError(
            ebcli.resources.strings.strings['ssh.noip'])
    security_groups = instance['SecurityGroups']

    # Get security group to open
    ssh_group = None
    has_restriction = False
    group_id = None
    for group in security_groups:
        group_id = group['GroupId']
        # see if group has ssh rule
        group = ebcli.lib.ec2.describe_security_group(group_id)
        for permission in group.get('IpPermissions', []):
            if permission.get('ToPort', None) == 22:
                # SSH Port group
                ssh_group = group_id
                for rng in permission.get('IpRanges', []):
                    ip_restriction = rng.get('CidrIp', None)
                    if ip_restriction is not None \
                            and ip_restriction != '0.0.0.0/0':
                        has_restriction = True

    if has_restriction and not force_open:
        print 'Found SSH restrictions; Force is False'
        print ebcli.resources.strings.strings['ssh.notopening']
    elif group_id:
        print 'INFO: No ssh restrictions were found'
        # Open up port for ssh
        print ebcli.resources.strings.strings['ssh.openingport']
        ebcli.lib.ec2.authorize_ssh(ssh_group or group_id)
        print ebcli.resources.strings.strings['ssh.portopen']

    fxn_kargs.update(key_file=_get_ssh_file(keypair_name), ip=ip)
    try:
        # call the given fxn while ssh on the remote
        # beanstalk host is still enabled
        return fxn(*fxn_args, **fxn_kargs)
    finally:
        if (not has_restriction or force_open) and group_id:
            print 'INFO: Revoking ssh access'
            ebcli.lib.ec2.revoke_ssh(ssh_group or group_id)
            print ebcli.resources.strings.strings['ssh.closeport']


def using_eb_ssh_context(fxn):
    """ decorator that changes fxn to run inside a context
        where ssh access to beanstalk has been granted to
        the outside world.  this access is revoked automatically
        regardless of of any errors occuring in the decorated
        function
    """
    def newf(*args, **kargs):
        ids = _get_instance_ids()
        fxn_args = args
        kargs.update(instance_id=ids[0])
        return beanstalk_ssh_wrapper(fxn, *fxn_args, **kargs)
    return newf


def using_fabric_context(fxn):
    """ decorator that changes fxn to run inside a context
        where fabric has been configured to connect to
        the beanstalk host using the correct user, key, and
        hostname
    """
    def newf(*args, **kargs):
        ip = kargs['ip']
        key = kargs['key_file']
        with api.settings(user=config.USER,
                          host_string=ip, key_filename=key):
            return fxn(*args, **kargs)
    return newf
