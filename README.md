# Remote server setup

A docker image and Python Fabric scripts to setup a new remote server.

I am using it against OVH, but it should work in AWS EC2 too.

## Running in interactive mode

If you run in your terminal
```bash
docker-compose -f docker-compose.yml -f docker-compose.interactive.yml run --rm execute
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
docker-compose -f docker-compose.yml -f docker-compose.local_test.yml run --rm execute
```
will print the REMOTE_USERNAME environment variable received inside the container.

## Running a remote test with root username and password

Running
```bash
docker-compose -f docker-compose.yml -f docker-compose.root_remote_test.yml run --rm execute
```
will try to connect to the remote server and get the OS name providing a root username and password.

## Running a remote test using a key

Running
```bash
docker-compose -f docker-compose.yml -f docker-compose.key_remote_test.yml run --rm execute
```
will try to connect to the remote server and get the OS name providing an authentication key.

## Automated deployment

```bash
fab -u your_remote_root_username -p your_remote_password -H your_remote_host_address prepare_new_server
```

## Development

If you want to make some changes and version it, [bumpversion](https://pypi.python.org/pypi/bumpversion) is configured

```bash
bumpversion patch
```
