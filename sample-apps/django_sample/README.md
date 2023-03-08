# Django Sample App

This is a minimal Django app for testing the judoscale package.

## Prerequisites

- Python 3
- Node
- [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)

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

Open https://requestinspector.com/p/judoscale-django in a browser. The sample app is configured to use this Request Catcher endpoint as a mock for the Judoscale Adapter API. This page will monitor all API requests sent from the adapter.

Start the app via `bin/dev`, then open http://localhost:5000. Continue to reload this page to collect and report more request metrics. You will see Judoscale Adatper API requests logged in Request Catcher.

## How to run the local django tests

```sh
$ ./bin/test
```
