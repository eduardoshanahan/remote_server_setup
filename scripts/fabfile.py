from fabric.api import *
from fabric.operations import reboot
from fabric.contrib.files import append, contains, exists, uncomment, comment, sed

import os

env.colorize_errors = True

@task
def type():
    '''
    Get details about the operating system
    '''
    run('uname -a')

@task
def prepare_new_server():
    '''
    Get a server and make it ready to be used in production
    '''
    username = os.environ['REMOTE_USERNAME']
    key_path = os.environ['REMOTE_PUBLIC_KEY'] 
    setup_key_access(username, key_path)
    setup_docker()

def setup_key_access(username, key_path):
    '''
    Prepare access using keys instead of password
    '''
    create_user(username)
    prepare_keys_directory(username)
    enable_write_authorized_keys(username)
    upload_key_for_user(username, key_path)
    disable_write_authorized_keys(username)
    tell_user_own_key(username)
    tell_key_does_not_need_password(username)
    authorize_keys()
    disable_password_authentication()
    restart_ssh()

def disable_write_authorized_keys(username):
    sudo('chmod u-w /home/{name}/.ssh/authorized_keys'.format(name=username))

def enable_write_authorized_keys(username):
    sudo('touch /home/{name}/.ssh/authorized_keys'.format(name=username))
    sudo('chmod u+w /home/{name}/.ssh/authorized_keys'.format(name=username))

def enable_password_authentication_settings():
    if (contains('/etc/ssh/sshd_config', 'PasswordAuthentication yes')):
        uncomment('/etc/ssh/sshd_config', 'PasswordAuthentication yes', use_sudo=True)

def disable_password_authentication():
    enable_password_authentication_settings()
    sed('/etc/ssh/sshd_config', 'PasswordAuthentication yes', 'PasswordAuthentication no')

def tell_key_does_not_need_password(username):
    condition = '{name} ALL=(ALL) NOPASSWD: ALL'.format(name=username)
    if (not contains('/etc/sudoers', condition)):
        append('/etc/sudoers',condition, use_sudo=True)

def authorize_keys():
    uncomment('/etc/ssh/sshd_config', '#AuthorizedKeysFile', use_sudo=True)

def prepare_keys_directory(username):
    sudo('mkdir -p /home/{name}/.ssh'.format(name=username))

def tell_user_own_key(username):
    sudo('chown {name} /home/{name}/.ssh/authorized_keys'.format(name=username))

def upload_key_for_user(username, key_path):
    # TODO: Instead of overwriting the keys, I should append if not already present
    put(key_path, '/home/{name}/.ssh/authorized_keys'.format(name=username))

def create_user(username):
    sudo('id -u {name} &>/dev/null || useradd --user-group --create-home --shell /bin/bash {name} || true'.format(name=username))

def restart_ssh():
    sudo('service ssh restart')

@task
def setup_docker():
    install_docker()
    docker_user = 'deploy'
    create_user(docker_user)
    setup_docker_user(docker_user)

def install_docker():
    sudo('curl -sSL https://get.docker.com/ | sh')

def setup_docker_user(username):
    sudo('usermod -aG docker {name}'.format(name=username))