# README

Microhubs-controller is an application that controls the opening and closing of microhubs, this data is shared with operators of shared mobility via MDS /stops

# How to deploy?

Build api with:

1. `docker build -t registry.gitlab.com/bikedashboard/microhubs-controller:<version_number> .` (see kubernetes deployment or https://gitlab.com/bikedashboard/dashboard-api/container_registry/387535 for the previous version, or run `kubectl edit deployment microhubs-controller` and check `template.spec.image`).

2. `docker push registry.gitlab.com/bikedashboard/microhubs-controller:<version_number>` (make sure you are logged in to gitlab registry)

3. edit deployement with `kubectl edit deployment microhubs-controller` replace version_number with the new version number.

In example:

    docker build -t registry.gitlab.com/bikedashboard/microhubs-controller:1.3.0 .

    docker push registry.gitlab.com/bikedashboard/microhubs-controller:1.3.0

    kubectl edit deployment microhubs-controller # And change version to 1.3.0

## How to install

Install go, see https://go.dev/doc/install

Install redis, i.e. `sudo apt-get install redis`

Install tile38, i.e. https://github.com/tidwall/tile38/releases

Run:

    export DEV=false
    export DB_NAME=deelfietsdashboard
    export DB_USER=deelfietsdashboard
    export DB_HOST=localhost
    export DB_PASSWORD=6iDMdFVz6iDMdFVz
    export REDIS_HOST=localhost:6379
    export TILE38_HOST=localhost:9851

Or put these ^ in a .env file and do `source .env`.

- Install Python 3.9:

    sudo apt-get install python3.9 python3.9-dev python3.9-venv

- Create an Python environment:

    python3.9 -m venv ENV

- Go into this environment:

    source ENV/bin/activate

- Install some other things:

    pip install --upgrade pip
    pip install --upgrade setuptools

- Install dependencies:

    pip install -r requirements.txt

## How to run

Start postgres.

Start redis-server:

    redis-server

Start tile38-server:

    ./tile38-server --appendonly no

Run:

    export DEV=false
    export DB_NAME=deelfietsdashboard
    export DB_USER=deelfietsdashboard
    export DB_HOST=localhost
    export DB_PASSWORD=x
    export REDIS_HOST=localhost:6379
    export TILE38_HOST=localhost:9851
    
    source .env
    source ENV/bin/activate
    python main.py

## Questions?

Email to info@deelfietsdashboard.nl
