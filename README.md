# Remote server setup

A docker image and Python Fabric scripts to setup a new remote server.

I am using it against OVH, but it should work in AWS EC2 too.

## Running in interactive mode

If you run in your terminal
```bash
docker-compose run --rm deployment
```
you will be left in a session where you can get a list of the fabric commands with a
```bash
fab -l
```

## Development

If you want to make some changes and version it, [bumpversion](https://pypi.python.org/pypi/bumpversion) is configured

```bash
bumpversion patch
```
