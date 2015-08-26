""" ebssh.fabric_commands
"""
import os, sys

from fabric import api

from ebssh.decorators import using_eb_ssh_context
from ebssh.decorators import using_fabric_context

@using_eb_ssh_context
@using_fabric_context
def run(remote_cmd, key_file=None, ip=None):
    """ run command on remote """
    api.run(remote_cmd)

@using_eb_ssh_context
@using_fabric_context
def put(local_path, remote_path='~', key_file=None, ip=None):
    """ put(local_path, remote_path) will scp local-path to remote-path"""
    assert all([local_path, key_file, ip])
    api.put(local_path, remote_path)

@using_eb_ssh_context
@using_fabric_context
def get(remote_path, local_path='.', key_file=None, ip=None):
    """ get(remote_path, local_path) will scp remote-path to local-path """
    assert all([remote_path, local_path, key_file, ip])
    api.get(remote_path, local_path)
