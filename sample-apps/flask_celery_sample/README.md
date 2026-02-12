# Flask Celery Sample App

This is a minimal Flask and Celery app for testing the judoscale package.

## Prerequisites

- Python 3.10+
- [Poetry 1.8+](https://python-poetry.org/)
- Node
- [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
- Redis

## Set up the app

```
$ poetry install
```

This will install the dependencies, including `judoscale` as a [path dependency](https://python-poetry.org/docs/dependency-specification/#path-dependencies).

## Run the app

Run `bin/dev` to start:

- a [tiny proxy server](https://github.com/judoscale/judoscale-adapter-proxy-server) that adds the `X-Request-Start` request header so we can test request queue time reporting; and
- the sample app for testing Celery with Flask.

## How to use this sample app

Open https://judoscale-python.requestcatcher.com in a browser. The sample app is configured to use this Request Catcher endpoint as a mock for the Judoscale Adapter API. This page will monitor all API requests sent from the adapter.

Start the app via `./bin/dev`, then open http://localhost:5006. Clicking on "Add task" will enqueue a task that sleeps between 3 and 5 seconds and then returns the sum of its arguments. The task is enqueued randomly to either the `high` queue or the `low` queue. You will see Judoscale Adapter API requests logged in Request Catcher.
