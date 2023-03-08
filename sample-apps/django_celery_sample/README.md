# Django and Celery Sample App

This is a minimal Django and Celery app for testing the judoscale package.

## Prerequisites

- Python 3.8+
- [Poetry 1.3+](https://python-poetry.org/)
- Node
- [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
- Redis

## Set up the app

```sh
$ poetry install
```

This will install the dependencies, including `judoscale` as a [path dependency](https://python-poetry.org/docs/dependency-specification/#path-dependencies).

## Run the app

Run `bin/dev` to run the app in development mode. This will run `heroku local`, which starts:

- a [tiny proxy server](https://github.com/judoscale/judoscale-adapter-proxy-server) that adds the `X-Request-Start` request header so we can test request queue time reporting; and
- the Django sample app.

## How to use this sample app

Open https://requestinspector.com/p/judoscale-django-celery in a browser. The sample app is configured to use this Request Catcher endpoint as a mock for the Judoscale Adapter API. This page will monitor all API requests sent from the adapter.

Start the app via `./bin/dev`, then open http://localhost:5000. Clicking on "Add task" will enqueue a task that sleeps between 3 and 5 seconds and then returns the sum of its arguments. The task is enqueued randomly to either the `high` queue or the `low` queue. You will see Judoscale Adapter API requests logged in Request Catcher.
