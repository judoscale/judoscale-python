# Flask Sample App

This is a minimal Django app to test the judoscale-python package.

## Prerequisites

- Python 3
- Node
- [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)

## Set up the app

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run the app

Run `bin/dev` to run the app in development mode. This will...

- Install the local judoscale-python package so unpublished changes can be tested.
- Use `heroku local` and a `Procfile` to start the following processes:
  - A [tiny proxy server](https://github.com/judoscale/judoscale-adapter-proxy-server) that adds the `X-Request-Start` request header so we can test request queue time reporting.
  - The Django sample app.

## How to use this sample app

Open https://judoscale-django.requestcatcher.com in a browser. The sample app is configured to use this Request Catcher endpoint as a mock for the Judoscale Adapter API. This page will monitor all API requests sent from the adapter.

Start the app via `bin/dev`, then open http://localhost:5000. Continue to reload this page to collect and report more request metrics. You will see Judoscale Adatper API requests logged in Request Catcher.

## How to run the local flask tests

From the `sample_apps/flask_sample` directory, run
```
python -m unittest tests
```
