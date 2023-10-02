import time

from django.http import HttpResponse
from django.shortcuts import render
from django_rq import job


@job("default")
def search(foo: str):
    print(f"Searching for {foo}...")
    time.sleep(3)
    return f"Found {foo}"


def task(request):
    search.delay("bar")
    return HttpResponse("OK")
