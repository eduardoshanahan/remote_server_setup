import os

from fabric.api import *
from fabric.contrib.files import append
from fabric.contrib.files import contains
from fabric.contrib.files import uncomment
from fabric.contrib.files import sed
from fabric.context_managers import shell_env

env.colorize_errors = True
env.hosts = [os.getenv('REMOTE_HOST')]


@task
def update_remote_host():
    """
    Update packages in the remote host
    """
    sudo('apt-get update')
    sudo('apt-get upgrade -y')


@task
def local_test():
    """
    Check if your environment variables are ready
    """
    print ('Local test')
    username = os.getenv('REMOTE_USERNAME')
    print ('Fabric has REMOTE_USERNAME with the value', username)


@task
def root_remote_test():
    """
    A small test to check if you can access your remote server using a password, it will try to get details about the operating system
    """
    print ('Root remote test')
    print ('pass', os.getenv('REMOTE_ROOT_PASSWORD'))
    env.user = os.getenv('REMOTE_ROOT_USERNAME')
    env.password = os.getenv('REMOTE_ROOT_PASSWORD')
    run('uname -a')

@task
def use_keys():
    """
    Setup key access to the remote server
    """
    print ('Use keys')
    env.user = os.getenv('REMOTE_USERNAME')
    private_key_filename = os.getenv('PRIVATE_KEY_FILENAME')
    docker_ssh_keys_path = os.getenv('DOCKER_SSH_KEYS_PATH')
    print (env.user, private_key_filename, docker_ssh_keys_path)
    env.key_filename=os.path.join('/',docker_ssh_keys_path,private_key_filename)
    print (env.key_filename)

@task
def key_remote_test():
    """
    A small test to check if you can access your remote server using a key, it will try to get details about the operating system
    """
    use_keys()
    print('Key remote test')
    run('uname -a')


@task
def prepare_new_server():
    """
    Get a server and make it ready to be used in production
    """
    print ('Prepare new server')
    env.user = os.getenv('REMOTE_ROOT_USERNAME')
    env.password = os.getenv('REMOTE_ROOT_PASSWORD')
    username = os.getenv('REMOTE_USERNAME')
    public_key_filename = os.getenv('PUBLIC_KEY_FILENAME')
    docker_ssh_keys_path = os.getenv('DOCKER_SSH_KEYS_PATH')
    public_key_path=os.path.join('/',docker_ssh_keys_path,public_key_filename)
    setup_key_access(username, public_key_path)
    setup_docker_with_deploy_user()


def setup_key_access(username, key_path):
    """
    Prepare access using keys instead of password
    """
    print('Setup key access')
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
    print('Disable write authorized keys')
    sudo('chmod u-w /home/{name}/.ssh/authorized_keys'.format(name=username))


def enable_write_authorized_keys(username):
    print ('Enable write authorized keys')
    sudo('touch /home/{name}/.ssh/authorized_keys'.format(name=username))
    sudo('chmod u+w /home/{name}/.ssh/authorized_keys'.format(name=username))


def enable_password_authentication_settings():
    print ('Enable password authentications settings')
    if contains('/etc/ssh/sshd_config', 'PasswordAuthentication yes'):
        uncomment('/etc/ssh/sshd_config', 'PasswordAuthentication yes', use_sudo=True)


def disable_password_authentication():
    print ('Disable password authentication')
    enable_password_authentication_settings()
    sed('/etc/ssh/sshd_config', 'PasswordAuthentication yes', 'PasswordAuthentication no')


def tell_key_does_not_need_password(username):
    print ('Tell key does not need password')
    condition = '{name} ALL=(ALL) NOPASSWD: ALL'.format(name=username)
    if not contains('/etc/sudoers', condition):
        append('/etc/sudoers',condition, use_sudo=True)


def authorize_keys():
    print ('Authorize keys')
    uncomment('/etc/ssh/sshd_config', '#AuthorizedKeysFile', use_sudo=True)


def prepare_keys_directory(username):
    print ('Prepare keys directory')
    sudo('mkdir -p /home/{name}/.ssh'.format(name=username))


def tell_user_own_key(username):
    print ('Tell that the user owns the key')
    sudo('chown {name} /home/{name}/.ssh/authorized_keys'.format(name=username))


def upload_key_for_user(username, key_path):
    print ('Upload key for user', username, key_path)
    # TODO: Instead of overwriting the keys, I should append if not already present
    put(key_path, '/home/{name}/.ssh/authorized_keys'.format(name=username))


def create_user(username):
    print('Create user')
    sudo('id -u {name} &>/dev/null || useradd --user-group --create-home --shell /bin/bash {name} || true'.format(name=username))


def restart_ssh():
    print ('Restart ssh')
    sudo('service ssh restart')


@task
def setup_docker_with_deploy_user():
    """
    Install docker and setup a 'deploy' user
    """
    print ('Setup Docker with "deploy" user')
    install_docker()
    docker_user = 'deploy'
    create_user(docker_user)
    setup_docker_user(docker_user)


def install_docker():
    print ('Install Docker')
    sudo('curl -sSL https://get.docker.com/ | sh')

@task
def setup_docker_compose():
    """
    Install Docker Compose
    """
    print('Install Docker-Compose')
    docker_compose_version = '1.8.0'
    sudo('sh -c "curl -L https://github.com/docker/compose/releases/download/{0}/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose"'.format(docker_compose_version))
    sudo('chmod +x /usr/local/bin/docker-compose')
    sudo('sh -c "curl -L https://raw.githubusercontent.com/docker/compose/{0}/contrib/completion/bash/docker-compose > /etc/bash_completion.d/docker-compose"'.format(docker_compose_version))


def setup_docker_user(username):
    print ('Setup Docker user')
    sudo('usermod -aG docker {name}'.format(name=username))
