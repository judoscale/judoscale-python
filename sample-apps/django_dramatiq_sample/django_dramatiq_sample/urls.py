from blog.views import index, many_tasks, one_task
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("", index, name="index"),
    path("task", one_task, name="one_task"),
    path("batch_task", many_tasks, name="many_tasks"),
    path("admin/", admin.site.urls),
]
