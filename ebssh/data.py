""" ebssh.data
"""
DEFAULT_USER = 'ec2-user'

# there are at least two options for where to find the envvars on the
# remote system, maybe more for other platforms and other standard
# AMIs in circulation?  annoying
SYS_ENV_PATH_OLD = '/opt/elasticbeanstalk/support/envvars.d/sysenv'
SYS_ENV_PATH_NEW = '/opt/elasticbeanstalk/support/envvars'
# aaaand for python beanstalks: /opt/python/current/env
