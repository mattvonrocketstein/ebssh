[About](#about) | [Installation](#installation) | [Examples](#examples) | [Contributing](#contributing)


<a name="about">ABOUT</a>
=========================

#### **Summary:**

`Ebssh` is a library that helps [fabric](http://www.fabfile.org/) talk to elastic beanstalk.

#### **Background:**

Elastic beanstalk (henceforth "beanstalk") is a PaaS offering from Amazon that simplifies deployment, autoscaling, etc.  If you don't already know what it is, you probably don't need this library.  The command line utility for beanstalk is called `eb`, and provided via the `ebcli` library.  The `eb ssh` invocation allows you to ssh into beanstalk instances,  and in some situations, `eb ssh` may work where a normal invocation of `ssh` would fail because `eb ssh` is flipping firewall rules on and off (via amazon API) in order to allow you to connect.  (Let's call this kind of setup a situation that allows only "restricted access".)  The `ebcli` package itself is maintained by amazon, and only unofficial forks are out in public.

#### **Problem:**
If your beanstalk setup only allows restricted access, it can be difficult to talk to it at all outside of using the existing `eb` command line client, and for the reasons mentioned above this client is difficult to extend and the code is difficult to reuse.  Commands like `eb scp` are also conspicuously missing.

#### **Solution:**

This library does the minimal amount of monkey-patching necessary to reuse as much of the ebcli code as possible, and provides things like context managers and fabric-friendly commands to perform various ssh operations with beanstalk instances.

#### **Limitations:**

Because of the way ssh access is made possible and then revoked, multiple ssh operations should not occur simultaneously.  Given a beanstalk application and environment, there is currently no way to choose which exact beanstalk instance you get connected to.  Theoretically this is a non-issue because the instances are all identical peers anyway and you're working with a stateless system (or else beanstalk would not be attractive for your use-case anyway).  This is pretty easy to fix but hasn't been prioritized.

<a name="installation">INSTALLATION</a>
=======================================

```
  $ git clone https://github.com/mattvonrocketstein/ebssh.git
  $ cd ebssh
  $ python setup.py develop
```


<a name="examples">Examples</a>
====================================

#### Minimal Fabric example

**Inside fabfile.py:**
```
from ebssh import config
from ebssh.fabric_commands import run_sysenv as run
from ebssh.fabric_commands import put, sudo, get


config.update(
  EB_APP = 'beanstalk_application_name',
  EB_ENV = 'beanstalk_environment_name',
  EB_USER = 'ec2-user',
  EB_KEY = 'beanstalk_key.pem',
  AWS_DEFAULT_REGION='us-east-1',
  AWS_ACCESS_KEY='access_key',
  AWS_SECRET_KEY='secret_key',)
```

The example above is a fully functioning fabfile, but of course it's also possible to use the fabric commands inside other fabric commands in all the usual ways.  For our minimal fabfile, `fab -l` gives:

```
$ fab -l
Available commands:
    get   get(remote_path, local_path) will scp remote-path to local-path
    put   put(local_path, remote_path) will scp local-path to remote-path
    run   run command on remote, using envvars
    sudo  run command on remote
```

The `run` command already knows about the beanstalk environment variables on the remote side.  For example:

```shell
$ fab run:"echo \$RDS_USERNAME"
INFO: defaulting to instance-id i-40b817e3
INFO: No ssh restrictions were found
INFO: Attempting to open port 22.
INFO: SSH port 22 open.
[52.0.41.174] run: echo $RDS_USERNAME
[52.0.41.174] out: database_user
INFO: Revoking ssh access
INFO: Closed port 22 on ec2 instance security group.
```

<a name="contributing">Contributing</a>
========================================

Patches welcome.
