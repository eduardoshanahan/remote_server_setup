# Remote server setup

A docker image and Python Fabric scripts to setup a new remote server.

I am using it against OVH, but it should work in AWS EC2 too.

## Running in interactive mode

If you run in your terminal
```bash
docker-compose -f docker-compose.yml -f interactive.yml run --rm execute
```
you will be left in a session where you can get a list of the fabric commands with a
```bash
fab -l
```

## Checking environment variables

Running
```bash
docker-compose run --rm execute
```
Should print the value contained in the environment variable REMOTE_USERNAME.

## Running a local test

Running
```bash
docker-compose -f docker-compose.yml -f local_test.yml run --rm execute
```
will print the REMOTE_USERNAME environment variable received inside the container.

## Running a remote test with root username and password

Running
```bash
docker-compose -f docker-compose.yml -f root_remote_test.yml run --rm execute
```
will try to connect to the remote server and get the OS name providing a root username and password.

## Prepare a new server with key authentication and Docker providing root username and password

Running
```bash
docker-compose -f docker-compose.yml -f prepare_new_server.yml run --rm execute
```
will try to connect to the remote server providing a root username and password, setting up an ssh key authentication and installing Docker.

## Running a remote test using a key

Running
```bash
docker-compose -f docker-compose.yml -f key_remote_test.yml run --rm execute
```
will try to connect to the remote server and get the OS name providing an authentication key.

## Automated deployment

```bash
fab -u your_remote_root_username -p your_remote_password -H your_remote_host_address prepare_new_server
```

## Managing your environment variables

For this scripts to work, you need to have a .env file located in the same directory as your docker-compose files.

A demo with the variables required is available as ```demo.env```. You can make a copy naming it ```.env``` and replacing the values with your own details.

Given the content of that file is private, and allows full control of your remote server, it is included in the .gitignore file, to keep it out of version control. At some point I will rework this area to use [Vault](https://www.vaultproject.io/) or something similar.

## Development

If you want to make some changes and version it, [bumpversion](https://pypi.python.org/pypi/bumpversion) is configured

```bash
bumpversion patch
```
