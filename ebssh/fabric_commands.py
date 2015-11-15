""" ebssh.fabric_commands
"""
from fabric import api

from ebssh import config
from ebssh.data import SYS_ENV_PATH_OLD, SYS_ENV_PATH_NEW
from ebssh.decorators import using_eb_ssh_context
from ebssh.decorators import using_fabric_context


@using_eb_ssh_context
@using_fabric_context
def run(remote_cmd, key_file=None, ip=None):
    """ run command on remote """
    assert isinstance(remote_cmd, basestring)
    return api.run(remote_cmd)


@using_eb_ssh_context
@using_fabric_context
def sudo(remote_cmd, key_file=None, ip=None, **kargs):
    """ run command on remote """
    assert isinstance(remote_cmd, basestring)
    return api.sudo(remote_cmd)


@using_eb_ssh_context
@using_fabric_context
def run_sysenv(remote_cmd, key_file=None, ip=None):
    """ run command on remote, using envvars """
    assert isinstance(remote_cmd, basestring)
    cmd = "[[ -e {0} ]] && envvars_file={0} || envvars_file={1} && source $envvars_file".format(
        SYS_ENV_PATH_OLD, SYS_ENV_PATH_NEW)
    with api.prefix(cmd):
        # prefix means that EB environment variables
        # should be taken into account
        return api.run(remote_cmd)


@using_eb_ssh_context
@using_fabric_context
def put(local_path, remote_path='~', key_file=None, ip=None):
    """ put(local_path, remote_path) will scp local-path to remote-path"""
    assert all([local_path, key_file, ip])
    return api.put(local_path, remote_path)


@using_eb_ssh_context
@using_fabric_context
def get(remote_path, local_path='.', key_file=None, ip=None):
    """ get(remote_path, local_path) will scp remote-path to local-path """
    assert all([remote_path, local_path, key_file, ip])
    return api.get(remote_path, local_path)
